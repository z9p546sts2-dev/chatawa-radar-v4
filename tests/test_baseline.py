"""DATA CORRECTNESS — Phase 5 ordinary close-to-close description."""

from __future__ import annotations

import unittest

from radar_v4.baseline import close_to_close_changes
from radar_v4.evidence import ProvenanceClass
from radar_v4.observation import Observation, ObservationPayload
from tests.helpers import envelope


def _obs(day: int, close: str, provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA"):
    return Observation.create(
        envelope(provenance=provenance, symbol=symbol, day=day),
        ObservationPayload(close=close),
    )


class BaselineTests(unittest.TestCase):
    def test_measured_changes_are_descriptive(self) -> None:
        report = close_to_close_changes((_obs(7, "10.0"), _obs(8, "10.5"), _obs(9, "10.0")))
        self.assertEqual(report.status, "MEASURED")
        self.assertEqual(report.claim_level, "LEVEL 0 — MEASURED")
        self.assertEqual(report.changes, ("0.5", "-0.5"))
        self.assertEqual(len(report.change_records), 2)
        self.assertEqual(report.change_records[0].from_close, "10.0")
        self.assertEqual(report.change_records[0].to_close, "10.5")
        self.assertEqual(report.change_records[0].difference, "0.5")
        self.assertTrue(report.change_records[0].from_market_timestamp)
        self.assertIn("not a threshold, signal, or edge", report.notes)

    def test_single_observation_is_insufficient(self) -> None:
        report = close_to_close_changes((_obs(7, "10.0"),))
        self.assertEqual(report.status, "INSUFFICIENT_EVIDENCE")
        self.assertEqual(report.claim_level, "NONE")

    def test_live_is_refused(self) -> None:
        report = close_to_close_changes(
            (
                _obs(7, "10.0", provenance=ProvenanceClass.LIVE, symbol="LIVE:AAA"),
                _obs(8, "10.5", provenance=ProvenanceClass.LIVE, symbol="LIVE:AAA"),
            )
        )
        self.assertEqual(report.status, "INVALID_COMPARISON")
        self.assertEqual(report.claim_level, "NONE")

    def test_mixed_interval_is_invalid(self) -> None:
        first = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA", day=7),
            ObservationPayload(close="10.0"),
        )
        second = Observation.create(
            envelope(
                provenance=ProvenanceClass.SYNTHETIC,
                symbol="SYN:AAA",
                day=8,
                interval="1h",
            ),
            ObservationPayload(close="10.5"),
        )
        report = close_to_close_changes((first, second))
        self.assertEqual(report.status, "INVALID_COMPARISON")
        self.assertEqual(report.claim_level, "NONE")


if __name__ == "__main__":
    unittest.main()
