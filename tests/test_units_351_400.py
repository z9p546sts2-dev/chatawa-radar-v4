"""SOFTWARE CORRECTNESS — Phase 5 units 351–400 inspectability."""

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
from radar_v4.name_lock import (
    double_json_scan,
    empty_pack_scan,
    leading_hyphen_scan,
    name_lock,
    reserved_stem_scan,
)
from radar_v4.record_eq import (
    freeze_determinism,
    name_lock_determinism,
    package_identity_determinism,
    path_lock_determinism,
    snapshot_count_bind,
    verify_path_record,
    write_path_record,
)
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


class Units351To400Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("name_lock", "snapshot_count_bind"):
            self.assertTrue(hasattr(package, name), name)
        for relative in ("radar_v4/name_lock.py", "radar_v4/record_eq.py"):
            py_compile(str(ROOT / relative), doraise=True)

    def test_highest_unit_is_400(self) -> None:
        self.assertEqual(PHASE5_HIGHEST_UNIT, 400)
        status = json.loads(workshop_status())
        self.assertEqual(status["highest_unit"], 400)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertEqual(stop["highest_unit"], 400)
        self.assertFalse(stop["vendor_authorized"])

    def test_synthetic_pack_name_and_equality(self) -> None:
        self.assertTrue(name_lock(PACK).valid)
        self.assertTrue(path_lock_determinism(PACK).valid)
        self.assertTrue(name_lock_determinism(PACK).valid)
        self.assertTrue(freeze_determinism(PACK).valid)
        self.assertTrue(package_identity_determinism().valid)
        count = snapshot_count_bind(PACK)
        self.assertTrue(count.valid, count.serialize())
        self.assertEqual(count.details["kept"], 3)
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "path.json"
            written = write_path_record(PACK, path)
            self.assertTrue(written.valid)
            self.assertTrue(verify_path_record(path).valid)

    def test_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            empty = Path(raw) / "empty"
            empty.mkdir()
            self.assertEqual(empty_pack_scan(empty).error_code, "EMPTY_PACK")
            (empty / "con.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual(reserved_stem_scan(empty).error_code, "RESERVED_STEM_REFUSED")
            (empty / "-hidden.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual(leading_hyphen_scan(empty).error_code, "LEADING_HYPHEN_REFUSED")
            (empty / "note.json.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual(double_json_scan(empty).error_code, "DOUBLE_JSON_REFUSED")
            self.assertFalse(name_lock(empty).valid)

    def test_catalogs(self) -> None:
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)

    def test_cli_new_commands(self) -> None:
        for command in (
            ["name-lock", "--pack", str(PACK)],
            ["path-lock-eq", "--pack", str(PACK)],
            ["name-lock-eq", "--pack", str(PACK)],
            ["freeze-eq", "--pack", str(PACK)],
            ["package-eq"],
            ["snapshot-count", "--pack", str(PACK)],
            ["compare-path-lock", "--left", str(PACK), "--right", str(PACK)],
        ):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(command)
            self.assertEqual(code, 0, f"{command} {stderr.getvalue()}")
            self.assertIn("document_kind", json.loads(stdout.getvalue()))


if __name__ == "__main__":
    unittest.main()
