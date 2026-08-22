"""SOFTWARE and DATA CORRECTNESS — Phase 5 series integrity."""

from __future__ import annotations

import importlib
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.observation import Observation, ObservationPayload
from radar_v4.series import inspect_series
from tests.helpers import envelope


def _obs(day: int, close: str = "10.0") -> Observation:
    return Observation.create(envelope(day=day), ObservationPayload(close=close))


class SeriesTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "inspect_series"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "series.py"), doraise=True)

    def test_orders_by_market_timestamp(self) -> None:
        report = inspect_series((_obs(9), _obs(7), _obs(8)))
        self.assertTrue(report.valid)
        days = [item.envelope.market_timestamp.day for item in report.ordered]
        self.assertEqual(days, [7, 8, 9])

    def test_duplicate_timestamp_is_invalid(self) -> None:
        report = inspect_series((_obs(7, "10.0"), _obs(7, "10.5")))
        self.assertFalse(report.valid)
        self.assertIn("DUPLICATE_MARKET_TIMESTAMP", report.issue_codes())


if __name__ == "__main__":
    unittest.main()
