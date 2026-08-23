"""SOFTWARE CORRECTNESS — Phase 5 units 1101–1150 inspectability."""

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
from radar_v4.content_set import content_set
from radar_v4.member_align import (
    member_align,
    member_align_determinism,
    member_align_status,
    verify_member_align_record,
    write_member_align_record,
)
from radar_v4.member_lock import verify_member_record, write_member_record
from radar_v4.member_set import (
    compare_member_set,
    member_set,
    member_set_determinism,
    member_set_status,
    verify_member_set_record,
    write_member_set_record,
)
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


class Units1101To1150Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("member_set", "member_align", "compare_member_set"):
            self.assertTrue(hasattr(package, name), name)
        py_compile(str(ROOT / "radar_v4/member_set.py"), doraise=True)
        py_compile(str(ROOT / "radar_v4/member_align.py"), doraise=True)

    def test_highest_unit_is_1150(self) -> None:
        self.assertGreaterEqual(PHASE5_HIGHEST_UNIT, 1150)
        status = json.loads(workshop_status())
        self.assertGreaterEqual(status["highest_unit"], 1150)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertGreaterEqual(stop["highest_unit"], 1150)
        self.assertFalse(stop["vendor_authorized"])

    def test_set_of_copies_and_align_to_other_path(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            left = root / "left"
            right = root / "right"
            copytree(PACK, left)
            copytree(PACK, right)
            locks = root / "locks"
            locks.mkdir()
            left_record = locks / "left-member.json"
            right_record = locks / "right-member.json"
            self.assertTrue(write_member_record(left, left_record).valid)
            self.assertTrue(write_member_record(right, right_record).valid)
            self.assertTrue(member_set(locks).valid)
            self.assertTrue(member_set_determinism(locks).valid)
            self.assertTrue(member_set_status(locks).valid)
            other = root / "other-locks"
            other.mkdir()
            self.assertTrue(write_member_record(left, other / "one.json").valid)
            self.assertTrue(write_member_record(right, other / "two.json").valid)
            self.assertTrue(compare_member_set(locks, other).valid)
            set_path = root / "member-set.json"
            self.assertTrue(write_member_set_record(locks, set_path).valid)
            self.assertTrue(verify_member_set_record(set_path).valid)
            self.assertTrue(member_align(left_record, right).valid)
            self.assertTrue(member_align_determinism(left_record, right).valid)
            self.assertTrue(member_align_status(left_record, right).valid)
            self.assertTrue(verify_member_record(left_record).valid)
            observation = right / "obs_2026-08-08.json"
            text = observation.read_text(encoding="utf-8")
            observation.write_text(text.replace('"10.50"', '"10.51"', 1), encoding="utf-8")
            aligned = member_align(left_record, right)
            self.assertFalse(aligned.valid)
            self.assertEqual(aligned.error_code, "MEMBER_ALIGN_MISMATCH")
            self.assertTrue(verify_member_record(left_record).valid)
            align_path = root / "member-align.json"
            copytree(PACK, root / "fresh")
            self.assertTrue(write_member_align_record(left_record, root / "fresh", align_path).valid)
            self.assertTrue(verify_member_align_record(align_path).valid)

    def test_digest_set_is_not_member_set(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            digest = "ab" * 32
            folder = root / "locks"
            folder.mkdir()
            (folder / "left.json").write_text(
                json.dumps(
                    {
                        "document_kind": "radar_v4.member_lock",
                        "valid": True,
                        "details": {
                            "source_path": str(root / "left-pack"),
                            "source_digest": digest,
                            "members": {"obs.json": "cd" * 32},
                        },
                    },
                    separators=(",", ":"),
                )
                + "\n",
                encoding="utf-8",
            )
            (folder / "right.json").write_text(
                json.dumps(
                    {
                        "document_kind": "radar_v4.member_lock",
                        "valid": True,
                        "details": {
                            "source_path": str(root / "right-pack"),
                            "source_digest": digest,
                            "members": {"obs.json": "ef" * 32},
                        },
                    },
                    separators=(",", ":"),
                )
                + "\n",
                encoding="utf-8",
            )
            self.assertTrue(content_set(folder).valid)
            refused = member_set(folder)
            self.assertFalse(refused.valid)
            self.assertEqual(refused.error_code, "MEMBER_BIND_MISMATCH")

    def test_refusals(self) -> None:
        missing = member_set(Path("/workspace/.radar-v4-missing-member-set"))
        self.assertFalse(missing.valid)
        self.assertEqual(missing.error_code, "UNREADABLE_PACK")
        missing_align = member_align(
            Path("/workspace/.radar-v4-missing-member-record.json"),
            PACK,
        )
        self.assertFalse(missing_align.valid)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.assertEqual(member_set(root).error_code, "MEMBER_SET_EMPTY")
            one = root / "one.json"
            self.assertTrue(write_member_record(PACK, one).valid)
            self.assertEqual(member_set(root).error_code, "MEMBER_SET_TOO_SMALL")
            fabricated = root / "fabricated.json"
            fabricated.write_text(
                '{"document_kind":"radar_v4.member_set","valid":true}\n',
                encoding="utf-8",
            )
            fake = verify_member_set_record(fabricated)
            self.assertFalse(fake.valid)
            self.assertEqual(fake.error_code, "MEMBER_SET_RECORD_INVALID")
            fake_align = root / "fabricated-align.json"
            fake_align.write_text(
                '{"document_kind":"radar_v4.member_align","valid":true}\n',
                encoding="utf-8",
            )
            align_check = verify_member_align_record(fake_align)
            self.assertFalse(align_check.valid)
            self.assertEqual(align_check.error_code, "MEMBER_ALIGN_INVALID")

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
            locks = root / "locks"
            locks.mkdir()
            self.assertTrue(write_member_record(left, locks / "left.json").valid)
            self.assertTrue(write_member_record(right, locks / "right.json").valid)
            other = root / "other"
            other.mkdir()
            self.assertTrue(write_member_record(left, other / "one.json").valid)
            self.assertTrue(write_member_record(right, other / "two.json").valid)
            left_record = locks / "left.json"
            commands = (
                ["member-set", "--path", str(locks)],
                ["member-set-eq", "--path", str(locks)],
                ["compare-member-set", "--left", str(locks), "--right", str(other)],
                ["member-set-status", "--path", str(locks)],
                ["member-align", "--record", str(left_record), "--live", str(right)],
                ["member-align-eq", "--record", str(left_record), "--live", str(right)],
                ["member-align-status", "--record", str(left_record), "--live", str(right)],
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
