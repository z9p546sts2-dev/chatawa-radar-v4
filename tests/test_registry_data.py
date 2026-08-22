"""DATA CORRECTNESS — Build Units 4–5 registry store and identity collision."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from radar_v4.evidence import EvidenceEnvelope, ProvenanceClass
from radar_v4.registry import EvidenceRegistry


def _create(symbol: str, retrieval_hour: int = 15) -> EvidenceEnvelope:
    return EvidenceEnvelope.create(
        provenance_class=ProvenanceClass.FIXTURE,
        provider="FIXTURE_SOURCE",
        symbol_or_universe=symbol,
        market_timestamp=datetime(2026, 8, 7, 14, tzinfo=timezone.utc),
        retrieval_timestamp=datetime(2026, 8, 7, retrieval_hour, tzinfo=timezone.utc),
        interval="1d",
        timezone="UTC",
        transformation_version="envelope-v1",
    )


class RegistryDataTests(unittest.TestCase):
    def test_invalid_record_is_not_stored(self) -> None:
        registry = EvidenceRegistry()
        bad = EvidenceEnvelope(
            provenance_class=None,
            provider="FIXTURE_SOURCE",
            symbol_or_universe="FIXTURE:BAD",
            market_timestamp=datetime(2026, 8, 7, 14, tzinfo=timezone.utc),
            retrieval_timestamp=datetime(2026, 8, 7, 15, tzinfo=timezone.utc),
            interval="1d",
            timezone="UTC",
            transformation_version="envelope-v1",
        )
        report = registry.put((bad,))
        self.assertEqual(report.accepted_count(), 0)
        self.assertEqual(registry.accepted_count(), 0)
        self.assertEqual(registry.quarantined_count(), 1)

    def test_same_checksum_is_idempotent(self) -> None:
        registry = EvidenceRegistry()
        envelope = _create("FIXTURE:UNIT5")
        first = registry.put((envelope,))
        second = registry.put((envelope,))
        self.assertEqual(first.accepted_count(), 1)
        self.assertEqual(second.accepted_count(), 1)
        self.assertEqual(registry.accepted_count(), 1)
        self.assertEqual(registry.quarantined_count(), 0)

    def test_same_identity_different_checksum_is_quarantined(self) -> None:
        registry = EvidenceRegistry()
        first = _create("FIXTURE:UNIT5", retrieval_hour=15)
        second = _create("FIXTURE:UNIT5", retrieval_hour=16)
        self.assertEqual(first.identity_key(), second.identity_key())
        self.assertNotEqual(first.checksum, second.checksum)
        registry.put((first,))
        report = registry.put((second,))
        self.assertEqual(report.accepted_count(), 0)
        self.assertEqual(report.quarantined_count(), 1)
        self.assertIn(
            "CONTRADICTORY_IDENTITY",
            report.quarantined[0].validation.issue_codes(),
        )
        stored = registry.get(first)
        self.assertEqual(stored.checksum, first.checksum)
        self.assertNotEqual(stored.checksum, second.checksum)

    def test_different_identities_can_both_store(self) -> None:
        registry = EvidenceRegistry()
        registry.put((_create("FIXTURE:A"), _create("FIXTURE:B")))
        self.assertEqual(registry.accepted_count(), 2)


if __name__ == "__main__":
    unittest.main()
