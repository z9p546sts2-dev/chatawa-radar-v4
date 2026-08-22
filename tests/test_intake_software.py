"""SOFTWARE CORRECTNESS — Build Unit 2.

These tests prove intake/quarantine software behavior only.
They do not prove market correctness, method validity, or edge.
"""

from __future__ import annotations

import importlib
import unittest
from datetime import datetime, timezone
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.evidence import EvidenceEnvelope, ProvenanceClass
from radar_v4.intake import IntakeReport, intake_envelopes
from radar_v4.validation import validate_envelope


def _aware(hour: int) -> datetime:
    return datetime(2026, 8, 7, hour, 0, 0, tzinfo=timezone.utc)


def _valid() -> EvidenceEnvelope:
    return EvidenceEnvelope.create(
        provenance_class=ProvenanceClass.FIXTURE,
        provider="FIXTURE_SOURCE",
        symbol_or_universe="FIXTURE:UNIT2",
        market_timestamp=_aware(14),
        retrieval_timestamp=_aware(15),
        interval="1d",
        timezone="UTC",
        transformation_version="envelope-v1",
    )


class IntakeSoftwareCorrectnessTests(unittest.TestCase):
    def test_modules_import(self) -> None:
        package = importlib.import_module("radar_v4")
        intake = importlib.import_module("radar_v4.intake")
        self.assertTrue(hasattr(package, "intake_envelopes"))
        self.assertTrue(hasattr(intake, "intake_envelopes"))

    def test_introduced_python_files_parse(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for path in (
            root / "radar_v4" / "intake.py",
            root / "tests" / "test_intake_software.py",
            root / "tests" / "test_intake_data.py",
        ):
            py_compile(str(path), doraise=True)

    def test_empty_batch_is_stable(self) -> None:
        report = intake_envelopes(())
        self.assertIsInstance(report, IntakeReport)
        self.assertEqual(report.accepted, ())
        self.assertEqual(report.quarantined, ())
        self.assertEqual(report, intake_envelopes(()))

    def test_valid_envelope_is_accepted(self) -> None:
        envelope = _valid()
        report = intake_envelopes((envelope,))
        self.assertEqual(report.accepted_count(), 1)
        self.assertEqual(report.quarantined_count(), 0)
        self.assertIs(report.accepted[0].envelope, envelope)
        self.assertTrue(report.accepted[0].validation.valid)

    def test_input_order_is_preserved_within_partitions(self) -> None:
        first = _valid()
        second = EvidenceEnvelope.create(
            provenance_class=ProvenanceClass.SYNTHETIC,
            provider="SYNTHETIC_SOURCE",
            symbol_or_universe="SYNTHETIC:UNIT2",
            market_timestamp=_aware(14),
            retrieval_timestamp=_aware(15),
            interval="1d",
            timezone="UTC",
            transformation_version="envelope-v1",
        )
        report = intake_envelopes((first, second))
        self.assertEqual(
            [record.envelope.symbol_or_universe for record in report.accepted],
            ["FIXTURE:UNIT2", "SYNTHETIC:UNIT2"],
        )

    def test_intake_does_not_mutate_envelopes(self) -> None:
        envelope = _valid()
        before = envelope.serialize()
        intake_envelopes((envelope,))
        self.assertEqual(envelope.serialize(), before)
        self.assertTrue(validate_envelope(envelope).valid)


if __name__ == "__main__":
    unittest.main()
