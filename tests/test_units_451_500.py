"""SOFTWARE CORRECTNESS — Phase 5 units 451–500 inspectability."""

from __future__ import annotations

import importlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.catalog_audit import audit_document_kinds, audit_reason_catalog
from radar_v4.cli import main
from radar_v4.journal_lock import (
    journal_entries_scan,
    journal_entry_shape_scan,
    journal_kind_scan,
    journal_lock,
    journal_lock_determinism,
    journal_source_scan,
    verify_journal_record,
    write_journal_record,
)
from radar_v4.local_session import run_session_from_pack
from radar_v4.quarantine_journal import write_quarantine_journal_file
from radar_v4.stamp import (
    compare_kind_lock,
    kind_lock_determinism,
    stamp_status_bind,
    verify_kind_record,
    write_kind_record,
)
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


def _write_clean_journal(directory: Path) -> Path:
    result = run_session_from_pack(PACK)
    path = directory / "journal.json"
    write_quarantine_journal_file(path, local=result)
    return path


class Units451To500Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("journal_lock", "stamp_status_bind"):
            self.assertTrue(hasattr(package, name), name)
        for relative in ("radar_v4/journal_lock.py", "radar_v4/stamp.py"):
            py_compile(str(ROOT / relative), doraise=True)

    def test_highest_unit_is_500(self) -> None:
        self.assertEqual(PHASE5_HIGHEST_UNIT, 500)
        status = json.loads(workshop_status())
        self.assertEqual(status["highest_unit"], 500)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertEqual(stop["highest_unit"], 500)
        self.assertFalse(stop["vendor_authorized"])

    def test_synthetic_journal_and_kind_binds(self) -> None:
        self.assertTrue(kind_lock_determinism(PACK).valid)
        self.assertTrue(compare_kind_lock(PACK, PACK).valid)
        self.assertTrue(stamp_status_bind(PACK).valid)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            journal = _write_clean_journal(root)
            self.assertTrue(journal_kind_scan(journal).valid)
            self.assertTrue(journal_entries_scan(journal).valid)
            self.assertTrue(journal_entry_shape_scan(journal).valid)
            self.assertTrue(journal_source_scan(journal).valid)
            locked = journal_lock(journal)
            self.assertTrue(locked.valid, locked.serialize())
            self.assertTrue(journal_lock_determinism(journal).valid)
            record_path = root / "journal-lock.json"
            written = write_journal_record(journal, record_path)
            self.assertTrue(written.valid)
            self.assertTrue(verify_journal_record(record_path).valid)
            kind_path = root / "kind.json"
            written_kind = write_kind_record(PACK, kind_path)
            self.assertTrue(written_kind.valid)
            self.assertTrue(verify_kind_record(kind_path).valid)

    def test_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            unlabeled = root / "unlabeled.json"
            unlabeled.write_text('{"entries":[]}\n', encoding="utf-8")
            self.assertEqual(journal_kind_scan(unlabeled).error_code, "JOURNAL_KIND_REFUSED")
            bad_entries = root / "bad-entries.json"
            bad_entries.write_text(
                '{"document_kind":"radar_v4.quarantine_journal","entries":{}}\n',
                encoding="utf-8",
            )
            self.assertEqual(journal_entries_scan(bad_entries).error_code, "JOURNAL_ENTRY_INVALID")
            bad_shape = root / "bad-shape.json"
            bad_shape.write_text(
                '{"document_kind":"radar_v4.quarantine_journal","entries":[{"source":"pack"}]}\n',
                encoding="utf-8",
            )
            self.assertEqual(journal_entry_shape_scan(bad_shape).error_code, "JOURNAL_ENTRY_INVALID")
            bad_source = root / "bad-source.json"
            bad_source.write_text(
                '{"document_kind":"radar_v4.quarantine_journal","entries":[{"code":"FILE_EXISTS","source":"broker"}]}\n',
                encoding="utf-8",
            )
            self.assertEqual(journal_source_scan(bad_source).error_code, "JOURNAL_SOURCE_REFUSED")
            self.assertFalse(journal_lock(unlabeled).valid)

    def test_catalogs(self) -> None:
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)

    def test_cli_new_commands(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            journal = _write_clean_journal(Path(raw))
            commands = (
                ["journal-lock", "--journal", str(journal)],
                ["journal-eq", "--journal", str(journal)],
                ["compare-journal-lock", "--left", str(journal), "--right", str(journal)],
                ["kind-lock-eq", "--pack", str(PACK)],
                ["compare-kind-lock", "--left", str(PACK), "--right", str(PACK)],
                ["stamp-bind", "--pack", str(PACK)],
            )
            for command in commands:
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    code = main(command)
                self.assertEqual(code, 0, f"{command} {stderr.getvalue()}")
                self.assertIn("document_kind", json.loads(stdout.getvalue()))


if __name__ == "__main__":
    unittest.main()
