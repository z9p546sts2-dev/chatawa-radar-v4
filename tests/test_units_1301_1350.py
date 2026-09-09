"""SOFTWARE CORRECTNESS — Phase 5 units 1301–1350 inspectability."""

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
from radar_v4.source_bind import (
    source_bind,
    source_bind_determinism,
    source_bind_status,
    verify_source_bind_record,
    write_source_bind_record,
)
from radar_v4.source_lock import (
    compare_source_lock,
    source_lock,
    source_lock_determinism,
    source_status_bind,
    verify_source_record,
    write_source_record,
)
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


def _write_source(
    path: Path,
    source_name: str = "synthetic.one-symbol.1d",
    provenance: str = "SYNTHETIC",
    authorized: bool = False,
) -> None:
    path.write_text(
        json.dumps(
            {
                "authorized": authorized,
                "document_kind": "radar_v4.source",
                "provenance_class": provenance,
                "source_name": source_name,
            },
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )


class Units1301To1350Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("source_lock", "source_bind", "compare_source_lock"):
            self.assertTrue(hasattr(package, name), name)
        py_compile(str(ROOT / "radar_v4/source_lock.py"), doraise=True)
        py_compile(str(ROOT / "radar_v4/source_bind.py"), doraise=True)

    def test_highest_unit_is_1350(self) -> None:
        self.assertEqual(PHASE5_HIGHEST_UNIT, 1350)
        status = json.loads(workshop_status())
        self.assertEqual(status["highest_unit"], 1350)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        self.assertFalse(status["vendor_authorized"])
        stop = json.loads(workshop_stop_record())
        self.assertEqual(stop["highest_unit"], 1350)
        self.assertFalse(stop["vendor_authorized"])
        self.assertFalse(stop["paper_trading_authorized"])

    def test_named_synthetic_source_binds_and_historical_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            honest = root / "honest.json"
            copy = root / "copy.json"
            _write_source(honest)
            _write_source(copy)
            self.assertTrue(source_lock(honest).valid)
            self.assertTrue(source_lock_determinism(honest).valid)
            self.assertTrue(compare_source_lock(honest, copy).valid)
            self.assertTrue(source_status_bind(honest).valid)
            self.assertTrue(source_bind(honest, PACK).valid)
            self.assertTrue(source_bind_determinism(honest, PACK).valid)
            self.assertTrue(source_bind_status(honest, PACK).valid)
            record = root / "source-lock.json"
            self.assertTrue(write_source_record(honest, record).valid)
            self.assertTrue(verify_source_record(record).valid)
            bind_path = root / "source-bind.json"
            self.assertTrue(write_source_bind_record(honest, PACK, bind_path).valid)
            self.assertTrue(verify_source_bind_record(bind_path).valid)
            unnamed = root / "unnamed.json"
            _write_source(unnamed, source_name="  ")
            refused_name = source_lock(unnamed)
            self.assertFalse(refused_name.valid)
            self.assertEqual(refused_name.error_code, "SOURCE_UNNAMED")
            claimed = root / "claimed.json"
            _write_source(claimed, authorized=True)
            refused_claim = source_lock(claimed)
            self.assertFalse(refused_claim.valid)
            self.assertEqual(refused_claim.error_code, "ADMISSION_CLAIM")
            historical = root / "historical.json"
            _write_source(historical, provenance="HISTORICAL")
            refused_hist = source_lock(historical)
            self.assertFalse(refused_hist.valid)
            self.assertEqual(refused_hist.error_code, "HISTORICAL_ADMISSION_NOT_AUTHORIZED")
            live = root / "live.json"
            _write_source(live, provenance="LIVE")
            refused_live = source_lock(live)
            self.assertFalse(refused_live.valid)
            self.assertEqual(refused_live.error_code, "LIVE_ADMISSION_NOT_AUTHORIZED")
            fixture = root / "fixture.json"
            _write_source(fixture, provenance="FIXTURE")
            self.assertTrue(source_lock(fixture).valid)
            mismatched = source_bind(fixture, PACK)
            self.assertFalse(mismatched.valid)
            self.assertEqual(mismatched.error_code, "SOURCE_MISMATCH")

    def test_refusals(self) -> None:
        missing = source_lock(Path("/workspace/.radar-v4-missing-source.json"))
        self.assertFalse(missing.valid)
        self.assertEqual(missing.error_code, "SOURCE_MISSING")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.assertEqual(source_lock(root).error_code, "SOURCE_MISSING")
            fabricated = root / "fabricated.json"
            fabricated.write_text(
                '{"document_kind":"radar_v4.source_lock","valid":true}\n',
                encoding="utf-8",
            )
            fake = verify_source_record(fabricated)
            self.assertFalse(fake.valid)
            self.assertEqual(fake.error_code, "SOURCE_RECORD_INVALID")
            fake_bind = root / "fabricated-bind.json"
            fake_bind.write_text(
                '{"document_kind":"radar_v4.source_bind","valid":true}\n',
                encoding="utf-8",
            )
            bind_check = verify_source_bind_record(fake_bind)
            self.assertFalse(bind_check.valid)
            self.assertEqual(bind_check.error_code, "SOURCE_BIND_INVALID")

    def test_catalogs_and_cli(self) -> None:
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            honest = root / "honest.json"
            other = root / "other.json"
            _write_source(honest)
            _write_source(other)
            commands = (
                ["source-lock", "--path", str(honest)],
                ["source-eq", "--path", str(honest)],
                ["compare-source", "--left", str(honest), "--right", str(other)],
                ["source-status", "--path", str(honest)],
                ["source-bind", "--source", str(honest), "--pack", str(PACK)],
                ["source-bind-eq", "--source", str(honest), "--pack", str(PACK)],
                ["source-bind-status", "--source", str(honest), "--pack", str(PACK)],
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
