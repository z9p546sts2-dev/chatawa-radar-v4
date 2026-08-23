"""SOFTWARE CORRECTNESS — Phase 5 units 401–450 inspectability."""

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
from radar_v4.kind_lock import (
    kind_describe,
    kind_lock,
    unlabeled_kind_scan,
    unknown_kind_scan,
    unreadable_kind_scan,
)
from radar_v4.record_eq import compare_name_lock, verify_name_record, write_name_record
from radar_v4.stamp import (
    export_name_check,
    name_status_bind,
    stamp_determinism,
    verify_stamp_record,
    workshop_stamp,
    write_stamp_record,
)
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


class Units401To450Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("kind_lock", "workshop_stamp"):
            self.assertTrue(hasattr(package, name), name)
        for relative in ("radar_v4/kind_lock.py", "radar_v4/stamp.py"):
            py_compile(str(ROOT / relative), doraise=True)

    def test_highest_unit_is_at_least_450(self) -> None:
        self.assertGreaterEqual(PHASE5_HIGHEST_UNIT, 450)
        status = json.loads(workshop_status())
        self.assertGreaterEqual(status["highest_unit"], 450)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertGreaterEqual(stop["highest_unit"], 450)
        self.assertFalse(stop["vendor_authorized"])

    def test_synthetic_pack_kind_and_stamp(self) -> None:
        self.assertTrue(kind_lock(PACK).valid)
        described = kind_describe(PACK)
        self.assertTrue(described.valid)
        names = {item["name"] for item in described.details["files"]}
        self.assertIn("declaration.json", names)
        self.assertTrue(workshop_stamp(PACK).valid)
        self.assertTrue(stamp_determinism(PACK).valid)
        self.assertTrue(compare_name_lock(PACK, PACK).valid)
        self.assertTrue(name_status_bind(PACK).valid)
        with tempfile.TemporaryDirectory() as raw:
            name_path = Path(raw) / "name.json"
            written_name = write_name_record(PACK, name_path)
            self.assertTrue(written_name.valid)
            self.assertTrue(verify_name_record(name_path).valid)
            stamp_path = Path(raw) / "stamp.json"
            written_stamp = write_stamp_record(PACK, stamp_path)
            self.assertTrue(written_stamp.valid)
            self.assertTrue(verify_stamp_record(stamp_path).valid)
            exported = export_name_check(PACK, Path(raw) / "export")
            self.assertTrue(exported.valid, exported.serialize())

    def test_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            pack = Path(raw)
            (pack / "note.json").write_text('{"hello":"world"}\n', encoding="utf-8")
            self.assertEqual(unlabeled_kind_scan(pack).error_code, "UNLABELED_KIND_REFUSED")
            (pack / "weird.json").write_text(
                '{"document_kind":"radar_v4.not_a_real_kind"}\n',
                encoding="utf-8",
            )
            self.assertEqual(unknown_kind_scan(pack).error_code, "UNKNOWN_DOCUMENT_KIND")
            (pack / "broken.json").write_text("{not json\n", encoding="utf-8")
            self.assertEqual(unreadable_kind_scan(pack).error_code, "UNREADABLE_JSON")
            self.assertFalse(kind_lock(pack).valid)

    def test_catalogs(self) -> None:
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)

    def test_cli_new_commands(self) -> None:
        for command in (
            ["kind-lock", "--pack", str(PACK)],
            ["kind-describe", "--pack", str(PACK)],
            ["stamp", "--pack", str(PACK)],
            ["stamp-eq", "--pack", str(PACK)],
            ["compare-stamp", "--left", str(PACK), "--right", str(PACK)],
            ["compare-name-lock", "--left", str(PACK), "--right", str(PACK)],
            ["name-bind", "--pack", str(PACK)],
        ):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(command)
            self.assertEqual(code, 0, f"{command} {stderr.getvalue()}")
            self.assertIn("document_kind", json.loads(stdout.getvalue()))


if __name__ == "__main__":
    unittest.main()
