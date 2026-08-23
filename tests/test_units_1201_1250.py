"""SOFTWARE CORRECTNESS — Phase 5 units 1201–1250 inspectability."""

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
from radar_v4.current_claim import (
    current_claim,
    current_claim_determinism,
    current_claim_status,
    verify_current_claim_record,
    write_current_claim_record,
)
from radar_v4.freshness_lock import (
    compare_freshness_lock,
    freshness_lock,
    freshness_lock_determinism,
    freshness_status_bind,
    verify_freshness_record,
    write_freshness_record,
)
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"
LAST_BAR = "2026-08-09T14:00:00.000000+00:00"
LATER = "2026-08-23T21:00:00.000000+00:00"


def _write_freshness(path: Path, as_of: str, claim_current: bool) -> None:
    path.write_text(
        json.dumps(
            {
                "as_of": as_of,
                "claim_current": claim_current,
                "document_kind": "radar_v4.freshness",
            },
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )


class Units1201To1250Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("freshness_lock", "current_claim", "compare_freshness_lock"):
            self.assertTrue(hasattr(package, name), name)
        py_compile(str(ROOT / "radar_v4/freshness_lock.py"), doraise=True)
        py_compile(str(ROOT / "radar_v4/current_claim.py"), doraise=True)

    def test_highest_unit_is_1250(self) -> None:
        self.assertGreaterEqual(PHASE5_HIGHEST_UNIT, 1250)
        status = json.loads(workshop_status())
        self.assertGreaterEqual(status["highest_unit"], 1250)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertGreaterEqual(stop["highest_unit"], 1250)
        self.assertFalse(stop["vendor_authorized"])

    def test_honest_stamp_passes_and_current_claim_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            honest = root / "honest.json"
            copy = root / "copy.json"
            _write_freshness(honest, LATER, False)
            _write_freshness(copy, LATER, False)
            self.assertTrue(freshness_lock(honest).valid)
            self.assertTrue(freshness_lock_determinism(honest).valid)
            self.assertTrue(compare_freshness_lock(honest, copy).valid)
            self.assertTrue(freshness_status_bind(honest).valid)
            self.assertTrue(current_claim(honest, PACK).valid)
            self.assertTrue(current_claim_determinism(honest, PACK).valid)
            self.assertTrue(current_claim_status(honest, PACK).valid)
            record = root / "freshness-lock.json"
            self.assertTrue(write_freshness_record(honest, record).valid)
            self.assertTrue(verify_freshness_record(record).valid)
            claim_path = root / "current-claim.json"
            self.assertTrue(write_current_claim_record(honest, PACK, claim_path).valid)
            self.assertTrue(verify_current_claim_record(claim_path).valid)
            lie = root / "lie.json"
            _write_freshness(lie, LATER, True)
            self.assertTrue(freshness_lock(lie).valid)
            refused = current_claim(lie, PACK)
            self.assertFalse(refused.valid)
            self.assertEqual(refused.error_code, "FRESH_STAMP_STALE_BARS")
            at_bar = root / "at-bar.json"
            _write_freshness(at_bar, LAST_BAR, True)
            self.assertTrue(current_claim(at_bar, PACK).valid)

    def test_refusals(self) -> None:
        missing = freshness_lock(Path("/workspace/.radar-v4-missing-freshness.json"))
        self.assertFalse(missing.valid)
        self.assertEqual(missing.error_code, "FRESHNESS_MISSING")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.assertEqual(freshness_lock(root).error_code, "FRESHNESS_MISSING")
            fabricated = root / "fabricated.json"
            fabricated.write_text(
                '{"document_kind":"radar_v4.freshness_lock","valid":true}\n',
                encoding="utf-8",
            )
            fake = verify_freshness_record(fabricated)
            self.assertFalse(fake.valid)
            self.assertEqual(fake.error_code, "FRESHNESS_RECORD_INVALID")
            fake_claim = root / "fabricated-claim.json"
            fake_claim.write_text(
                '{"document_kind":"radar_v4.current_claim","valid":true}\n',
                encoding="utf-8",
            )
            claim_check = verify_current_claim_record(fake_claim)
            self.assertFalse(claim_check.valid)
            self.assertEqual(claim_check.error_code, "CURRENT_CLAIM_INVALID")

    def test_catalogs_and_cli(self) -> None:
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            honest = root / "honest.json"
            other = root / "other.json"
            _write_freshness(honest, LATER, False)
            _write_freshness(other, LATER, False)
            commands = (
                ["freshness-lock", "--path", str(honest)],
                ["freshness-eq", "--path", str(honest)],
                ["compare-freshness", "--left", str(honest), "--right", str(other)],
                ["freshness-status", "--path", str(honest)],
                ["current-claim", "--freshness", str(honest), "--pack", str(PACK)],
                ["current-claim-eq", "--freshness", str(honest), "--pack", str(PACK)],
                ["current-claim-status", "--freshness", str(honest), "--pack", str(PACK)],
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
