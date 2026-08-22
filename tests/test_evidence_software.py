"""SOFTWARE CORRECTNESS — Build Unit 1.

These tests prove software behavior only. They do not prove market
correctness, usefulness, method validity, or edge.
"""

from __future__ import annotations

import importlib
import unittest
from datetime import datetime, timezone
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.evidence import EvidenceEnvelope, ProvenanceClass, SERIALIZATION_RULES
from radar_v4.validation import ValidationResult, validate_envelope


def _aware(year: int, month: int, day: int, hour: int = 12) -> datetime:
    return datetime(year, month, day, hour, 0, 0, tzinfo=timezone.utc)


def _valid_envelope() -> EvidenceEnvelope:
    return EvidenceEnvelope.create(
        provenance_class=ProvenanceClass.FIXTURE,
        provider="FIXTURE_SOURCE",
        symbol_or_universe="FIXTURE:UNIT1",
        market_timestamp=_aware(2026, 8, 7, 14),
        retrieval_timestamp=_aware(2026, 8, 7, 15),
        interval="1d",
        timezone="UTC",
        transformation_version="envelope-v1",
    )


class SoftwareCorrectnessTests(unittest.TestCase):
    def test_modules_import(self) -> None:
        package = importlib.import_module("radar_v4")
        evidence = importlib.import_module("radar_v4.evidence")
        validation = importlib.import_module("radar_v4.validation")
        self.assertTrue(hasattr(package, "EvidenceEnvelope"))
        self.assertTrue(hasattr(evidence, "EvidenceEnvelope"))
        self.assertTrue(hasattr(validation, "validate_envelope"))

    def test_introduced_python_files_parse(self) -> None:
        root = Path(__file__).resolve().parents[1]
        files = [
            root / "radar_v4" / "__init__.py",
            root / "radar_v4" / "evidence.py",
            root / "radar_v4" / "validation.py",
            root / "tests" / "test_evidence_software.py",
            root / "tests" / "test_evidence_data.py",
        ]
        for path in files:
            py_compile(str(path), doraise=True)

    def test_valid_envelope_construction(self) -> None:
        envelope = _valid_envelope()
        result = validate_envelope(envelope)
        self.assertTrue(result.valid)
        self.assertEqual(result.issues, ())
        self.assertEqual(envelope.provenance_class, ProvenanceClass.FIXTURE.value)
        self.assertIsNotNone(envelope.checksum)

    def test_identical_input_serializes_deterministically(self) -> None:
        first = _valid_envelope().serialize()
        second = _valid_envelope().serialize()
        self.assertEqual(first, second)
        self.assertTrue(SERIALIZATION_RULES)

    def test_serialize_deserialize_round_trip_preserves_identity(self) -> None:
        original = _valid_envelope()
        restored = EvidenceEnvelope.deserialize(original.serialize())
        self.assertEqual(original.provenance_class, restored.provenance_class)
        self.assertEqual(original.provider, restored.provider)
        self.assertEqual(original.symbol_or_universe, restored.symbol_or_universe)
        self.assertEqual(original.market_timestamp, restored.market_timestamp)
        self.assertEqual(original.retrieval_timestamp, restored.retrieval_timestamp)
        self.assertEqual(original.interval, restored.interval)
        self.assertEqual(original.timezone, restored.timezone)
        self.assertEqual(original.transformation_version, restored.transformation_version)
        self.assertEqual(original.checksum, restored.checksum)
        self.assertEqual(original.context_decision_use_tag, restored.context_decision_use_tag)

    def test_checksum_generation_is_deterministic(self) -> None:
        first = _valid_envelope()
        second = _valid_envelope()
        self.assertEqual(first.checksum, second.checksum)
        self.assertEqual(first.compute_checksum(), second.compute_checksum())
        self.assertNotIn(first.checksum, first.canonical_bytes().decode("utf-8"))

    def test_checksum_mismatch_is_detected(self) -> None:
        envelope = _valid_envelope().with_checksum("0" * 64)
        result = validate_envelope(envelope)
        self.assertFalse(result.valid)
        self.assertIn("CHECKSUM_MISMATCH", result.issue_codes())

    def test_validation_result_has_stable_structured_form(self) -> None:
        envelope = EvidenceEnvelope(
            provenance_class=None,
            provider=None,
            symbol_or_universe=None,
            market_timestamp=None,
            retrieval_timestamp=None,
            interval=None,
            timezone=None,
            transformation_version=None,
        )
        first = validate_envelope(envelope)
        second = validate_envelope(envelope)
        self.assertIsInstance(first, ValidationResult)
        self.assertFalse(first.valid)
        self.assertGreater(len(first.issues), 1)
        self.assertEqual(first, second)
        self.assertEqual(first.issue_codes(), second.issue_codes())
        for issue in first.issues:
            self.assertTrue(issue.code)
            self.assertTrue(issue.reason)
            self.assertTrue(issue.field)


if __name__ == "__main__":
    unittest.main()
