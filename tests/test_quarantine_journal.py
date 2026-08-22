"""SOFTWARE CORRECTNESS — Phase 5 quarantine journal."""

from __future__ import annotations

import importlib
import json
import tempfile
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.local_session import run_session_from_pack
from radar_v4.quarantine_journal import (
    read_quarantine_journal_file,
    serialize_quarantine_journal,
    write_quarantine_journal_file,
)
from radar_v4.snapshot_files import SnapshotFileError


class QuarantineJournalTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "serialize_quarantine_journal"))
        self.assertTrue(hasattr(package, "read_quarantine_journal_file"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "quarantine_journal.py"), doraise=True)

    def test_unusable_pack_journal_does_not_invent_a_session(self) -> None:
        result = run_session_from_pack("/tmp/radar-v4-no-such-journal-pack")
        document = json.loads(serialize_quarantine_journal(local=result))
        self.assertGreaterEqual(document["refusal_count"], 1)
        codes = {entry["code"] for entry in document["entries"]}
        self.assertIn("UNREADABLE_PACK", codes)
        self.assertIsNone(result.session)
        self.assertEqual(document["document_kind"], "radar_v4.quarantine_journal")
        self.assertEqual(document["journal_version"], 1)

    def test_read_refuses_wrong_document_kind(self) -> None:
        result = run_session_from_pack("/tmp/radar-v4-no-such-journal-pack")
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "journal.json"
            write_quarantine_journal_file(path, local=result)
            loaded = read_quarantine_journal_file(path)
            self.assertEqual(loaded["document_kind"], "radar_v4.quarantine_journal")
            path.write_text('{"document_kind":"not-a-journal","entries":[]}', encoding="utf-8")
            with self.assertRaises(SnapshotFileError) as ctx:
                read_quarantine_journal_file(path)
            self.assertEqual(ctx.exception.code, "UNREADABLE_JOURNAL")


if __name__ == "__main__":
    unittest.main()
