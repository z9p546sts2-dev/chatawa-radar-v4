"""SOFTWARE CORRECTNESS — Phase 5 units 851–900 inspectability."""

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
from radar_v4.digest_lock import (
    compare_digest_lock,
    digest_lock,
    digest_lock_determinism,
    digest_status_bind,
    verify_digest_record,
    write_digest_record,
)
from radar_v4.integrity import source_digest
from radar_v4.leftover_lock import leftover_lock, write_leftover_record, verify_leftover_record
from radar_v4.safety_lock import safety_lock, write_safety_record, verify_safety_record
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


class Units851To900Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("digest_lock", "source_digest"):
            self.assertTrue(hasattr(package, name), name)
        py_compile(str(ROOT / "radar_v4/digest_lock.py"), doraise=True)
        py_compile(str(ROOT / "radar_v4/integrity.py"), doraise=True)

    def test_highest_unit_is_900(self) -> None:
        self.assertEqual(PHASE5_HIGHEST_UNIT, 900)
        status = json.loads(workshop_status())
        self.assertEqual(status["highest_unit"], 900)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertEqual(stop["highest_unit"], 900)
        self.assertFalse(stop["vendor_authorized"])

    def test_synthetic_digest_and_source_identity(self) -> None:
        locked = digest_lock(PACK)
        self.assertTrue(locked.valid)
        self.assertEqual(len(locked.details["source_digest"]), 64)
        self.assertTrue(digest_lock_determinism(PACK).valid)
        self.assertTrue(compare_digest_lock(PACK, PACK).valid)
        self.assertTrue(digest_status_bind(PACK).valid)
        safety = safety_lock(PACK)
        leftover = leftover_lock(PACK)
        self.assertTrue(safety.valid)
        self.assertTrue(leftover.valid)
        self.assertEqual(safety.details["source_digest"], locked.details["source_digest"])
        self.assertEqual(leftover.details["source_digest"], locked.details["source_digest"])
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            digest_path = root / "digest-lock.json"
            written = write_digest_record(PACK, digest_path)
            self.assertTrue(written.valid)
            self.assertTrue(verify_digest_record(digest_path).valid)
            safety_path = root / "safety-lock.json"
            self.assertTrue(write_safety_record(PACK, safety_path).valid)
            self.assertIn("source_digest", json.loads(safety_path.read_text(encoding="utf-8"))["details"])
            leftover_path = root / "leftover-lock.json"
            self.assertTrue(write_leftover_record(PACK, leftover_path).valid)
            self.assertIn("source_digest", json.loads(leftover_path.read_text(encoding="utf-8"))["details"])
            fabricated = root / "fabricated.json"
            fabricated.write_text(
                '{"document_kind":"radar_v4.digest_lock","valid":true}\n',
                encoding="utf-8",
            )
            fake = verify_digest_record(fabricated)
            self.assertFalse(fake.valid)
            self.assertEqual(fake.error_code, "DIGEST_RECORD_INVALID")

    def test_same_path_swap_refuses_stale_lock(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            pack = root / "pack"
            copytree(PACK, pack)
            record = root / "safety-lock.json"
            self.assertTrue(write_safety_record(pack, record).valid)
            self.assertTrue(verify_safety_record(record).valid)
            before = source_digest(pack)
            observation = pack / "obs_2026-08-08.json"
            text = observation.read_text(encoding="utf-8")
            observation.write_text(text.replace('"10.50"', '"10.51"', 1), encoding="utf-8")
            self.assertNotEqual(source_digest(pack), before)
            self.assertTrue(safety_lock(pack).valid)
            swapped = verify_safety_record(record)
            self.assertFalse(swapped.valid)
            self.assertEqual(swapped.error_code, "RECORD_MISMATCH")
            digest_record = root / "digest-lock.json"
            self.assertTrue(write_digest_record(pack, digest_record).valid)
            observation.write_text(text, encoding="utf-8")
            digest_swapped = verify_digest_record(digest_record)
            self.assertFalse(digest_swapped.valid)
            self.assertEqual(digest_swapped.error_code, "RECORD_MISMATCH")

    def test_refusals(self) -> None:
        missing = digest_lock(Path("/workspace/.radar-v4-missing-digest-pack"))
        self.assertFalse(missing.valid)
        self.assertEqual(missing.error_code, "UNREADABLE_PACK")
        self.assertEqual(source_digest(Path("/workspace/.radar-v4-missing-digest-pack")), "")

    def test_catalogs_and_cli(self) -> None:
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)
        commands = (
            ["digest-lock", "--path", str(PACK)],
            ["digest-eq", "--path", str(PACK)],
            ["compare-digest-lock", "--left", str(PACK), "--right", str(PACK)],
            ["digest-status", "--path", str(PACK)],
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
