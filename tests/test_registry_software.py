"""SOFTWARE CORRECTNESS — Build Unit 4 in-memory registry."""

from __future__ import annotations

import importlib
import unittest
from datetime import datetime, timezone
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.evidence import EvidenceEnvelope, ProvenanceClass
from radar_v4.registry import EvidenceRegistry


def _valid(symbol: str = "FIXTURE:UNIT4") -> EvidenceEnvelope:
    return EvidenceEnvelope.create(
        provenance_class=ProvenanceClass.FIXTURE,
        provider="FIXTURE_SOURCE",
        symbol_or_universe=symbol,
        market_timestamp=datetime(2026, 8, 7, 14, tzinfo=timezone.utc),
        retrieval_timestamp=datetime(2026, 8, 7, 15, tzinfo=timezone.utc),
        interval="1d",
        timezone="UTC",
        transformation_version="envelope-v1",
    )


class RegistrySoftwareTests(unittest.TestCase):
    def test_modules_import(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "EvidenceRegistry"))

    def test_files_parse(self) -> None:
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "registry.py"), doraise=True)

    def test_put_and_get_round_trip(self) -> None:
        registry = EvidenceRegistry()
        envelope = _valid()
        report = registry.put((envelope,))
        self.assertEqual(report.accepted_count(), 1)
        stored = registry.get(envelope)
        self.assertIsNotNone(stored)
        self.assertEqual(stored.checksum, envelope.checksum)

    def test_empty_registry_counts(self) -> None:
        registry = EvidenceRegistry()
        self.assertEqual(registry.accepted_count(), 0)
        self.assertEqual(registry.quarantined_count(), 0)


if __name__ == "__main__":
    unittest.main()
