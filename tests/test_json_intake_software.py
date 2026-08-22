"""SOFTWARE CORRECTNESS — Build Unit 3 JSON document intake."""

from __future__ import annotations

import importlib
import unittest
from datetime import datetime, timezone
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.evidence import EvidenceEnvelope, ProvenanceClass
from radar_v4.json_intake import DocumentIntakeReport, intake_json_text


def _valid() -> EvidenceEnvelope:
    return EvidenceEnvelope.create(
        provenance_class=ProvenanceClass.FIXTURE,
        provider="FIXTURE_SOURCE",
        symbol_or_universe="FIXTURE:UNIT3",
        market_timestamp=datetime(2026, 8, 7, 14, tzinfo=timezone.utc),
        retrieval_timestamp=datetime(2026, 8, 7, 15, tzinfo=timezone.utc),
        interval="1d",
        timezone="UTC",
        transformation_version="envelope-v1",
    )


class JsonIntakeSoftwareTests(unittest.TestCase):
    def test_modules_import(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "intake_json_text"))

    def test_files_parse(self) -> None:
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "json_intake.py"), doraise=True)

    def test_single_object_round_trip(self) -> None:
        envelope = _valid()
        report = intake_json_text(envelope.serialize())
        self.assertIsInstance(report, DocumentIntakeReport)
        self.assertEqual(report.accepted_count(), 1)
        self.assertEqual(report.unreadable_count(), 0)
        self.assertEqual(report.accepted[0].envelope.checksum, envelope.checksum)

    def test_array_preserves_order(self) -> None:
        first = _valid()
        second = EvidenceEnvelope.create(
            provenance_class=ProvenanceClass.SYNTHETIC,
            provider="SYNTHETIC_SOURCE",
            symbol_or_universe="SYNTHETIC:UNIT3",
            market_timestamp=datetime(2026, 8, 7, 14, tzinfo=timezone.utc),
            retrieval_timestamp=datetime(2026, 8, 7, 15, tzinfo=timezone.utc),
            interval="1d",
            timezone="UTC",
            transformation_version="envelope-v1",
        )
        text = f"[{first.serialize()},{second.serialize()}]"
        report = intake_json_text(text)
        self.assertEqual(
            [item.envelope.symbol_or_universe for item in report.accepted],
            ["FIXTURE:UNIT3", "SYNTHETIC:UNIT3"],
        )


if __name__ == "__main__":
    unittest.main()
