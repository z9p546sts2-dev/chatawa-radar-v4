"""SOFTWARE and DATA CORRECTNESS — Phase 5 local pack/snapshot session."""

from __future__ import annotations

import importlib
import json
import tempfile
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.dataset import DatasetDeclaration
from radar_v4.evidence import ProvenanceClass
from radar_v4.local_session import (
    run_session_from_pack,
    run_session_from_snapshot,
    run_session_from_snapshot_file,
)
from radar_v4.session_report import serialize_local_session_report
from radar_v4.observation import Observation, ObservationPayload
from radar_v4.session import run_dataset_session
from radar_v4.snapshot_files import write_snapshot_file
from tests.helpers import envelope


def _declaration() -> DatasetDeclaration:
    return DatasetDeclaration(
        dataset_id="phase5-local",
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


def _obs(day: int, close: str) -> Observation:
    return Observation.create(
        envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA", day=day),
        ObservationPayload(close=close),
    )


class LocalSessionTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "run_session_from_pack"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "local_session.py"), doraise=True)

    def test_pack_session_measures_close_to_close(self) -> None:
        first = _obs(7, "10.00")
        second = _obs(8, "12.00")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "declaration.json").write_text(
                json.dumps(
                    {
                        "dataset_id": "phase5-local",
                        "provenance_class": "SYNTHETIC",
                        "provider": "PHASE5_SOURCE",
                        "universe": "SYN:AAA",
                        "interval": "1d",
                        "timezone": "UTC",
                        "transformation_version": "phase5-v1",
                        "adjustment_policy": "UNADJUSTED",
                        "locked_question": "ordinary close-to-close changes for one symbol",
                        "primary_metric": "close-to-close difference",
                    }
                ),
                encoding="utf-8",
            )
            for name, item in (("a.json", first), ("b.json", second)):
                (root / name).write_text(
                    json.dumps(
                        {
                            "envelope": item.envelope.serialize(),
                            "payload": item.payload.canonical_payload(),
                        }
                    ),
                    encoding="utf-8",
                )
            result = run_session_from_pack(root)
        self.assertIsNone(result.error_code)
        assert result.session is not None
        assert result.session.baseline is not None
        self.assertEqual(result.session.baseline.status, "MEASURED")
        self.assertEqual(result.session.baseline.changes, ("2.00",))

    def test_unusable_pack_does_not_invent_a_session(self) -> None:
        result = run_session_from_pack("/tmp/radar-v4-no-such-local-session")
        self.assertEqual(result.error_code, "PACK_NOT_USABLE")
        self.assertIsNone(result.session)
        document = json.loads(serialize_local_session_report(result))
        self.assertIsNone(document["session"])
        self.assertEqual(document["error_code"], "PACK_NOT_USABLE")
        self.assertIn("UNREADABLE_PACK", document["pack_unreadable_codes"])

    def test_snapshot_round_trip_replays_baseline(self) -> None:
        first = _obs(7, "10.00")
        second = _obs(8, "11.50")
        original = run_dataset_session(
            _declaration(),
            (first.envelope, second.envelope),
            (first, second),
        )
        replayed = run_session_from_snapshot(original.snapshot)
        self.assertIsNotNone(replayed.baseline)
        assert original.baseline is not None and replayed.baseline is not None
        self.assertEqual(replayed.baseline.changes, original.baseline.changes)

        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "snapshot.json"
            write_snapshot_file(path, original.snapshot)
            from_file = run_session_from_snapshot_file(path)
        assert from_file.baseline is not None
        self.assertEqual(from_file.baseline.changes, original.baseline.changes)


if __name__ == "__main__":
    unittest.main()
