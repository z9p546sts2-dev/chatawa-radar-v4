"""DATA CORRECTNESS — Build Unit 1.

These tests prove identity/provenance rejection behavior only.
They do not prove that any market value is true.
"""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from radar_v4.evidence import EvidenceEnvelope, ProvenanceClass
from radar_v4.validation import validate_envelope


def _aware(hour: int = 14) -> datetime:
    return datetime(2026, 8, 7, hour, 0, 0, tzinfo=timezone.utc)


def _base(**overrides: object) -> EvidenceEnvelope:
    values: dict[str, object] = {
        "provenance_class": ProvenanceClass.SYNTHETIC.value,
        "provider": "SYNTHETIC_SOURCE",
        "symbol_or_universe": "SYNTHETIC:UNIT1",
        "market_timestamp": _aware(14),
        "retrieval_timestamp": _aware(15),
        "interval": "1d",
        "timezone": "UTC",
        "transformation_version": "envelope-v1",
        "checksum": None,
        "context_decision_use_tag": None,
    }
    values.update(overrides)
    unsigned = EvidenceEnvelope(**values)  # type: ignore[arg-type]
    if unsigned.checksum is None and "checksum" not in overrides:
        return unsigned.with_checksum(unsigned.compute_checksum())
    return unsigned


class DataCorrectnessTests(unittest.TestCase):
    def test_missing_provenance_class_rejected(self) -> None:
        result = validate_envelope(_base(provenance_class=None))
        self.assertFalse(result.valid)
        self.assertIn("MISSING_PROVENANCE_CLASS", result.issue_codes())

    def test_unknown_provenance_class_rejected(self) -> None:
        result = validate_envelope(_base(provenance_class="LOOKS_LIVE"))
        self.assertFalse(result.valid)
        self.assertIn("UNKNOWN_PROVENANCE_CLASS", result.issue_codes())

    def test_missing_provider_rejected(self) -> None:
        result = validate_envelope(_base(provider=""))
        self.assertFalse(result.valid)
        self.assertIn("MISSING_PROVIDER", result.issue_codes())

    def test_missing_symbol_or_universe_rejected(self) -> None:
        result = validate_envelope(_base(symbol_or_universe=None))
        self.assertFalse(result.valid)
        self.assertIn("MISSING_SYMBOL_OR_UNIVERSE", result.issue_codes())

    def test_invalid_timestamp_rejected(self) -> None:
        naive = datetime(2026, 8, 7, 14, 0, 0)
        result = validate_envelope(_base(market_timestamp=naive))
        self.assertFalse(result.valid)
        self.assertIn("INVALID_MARKET_TIMESTAMP", result.issue_codes())

    def test_missing_interval_rejected(self) -> None:
        result = validate_envelope(_base(interval=None))
        self.assertFalse(result.valid)
        self.assertIn("MISSING_INTERVAL", result.issue_codes())

    def test_missing_timezone_rejected_without_utc_default(self) -> None:
        result = validate_envelope(_base(timezone=None))
        self.assertFalse(result.valid)
        self.assertIn("MISSING_TIMEZONE", result.issue_codes())
        reasons = " ".join(issue.reason for issue in result.issues)
        self.assertIn("not defaulted to UTC", reasons)

    def test_missing_transformation_version_rejected(self) -> None:
        result = validate_envelope(_base(transformation_version=""))
        self.assertFalse(result.valid)
        self.assertIn("MISSING_TRANSFORMATION_VERSION", result.issue_codes())

    def test_contradictory_checksum_rejected(self) -> None:
        result = validate_envelope(_base(checksum="ab" * 32))
        self.assertFalse(result.valid)
        self.assertIn("CHECKSUM_MISMATCH", result.issue_codes())

    def test_malformed_checksum_rejected(self) -> None:
        result = validate_envelope(_base(checksum="not-a-digest"))
        self.assertFalse(result.valid)
        self.assertIn("MALFORMED_CHECKSUM", result.issue_codes())

    def test_fixture_and_synthetic_remain_identifiable(self) -> None:
        fixture = EvidenceEnvelope.create(
            provenance_class=ProvenanceClass.FIXTURE,
            provider="FIXTURE_SOURCE",
            symbol_or_universe="FIXTURE:UNIT1",
            market_timestamp=_aware(14),
            retrieval_timestamp=_aware(15),
            interval="1d",
            timezone="UTC",
            transformation_version="envelope-v1",
        )
        synthetic = EvidenceEnvelope.create(
            provenance_class=ProvenanceClass.SYNTHETIC,
            provider="SYNTHETIC_SOURCE",
            symbol_or_universe="SYNTHETIC:UNIT1",
            market_timestamp=_aware(14),
            retrieval_timestamp=_aware(15),
            interval="1d",
            timezone="UTC",
            transformation_version="envelope-v1",
        )
        restored_fixture = EvidenceEnvelope.deserialize(fixture.serialize())
        restored_synthetic = EvidenceEnvelope.deserialize(synthetic.serialize())
        self.assertEqual(restored_fixture.provenance_class, "FIXTURE")
        self.assertEqual(restored_synthetic.provenance_class, "SYNTHETIC")
        self.assertTrue(validate_envelope(restored_fixture).valid)
        self.assertTrue(validate_envelope(restored_synthetic).valid)
        self.assertIn("FIXTURE", fixture.serialize())
        self.assertIn("SYNTHETIC", synthetic.serialize())


if __name__ == "__main__":
    unittest.main()
