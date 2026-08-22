"""SOFTWARE CORRECTNESS — Phase 5 snapshot comparison."""

from __future__ import annotations

import importlib
import tempfile
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.dataset import DatasetDeclaration
from radar_v4.evidence import ProvenanceClass
from radar_v4.observation import Observation, ObservationPayload
from radar_v4.session import run_dataset_session
from radar_v4.snapshot_compare import compare_snapshot_files, compare_snapshots
from radar_v4.snapshot_files import write_snapshot_file
from tests.helpers import envelope


def _declaration(**overrides: str) -> DatasetDeclaration:
    values = dict(
        dataset_id="phase5-compare",
        provenance_class=ProvenanceClass.SYNTHETIC.value,
        provider="PHASE5_SOURCE",
        universe="SYN:AAA",
        interval="1d",
        timezone="UTC",
        transformation_version="phase5-v1",
        adjustment_policy="UNADJUSTED",
        locked_question="ordinary close-to-close changes for one symbol",
        primary_metric="close-to-close difference",
    )
    values.update(overrides)
    return DatasetDeclaration(**values)  # type: ignore[arg-type]


def _obs(day: int, close: str) -> Observation:
    return Observation.create(
        envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA", day=day),
        ObservationPayload(close=close),
    )


class SnapshotCompareTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "compare_snapshots"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "snapshot_compare.py"), doraise=True)

    def test_identical_snapshots_are_equal(self) -> None:
        first = _obs(7, "10.00")
        second = _obs(8, "11.00")
        result = run_dataset_session(
            _declaration(), (first.envelope, second.envelope), (first, second)
        )
        comparison = compare_snapshots(result.snapshot, result.snapshot)
        self.assertTrue(comparison.equal)
        self.assertEqual(comparison.declaration_mismatches, ())

    def test_declaration_and_membership_differences(self) -> None:
        first = _obs(7, "10.00")
        second = _obs(8, "11.00")
        left = run_dataset_session(
            _declaration(), (first.envelope, second.envelope), (first, second)
        )
        right = run_dataset_session(
            _declaration(dataset_id="phase5-compare-b"),
            (first.envelope,),
            (first,),
        )
        comparison = compare_snapshots(left.snapshot, right.snapshot)
        self.assertFalse(comparison.equal)
        self.assertIn("dataset_id", comparison.declaration_mismatches)
        self.assertEqual(len(comparison.left_only_envelope_checksums), 1)

    def test_file_compare_round_trip(self) -> None:
        item = _obs(7, "10.00")
        result = run_dataset_session(_declaration(), (item.envelope,), (item,))
        with tempfile.TemporaryDirectory() as raw:
            left = Path(raw) / "left.json"
            right = Path(raw) / "right.json"
            write_snapshot_file(left, result.snapshot)
            write_snapshot_file(right, result.snapshot)
            self.assertTrue(compare_snapshot_files(left, right).equal)


if __name__ == "__main__":
    unittest.main()
