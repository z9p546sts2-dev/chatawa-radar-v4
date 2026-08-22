"""SOFTWARE and DATA CORRECTNESS — Phase 5 dataset session."""

from __future__ import annotations

import importlib
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.dataset import DatasetDeclaration
from radar_v4.evidence import ProvenanceClass
from radar_v4.observation import Observation, ObservationPayload
from radar_v4.session import run_dataset_session
from tests.helpers import envelope


def _declaration(**overrides: str) -> DatasetDeclaration:
    values = dict(
        dataset_id="phase5-session",
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


def _obs(day: int, close: str, provenance=ProvenanceClass.SYNTHETIC) -> Observation:
    return Observation.create(
        envelope(provenance=provenance, symbol="SYN:AAA", day=day),
        ObservationPayload(close=close),
    )


class DatasetSessionTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "run_dataset_session"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "session.py"), doraise=True)

    def test_valid_session_runs_baseline_and_snapshot(self) -> None:
        first = _obs(7, "10.00")
        second = _obs(8, "12.00")
        result = run_dataset_session(
            _declaration(),
            (first.envelope, second.envelope),
            (first, second),
        )
        self.assertEqual(result.admission.accepted_count(), 2)
        self.assertEqual(result.admission.quarantined_count(), 0)
        self.assertTrue(result.series.valid)
        self.assertIsNotNone(result.baseline)
        assert result.baseline is not None
        self.assertEqual(result.baseline.claim_level, "LEVEL 0 — MEASURED")
        self.assertEqual(result.baseline.status, "MEASURED")
        self.assertEqual(result.baseline.changes, ("2.00",))
        self.assertEqual(len(result.snapshot.observations), 2)
        self.assertEqual(result.snapshot.declaration.dataset_id, "phase5-session")

    def test_orphan_observation_is_dropped_not_repaired(self) -> None:
        first = _obs(7, "10.00")
        second = _obs(8, "12.00")
        result = run_dataset_session(_declaration(), (first.envelope,), (first, second))
        self.assertEqual(result.kept_observation_count(), 1)
        self.assertEqual(result.rejected_observation_count(), 1)
        self.assertEqual(
            result.rejected_observations[0][1].issue_codes(),
            ("OBSERVATION_NOT_ADMITTED",),
        )
        self.assertEqual(len(result.snapshot.observations), 1)
        self.assertIsNotNone(result.baseline)
        assert result.baseline is not None
        self.assertEqual(result.baseline.status, "INSUFFICIENT_EVIDENCE")

    def test_live_envelope_is_quarantined_not_admitted(self) -> None:
        live = _obs(7, "10.00", provenance=ProvenanceClass.LIVE)
        kept = _obs(8, "11.00")
        later = _obs(9, "12.00")
        result = run_dataset_session(
            _declaration(),
            (live.envelope, kept.envelope, later.envelope),
            (live, kept, later),
        )
        self.assertEqual(result.admission.accepted_count(), 2)
        self.assertEqual(result.admission.quarantined_count(), 1)
        self.assertIn(
            "DATASET_DECLARATION_MISMATCH",
            result.admission.quarantined[0].validation.issue_codes(),
        )
        self.assertEqual(result.kept_observation_count(), 2)
        self.assertEqual(
            result.rejected_observations[0][1].issue_codes(),
            ("OBSERVATION_NOT_ADMITTED",),
        )
        self.assertNotIn(
            ProvenanceClass.LIVE.value,
            [item.envelope.provenance_class for item in result.snapshot.observations],
        )

    def test_duplicate_market_timestamp_blocks_baseline(self) -> None:
        first = _obs(7, "10.00")
        duplicate = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA", day=7),
            ObservationPayload(close="11.00"),
        )
        result = run_dataset_session(
            _declaration(),
            (first.envelope, duplicate.envelope),
            (first, duplicate),
        )
        self.assertFalse(result.series.valid)
        self.assertIsNone(result.baseline)
        self.assertIn("DUPLICATE_MARKET_TIMESTAMP", result.series.issue_codes())


if __name__ == "__main__":
    unittest.main()
