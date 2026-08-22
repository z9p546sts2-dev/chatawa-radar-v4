"""SOFTWARE CORRECTNESS — Phase 5 dataset snapshot."""

from __future__ import annotations

import importlib
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.dataset import DatasetDeclaration
from radar_v4.evidence import ProvenanceClass
from radar_v4.observation import Observation, ObservationPayload
from radar_v4.snapshot import DatasetSnapshot, make_snapshot
from tests.helpers import envelope


class SnapshotTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "DatasetSnapshot"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "snapshot.py"), doraise=True)

    def test_round_trip_is_deterministic(self) -> None:
        declaration = DatasetDeclaration(
            dataset_id="phase5-snap",
            provenance_class=ProvenanceClass.SYNTHETIC.value,
            provider="PHASE5_SOURCE",
            universe="FIXTURE:AAA",
            interval="1d",
            timezone="UTC",
            transformation_version="phase5-v1",
            adjustment_policy="UNADJUSTED",
            locked_question="ordinary close-to-close changes for one symbol",
            primary_metric="close-to-close difference",
        )
        item = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC),
            ObservationPayload(close="10.25"),
        )
        first = make_snapshot(declaration, (item,)).serialize()
        second = make_snapshot(declaration, (item,)).serialize()
        self.assertEqual(first, second)
        restored = DatasetSnapshot.deserialize(first)
        self.assertEqual(restored.declaration.dataset_id, "phase5-snap")
        self.assertEqual(restored.observations[0].payload.close, "10.25")
        self.assertEqual(restored.serialize(), first)


if __name__ == "__main__":
    unittest.main()
