"""SOFTWARE CORRECTNESS — Phase 5 units 501–550 inspectability."""

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
from radar_v4.local_session import run_session_from_pack
from radar_v4.report_lock import (
    report_checksum_scan,
    report_kind_scan,
    report_lock,
    report_lock_determinism,
    report_measured_scan,
    report_status_bind,
    verify_report_record,
    write_report_record,
)
from radar_v4.ruler_lock import (
    compare_ruler_lock,
    pack_ruler_lock,
    report_ruler_bind,
    ruler_lock_determinism,
    verify_ruler_record,
    write_ruler_record,
)
from radar_v4.session_report import (
    serialize_admission_report,
    write_local_session_report_file,
)
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


def _write_local_report(directory: Path) -> Path:
    result = run_session_from_pack(PACK)
    path = directory / "report.json"
    write_local_session_report_file(path, result)
    return path


class Units501To550Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("report_lock", "pack_ruler_lock"):
            self.assertTrue(hasattr(package, name), name)
        for relative in ("radar_v4/report_lock.py", "radar_v4/ruler_lock.py"):
            py_compile(str(ROOT / relative), doraise=True)

    def test_highest_unit_is_550(self) -> None:
        self.assertEqual(PHASE5_HIGHEST_UNIT, 550)
        status = json.loads(workshop_status())
        self.assertEqual(status["highest_unit"], 550)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertEqual(stop["highest_unit"], 550)
        self.assertFalse(stop["vendor_authorized"])

    def test_synthetic_report_and_ruler(self) -> None:
        self.assertTrue(pack_ruler_lock(PACK).valid)
        self.assertTrue(ruler_lock_determinism(PACK).valid)
        self.assertTrue(compare_ruler_lock(PACK, PACK).valid)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            report = _write_local_report(root)
            self.assertTrue(report_kind_scan(report).valid)
            self.assertTrue(report_checksum_scan(report).valid)
            self.assertTrue(report_measured_scan(report).valid)
            locked = report_lock(report)
            self.assertTrue(locked.valid, locked.serialize())
            self.assertTrue(report_lock_determinism(report).valid)
            self.assertTrue(report_status_bind(report).valid)
            bind = report_ruler_bind(report, PACK)
            self.assertTrue(bind.valid, bind.serialize())
            record_path = root / "report-lock.json"
            written = write_report_record(report, record_path)
            self.assertTrue(written.valid)
            self.assertTrue(verify_report_record(record_path).valid)
            ruler_path = root / "ruler-lock.json"
            written_ruler = write_ruler_record(PACK, ruler_path)
            self.assertTrue(written_ruler.valid)
            self.assertTrue(verify_ruler_record(ruler_path).valid)

    def test_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            unlabeled = root / "unlabeled.json"
            unlabeled.write_text('{"snapshot_checksum":"abc"}\n', encoding="utf-8")
            self.assertEqual(report_kind_scan(unlabeled).error_code, "REPORT_KIND_REFUSED")
            missing = root / "missing.json"
            missing.write_text(
                '{"document_kind":"radar_v4.session_report"}\n',
                encoding="utf-8",
            )
            self.assertEqual(report_checksum_scan(missing).error_code, "REPORT_CHECKSUM_MISSING")
            measured = root / "measured.json"
            result = run_session_from_pack(PACK, measure=False)
            measured.write_text(
                serialize_admission_report(result).replace('"measured":false', '"measured":true')
                + "\n",
                encoding="utf-8",
            )
            self.assertEqual(report_measured_scan(measured).error_code, "REPORT_MEASURED_REFUSED")
            self.assertFalse(report_lock(unlabeled).valid)
            ruler = root / "ruler.json"
            ruler.write_text('{"document_kind":"radar_v4.note"}\n', encoding="utf-8")
            from radar_v4.ruler_lock import ruler_lock

            self.assertEqual(ruler_lock(ruler).error_code, "RULER_KIND_REFUSED")

    def test_catalogs(self) -> None:
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)

    def test_cli_new_commands(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            report = _write_local_report(Path(raw))
            commands = (
                ["report-lock", "--report", str(report)],
                ["report-eq", "--report", str(report)],
                ["compare-report-lock", "--left", str(report), "--right", str(report)],
                ["ruler-lock", "--pack", str(PACK)],
                ["ruler-eq", "--pack", str(PACK)],
                ["compare-ruler-lock", "--left", str(PACK), "--right", str(PACK)],
                ["report-ruler", "--report", str(report), "--pack", str(PACK)],
                ["report-status", "--report", str(report)],
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
