"""SOFTWARE CORRECTNESS — Phase 5 units 1001–1050 inspectability."""

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
from radar_v4.content_set import (
    compare_content_set,
    content_set,
    content_set_determinism,
    content_set_status,
    verify_content_set_record,
    write_content_set_record,
)
from radar_v4.copy_set import (
    compare_copy_set,
    copy_set,
    copy_set_determinism,
    copy_set_status,
    verify_copy_set_record,
    write_copy_set_record,
)
from radar_v4.lock_set import compare_lock_set, lock_set
from radar_v4.safety_lock import write_safety_record
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


class Units1001To1050Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("content_set", "copy_set", "compare_content_set", "compare_copy_set"):
            self.assertTrue(hasattr(package, name), name)
        py_compile(str(ROOT / "radar_v4/content_set.py"), doraise=True)
        py_compile(str(ROOT / "radar_v4/copy_set.py"), doraise=True)

    def test_highest_unit_is_1050(self) -> None:
        self.assertEqual(PHASE5_HIGHEST_UNIT, 1050)
        status = json.loads(workshop_status())
        self.assertEqual(status["highest_unit"], 1050)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertEqual(stop["highest_unit"], 1050)
        self.assertFalse(stop["vendor_authorized"])

    def test_copy_folders_match_content_not_path(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            left_pack = root / "left"
            right_pack = root / "right"
            copytree(PACK, left_pack)
            copytree(PACK, right_pack)
            locks = root / "locks"
            locks.mkdir()
            left_safety = locks / "left-safety.json"
            right_safety = locks / "right-safety.json"
            self.assertTrue(write_safety_record(left_pack, left_safety).valid)
            self.assertTrue(write_safety_record(right_pack, right_safety).valid)
            self.assertTrue(content_set(locks).valid)
            self.assertTrue(content_set_determinism(locks).valid)
            self.assertTrue(content_set_status(locks).valid)
            path_set = lock_set(locks)
            self.assertFalse(path_set.valid)
            self.assertEqual(path_set.error_code, "LOCK_BIND_MISMATCH")
            copies = root / "copies"
            copies.mkdir()
            copytree(PACK, copies / "a")
            copytree(PACK, copies / "b")
            self.assertTrue(copy_set(copies).valid)
            self.assertTrue(copy_set_determinism(copies).valid)
            self.assertTrue(copy_set_status(copies).valid)
            self.assertFalse(content_set(copies).valid)
            self.assertEqual(content_set(copies).error_code, "CONTENT_SET_EMPTY")
            self.assertFalse(copy_set(locks).valid)
            self.assertEqual(copy_set(locks).error_code, "COPY_SET_EMPTY")
            other_locks = root / "other-locks"
            other_locks.mkdir()
            self.assertTrue(write_safety_record(left_pack, other_locks / "one.json").valid)
            self.assertTrue(write_safety_record(right_pack, other_locks / "two.json").valid)
            self.assertTrue(compare_content_set(locks, other_locks).valid)
            self.assertFalse(compare_lock_set(locks, other_locks).valid)
            other_copies = root / "other-copies"
            other_copies.mkdir()
            copytree(PACK, other_copies / "c")
            copytree(PACK, other_copies / "d")
            self.assertTrue(compare_copy_set(copies, other_copies).valid)
            set_path = root / "content-set.json"
            self.assertTrue(write_content_set_record(locks, set_path).valid)
            self.assertTrue(verify_content_set_record(set_path).valid)
            copy_path = root / "copy-set.json"
            self.assertTrue(write_copy_set_record(copies, copy_path).valid)
            self.assertTrue(verify_copy_set_record(copy_path).valid)

    def test_different_content_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            left_pack = root / "left"
            right_pack = root / "right"
            copytree(PACK, left_pack)
            copytree(PACK, right_pack)
            observation = right_pack / "obs_2026-08-08.json"
            text = observation.read_text(encoding="utf-8")
            observation.write_text(text.replace('"10.50"', '"10.51"', 1), encoding="utf-8")
            locks = root / "locks"
            locks.mkdir()
            self.assertTrue(write_safety_record(left_pack, locks / "left.json").valid)
            self.assertTrue(write_safety_record(right_pack, locks / "right.json").valid)
            mixed = content_set(locks)
            self.assertFalse(mixed.valid)
            self.assertEqual(mixed.error_code, "CONTENT_BIND_MISMATCH")
            copies = root / "copies"
            copies.mkdir()
            copytree(left_pack, copies / "a")
            copytree(right_pack, copies / "b")
            refused = copy_set(copies)
            self.assertFalse(refused.valid)
            self.assertEqual(refused.error_code, "CONTENT_MISMATCH")

    def test_refusals(self) -> None:
        missing = content_set(Path("/workspace/.radar-v4-missing-content-set"))
        self.assertFalse(missing.valid)
        self.assertEqual(missing.error_code, "UNREADABLE_PACK")
        missing_copies = copy_set(Path("/workspace/.radar-v4-missing-copy-set"))
        self.assertFalse(missing_copies.valid)
        self.assertEqual(missing_copies.error_code, "UNREADABLE_PACK")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.assertEqual(content_set(root).error_code, "CONTENT_SET_EMPTY")
            self.assertEqual(copy_set(root).error_code, "COPY_SET_EMPTY")
            one = root / "one.json"
            self.assertTrue(write_safety_record(PACK, one).valid)
            self.assertEqual(content_set(root).error_code, "CONTENT_SET_TOO_SMALL")
            only = root / "only-copy"
            copytree(PACK, only)
            self.assertEqual(copy_set(root).error_code, "COPY_SET_TOO_SMALL")
            pack_as_set = content_set(PACK)
            self.assertFalse(pack_as_set.valid)
            self.assertEqual(pack_as_set.error_code, "LOCK_RECORD_INVALID")
            fabricated = root / "fabricated.json"
            fabricated.write_text(
                '{"document_kind":"radar_v4.content_set","valid":true}\n',
                encoding="utf-8",
            )
            fake = verify_content_set_record(fabricated)
            self.assertFalse(fake.valid)
            self.assertEqual(fake.error_code, "CONTENT_SET_RECORD_INVALID")
            fake_copy = root / "fabricated-copy.json"
            fake_copy.write_text(
                '{"document_kind":"radar_v4.copy_set","valid":true}\n',
                encoding="utf-8",
            )
            copy_check = verify_copy_set_record(fake_copy)
            self.assertFalse(copy_check.valid)
            self.assertEqual(copy_check.error_code, "COPY_SET_RECORD_INVALID")

    def test_catalogs_and_cli(self) -> None:
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            locks = root / "locks"
            locks.mkdir()
            left_pack = root / "left"
            right_pack = root / "right"
            copytree(PACK, left_pack)
            copytree(PACK, right_pack)
            self.assertTrue(write_safety_record(left_pack, locks / "left.json").valid)
            self.assertTrue(write_safety_record(right_pack, locks / "right.json").valid)
            copies = root / "copies"
            copies.mkdir()
            copytree(PACK, copies / "a")
            copytree(PACK, copies / "b")
            other_locks = root / "other-locks"
            other_locks.mkdir()
            self.assertTrue(write_safety_record(left_pack, other_locks / "one.json").valid)
            self.assertTrue(write_safety_record(right_pack, other_locks / "two.json").valid)
            other_copies = root / "other-copies"
            other_copies.mkdir()
            copytree(PACK, other_copies / "c")
            copytree(PACK, other_copies / "d")
            commands = (
                ["content-set", "--path", str(locks)],
                ["content-set-eq", "--path", str(locks)],
                ["compare-content-set", "--left", str(locks), "--right", str(other_locks)],
                ["content-set-status", "--path", str(locks)],
                ["copy-set", "--path", str(copies)],
                ["copy-set-eq", "--path", str(copies)],
                ["compare-copy-set", "--left", str(copies), "--right", str(other_copies)],
                ["copy-set-status", "--path", str(copies)],
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
