"""SOFTWARE CORRECTNESS — Phase 5 units 901–950 inspectability."""

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
from radar_v4.digest_lock import write_digest_record
from radar_v4.leftover_lock import write_leftover_record
from radar_v4.lock_bind import (
    bind_lock_records,
    lock_bind_determinism,
    lock_bind_status,
    lock_identity,
    verify_lock_bind_record,
    write_lock_bind_record,
)
from radar_v4.lock_set import (
    compare_lock_set,
    lock_set,
    lock_set_determinism,
    lock_set_status,
    verify_lock_set_record,
    write_lock_set_record,
)
from radar_v4.safety_lock import write_safety_record
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


def _write_same_source_locks(folder: Path) -> tuple[Path, Path, Path]:
    folder.mkdir()
    safety = folder / "safety-lock.json"
    leftover = folder / "leftover-lock.json"
    digest = folder / "digest-lock.json"
    assert write_safety_record(PACK, safety).valid
    assert write_leftover_record(PACK, leftover).valid
    assert write_digest_record(PACK, digest).valid
    return safety, leftover, digest


class Units901To950Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("bind_lock_records", "lock_set"):
            self.assertTrue(hasattr(package, name), name)
        py_compile(str(ROOT / "radar_v4/lock_bind.py"), doraise=True)
        py_compile(str(ROOT / "radar_v4/lock_set.py"), doraise=True)

    def test_highest_unit_is_950(self) -> None:
        self.assertEqual(PHASE5_HIGHEST_UNIT, 950)
        status = json.loads(workshop_status())
        self.assertEqual(status["highest_unit"], 950)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertEqual(stop["highest_unit"], 950)
        self.assertFalse(stop["vendor_authorized"])

    def test_same_source_locks_bind_and_set(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            locks = root / "locks"
            safety, leftover, digest = _write_same_source_locks(locks)
            self.assertTrue(lock_identity(safety).valid)
            bound = bind_lock_records(safety, leftover)
            self.assertTrue(bound.valid, bound)
            self.assertTrue(lock_bind_determinism(safety, leftover).valid)
            self.assertTrue(lock_bind_status(safety, leftover).valid)
            self.assertTrue(bind_lock_records(safety, digest).valid)
            self.assertTrue(lock_set(locks).valid)
            self.assertTrue(lock_set_determinism(locks).valid)
            self.assertTrue(compare_lock_set(locks, locks).valid)
            self.assertTrue(lock_set_status(locks).valid)
            bind_path = root / "lock-bind.json"
            self.assertTrue(write_lock_bind_record(safety, leftover, bind_path).valid)
            self.assertTrue(verify_lock_bind_record(bind_path).valid)
            set_path = root / "lock-set.json"
            self.assertTrue(write_lock_set_record(locks, set_path).valid)
            self.assertTrue(verify_lock_set_record(set_path).valid)

    def test_mixed_source_locks_are_refused(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            other = root / "other"
            copytree(PACK, other)
            observation = other / "obs_2026-08-08.json"
            text = observation.read_text(encoding="utf-8")
            observation.write_text(text.replace('"10.50"', '"10.51"', 1), encoding="utf-8")
            locks = root / "locks"
            safety, leftover, _digest = _write_same_source_locks(locks)
            foreign = root / "foreign-leftover.json"
            self.assertTrue(write_leftover_record(other, foreign).valid)
            mixed = bind_lock_records(safety, foreign)
            self.assertFalse(mixed.valid)
            self.assertEqual(mixed.error_code, "LOCK_BIND_MISMATCH")
            bind_path = root / "lock-bind.json"
            self.assertTrue(write_lock_bind_record(safety, leftover, bind_path).valid)
            leftover.write_text(foreign.read_text(encoding="utf-8"), encoding="utf-8")
            swapped = verify_lock_bind_record(bind_path)
            self.assertFalse(swapped.valid)
            set_mixed = root / "mixed-set"
            set_mixed.mkdir()
            write_safety_record(PACK, set_mixed / "safety-lock.json")
            write_leftover_record(other, set_mixed / "leftover-lock.json")
            refused = lock_set(set_mixed)
            self.assertFalse(refused.valid)
            self.assertEqual(refused.error_code, "LOCK_BIND_MISMATCH")

    def test_refusals(self) -> None:
        missing = lock_set(Path("/workspace/.radar-v4-missing-lock-set"))
        self.assertFalse(missing.valid)
        self.assertEqual(missing.error_code, "UNREADABLE_PACK")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            empty = lock_set(root)
            self.assertFalse(empty.valid)
            self.assertEqual(empty.error_code, "LOCK_SET_EMPTY")
            one = root / "one.json"
            self.assertTrue(write_safety_record(PACK, one).valid)
            small = lock_set(root)
            self.assertFalse(small.valid)
            self.assertEqual(small.error_code, "LOCK_SET_TOO_SMALL")
            pack_as_set = lock_set(PACK)
            self.assertFalse(pack_as_set.valid)
            self.assertEqual(pack_as_set.error_code, "LOCK_RECORD_INVALID")
            fabricated = root / "fabricated.json"
            fabricated.write_text(
                '{"document_kind":"radar_v4.lock_bind","valid":true}\n',
                encoding="utf-8",
            )
            fake_bind = verify_lock_bind_record(fabricated)
            self.assertFalse(fake_bind.valid)
            self.assertEqual(fake_bind.error_code, "LOCK_BIND_INVALID")
            fake_set = root / "fabricated-set.json"
            fake_set.write_text(
                '{"document_kind":"radar_v4.lock_set","valid":true}\n',
                encoding="utf-8",
            )
            set_check = verify_lock_set_record(fake_set)
            self.assertFalse(set_check.valid)
            self.assertEqual(set_check.error_code, "LOCK_SET_RECORD_INVALID")

    def test_catalogs_and_cli(self) -> None:
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)
        with tempfile.TemporaryDirectory() as raw:
            locks = Path(raw) / "locks"
            safety, leftover, _digest = _write_same_source_locks(locks)
            commands = (
                ["bind-locks", "--left", str(safety), "--right", str(leftover)],
                ["bind-eq", "--left", str(safety), "--right", str(leftover)],
                ["bind-status", "--left", str(safety), "--right", str(leftover)],
                ["lock-set", "--path", str(locks)],
                ["lock-set-eq", "--path", str(locks)],
                ["compare-lock-set", "--left", str(locks), "--right", str(locks)],
                ["lock-set-status", "--path", str(locks)],
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
