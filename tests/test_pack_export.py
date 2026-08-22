"""SOFTWARE and DATA CORRECTNESS — Phase 5 snapshot-to-pack export."""

from __future__ import annotations

import importlib
import tempfile
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.dataset import DatasetDeclaration
from radar_v4.dataset_pack import load_dataset_pack
from radar_v4.evidence import ProvenanceClass
from radar_v4.local_session import run_session_from_pack
from radar_v4.observation import Observation, ObservationPayload
from radar_v4.pack_export import PackExportError, export_snapshot_to_pack
from radar_v4.pack_manifest import verify_pack_manifest
from radar_v4.session import run_dataset_session
from tests.helpers import envelope


def _declaration(provenance: str = "SYNTHETIC") -> DatasetDeclaration:
    return DatasetDeclaration(
        dataset_id="phase5-export",
        provenance_class=provenance,
        provider="PHASE5_SOURCE",
        universe="SYN:AAA",
        interval="1d",
        timezone="UTC",
        transformation_version="phase5-v1",
        adjustment_policy="UNADJUSTED",
        locked_question="ordinary close-to-close changes for one symbol",
        primary_metric="close-to-close difference",
    )


class PackExportTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "export_snapshot_to_pack"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "pack_export.py"), doraise=True)

    def test_export_round_trips_through_pack_session(self) -> None:
        first = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA", day=7),
            ObservationPayload(close="10.00"),
        )
        second = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA", day=8),
            ObservationPayload(close="12.00"),
        )
        original = run_dataset_session(
            _declaration(), (first.envelope, second.envelope), (first, second)
        )
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw) / "pack"
            export_snapshot_to_pack(original.snapshot, out)
            verify_pack_manifest(out)
            loaded = load_dataset_pack(out)
            self.assertTrue(loaded.usable())
            replayed = run_session_from_pack(out)
        assert replayed.session is not None and replayed.session.baseline is not None
        assert original.baseline is not None
        self.assertEqual(replayed.session.baseline.changes, original.baseline.changes)

    def test_historical_export_is_refused(self) -> None:
        item = Observation.create(
            envelope(provenance=ProvenanceClass.HISTORICAL, symbol="SYN:AAA"),
            ObservationPayload(close="10.00"),
        )
        result = run_dataset_session(
            _declaration("HISTORICAL"), (item.envelope,), (item,)
        )
        with tempfile.TemporaryDirectory() as raw:
            with self.assertRaises(PackExportError) as ctx:
                export_snapshot_to_pack(result.snapshot, Path(raw) / "pack")
        self.assertEqual(ctx.exception.code, "PACK_PROVENANCE_NOT_ALLOWED")

    def test_non_empty_directory_is_refused(self) -> None:
        item = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA"),
            ObservationPayload(close="10.00"),
        )
        result = run_dataset_session(_declaration(), (item.envelope,), (item,))
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw)
            (out / "already.txt").write_text("no", encoding="utf-8")
            with self.assertRaises(PackExportError) as ctx:
                export_snapshot_to_pack(result.snapshot, out)
        self.assertEqual(ctx.exception.code, "PACK_EXPORT_DIRECTORY_NOT_EMPTY")


if __name__ == "__main__":
    unittest.main()
