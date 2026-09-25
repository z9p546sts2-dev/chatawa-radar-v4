"""VTI date-only observer accepts a private capture without pack admission."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from radar_v4.cli import main
from radar_v4.vti_date_observe import SOURCE, observe_vti_capture


def _source() -> dict:
    return {
        "historicalPrice": {"ticker": "VTI"},
        "premiumDiscountDetails": [{"pdDetails": [
            {"effectiveDate": "09/21/2026", "marketPrice": "$10.00",
             "nav": "$9.95", "premiumDiscountAmount": "$0.05"},
            {"effectiveDate": "09/22/2026", "marketPrice": "$10.50",
             "nav": "$10.45", "premiumDiscountAmount": "$0.05"},
            {"effectiveDate": "09/23/2026", "marketPrice": "$10.00",
             "nav": "$9.95", "premiumDiscountAmount": "$0.05"},
        ]}],
    }


def _receipt() -> dict:
    return {
        "status": "SOURCE_CAPTURE_ONLY_NOT_RADAR_ADMITTED",
        "instrument": "VTI",
        "source_url": SOURCE,
        "session_date": "2026-09-23",
        "retrieved_at_utc": "2026-09-24T19:00:00.0000000Z",
        "market_timestamp": None,
        "latest_three_rows": [
            {"Date": "/Date(1789948800000)/", "MarketPrice": "$10.00",
             "NAV": "$9.95", "Premium": "$0.05"},
            {"Date": "/Date(1790035200000)/", "MarketPrice": "$10.50",
             "NAV": "$10.45", "Premium": "$0.05"},
            {"Date": "/Date(1790121600000)/", "MarketPrice": "$10.00",
             "NAV": "$9.95", "Premium": "$0.05"},
        ],
    }


class VtiDateObserveTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name) / "vti-2026-09-23"
        self.directory.mkdir()
        self.source = _source()
        self.receipt = _receipt()
        self.write()

    def write(self):
        (self.directory / "receipt.json").write_text(json.dumps(self.receipt))
        (self.directory / "vanguard-response.json").write_text(json.dumps(self.source))

    def test_private_description_and_cli(self):
        result = observe_vti_capture(self.directory)
        self.assertEqual(result["close_to_close_difference"], "-0.50")
        self.assertEqual(result["previous_session_date"], "2026-09-22")
        self.assertIsNone(result["market_timestamp"])
        self.assertFalse(result["radar_pack_admitted"])
        self.assertEqual(main(["observe-vti-date", "--capture", str(self.directory)]), 0)

    def test_source_ticker_and_receipt_conflict_refused(self):
        self.source["historicalPrice"]["ticker"] = "SPY"
        self.write()
        with self.assertRaises(ValueError):
            observe_vti_capture(self.directory)
        self.source["historicalPrice"]["ticker"] = "VTI"
        self.receipt["latest_three_rows"][-1]["MarketPrice"] = "$100"
        self.write()
        with self.assertRaisesRegex(ValueError, "disagree"):
            observe_vti_capture(self.directory)

    def test_duplicate_date_and_future_retrieval_refused(self):
        self.source["premiumDiscountDetails"][0]["pdDetails"][1]["effectiveDate"] = "09/21/2026"
        self.write()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            observe_vti_capture(self.directory)
        self.source = _source()
        self.receipt["retrieved_at_utc"] = "2026-09-22T19:00:00Z"
        self.write()
        with self.assertRaisesRegex(ValueError, "retrieval date"):
            observe_vti_capture(self.directory)

    def test_missing_or_fabricated_market_timestamp_refused(self):
        self.receipt["market_timestamp"] = "2026-09-23T16:00:00-04:00"
        self.write()
        with self.assertRaisesRegex(ValueError, "identity or timestamp"):
            observe_vti_capture(self.directory)
        self.receipt["market_timestamp"] = None
        (self.directory / "vanguard-response.json").unlink()
        with self.assertRaisesRegex(ValueError, "missing"):
            observe_vti_capture(self.directory)


if __name__ == "__main__":
    unittest.main()
