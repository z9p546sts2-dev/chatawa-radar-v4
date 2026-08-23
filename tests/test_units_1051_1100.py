"""SOFTWARE CORRECTNESS — Phase 5 units 1051–1100 inspectability."""

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
from radar_v4.content_bind import content_bind
from radar_v4.content_lock import compare_content_lock
from radar_v4.member_bind import (
    member_bind,
    member_bind_determinism,
    member_bind_status,
    verify_member_bind_record,
    write_member_bind_record,
)
from radar_v4.member_lock import (
    compare_member_lock,
    member_lock,
    member_lock_determinism,
    member_status_bind,
    verify_member_record,
    write_member_record,
)
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


class Units1051To1100Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("member_lock", "member_bind", "compare_member_lock"):
            self.assertTrue(hasattr(package, name), name)
        py_compile(str(ROOT / "radar_v4/member_lock.py"), doraise=True)
        py_compile(str(ROOT / "radar_v4/member_bind.py"), doraise=True)

    def test_highest_unit_is_1100(self) -> None:
        self.assertEqual(PHASE5_HIGHEST_UNIT, 1100)
        status = json.loads(workshop_status())
        self.assertEqual(status["highest_unit"], 1100)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertEqual(stop["highest_unit"], 1100)
        self.assertFalse(stop["vendor_authorized"])

    def test_copies_match_and_changed_file_is_named(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            left = root / "left"
            right = root / "right"
            copytree(PACK, left)
            copytree(PACK, right)
            self.assertTrue(member_lock(left).valid)
            self.assertTrue(member_lock_determinism(left).valid)
            self.assertTrue(compare_member_lock(left, right).valid)
            self.assertTrue(compare_content_lock(left, right).valid)
            self.assertTrue(member_status_bind(left).valid)
            observation = right / "obs_2026-08-08.json"
            text = observation.read_text(encoding="utf-8")
            observation.write_text(text.replace('"10.50"', '"10.51"', 1), encoding="utf-8")
            named = compare_member_lock(left, right)
            self.assertFalse(named.valid)
            self.assertEqual(named.error_code, "MEMBER_MISMATCH")
            self.assertEqual(named.details["changed"], ["obs_2026-08-08.json"])
            digest_only = compare_content_lock(left, right)
            self.assertFalse(digest_only.valid)
            self.assertEqual(digest_only.error_code, "CONTENT_MISMATCH")
            extra_pack = root / "extra"
            copytree(PACK, extra_pack)
            (extra_pack / "bonus.txt").write_text("bonus\n", encoding="utf-8")
            extra = compare_member_lock(left, extra_pack)
            self.assertFalse(extra.valid)
            self.assertEqual(extra.error_code, "MEMBER_EXTRA")
            self.assertEqual(extra.details["extra"], ["bonus.txt"])
            absent_pack = root / "absent"
            copytree(PACK, absent_pack)
            (absent_pack / "obs_2026-08-08.json").unlink()
            absent = compare_member_lock(left, absent_pack)
            self.assertFalse(absent.valid)
            self.assertEqual(absent.error_code, "MEMBER_ABSENT")
            self.assertEqual(absent.details["missing"], ["obs_2026-08-08.json"])
            record = root / "member-lock.json"
            self.assertTrue(write_member_record(left, record).valid)
            self.assertTrue(verify_member_record(record).valid)
            left_record = root / "left-member.json"
            right_same = root / "right-same"
            copytree(PACK, right_same)
            right_record = root / "right-member.json"
            self.assertTrue(write_member_record(left, left_record).valid)
            self.assertTrue(write_member_record(right_same, right_record).valid)
            self.assertTrue(member_bind(left_record, right_record).valid)
            self.assertTrue(member_bind_determinism(left_record, right_record).valid)
            self.assertTrue(member_bind_status(left_record, right_record).valid)
            bind_path = root / "member-bind.json"
            self.assertTrue(write_member_bind_record(left_record, right_record, bind_path).valid)
            self.assertTrue(verify_member_bind_record(bind_path).valid)

    def test_digest_match_is_not_member_identity(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            digest = "ab" * 32
            left = root / "left.json"
            right = root / "right.json"
            left.write_text(
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
            right.write_text(
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
            self.assertTrue(content_bind(left, right).valid)
            bind = member_bind(left, right)
            self.assertFalse(bind.valid)
            self.assertEqual(bind.error_code, "MEMBER_BIND_MISMATCH")

    def test_refusals(self) -> None:
        missing = member_lock(Path("/workspace/.radar-v4-missing-member-pack"))
        self.assertFalse(missing.valid)
        self.assertEqual(missing.error_code, "UNREADABLE_PACK")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fabricated = root / "fabricated.json"
            fabricated.write_text(
                '{"document_kind":"radar_v4.member_lock","valid":true}\n',
                encoding="utf-8",
            )
            fake = verify_member_record(fabricated)
            self.assertFalse(fake.valid)
            self.assertEqual(fake.error_code, "MEMBER_RECORD_INVALID")
            fake_bind = root / "fabricated-bind.json"
            fake_bind.write_text(
                '{"document_kind":"radar_v4.member_bind","valid":true}\n',
                encoding="utf-8",
            )
            bind_check = verify_member_bind_record(fake_bind)
            self.assertFalse(bind_check.valid)
            self.assertEqual(bind_check.error_code, "MEMBER_BIND_INVALID")

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
            left_record = root / "left-member.json"
            right_record = root / "right-member.json"
            self.assertTrue(write_member_record(left, left_record).valid)
            self.assertTrue(write_member_record(right, right_record).valid)
            commands = (
                ["member-lock", "--path", str(left)],
                ["member-eq", "--path", str(left)],
                ["compare-members", "--left", str(left), "--right", str(right)],
                ["member-status", "--path", str(left)],
                ["member-bind", "--left", str(left_record), "--right", str(right_record)],
                ["member-bind-eq", "--left", str(left_record), "--right", str(right_record)],
                ["member-bind-status", "--left", str(left_record), "--right", str(right_record)],
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
