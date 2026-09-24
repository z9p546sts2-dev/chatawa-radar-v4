"""SOFTWARE and DATA CORRECTNESS — Phase 5 observation payload."""

from __future__ import annotations

import importlib
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.observation import Observation, ObservationPayload
from radar_v4.observation_validation import validate_observation
from tests.helpers import envelope


class ObservationTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "Observation"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "observation.py"), doraise=True)
        py_compile(str(root / "radar_v4" / "observation_validation.py"), doraise=True)

    def test_valid_payload(self) -> None:
        item = Observation.create(
            envelope(),
            ObservationPayload(open="10.0", high="11.0", low="9.5", close="10.5"),
        )
        self.assertTrue(validate_observation(item).valid)
        self.assertEqual(item.payload_checksum, item.payload.compute_checksum())

    def test_close_outside_range_rejected(self) -> None:
        item = Observation.create(
            envelope(),
            ObservationPayload(open="10.0", high="11.0", low="9.5", close="12.0"),
        )
        result = validate_observation(item)
        self.assertFalse(result.valid)
        self.assertIn("OHLC_CONTRADICTION", result.issue_codes())

    def test_payload_checksum_mismatch_rejected(self) -> None:
        item = Observation(
            envelope=envelope(),
            payload=ObservationPayload(close="10.0"),
            payload_checksum="0" * 64,
        )
        result = validate_observation(item)
        self.assertFalse(result.valid)
        self.assertIn("PAYLOAD_CHECKSUM_MISMATCH", result.issue_codes())

    def test_invalid_close_rejected(self) -> None:
        item = Observation.create(envelope(), ObservationPayload(close="not-a-number"))
        result = validate_observation(item)
        self.assertFalse(result.valid)
        self.assertIn("INVALID_CLOSE", result.issue_codes())

    def test_nonfinite_values_are_refused_without_crashing(self) -> None:
        for field, value in (
            ("close", "NaN"),
            ("close", "Infinity"),
            ("open", "sNaN"),
            ("high", "NaN"),
            ("low", "-Infinity"),
            ("volume", "Infinity"),
        ):
            with self.subTest(field=field, value=value):
                payload = {"close": "10", "high": "11", "low": "9", field: value}
                result = validate_observation(
                    Observation.create(envelope(), ObservationPayload(**payload))
                )
                self.assertFalse(result.valid)
                self.assertIn(f"INVALID_{field.upper()}", result.issue_codes())

    def test_negative_volume_rejected(self) -> None:
        item = Observation.create(envelope(), ObservationPayload(close="10", volume="-1"))
        self.assertIn("INVALID_VOLUME", validate_observation(item).issue_codes())

    def test_open_outside_range_rejected(self) -> None:
        item = Observation.create(
            envelope(), ObservationPayload(open="12", high="11", low="9", close="10")
        )
        self.assertIn("OHLC_CONTRADICTION", validate_observation(item).issue_codes())

    def test_negative_price_allowed_for_asset_agnostic_observation(self) -> None:
        item = Observation.create(
            envelope(), ObservationPayload(open="-10", high="-9", low="-11", close="-10")
        )
        self.assertTrue(validate_observation(item).valid)


if __name__ == "__main__":
    unittest.main()
