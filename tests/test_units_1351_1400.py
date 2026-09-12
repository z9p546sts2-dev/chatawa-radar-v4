"""SOFTWARE CORRECTNESS — Phase 5 units 1351–1400 inspectability."""

from __future__ import annotations

import importlib
import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.catalog_audit import audit_document_kinds, audit_reason_catalog
from radar_v4.cli import main
from radar_v4.dataset_pack import load_dataset_pack
from radar_v4.need_bind import (
    need_bind,
    need_bind_determinism,
    need_bind_status,
    verify_need_bind_record,
    write_need_bind_record,
)
from radar_v4.need_lock import (
    compare_need_lock,
    need_lock,
    need_lock_determinism,
    need_status_bind,
    verify_need_record,
    write_need_record,
)
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


def _write_need(
    path: Path,
    *,
    sufficient: bool = True,
    purchase: bool = False,
    adjustment: str = "UNADJUSTED",
    staleness: str = "NONE",
) -> None:
    path.write_text(
        json.dumps(
            {
                "adjustment_policy": adjustment,
                "bounded_file_sufficient": sufficient,
                "document_kind": "radar_v4.need",
                "max_staleness": staleness,
                "purchase_authorized": purchase,
            },
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )


class Units1351To1400Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("need_lock", "need_bind", "compare_need_lock"):
            self.assertTrue(hasattr(package, name), name)
        py_compile(str(ROOT / "radar_v4/need_lock.py"), doraise=True)
        py_compile(str(ROOT / "radar_v4/need_bind.py"), doraise=True)

    def test_highest_unit_is_1400(self) -> None:
        self.assertEqual(PHASE5_HIGHEST_UNIT, 1400)
        status = json.loads(workshop_status())
        self.assertEqual(status["highest_unit"], 1400)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        self.assertFalse(status["vendor_authorized"])
        stop = json.loads(workshop_stop_record())
        self.assertEqual(stop["highest_unit"], 1400)
        self.assertFalse(stop["vendor_authorized"])
        self.assertFalse(stop["paper_trading_authorized"])

    def test_bounded_file_binds_and_purchase_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            honest = root / "honest.json"
            copy = root / "copy.json"
            _write_need(honest)
            _write_need(copy)
            self.assertTrue(need_lock(honest).valid)
            self.assertTrue(need_lock_determinism(honest).valid)
            self.assertTrue(compare_need_lock(honest, copy).valid)
            self.assertTrue(need_status_bind(honest).valid)
            self.assertTrue(need_bind(honest, PACK).valid)
            self.assertTrue(need_bind_determinism(honest, PACK).valid)
            self.assertTrue(need_bind_status(honest, PACK).valid)
            record = root / "need-lock.json"
            self.assertTrue(write_need_record(honest, record).valid)
            self.assertTrue(verify_need_record(record).valid)
            bind_path = root / "need-bind.json"
            self.assertTrue(write_need_bind_record(honest, PACK, bind_path).valid)
            self.assertTrue(verify_need_bind_record(bind_path).valid)
            skipped = root / "skipped.json"
            _write_need(skipped, sufficient=False)
            refused_file = need_lock(skipped)
            self.assertFalse(refused_file.valid)
            self.assertEqual(refused_file.error_code, "BOUNDED_FILE_SKIPPED")
            claimed = root / "claimed.json"
            _write_need(claimed, purchase=True)
            refused_claim = need_lock(claimed)
            self.assertFalse(refused_claim.valid)
            self.assertEqual(refused_claim.error_code, "PURCHASE_CLAIM")
            undeclared_adj = root / "undeclared-adj.json"
            _write_need(undeclared_adj, adjustment="  ")
            refused_adj = need_lock(undeclared_adj)
            self.assertFalse(refused_adj.valid)
            self.assertEqual(refused_adj.error_code, "ADJUSTMENT_UNDECLARED")
            undeclared_stale = root / "undeclared-stale.json"
            _write_need(undeclared_stale, staleness="  ")
            refused_stale = need_lock(undeclared_stale)
            self.assertFalse(refused_stale.valid)
            self.assertEqual(refused_stale.error_code, "STALENESS_UNDECLARED")
            mismatched = root / "mismatched.json"
            _write_need(mismatched, adjustment="SPLIT_ADJUSTED")
            refused_match = need_bind(mismatched, PACK)
            self.assertFalse(refused_match.valid)
            self.assertEqual(refused_match.error_code, "ADJUSTMENT_MISMATCH")
            stale_mismatch = root / "stale-mismatch.json"
            _write_need(stale_mismatch, staleness="1d")
            refused_need = need_bind(stale_mismatch, PACK)
            self.assertFalse(refused_need.valid)
            self.assertEqual(refused_need.error_code, "NEED_MISMATCH")

    def test_refusals(self) -> None:
        missing = need_lock(Path("/workspace/.radar-v4-missing-need.json"))
        self.assertFalse(missing.valid)
        self.assertEqual(missing.error_code, "NEED_MISSING")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.assertEqual(need_lock(root).error_code, "NEED_MISSING")
            fabricated = root / "fabricated.json"
            fabricated.write_text(
                '{"document_kind":"radar_v4.need_lock","valid":true}\n',
                encoding="utf-8",
            )
            fake = verify_need_record(fabricated)
            self.assertFalse(fake.valid)
            self.assertEqual(fake.error_code, "NEED_RECORD_INVALID")
            fake_bind = root / "fabricated-bind.json"
            fake_bind.write_text(
                '{"document_kind":"radar_v4.need_bind","valid":true}\n',
                encoding="utf-8",
            )
            bind_check = verify_need_bind_record(fake_bind)
            self.assertFalse(bind_check.valid)
            self.assertEqual(bind_check.error_code, "NEED_BIND_INVALID")
            pack_copy = root / "pack"
            shutil.copytree(PACK, pack_copy)
            _write_need(pack_copy / "need.json")
            report = load_dataset_pack(pack_copy)
            self.assertTrue(report.usable())
            self.assertEqual(report.declaration.adjustment_policy, "UNADJUSTED")

    def test_catalogs_and_cli(self) -> None:
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            honest = root / "honest.json"
            other = root / "other.json"
            _write_need(honest)
            _write_need(other)
            commands = (
                ["need-lock", "--path", str(honest)],
                ["need-eq", "--path", str(honest)],
                ["compare-need", "--left", str(honest), "--right", str(other)],
                ["need-status", "--path", str(honest)],
                ["need-bind", "--need", str(honest), "--pack", str(PACK)],
                ["need-bind-eq", "--need", str(honest), "--pack", str(PACK)],
                ["need-bind-status", "--need", str(honest), "--pack", str(PACK)],
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
