"""SOFTWARE CORRECTNESS — Phase 5 units 951–1000 inspectability."""

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
from radar_v4.content_bind import (
    content_bind,
    content_bind_determinism,
    content_bind_status,
    verify_content_bind_record,
    write_content_bind_record,
)
from radar_v4.content_lock import (
    compare_content_lock,
    content_lock,
    content_lock_determinism,
    content_status_bind,
    verify_content_record,
    write_content_record,
)
from radar_v4.digest_lock import compare_digest_lock
from radar_v4.lock_bind import bind_lock_records
from radar_v4.safety_lock import write_safety_record
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


class Units951To1000Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("content_lock", "content_bind", "compare_content_lock"):
            self.assertTrue(hasattr(package, name), name)
        py_compile(str(ROOT / "radar_v4/content_lock.py"), doraise=True)
        py_compile(str(ROOT / "radar_v4/content_bind.py"), doraise=True)

    def test_highest_unit_is_1000(self) -> None:
        self.assertEqual(PHASE5_HIGHEST_UNIT, 1000)
        status = json.loads(workshop_status())
        self.assertEqual(status["highest_unit"], 1000)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertEqual(stop["highest_unit"], 1000)
        self.assertFalse(stop["vendor_authorized"])

    def test_copies_match_content_not_path(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            left = root / "left"
            right = root / "right"
            copytree(PACK, left)
            copytree(PACK, right)
            self.assertTrue(content_lock(left).valid)
            self.assertTrue(content_lock_determinism(left).valid)
            self.assertTrue(compare_content_lock(left, right).valid)
            self.assertTrue(content_status_bind(left).valid)
            path_compare = compare_digest_lock(left, right)
            self.assertFalse(path_compare.valid)
            record = root / "content-lock.json"
            self.assertTrue(write_content_record(left, record).valid)
            self.assertTrue(verify_content_record(record).valid)
            left_safety = root / "left-safety.json"
            right_safety = root / "right-safety.json"
            self.assertTrue(write_safety_record(left, left_safety).valid)
            self.assertTrue(write_safety_record(right, right_safety).valid)
            self.assertTrue(content_bind(left_safety, right_safety).valid)
            self.assertTrue(content_bind_determinism(left_safety, right_safety).valid)
            self.assertTrue(content_bind_status(left_safety, right_safety).valid)
            path_bind = bind_lock_records(left_safety, right_safety)
            self.assertFalse(path_bind.valid)
            self.assertEqual(path_bind.error_code, "LOCK_BIND_MISMATCH")
            bind_path = root / "content-bind.json"
            self.assertTrue(write_content_bind_record(left_safety, right_safety, bind_path).valid)
            self.assertTrue(verify_content_bind_record(bind_path).valid)

    def test_different_content_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            left = root / "left"
            right = root / "right"
            copytree(PACK, left)
            copytree(PACK, right)
            observation = right / "obs_2026-08-08.json"
            text = observation.read_text(encoding="utf-8")
            observation.write_text(text.replace('"10.50"', '"10.51"', 1), encoding="utf-8")
            mismatch = compare_content_lock(left, right)
            self.assertFalse(mismatch.valid)
            self.assertEqual(mismatch.error_code, "CONTENT_MISMATCH")
            left_safety = root / "left-safety.json"
            right_safety = root / "right-safety.json"
            self.assertTrue(write_safety_record(left, left_safety).valid)
            self.assertTrue(write_safety_record(right, right_safety).valid)
            bind = content_bind(left_safety, right_safety)
            self.assertFalse(bind.valid)
            self.assertEqual(bind.error_code, "CONTENT_BIND_MISMATCH")

    def test_refusals(self) -> None:
        missing = content_lock(Path("/workspace/.radar-v4-missing-content-pack"))
        self.assertFalse(missing.valid)
        self.assertEqual(missing.error_code, "UNREADABLE_PACK")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fabricated = root / "fabricated.json"
            fabricated.write_text(
                '{"document_kind":"radar_v4.content_lock","valid":true}\n',
                encoding="utf-8",
            )
            fake = verify_content_record(fabricated)
            self.assertFalse(fake.valid)
            self.assertEqual(fake.error_code, "CONTENT_RECORD_INVALID")
            fake_bind = root / "fabricated-bind.json"
            fake_bind.write_text(
                '{"document_kind":"radar_v4.content_bind","valid":true}\n',
                encoding="utf-8",
            )
            bind_check = verify_content_bind_record(fake_bind)
            self.assertFalse(bind_check.valid)
            self.assertEqual(bind_check.error_code, "CONTENT_BIND_INVALID")

    def test_catalogs_and_cli(self) -> None:
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            left = root / "left"
            right = root / "right"
            copytree(PACK, left)
            copytree(PACK, right)
            left_safety = root / "left-safety.json"
            right_safety = root / "right-safety.json"
            self.assertTrue(write_safety_record(left, left_safety).valid)
            self.assertTrue(write_safety_record(right, right_safety).valid)
            commands = (
                ["content-lock", "--path", str(left)],
                ["content-eq", "--path", str(left)],
                ["compare-content", "--left", str(left), "--right", str(right)],
                ["content-status", "--path", str(left)],
                ["content-bind", "--left", str(left_safety), "--right", str(right_safety)],
                ["content-bind-eq", "--left", str(left_safety), "--right", str(right_safety)],
                ["content-bind-status", "--left", str(left_safety), "--right", str(right_safety)],
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
