"""DATA CORRECTNESS — Build Unit 3 JSON document intake."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from radar_v4.evidence import EvidenceEnvelope, ProvenanceClass
from radar_v4.json_intake import intake_json_text


class JsonIntakeDataTests(unittest.TestCase):
    def test_unreadable_json_is_not_an_envelope(self) -> None:
        report = intake_json_text("{not json")
        self.assertEqual(report.accepted_count(), 0)
        self.assertEqual(report.quarantined_count(), 0)
        self.assertEqual(report.unreadable_count(), 1)
        self.assertEqual(report.unreadable[0].code, "UNREADABLE_JSON")

    def test_non_object_root_is_unreadable(self) -> None:
        report = intake_json_text("12")
        self.assertEqual(report.unreadable[0].code, "UNREADABLE_JSON")
        self.assertEqual(report.accepted_count(), 0)

    def test_identity_invalid_object_is_quarantined(self) -> None:
        envelope = EvidenceEnvelope.create(
            provenance_class=ProvenanceClass.FIXTURE,
            provider="FIXTURE_SOURCE",
            symbol_or_universe="FIXTURE:UNIT3",
            market_timestamp=datetime(2026, 8, 7, 14, tzinfo=timezone.utc),
            retrieval_timestamp=datetime(2026, 8, 7, 15, tzinfo=timezone.utc),
            interval="1d",
            timezone="UTC",
            transformation_version="envelope-v1",
        )
        broken = envelope.with_checksum("0" * 64)
        report = intake_json_text(broken.serialize())
        self.assertEqual(report.accepted_count(), 0)
        self.assertEqual(report.quarantined_count(), 1)
        self.assertEqual(report.unreadable_count(), 0)
        self.assertIn("CHECKSUM_MISMATCH", report.quarantined[0].validation.issue_codes())

    def test_array_item_that_is_not_object_is_unreadable(self) -> None:
        report = intake_json_text("[1,2]")
        self.assertEqual(report.accepted_count(), 0)
        self.assertEqual(report.unreadable_count(), 2)
        self.assertEqual(report.unreadable[0].code, "UNREADABLE_ITEM")


if __name__ == "__main__":
    unittest.main()
