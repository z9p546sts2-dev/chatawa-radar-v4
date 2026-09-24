"""Offline receipt tests use artificial schema records, never market evidence."""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import timedelta
from hashlib import sha256
from pathlib import Path

from radar_v4.evidence import EvidenceEnvelope, ProvenanceClass
from radar_v4.manual_observation import ManualObservationError, prepare_manual_observation
from radar_v4.observation import Observation, ObservationPayload
from tests.helpers import envelope


class ManualObservationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.custody = self.base / "private"
        self.custody.mkdir(mode=0o700)
        self.raw = self.base / "raw.txt"
        self.raw.write_bytes(b'{"artificial":"completed-bar"}')
        self.observation_path = self.base / "observation.json"

    def _write_observation(self, item: Observation) -> None:
        self.observation_path.write_text(
            json.dumps(
                {
                    "envelope": item.envelope.serialize(),
                    "payload": item.payload.canonical_payload(),
                    "payload_checksum": item.payload_checksum,
                }
            ),
            encoding="utf-8",
        )

    def test_append_only_receipt_preserves_raw_and_observation_hashes(self) -> None:
        item = Observation.create(
            envelope(provenance=ProvenanceClass.HISTORICAL, symbol="TEST_ONLY"),
            ObservationPayload(close="10.00"),
        )
        self._write_observation(item)
        first = prepare_manual_observation(self.observation_path, self.raw, self.custody)
        receipt = json.loads(first.read_text(encoding="utf-8"))
        self.assertEqual(receipt["review_status"], "pending_source_review")
        self.assertEqual(receipt["raw_sha256"], sha256(self.raw.read_bytes()).hexdigest())
        self.assertEqual(
            receipt["observation_sha256"],
            sha256(self.observation_path.read_bytes()).hexdigest(),
        )
        self.assertEqual((first.parent / "raw.bin").read_bytes(), self.raw.read_bytes())
        second = prepare_manual_observation(self.observation_path, self.raw, self.custody)
        self.assertNotEqual(first, second)
        self.assertEqual(json.loads(first.read_text(encoding="utf-8")), receipt)

    def test_missing_checksum_and_fixture_provenance_are_refused(self) -> None:
        historical = Observation.create(
            envelope(provenance=ProvenanceClass.HISTORICAL),
            ObservationPayload(close="10"),
        )
        self.observation_path.write_text(
            json.dumps(
                {
                    "envelope": historical.envelope.serialize(),
                    "payload": historical.payload.canonical_payload(),
                }
            ),
            encoding="utf-8",
        )
        with self.assertRaises(ManualObservationError) as error:
            prepare_manual_observation(self.observation_path, self.raw, self.custody)
        self.assertEqual(error.exception.code, "INVALID_OBSERVATION")
        self.assertEqual(list(self.custody.iterdir()), [])

        fixture = Observation.create(envelope(), ObservationPayload(close="10"))
        self._write_observation(fixture)
        with self.assertRaises(ManualObservationError) as error:
            prepare_manual_observation(self.observation_path, self.raw, self.custody)
        self.assertEqual(error.exception.code, "OBSERVATION_NOT_ADMITTED")

    def test_retrieval_before_market_is_refused(self) -> None:
        initial = envelope(provenance=ProvenanceClass.HISTORICAL)
        earlier = EvidenceEnvelope.create(
            provenance_class=ProvenanceClass.HISTORICAL,
            provider=initial.provider or "",
            symbol_or_universe=initial.symbol_or_universe or "",
            market_timestamp=initial.market_timestamp,
            retrieval_timestamp=initial.market_timestamp - timedelta(minutes=1),
            interval="1d",
            timezone="UTC",
            transformation_version="test-only",
        )
        self._write_observation(Observation.create(earlier, ObservationPayload(close="10")))
        with self.assertRaises(ManualObservationError) as error:
            prepare_manual_observation(self.observation_path, self.raw, self.custody)
        self.assertEqual(error.exception.code, "RETRIEVAL_BEFORE_MARKET")
        self.assertEqual(list(self.custody.iterdir()), [])

    def test_repository_custody_path_is_refused(self) -> None:
        with self.assertRaises(ManualObservationError) as error:
            prepare_manual_observation(self.observation_path, self.raw, Path(__file__).resolve().parents[1])
        self.assertEqual(error.exception.code, "PUBLIC_PATH_REFUSED")

    def test_raw_file_must_be_distinct(self) -> None:
        with self.assertRaises(ManualObservationError) as error:
            prepare_manual_observation(self.raw, self.raw, self.custody)
        self.assertEqual(error.exception.code, "INVALID_OBSERVATION")

    def test_other_git_worktree_is_not_custody(self) -> None:
        worktree = self.base / "another-project"
        worktree.mkdir()
        (worktree / ".git").mkdir()
        candidate = worktree / "custody"
        candidate.mkdir(mode=0o700)
        with self.assertRaises(ManualObservationError) as error:
            prepare_manual_observation(self.observation_path, self.raw, candidate)
        self.assertEqual(error.exception.code, "PUBLIC_PATH_REFUSED")


if __name__ == "__main__":
    unittest.main()
