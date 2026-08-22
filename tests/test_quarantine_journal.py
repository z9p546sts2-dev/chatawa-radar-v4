"""SOFTWARE CORRECTNESS — Phase 5 quarantine journal."""

from __future__ import annotations

import importlib
import json
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.local_session import run_session_from_pack
from radar_v4.quarantine_journal import serialize_quarantine_journal


class QuarantineJournalTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "serialize_quarantine_journal"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "quarantine_journal.py"), doraise=True)

    def test_unusable_pack_journal_does_not_invent_a_session(self) -> None:
        result = run_session_from_pack("/tmp/radar-v4-no-such-journal-pack")
        document = json.loads(serialize_quarantine_journal(local=result))
        self.assertGreaterEqual(document["refusal_count"], 1)
        codes = {entry["code"] for entry in document["entries"]}
        self.assertIn("UNREADABLE_PACK", codes)
        self.assertIsNone(result.session)


if __name__ == "__main__":
    unittest.main()
