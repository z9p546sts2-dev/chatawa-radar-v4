"""DATA CORRECTNESS — Build Unit 2.

These tests prove quarantine of invalid identity records.
They do not prove that any market value is true.
"""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from radar_v4.evidence import EvidenceEnvelope, ProvenanceClass
from radar_v4.intake import intake_envelopes


def _aware(hour: int) -> datetime:
    return datetime(2026, 8, 7, hour, 0, 0, tzinfo=timezone.utc)


def _valid(symbol: str = "FIXTURE:UNIT2") -> EvidenceEnvelope:
    return EvidenceEnvelope.create(
        provenance_class=ProvenanceClass.FIXTURE,
        provider="FIXTURE_SOURCE",
        symbol_or_universe=symbol,
        market_timestamp=_aware(14),
        retrieval_timestamp=_aware(15),
        interval="1d",
        timezone="UTC",
        transformation_version="envelope-v1",
    )


class IntakeDataCorrectnessTests(unittest.TestCase):
    def test_invalid_identity_is_quarantined(self) -> None:
        bad = EvidenceEnvelope(
            provenance_class=None,
            provider="FIXTURE_SOURCE",
            symbol_or_universe="FIXTURE:BAD",
            market_timestamp=_aware(14),
            retrieval_timestamp=_aware(15),
            interval="1d",
            timezone="UTC",
            transformation_version="envelope-v1",
        )
        report = intake_envelopes((bad,))
        self.assertEqual(report.accepted_count(), 0)
        self.assertEqual(report.quarantined_count(), 1)
        self.assertIn(
            "MISSING_PROVENANCE_CLASS",
            report.quarantined[0].validation.issue_codes(),
        )
        self.assertIs(report.quarantined[0].envelope, bad)

    def test_unknown_provenance_is_quarantined(self) -> None:
        unknown = EvidenceEnvelope(
            provenance_class="LOOKS_LIVE",
            provider="FIXTURE_SOURCE",
            symbol_or_universe="FIXTURE:UNKNOWN",
            market_timestamp=_aware(14),
            retrieval_timestamp=_aware(15),
            interval="1d",
            timezone="UTC",
            transformation_version="envelope-v1",
            checksum=None,
        )
        unknown = unknown.with_checksum(unknown.compute_checksum())
        report = intake_envelopes((unknown,))
        self.assertEqual(report.accepted_count(), 0)
        self.assertIn(
            "UNKNOWN_PROVENANCE_CLASS",
            report.quarantined[0].validation.issue_codes(),
        )

    def test_mixed_batch_partitions_without_repair(self) -> None:
        good = _valid()
        broken_checksum = good.with_checksum("0" * 64)
        report = intake_envelopes((good, broken_checksum))
        self.assertEqual(report.accepted_count(), 1)
        self.assertEqual(report.quarantined_count(), 1)
        self.assertIs(report.accepted[0].envelope, good)
        self.assertEqual(broken_checksum.checksum, "0" * 64)
        self.assertIn("CHECKSUM_MISMATCH", report.quarantined[0].validation.issue_codes())

    def test_quarantine_does_not_rewrite_invalid_into_valid(self) -> None:
        missing_timezone = EvidenceEnvelope(
            provenance_class=ProvenanceClass.SYNTHETIC.value,
            provider="SYNTHETIC_SOURCE",
            symbol_or_universe="SYNTHETIC:UNIT2",
            market_timestamp=_aware(14),
            retrieval_timestamp=_aware(15),
            interval="1d",
            timezone=None,
            transformation_version="envelope-v1",
        )
        report = intake_envelopes((missing_timezone,))
        quarantined = report.quarantined[0].envelope
        self.assertIsNone(quarantined.timezone)
        self.assertFalse(report.quarantined[0].validation.valid)
        self.assertEqual(report.accepted_count(), 0)

    def test_fixture_and_synthetic_can_be_accepted_together(self) -> None:
        fixture = _valid("FIXTURE:UNIT2")
        synthetic = EvidenceEnvelope.create(
            provenance_class=ProvenanceClass.SYNTHETIC,
            provider="SYNTHETIC_SOURCE",
            symbol_or_universe="SYNTHETIC:UNIT2",
            market_timestamp=_aware(14),
            retrieval_timestamp=_aware(15),
            interval="1d",
            timezone="UTC",
            transformation_version="envelope-v1",
        )
        report = intake_envelopes((fixture, synthetic))
        self.assertEqual(report.accepted_count(), 2)
        self.assertEqual(report.quarantined_count(), 0)
        classes = [record.envelope.provenance_class for record in report.accepted]
        self.assertEqual(classes, ["FIXTURE", "SYNTHETIC"])


if __name__ == "__main__":
    unittest.main()
