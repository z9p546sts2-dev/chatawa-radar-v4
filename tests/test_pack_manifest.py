"""SOFTWARE CORRECTNESS — Phase 5 pack integrity manifest."""

from __future__ import annotations

import importlib
import json
import tempfile
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.dataset_pack import load_dataset_pack
from radar_v4.evidence import ProvenanceClass
from radar_v4.local_session import run_session_from_pack
from radar_v4.observation import Observation, ObservationPayload
from radar_v4.pack_manifest import (
    PackManifestError,
    compare_pack_manifests,
    verify_pack_manifest,
    write_pack_manifest,
)
from tests.helpers import envelope
from tests.test_dataset_pack import _declaration, _write_obs


class PackManifestTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "write_pack_manifest"))
        self.assertTrue(hasattr(package, "compare_pack_manifests"))
        self.assertTrue(hasattr(package, "ManifestComparison"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "pack_manifest.py"), doraise=True)

    def test_write_and_verify(self) -> None:
        item = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA"),
            ObservationPayload(close="10.00"),
        )
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "declaration.json").write_text(
                json.dumps(_declaration()), encoding="utf-8"
            )
            _write_obs(root / "obs.json", item)
            write_pack_manifest(root)
            verify_pack_manifest(root)
            (root / "obs.json").write_text("tampered", encoding="utf-8")
            with self.assertRaises(PackManifestError) as ctx:
                verify_pack_manifest(root)
            self.assertEqual(ctx.exception.code, "MANIFEST_CHECKSUM_MISMATCH")

    def test_journal_file_is_not_loaded_as_an_observation(self) -> None:
        item = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA"),
            ObservationPayload(close="10.00"),
        )
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "declaration.json").write_text(
                json.dumps(_declaration()), encoding="utf-8"
            )
            _write_obs(root / "obs.json", item)
            (root / "journal.json").write_text('{"not":"an observation"}', encoding="utf-8")
            report = load_dataset_pack(root)
        self.assertTrue(report.usable())
        self.assertEqual(report.observation_intake.accepted_count(), 1)
        self.assertEqual(report.observation_intake.unreadable_count(), 0)

    def test_repo_synthetic_pack_matches_its_manifest(self) -> None:
        root = Path(__file__).resolve().parents[1] / "fixtures" / "synthetic_one_symbol_1d"
        verify_pack_manifest(root)

    def test_tampered_manifested_pack_is_not_usable(self) -> None:
        item = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA"),
            ObservationPayload(close="10.00"),
        )
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "declaration.json").write_text(
                json.dumps(_declaration()), encoding="utf-8"
            )
            _write_obs(root / "obs.json", item)
            write_pack_manifest(root)
            (root / "obs.json").write_text("tampered", encoding="utf-8")
            report = load_dataset_pack(root)
            session = run_session_from_pack(root)
        self.assertFalse(report.usable())
        self.assertEqual(report.pack_issues[0].code, "MANIFEST_CHECKSUM_MISMATCH")
        self.assertIsNone(session.session)

    def test_require_manifest_refuses_a_pack_without_one(self) -> None:
        item = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA"),
            ObservationPayload(close="10.00"),
        )
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "declaration.json").write_text(
                json.dumps(_declaration()), encoding="utf-8"
            )
            _write_obs(root / "obs.json", item)
            report = load_dataset_pack(root, require_manifest=True)
        self.assertFalse(report.usable())
        self.assertEqual(report.pack_issues[0].code, "MANIFEST_REQUIRED")

    def test_compare_identical_manifests(self) -> None:
        root = Path(__file__).resolve().parents[1] / "fixtures" / "synthetic_one_symbol_1d"
        comparison = compare_pack_manifests(root, root)
        self.assertTrue(comparison.equal)

    def test_compare_reports_digest_mismatch(self) -> None:
        first = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA"),
            ObservationPayload(close="10.00"),
        )
        second = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA"),
            ObservationPayload(close="11.00"),
        )
        with tempfile.TemporaryDirectory() as raw:
            left = Path(raw) / "left"
            right = Path(raw) / "right"
            left.mkdir()
            right.mkdir()
            (left / "declaration.json").write_text(
                json.dumps(_declaration()), encoding="utf-8"
            )
            (right / "declaration.json").write_text(
                json.dumps(_declaration()), encoding="utf-8"
            )
            _write_obs(left / "obs.json", first)
            _write_obs(right / "obs.json", second)
            write_pack_manifest(left)
            write_pack_manifest(right)
            comparison = compare_pack_manifests(left, right)
        self.assertFalse(comparison.equal)
        self.assertEqual(comparison.digest_mismatches, ("obs.json",))


if __name__ == "__main__":
    unittest.main()
