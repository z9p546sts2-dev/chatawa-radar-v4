"""SOFTWARE CORRECTNESS — Phase 5 snapshot checksum sidecar."""

from __future__ import annotations

import importlib
import tempfile
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.checksum_sidecar import (
    sidecar_path,
    verify_checksum_sidecar,
    write_checksum_sidecar,
)
from radar_v4.dataset import DatasetDeclaration
from radar_v4.evidence import ProvenanceClass
from radar_v4.observation import Observation, ObservationPayload
from radar_v4.session import run_dataset_session
from radar_v4.snapshot_files import SnapshotFileError, write_snapshot_file
from tests.helpers import envelope


class ChecksumSidecarTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "write_checksum_sidecar"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "checksum_sidecar.py"), doraise=True)

    def test_write_and_verify(self) -> None:
        declaration = DatasetDeclaration(
            dataset_id="phase5-sidecar",
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
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "snap.json"
            write_snapshot_file(path, result.snapshot)
            written = write_checksum_sidecar(path)
            self.assertEqual(written, sidecar_path(path))
            verification = verify_checksum_sidecar(path)
            self.assertTrue(verification.matched)
            written.write_text("0" * 64 + "\n", encoding="utf-8")
            mismatched = verify_checksum_sidecar(path)
            self.assertFalse(mismatched.matched)

    def test_missing_sidecar_does_not_invent_a_checksum(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "snap.json"
            path.write_text("{}", encoding="utf-8")
            with self.assertRaises(SnapshotFileError) as ctx:
                verify_checksum_sidecar(path)
            self.assertEqual(ctx.exception.code, "UNREADABLE_SIDECAR")


if __name__ == "__main__":
    unittest.main()
