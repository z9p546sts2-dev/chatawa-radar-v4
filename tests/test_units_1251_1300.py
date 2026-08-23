"""SOFTWARE CORRECTNESS — Phase 5 units 1251–1300 inspectability."""

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
from radar_v4.horizon_bind import (
    horizon_bind,
    horizon_bind_determinism,
    horizon_bind_status,
    verify_horizon_bind_record,
    write_horizon_bind_record,
)
from radar_v4.horizon_lock import (
    compare_horizon_lock,
    horizon_lock,
    horizon_lock_determinism,
    horizon_status_bind,
    verify_horizon_record,
    write_horizon_record,
)
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"
LAST_BAR = "2026-08-09T14:00:00.000000+00:00"
EARLIER = "2026-08-07T14:00:00.000000+00:00"
LATER = "2026-08-23T21:00:00.000000+00:00"


def _write_horizon(path: Path, as_of: str, include_through: str) -> None:
    path.write_text(
        json.dumps(
            {
                "as_of": as_of,
                "document_kind": "radar_v4.horizon",
                "include_through": include_through,
            },
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )


class Units1251To1300Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("horizon_lock", "horizon_bind", "compare_horizon_lock"):
            self.assertTrue(hasattr(package, name), name)
        py_compile(str(ROOT / "radar_v4/horizon_lock.py"), doraise=True)
        py_compile(str(ROOT / "radar_v4/horizon_bind.py"), doraise=True)

    def test_highest_unit_is_1300(self) -> None:
        self.assertEqual(PHASE5_HIGHEST_UNIT, 1300)
        status = json.loads(workshop_status())
        self.assertEqual(status["highest_unit"], 1300)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertEqual(stop["highest_unit"], 1300)
        self.assertFalse(stop["vendor_authorized"])

    def test_honest_window_binds_and_lookahead_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            honest = root / "honest.json"
            copy = root / "copy.json"
            _write_horizon(honest, LAST_BAR, LAST_BAR)
            _write_horizon(copy, LAST_BAR, LAST_BAR)
            self.assertTrue(horizon_lock(honest).valid)
            self.assertTrue(horizon_lock_determinism(honest).valid)
            self.assertTrue(compare_horizon_lock(honest, copy).valid)
            self.assertTrue(horizon_status_bind(honest).valid)
            self.assertTrue(horizon_bind(honest, PACK).valid)
            self.assertTrue(horizon_bind_determinism(honest, PACK).valid)
            self.assertTrue(horizon_bind_status(honest, PACK).valid)
            record = root / "horizon-lock.json"
            self.assertTrue(write_horizon_record(honest, record).valid)
            self.assertTrue(verify_horizon_record(record).valid)
            bind_path = root / "horizon-bind.json"
            self.assertTrue(write_horizon_bind_record(honest, PACK, bind_path).valid)
            self.assertTrue(verify_horizon_bind_record(bind_path).valid)
            later_clock = root / "later-clock.json"
            _write_horizon(later_clock, LATER, LAST_BAR)
            self.assertTrue(horizon_lock(later_clock).valid)
            self.assertTrue(horizon_bind(later_clock, PACK).valid)
            window = root / "lookahead-window.json"
            _write_horizon(window, LAST_BAR, LATER)
            refused = horizon_lock(window)
            self.assertFalse(refused.valid)
            self.assertEqual(refused.error_code, "LOOKAHEAD_WINDOW")
            early = root / "early.json"
            _write_horizon(early, EARLIER, EARLIER)
            self.assertTrue(horizon_lock(early).valid)
            bind_refused = horizon_bind(early, PACK)
            self.assertFalse(bind_refused.valid)
            self.assertEqual(bind_refused.error_code, "LOOKAHEAD_BAR")

    def test_refusals(self) -> None:
        missing = horizon_lock(Path("/workspace/.radar-v4-missing-horizon.json"))
        self.assertFalse(missing.valid)
        self.assertEqual(missing.error_code, "HORIZON_MISSING")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.assertEqual(horizon_lock(root).error_code, "HORIZON_MISSING")
            fabricated = root / "fabricated.json"
            fabricated.write_text(
                '{"document_kind":"radar_v4.horizon_lock","valid":true}\n',
                encoding="utf-8",
            )
            fake = verify_horizon_record(fabricated)
            self.assertFalse(fake.valid)
            self.assertEqual(fake.error_code, "HORIZON_RECORD_INVALID")
            fake_bind = root / "fabricated-bind.json"
            fake_bind.write_text(
                '{"document_kind":"radar_v4.horizon_bind","valid":true}\n',
                encoding="utf-8",
            )
            bind_check = verify_horizon_bind_record(fake_bind)
            self.assertFalse(bind_check.valid)
            self.assertEqual(bind_check.error_code, "HORIZON_BIND_INVALID")

    def test_catalogs_and_cli(self) -> None:
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            honest = root / "honest.json"
            other = root / "other.json"
            _write_horizon(honest, LAST_BAR, LAST_BAR)
            _write_horizon(other, LAST_BAR, LAST_BAR)
            commands = (
                ["horizon-lock", "--path", str(honest)],
                ["horizon-eq", "--path", str(honest)],
                ["compare-horizon", "--left", str(honest), "--right", str(other)],
                ["horizon-status", "--path", str(honest)],
                ["horizon-bind", "--horizon", str(honest), "--pack", str(PACK)],
                ["horizon-bind-eq", "--horizon", str(honest), "--pack", str(PACK)],
                ["horizon-bind-status", "--horizon", str(honest), "--pack", str(PACK)],
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
