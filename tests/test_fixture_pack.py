"""SOFTWARE and DATA CORRECTNESS — Build Unit 6 fixture pack loader."""

from __future__ import annotations

import importlib
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.evidence import EvidenceEnvelope, ProvenanceClass
from radar_v4.fixture_pack import load_fixture_pack


def _envelope(provenance: ProvenanceClass, symbol: str) -> EvidenceEnvelope:
    return EvidenceEnvelope.create(
        provenance_class=provenance,
        provider="PACK_SOURCE",
        symbol_or_universe=symbol,
        market_timestamp=datetime(2026, 8, 7, 14, tzinfo=timezone.utc),
        retrieval_timestamp=datetime(2026, 8, 7, 15, tzinfo=timezone.utc),
        interval="1d",
        timezone="UTC",
        transformation_version="envelope-v1",
    )


class FixturePackTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "load_fixture_pack"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "fixture_pack.py"), doraise=True)

    def test_missing_directory_is_unreadable(self) -> None:
        report = load_fixture_pack("/tmp/radar-v4-no-such-pack")
        self.assertEqual(report.unreadable[0].code, "UNREADABLE_PACK")
        self.assertEqual(report.accepted_count(), 0)

    def test_fixture_file_is_accepted(self) -> None:
        envelope = _envelope(ProvenanceClass.FIXTURE, "FIXTURE:PACK")
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "sample.json"
            path.write_text(envelope.serialize(), encoding="utf-8")
            report = load_fixture_pack(raw)
        self.assertEqual(report.accepted_count(), 1)
        self.assertEqual(report.accepted[0].envelope.symbol_or_universe, "FIXTURE:PACK")

    def test_historical_label_is_quarantined_by_pack_policy(self) -> None:
        envelope = _envelope(ProvenanceClass.HISTORICAL, "HIST:PACK")
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "historical.json"
            path.write_text(envelope.serialize(), encoding="utf-8")
            report = load_fixture_pack(raw)
        self.assertEqual(report.accepted_count(), 0)
        self.assertEqual(report.quarantined_count(), 1)
        self.assertIn(
            "PACK_PROVENANCE_NOT_ALLOWED",
            report.quarantined[0].validation.issue_codes(),
        )


if __name__ == "__main__":
    unittest.main()
