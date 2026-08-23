"""SOFTWARE CORRECTNESS — Phase 5 units 801–850 inspectability."""

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

from radar_v4.catalog_audit import audit_document_kinds, audit_reason_catalog
from radar_v4.cli import main
from radar_v4.leftover_lock import (
    compare_leftover_lock,
    leftover_lock,
    leftover_lock_determinism,
    leftover_status_bind,
    verify_leftover_record,
    write_leftover_record,
)
from radar_v4.safety_lock import (
    compare_safety_lock,
    safety_lock,
    safety_lock_determinism,
    safety_status_bind,
    verify_safety_record,
    write_safety_record,
)
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


class Units801To850Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("safety_lock", "leftover_lock"):
            self.assertTrue(hasattr(package, name), name)
        for relative in ("radar_v4/safety_lock.py", "radar_v4/leftover_lock.py"):
            py_compile(str(ROOT / relative), doraise=True)

    def test_highest_unit_is_850(self) -> None:
        self.assertEqual(PHASE5_HIGHEST_UNIT, 850)
        status = json.loads(workshop_status())
        self.assertEqual(status["highest_unit"], 850)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertEqual(stop["highest_unit"], 850)
        self.assertFalse(stop["vendor_authorized"])

    def test_synthetic_safety_and_leftover(self) -> None:
        self.assertTrue(safety_lock(PACK).valid)
        self.assertTrue(safety_lock_determinism(PACK).valid)
        self.assertTrue(compare_safety_lock(PACK, PACK).valid)
        self.assertTrue(safety_status_bind(PACK).valid)
        self.assertTrue(leftover_lock(PACK).valid)
        self.assertTrue(leftover_lock_determinism(PACK).valid)
        self.assertTrue(compare_leftover_lock(PACK, PACK).valid)
        self.assertTrue(leftover_status_bind(PACK).valid)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            safety_path = root / "safety-lock.json"
            written = write_safety_record(PACK, safety_path)
            self.assertTrue(written.valid)
            self.assertTrue(verify_safety_record(safety_path).valid)
            leftover_path = root / "leftover-lock.json"
            written_leftover = write_leftover_record(PACK, leftover_path)
            self.assertTrue(written_leftover.valid)
            self.assertTrue(verify_leftover_record(leftover_path).valid)
            fabricated = root / "fabricated.json"
            fabricated.write_text(
                '{"document_kind":"radar_v4.safety_lock","valid":true}\n',
                encoding="utf-8",
            )
            fake = verify_safety_record(fabricated)
            self.assertFalse(fake.valid)
            self.assertEqual(fake.error_code, "SAFETY_RECORD_INVALID")
            leftover_fake = root / "leftover-fabricated.json"
            leftover_fake.write_text(
                '{"document_kind":"radar_v4.leftover_lock","valid":true}\n',
                encoding="utf-8",
            )
            leftover_check = verify_leftover_record(leftover_fake)
            self.assertFalse(leftover_check.valid)
            self.assertEqual(leftover_check.error_code, "LEFTOVER_RECORD_INVALID")
            stale = root / "stale"
            copytree(PACK, stale)
            stale_record = root / "stale-leftover.json"
            self.assertTrue(write_leftover_record(stale, stale_record).valid)
            (stale / "foo.tmp").write_text("leftover\n", encoding="utf-8")
            stale_verify = verify_leftover_record(stale_record)
            self.assertFalse(stale_verify.valid)

    def test_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            bom = root / "bom"
            copytree(PACK, bom)
            (bom / "declaration.json").write_bytes(
                b"\xef\xbb\xbf" + (bom / "declaration.json").read_bytes()
            )
            self.assertEqual(safety_lock(bom).error_code, "PACK_BOM")
            nested = root / "nested"
            copytree(PACK, nested)
            subdir = nested / "subdir"
            subdir.mkdir()
            (subdir / "x.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual(safety_lock(nested).error_code, "PACK_NESTED_JSON")
            tmp = root / "tmp"
            copytree(PACK, tmp)
            (tmp / "foo.tmp").write_text("leftover\n", encoding="utf-8")
            self.assertEqual(leftover_lock(tmp).error_code, "PACK_TMP_LEFTOVER")
            orphan = root / "orphan"
            copytree(PACK, orphan)
            (orphan / "missing.json.sha256").write_text("00" * 32 + "\n", encoding="utf-8")
            self.assertEqual(leftover_lock(orphan).error_code, "SIDECAR_ORPHAN")

    def test_catalogs(self) -> None:
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)

    def test_cli_new_commands(self) -> None:
        commands = (
            ["safety-lock", "--pack", str(PACK)],
            ["safety-eq", "--pack", str(PACK)],
            ["compare-safety-lock", "--left", str(PACK), "--right", str(PACK)],
            ["safety-status", "--pack", str(PACK)],
            ["leftover-lock", "--pack", str(PACK)],
            ["leftover-eq", "--pack", str(PACK)],
            ["compare-leftover-lock", "--left", str(PACK), "--right", str(PACK)],
            ["leftover-status", "--pack", str(PACK)],
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
