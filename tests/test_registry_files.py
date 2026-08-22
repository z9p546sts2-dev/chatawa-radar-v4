"""SOFTWARE CORRECTNESS — Phase 5 local registry files."""

from __future__ import annotations

import importlib
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.evidence import EvidenceEnvelope, ProvenanceClass
from radar_v4.registry import EvidenceRegistry
from radar_v4.registry_files import RegistryFileError, read_registry_file, write_registry_file


def _valid(symbol: str = "FIXTURE:REGFILE") -> EvidenceEnvelope:
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


class RegistryFileTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "write_registry_file"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "registry_files.py"), doraise=True)

    def test_round_trip_preserves_accepted_and_quarantined(self) -> None:
        registry = EvidenceRegistry()
        good = _valid()
        bad = good.with_checksum("0" * 64)
        registry.put((good, bad))
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "registry.json"
            write_registry_file(path, registry)
            loaded = read_registry_file(path)
        self.assertEqual(loaded.accepted_count(), 1)
        self.assertEqual(loaded.quarantined_count(), 1)
        self.assertEqual(loaded.accepted_envelopes()[0].checksum, good.checksum)
        self.assertIn(
            "CHECKSUM_MISMATCH",
            loaded.quarantined_records()[0].validation.issue_codes(),
        )

    def test_unreadable_file_does_not_invent_registry(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "bad.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaises(RegistryFileError) as ctx:
                read_registry_file(path)
        self.assertEqual(ctx.exception.code, "UNREADABLE_REGISTRY_FILE")

    def test_wrong_document_kind_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "registry.json"
            path.write_text(
                '{"document_kind":"not-a-registry","accepted":[],"quarantined":[]}',
                encoding="utf-8",
            )
            with self.assertRaises(RegistryFileError) as ctx:
                read_registry_file(path)
            self.assertEqual(ctx.exception.code, "UNREADABLE_REGISTRY_FILE")


if __name__ == "__main__":
    unittest.main()
