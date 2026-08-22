"""SOFTWARE CORRECTNESS — Phase 5 close-to-close continuity."""

from __future__ import annotations

import importlib
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.baseline import CloseToCloseChange, close_to_close_changes
from radar_v4.change_continuity import inspect_change_records
from radar_v4.evidence import ProvenanceClass
from radar_v4.observation import Observation, ObservationPayload
from tests.helpers import envelope


class ChangeContinuityTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "inspect_change_records"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "change_continuity.py"), doraise=True)

    def test_measured_records_are_continuous(self) -> None:
        report = close_to_close_changes(
            (
                Observation.create(
                    envelope(
                        provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA", day=7
                    ),
                    ObservationPayload(close="10.0"),
                ),
                Observation.create(
                    envelope(
                        provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA", day=8
                    ),
                    ObservationPayload(close="10.5"),
                ),
                Observation.create(
                    envelope(
                        provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA", day=9
                    ),
                    ObservationPayload(close="10.0"),
                ),
            )
        )
        self.assertTrue(inspect_change_records(report.change_records).valid)

    def test_broken_chain_is_refused(self) -> None:
        records = (
            CloseToCloseChange(
                from_market_timestamp="2026-08-07T14:00:00.000000+00:00",
                to_market_timestamp="2026-08-08T14:00:00.000000+00:00",
                from_close="10.0",
                to_close="10.5",
                difference="0.5",
            ),
            CloseToCloseChange(
                from_market_timestamp="2026-08-09T14:00:00.000000+00:00",
                to_market_timestamp="2026-08-10T14:00:00.000000+00:00",
                from_close="11.0",
                to_close="11.5",
                difference="0.5",
            ),
        )
        result = inspect_change_records(records)
        self.assertFalse(result.valid)
        self.assertIn("CHANGE_DISCONTINUITY", result.issue_codes())


if __name__ == "__main__":
    unittest.main()
