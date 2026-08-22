"""SOFTWARE CORRECTNESS — Phase 5 snapshot integrity verify."""

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
from radar_v4.snapshot_files import write_snapshot_file
from radar_v4.snapshot_verify import verify_snapshot, verify_snapshot_file
from tests.helpers import envelope


class SnapshotVerifyTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "verify_snapshot"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "snapshot_verify.py"), doraise=True)

    def test_expected_checksum_match_and_mismatch(self) -> None:
        declaration = DatasetDeclaration(
            dataset_id="phase5-verify",
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
        item = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA"),
            ObservationPayload(close="10.00"),
        )
        result = run_dataset_session(declaration, (item.envelope,), (item,))
        checksum = result.snapshot.integrity_checksum()
        matched = verify_snapshot(result.snapshot, checksum)
        self.assertTrue(matched.matched)
        mismatched = verify_snapshot(result.snapshot, "0" * 64)
        self.assertFalse(mismatched.matched)
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "snap.json"
            write_snapshot_file(path, result.snapshot)
            from_file = verify_snapshot_file(path, checksum)
        self.assertTrue(from_file.matched)


if __name__ == "__main__":
    unittest.main()
