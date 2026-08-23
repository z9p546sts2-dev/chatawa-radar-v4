"""SOFTWARE CORRECTNESS — Phase 5 units 301–350 inspectability."""

from __future__ import annotations

import importlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from py_compile import compile as py_compile
from shutil import copytree

from radar_v4.bind_check import (
    close_sign_describe,
    export_byte_check,
    freeze_status_bind,
    journal_code_catalog,
    retrieval_unique_describe,
    verify_byte_record,
    write_byte_record,
)
from radar_v4.catalog_audit import audit_document_kinds, audit_reason_catalog
from radar_v4.cli import main
from radar_v4.local_session import run_session_from_pack
from radar_v4.path_lock import backup_leftover_scan, path_lock, space_name_scan
from radar_v4.quarantine_journal import write_quarantine_journal_file
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


class Units301To350Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("path_lock", "freeze_status_bind"):
            self.assertTrue(hasattr(package, name), name)
        for relative in ("radar_v4/path_lock.py", "radar_v4/bind_check.py"):
            py_compile(str(ROOT / relative), doraise=True)

    def test_highest_unit_is_at_least_350(self) -> None:
        self.assertGreaterEqual(PHASE5_HIGHEST_UNIT, 350)
        status = json.loads(workshop_status())
        self.assertGreaterEqual(status["highest_unit"], 350)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertGreaterEqual(stop["highest_unit"], 350)
        self.assertFalse(stop["vendor_authorized"])

    def test_synthetic_pack_path_and_bind(self) -> None:
        self.assertTrue(path_lock(PACK).valid)
        signs = close_sign_describe(PACK)
        self.assertEqual(signs.details["negatives"], 0)
        self.assertEqual(retrieval_unique_describe(PACK).details["count"], 0)
        bind = freeze_status_bind(PACK)
        self.assertTrue(bind.valid, bind.serialize())
        result = run_session_from_pack(PACK)
        with tempfile.TemporaryDirectory() as raw:
            journal = Path(raw) / "journal.json"
            write_quarantine_journal_file(journal, local=result)
            self.assertTrue(journal_code_catalog(journal).valid)
            byte_path = Path(raw) / "byte.json"
            written = write_byte_record(PACK, byte_path)
            self.assertTrue(written.valid)
            self.assertTrue(verify_byte_record(byte_path).valid)
            exported = Path(raw) / "exported"
            export_check = export_byte_check(PACK, exported)
            self.assertTrue(export_check.valid, export_check.serialize())

    def test_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            copied = Path(raw) / "copy"
            copytree(PACK, copied)
            (copied / "note.bak").write_text("x", encoding="utf-8")
            self.assertEqual(backup_leftover_scan(copied).error_code, "BACKUP_LEFTOVER")
            (copied / "bad name.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual(space_name_scan(copied).error_code, "SPACE_IN_NAME")
            self.assertFalse(path_lock(copied).valid)
            unknown = Path(raw) / "unknown.json"
            unknown.write_text(
                '{"document_kind":"radar_v4.quarantine_journal","entries":[{"code":"NOT_A_REAL_CODE","reason":"x","source":"pack"}],"journal_version":1,"refusal_count":1}\n',
                encoding="utf-8",
            )
            self.assertEqual(journal_code_catalog(unknown).error_code, "CODE_UNKNOWN")

    def test_catalogs(self) -> None:
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)

    def test_cli_new_commands(self) -> None:
        for command in (
            ["path-lock", "--pack", str(PACK)],
            ["close-sign", "--pack", str(PACK)],
            ["retrieval-unique", "--pack", str(PACK)],
            ["freeze-bind", "--pack", str(PACK)],
        ):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(command)
            self.assertEqual(code, 0, f"{command} {stderr.getvalue()}")
            self.assertIn("document_kind", json.loads(stdout.getvalue()))


if __name__ == "__main__":
    unittest.main()
