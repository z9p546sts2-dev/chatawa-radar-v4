"""SOFTWARE CORRECTNESS — Phase 5 units 1151–1200 inspectability."""

from __future__ import annotations

import importlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.cadence_bind import (
    cadence_bind,
    cadence_bind_determinism,
    cadence_bind_status,
    verify_cadence_bind_record,
    write_cadence_bind_record,
)
from radar_v4.cadence_lock import (
    cadence_lock,
    cadence_lock_determinism,
    cadence_status_bind,
    compare_cadence_lock,
    verify_cadence_record,
    write_cadence_record,
)
from radar_v4.catalog_audit import audit_document_kinds, audit_reason_catalog
from radar_v4.cli import main
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


def _write_cadence(path: Path, interval: str, evaluation: str) -> None:
    path.write_text(
        json.dumps(
            {
                "document_kind": "radar_v4.cadence",
                "evaluation_cadence": evaluation,
                "interval": interval,
            },
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )


class Units1151To1200Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("cadence_lock", "cadence_bind", "compare_cadence_lock"):
            self.assertTrue(hasattr(package, name), name)
        py_compile(str(ROOT / "radar_v4/cadence_lock.py"), doraise=True)
        py_compile(str(ROOT / "radar_v4/cadence_bind.py"), doraise=True)

    def test_highest_unit_is_1200(self) -> None:
        self.assertGreaterEqual(PHASE5_HIGHEST_UNIT, 1200)
        status = json.loads(workshop_status())
        self.assertGreaterEqual(status["highest_unit"], 1200)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertGreaterEqual(stop["highest_unit"], 1200)
        self.assertFalse(stop["vendor_authorized"])

    def test_matching_cadence_binds_and_overrun_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            daily = root / "daily.json"
            copy = root / "copy.json"
            _write_cadence(daily, "1d", "1d")
            _write_cadence(copy, "1d", "1d")
            self.assertTrue(cadence_lock(daily).valid)
            self.assertTrue(cadence_lock_determinism(daily).valid)
            self.assertTrue(compare_cadence_lock(daily, copy).valid)
            self.assertTrue(cadence_status_bind(daily).valid)
            self.assertTrue(cadence_bind(daily, PACK).valid)
            self.assertTrue(cadence_bind_determinism(daily, PACK).valid)
            self.assertTrue(cadence_bind_status(daily, PACK).valid)
            record = root / "cadence-lock.json"
            self.assertTrue(write_cadence_record(daily, record).valid)
            self.assertTrue(verify_cadence_record(record).valid)
            bind_path = root / "cadence-bind.json"
            self.assertTrue(write_cadence_bind_record(daily, PACK, bind_path).valid)
            self.assertTrue(verify_cadence_bind_record(bind_path).valid)
            overrun = root / "overrun.json"
            _write_cadence(overrun, "1d", "1m")
            refused = cadence_lock(overrun)
            self.assertFalse(refused.valid)
            self.assertEqual(refused.error_code, "CADENCE_OVERRUN")
            bind_refused = cadence_bind(overrun, PACK)
            self.assertFalse(bind_refused.valid)
            self.assertEqual(bind_refused.error_code, "CADENCE_OVERRUN")

    def test_pack_interval_mismatch_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            hourly = root / "hourly.json"
            _write_cadence(hourly, "1h", "1h")
            self.assertTrue(cadence_lock(hourly).valid)
            bind = cadence_bind(hourly, PACK)
            self.assertFalse(bind.valid)
            self.assertEqual(bind.error_code, "CADENCE_MISMATCH")

    def test_refusals(self) -> None:
        missing = cadence_lock(Path("/workspace/.radar-v4-missing-cadence.json"))
        self.assertFalse(missing.valid)
        self.assertEqual(missing.error_code, "CADENCE_MISSING")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.assertEqual(cadence_lock(root).error_code, "CADENCE_MISSING")
            unknown = root / "unknown.json"
            _write_cadence(unknown, "1d", "tick")
            self.assertEqual(cadence_lock(unknown).error_code, "CADENCE_UNKNOWN")
            fabricated = root / "fabricated.json"
            fabricated.write_text(
                '{"document_kind":"radar_v4.cadence_lock","valid":true}\n',
                encoding="utf-8",
            )
            fake = verify_cadence_record(fabricated)
            self.assertFalse(fake.valid)
            self.assertEqual(fake.error_code, "CADENCE_RECORD_INVALID")
            fake_bind = root / "fabricated-bind.json"
            fake_bind.write_text(
                '{"document_kind":"radar_v4.cadence_bind","valid":true}\n',
                encoding="utf-8",
            )
            bind_check = verify_cadence_bind_record(fake_bind)
            self.assertFalse(bind_check.valid)
            self.assertEqual(bind_check.error_code, "CADENCE_BIND_INVALID")

    def test_catalogs_and_cli(self) -> None:
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            daily = root / "daily.json"
            other = root / "other.json"
            _write_cadence(daily, "1d", "1d")
            _write_cadence(other, "1d", "1d")
            commands = (
                ["cadence-lock", "--path", str(daily)],
                ["cadence-eq", "--path", str(daily)],
                ["compare-cadence", "--left", str(daily), "--right", str(other)],
                ["cadence-status", "--path", str(daily)],
                ["cadence-bind", "--cadence", str(daily), "--pack", str(PACK)],
                ["cadence-bind-eq", "--cadence", str(daily), "--pack", str(PACK)],
                ["cadence-bind-status", "--cadence", str(daily), "--pack", str(PACK)],
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
