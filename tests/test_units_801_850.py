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

from radar_v4.audit_lock import verify_audit_record
from radar_v4.bind_check import verify_byte_record
from radar_v4.bundle_lock import verify_bundle_record
from radar_v4.catalog_audit import audit_document_kinds, audit_reason_catalog
from radar_v4.chain_lock import verify_chain_record
from radar_v4.cli import main
from radar_v4.disp_lock import verify_disposition_record
from radar_v4.export_lock import verify_export_record
from radar_v4.freeze import verify_freeze_record
from radar_v4.journal_lock import verify_journal_record
from radar_v4.record_eq import verify_name_record, verify_path_record
from radar_v4.report_lock import verify_report_record
from radar_v4.ruler_lock import verify_ruler_record
from radar_v4.sidecar_lock import verify_sidecar_record
from radar_v4.snapshot_lock import verify_snapshot_record
from radar_v4.stamp import verify_kind_record, verify_stamp_record
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
        self.assertGreaterEqual(PHASE5_HIGHEST_UNIT, 850)
        status = json.loads(workshop_status())
        self.assertGreaterEqual(status["highest_unit"], 850)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertGreaterEqual(stop["highest_unit"], 850)
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

    def test_remaining_verify_refuses_kind_valid_only(self) -> None:
        cases = (
            (verify_audit_record, "radar_v4.audit_lock", "AUDIT_RECORD_INVALID"),
            (verify_bundle_record, "radar_v4.bundle_lock", "BUNDLE_RECORD_INVALID"),
            (verify_byte_record, "radar_v4.byte_check", "BYTE_RECORD_INVALID"),
            (verify_chain_record, "radar_v4.chain_lock", "CHAIN_RECORD_INVALID"),
            (verify_disposition_record, "radar_v4.disposition_lock", "DISPOSITION_RECORD_INVALID"),
            (verify_export_record, "radar_v4.export_lock", "EXPORT_RECORD_INVALID"),
            (verify_freeze_record, "radar_v4.freeze", "FREEZE_FAILED"),
            (verify_journal_record, "radar_v4.journal_lock", "JOURNAL_RECORD_INVALID"),
            (verify_kind_record, "radar_v4.kind_lock", "KIND_RECORD_INVALID"),
            (verify_name_record, "radar_v4.name_lock", "NAME_RECORD_INVALID"),
            (verify_path_record, "radar_v4.path_lock", "PATH_RECORD_INVALID"),
            (verify_report_record, "radar_v4.report_lock", "REPORT_RECORD_INVALID"),
            (verify_ruler_record, "radar_v4.ruler_lock", "RULER_RECORD_INVALID"),
            (verify_sidecar_record, "radar_v4.sidecar_lock", "SIDECAR_RECORD_INVALID"),
            (verify_snapshot_record, "radar_v4.snapshot_lock", "SNAPSHOT_RECORD_INVALID"),
            (verify_stamp_record, "radar_v4.workshop_stamp", "STAMP_RECORD_INVALID"),
        )
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for verify, kind, code in cases:
                path = root / f"{kind.replace('.', '_')}.json"
                path.write_text(
                    json.dumps({"document_kind": kind, "valid": True}) + "\n",
                    encoding="utf-8",
                )
                check = verify(path)
                self.assertFalse(check.valid, kind)
                self.assertEqual(check.error_code, code, kind)


if __name__ == "__main__":
    unittest.main()
