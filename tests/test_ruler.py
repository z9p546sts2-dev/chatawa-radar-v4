"""SOFTWARE CORRECTNESS — Phase 5 measurement ruler identity."""

from __future__ import annotations

import importlib
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.dataset import DatasetDeclaration
from radar_v4.evidence import ProvenanceClass
from radar_v4.local_session import run_session_from_snapshot
from radar_v4.observation import Observation, ObservationPayload
from radar_v4.ruler import RulerMismatchError, ruler_checksum, rulers_match
from radar_v4.session import run_dataset_session
from tests.helpers import envelope


def _declaration(**overrides: str) -> DatasetDeclaration:
    values = dict(
        dataset_id="phase5-ruler",
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


class RulerTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "ruler_checksum"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "ruler.py"), doraise=True)

    def test_dataset_id_is_not_the_ruler(self) -> None:
        self.assertTrue(rulers_match(_declaration(), _declaration(dataset_id="other")))
        self.assertEqual(
            ruler_checksum(_declaration()),
            ruler_checksum(_declaration(dataset_id="other")),
        )

    def test_interval_change_is_a_different_ruler(self) -> None:
        self.assertFalse(rulers_match(_declaration(), _declaration(interval="1h")))

    def test_replay_refuses_unexpected_ruler(self) -> None:
        item = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA"),
            ObservationPayload(close="10.00"),
        )
        result = run_dataset_session(
            _declaration(), (item.envelope,), (item,)
        )
        with self.assertRaises(RulerMismatchError) as ctx:
            run_session_from_snapshot(result.snapshot, expected_ruler="0" * 64)
        self.assertEqual(ctx.exception.code, "RULER_MISMATCH")
        replayed = run_session_from_snapshot(
            result.snapshot, expected_ruler=ruler_checksum(result.snapshot.declaration)
        )
        self.assertEqual(replayed.snapshot.declaration.dataset_id, "phase5-ruler")


if __name__ == "__main__":
    unittest.main()
