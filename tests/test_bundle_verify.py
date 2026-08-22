"""SOFTWARE CORRECTNESS — Phase 5 snapshot bundle verify."""

from __future__ import annotations

import importlib
import tempfile
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.bundle_verify import verify_snapshot_bundle
from radar_v4.checksum_sidecar import write_checksum_sidecar
from radar_v4.dataset import DatasetDeclaration
from radar_v4.evidence import ProvenanceClass
from radar_v4.observation import Observation, ObservationPayload
from radar_v4.ruler_file import write_ruler_sidecar
from radar_v4.session import run_dataset_session
from radar_v4.snapshot_files import write_snapshot_file
from tests.helpers import envelope


def _session():
    declaration = DatasetDeclaration(
        dataset_id="phase5-bundle",
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
    return run_dataset_session(declaration, (item.envelope,), (item,))


class BundleVerifyTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "verify_snapshot_bundle"))
        self.assertTrue(hasattr(package, "BundleVerification"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "bundle_verify.py"), doraise=True)

    def test_optional_sidecars_are_not_required(self) -> None:
        result = _session()
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "snap.json"
            write_snapshot_file(path, result.snapshot)
            verification = verify_snapshot_bundle(path)
        self.assertTrue(verification.matched)
        self.assertFalse(verification.sidecar_present)
        self.assertFalse(verification.ruler_present)
        self.assertIsNone(verification.sidecar_matched)
        self.assertIsNone(verification.ruler_matched)

    def test_require_sidecar_refuses_a_missing_file(self) -> None:
        result = _session()
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "snap.json"
            write_snapshot_file(path, result.snapshot)
            verification = verify_snapshot_bundle(path, require_sidecar=True)
        self.assertFalse(verification.matched)
        self.assertEqual(verification.issues, ("BUNDLE_SIDECAR_MISSING",))

    def test_matching_sidecars_pass(self) -> None:
        result = _session()
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "snap.json"
            write_snapshot_file(path, result.snapshot)
            write_checksum_sidecar(path)
            write_ruler_sidecar(path, result.snapshot.declaration)
            verification = verify_snapshot_bundle(
                path, require_sidecar=True, require_ruler=True
            )
        self.assertTrue(verification.matched)
        self.assertTrue(verification.sidecar_matched)
        self.assertTrue(verification.ruler_matched)

    def test_tampered_sidecar_fails(self) -> None:
        result = _session()
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "snap.json"
            write_snapshot_file(path, result.snapshot)
            sidecar = write_checksum_sidecar(path)
            sidecar.write_text("0" * 64 + "\n", encoding="utf-8")
            verification = verify_snapshot_bundle(path)
        self.assertFalse(verification.matched)
        self.assertEqual(verification.issues, ("SNAPSHOT_CHECKSUM_MISMATCH",))


if __name__ == "__main__":
    unittest.main()
