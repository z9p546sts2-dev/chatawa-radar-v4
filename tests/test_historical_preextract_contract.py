"""Pre-extract historical admission hardening tests.

FIXTURE/SYNTHETIC only. No vendor client, API key, market bytes, source
authorization, extract authorization, Units 1401+, or Phase 6.

These tests verify the minimum production controls authorized for the first
bounded 30-session HISTORICAL learning cycle while preserving the distinction
between a bounded manifest and a general exchange-calendar engine.
"""

from __future__ import annotations

import unittest
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from radar_v4.baseline import close_to_close_changes
from radar_v4.dataset import DatasetDeclaration
from radar_v4.evidence import EvidenceEnvelope, ProvenanceClass
from radar_v4.observation import Observation, ObservationPayload
from radar_v4.observation_validation import validate_observation
from radar_v4.series import inspect_series
from radar_v4.session import run_dataset_session

NY = ZoneInfo("America/New_York")

EXPECTED_SESSIONS = (
    date(2024, 11, 18),
    date(2024, 11, 19),
    date(2024, 11, 20),
    date(2024, 11, 21),
    date(2024, 11, 22),
    date(2024, 11, 25),
    date(2024, 11, 26),
    date(2024, 11, 27),
    date(2024, 11, 29),
    date(2024, 12, 2),
    date(2024, 12, 3),
    date(2024, 12, 4),
    date(2024, 12, 5),
    date(2024, 12, 6),
    date(2024, 12, 9),
    date(2024, 12, 10),
    date(2024, 12, 11),
    date(2024, 12, 12),
    date(2024, 12, 13),
    date(2024, 12, 16),
    date(2024, 12, 17),
    date(2024, 12, 18),
    date(2024, 12, 19),
    date(2024, 12, 20),
    date(2024, 12, 23),
    date(2024, 12, 24),
    date(2024, 12, 26),
    date(2024, 12, 27),
    date(2024, 12, 30),
    date(2024, 12, 31),
)

EARLY_CLOSES = {date(2024, 11, 29), date(2024, 12, 24)}
KNOWN_CLOSED_WEEKDAYS = {date(2024, 11, 28), date(2024, 12, 25)}
MANIFEST_START = date(2024, 11, 18)
MANIFEST_END = date(2024, 12, 31)


def _stamp(day: date, hour: int = 16) -> datetime:
    return datetime(day.year, day.month, day.day, hour, 0, 0, tzinfo=NY)


def _obs(
    day: date,
    close: str,
    *,
    symbol: str = "SYN:SPY",
    interval: str = "1d",
    timezone_name: str = "America/New_York",
    market: datetime | None = None,
    transformation_version: str = "phase5-v1",
) -> Observation:
    envelope = EvidenceEnvelope.create(
        provenance_class=ProvenanceClass.SYNTHETIC,
        provider="PREEXTRACT_CONTRACT",
        symbol_or_universe=symbol,
        market_timestamp=market or _stamp(day),
        retrieval_timestamp=_stamp(day, 17),
        interval=interval,
        timezone=timezone_name,
        transformation_version=transformation_version,
    )
    return Observation.create(envelope, ObservationPayload(close=close))


def _declaration(*, use_manifest: bool = True) -> DatasetDeclaration:
    return DatasetDeclaration(
        dataset_id="synthetic.preextract.spy.30",
        provenance_class="SYNTHETIC",
        provider="PREEXTRACT_CONTRACT",
        universe="SYN:SPY",
        interval="1d",
        timezone="America/New_York",
        transformation_version="phase5-v1",
        adjustment_policy="UNADJUSTED",
        locked_question="ordinary close-to-close changes for one symbol",
        primary_metric="close-to-close difference",
        max_staleness="NONE",
        expected_session_dates=(
            tuple(day.isoformat() for day in EXPECTED_SESSIONS) if use_manifest else ()
        ),
    )


def _weekdays_minus_known_closed() -> tuple[date, ...]:
    """Civil Mon-Fri in the frozen window, minus KNOWN_CLOSED_WEEKDAYS.

    Not an exchange calendar. Not a holiday API.
    """
    days: list[date] = []
    cursor = MANIFEST_START
    while cursor <= MANIFEST_END:
        if cursor.weekday() < 5 and cursor not in KNOWN_CLOSED_WEEKDAYS:
            days.append(cursor)
        cursor += timedelta(days=1)
    return tuple(days)


def _kept_checksums(result) -> set[str]:
    return {item.envelope.checksum for item in result.observations}


class ExpectedSessionManifestTests(unittest.TestCase):
    def test_manifest_has_exactly_30_unique_sessions(self) -> None:
        self.assertEqual(len(EXPECTED_SESSIONS), 30)
        self.assertEqual(len(set(EXPECTED_SESSIONS)), 30)
        self.assertEqual(EXPECTED_SESSIONS[0], date(2024, 11, 18))
        self.assertEqual(EXPECTED_SESSIONS[-1], date(2024, 12, 31))

    def test_manifest_equals_weekdays_minus_known_closed(self) -> None:
        self.assertEqual(EXPECTED_SESSIONS, _weekdays_minus_known_closed())

    def test_known_closed_weekdays_are_not_expected_sessions(self) -> None:
        for day in KNOWN_CLOSED_WEEKDAYS:
            self.assertNotIn(day, EXPECTED_SESSIONS)

    def test_early_closes_are_expected_completed_sessions(self) -> None:
        for day in EARLY_CLOSES:
            self.assertIn(day, EXPECTED_SESSIONS)


class AdmissionHardeningTests(unittest.TestCase):
    def test_wrong_symbol_is_refused_by_dataset_declaration(self) -> None:
        good = _obs(EXPECTED_SESSIONS[0], "100.00")
        wrong = _obs(EXPECTED_SESSIONS[1], "100.10", symbol="SYN:OTHER")
        result = run_dataset_session(
            _declaration(),
            (good.envelope, wrong.envelope),
            (good, wrong),
        )
        codes = [
            code
            for record in result.admission.quarantined
            for code in record.validation.issue_codes()
        ]
        self.assertIn("DATASET_DECLARATION_MISMATCH", codes)
        self.assertEqual(result.kept_observation_count(), 1)

    def test_wrong_interval_is_refused_by_dataset_declaration(self) -> None:
        good = _obs(EXPECTED_SESSIONS[0], "100.00")
        wrong = _obs(EXPECTED_SESSIONS[1], "100.10", interval="1h")
        result = run_dataset_session(
            _declaration(),
            (good.envelope, wrong.envelope),
            (good, wrong),
        )
        codes = [
            code
            for record in result.admission.quarantined
            for code in record.validation.issue_codes()
        ]
        self.assertIn("DATASET_DECLARATION_MISMATCH", codes)
        self.assertEqual(result.kept_observation_count(), 1)
        self.assertNotIn(wrong.envelope.checksum, _kept_checksums(result))

    def test_transformation_version_mismatch_is_refused(self) -> None:
        good = _obs(EXPECTED_SESSIONS[0], "100.00")
        wrong = _obs(
            EXPECTED_SESSIONS[1],
            "100.10",
            transformation_version="phase5-v1-mutated",
        )
        result = run_dataset_session(
            _declaration(),
            (good.envelope, wrong.envelope),
            (good, wrong),
        )
        codes = [
            code
            for record in result.admission.quarantined
            for code in record.validation.issue_codes()
        ]
        self.assertIn("DATASET_DECLARATION_MISMATCH", codes)
        self.assertEqual(result.kept_observation_count(), 1)
        self.assertNotIn(wrong.envelope.checksum, _kept_checksums(result))

    def test_exact_duplicate_timestamp_refuses_series_measurement(self) -> None:
        first = _obs(EXPECTED_SESSIONS[0], "100.00")
        second = _obs(EXPECTED_SESSIONS[0], "100.10")
        report = inspect_series((first, second))
        self.assertFalse(report.valid)
        self.assertIn("DUPLICATE_MARKET_TIMESTAMP", report.issue_codes())
        result = run_dataset_session(
            _declaration(),
            (first.envelope, second.envelope),
            (first, second),
        )
        self.assertFalse(result.series.valid)
        self.assertIsNone(result.baseline)

    def test_clean_order_is_deterministic(self) -> None:
        later = _obs(EXPECTED_SESSIONS[1], "100.25")
        earlier = _obs(EXPECTED_SESSIONS[0], "100.00")
        left = close_to_close_changes((later, earlier))
        right = close_to_close_changes((earlier, later))
        self.assertEqual(left.status, "MEASURED")
        self.assertEqual(right.status, "MEASURED")
        self.assertEqual(left.changes, ("0.25",))
        self.assertEqual(left.changes, right.changes)

    def test_known_closed_weekday_is_refused_by_bounded_manifest(self) -> None:
        valid = _obs(EXPECTED_SESSIONS[0], "100.00")
        holiday = _obs(date(2024, 11, 28), "99.50")
        result = run_dataset_session(
            _declaration(),
            (valid.envelope, holiday.envelope),
            (valid, holiday),
        )
        codes = [
            code
            for record in result.admission.quarantined
            for code in record.validation.issue_codes()
        ]
        self.assertIn("SESSION_DATE_NOT_IN_MANIFEST", codes)
        self.assertEqual(result.kept_observation_count(), 1)
        self.assertNotIn(holiday.envelope.checksum, _kept_checksums(result))

    def test_outside_window_row_is_refused_by_bounded_manifest(self) -> None:
        outside = _obs(date(2024, 11, 15), "99.90")
        inside = _obs(EXPECTED_SESSIONS[0], "100.00")
        result = run_dataset_session(
            _declaration(),
            (outside.envelope, inside.envelope),
            (outside, inside),
        )
        codes = [
            code
            for record in result.admission.quarantined
            for code in record.validation.issue_codes()
        ]
        self.assertIn("SESSION_DATE_NOT_IN_MANIFEST", codes)
        self.assertEqual(result.kept_observation_count(), 1)
        self.assertNotIn(outside.envelope.checksum, _kept_checksums(result))

    def test_same_session_date_different_timestamps_refuses_measurement(self) -> None:
        day = EXPECTED_SESSIONS[0]
        first = _obs(day, "100.00", market=_stamp(day, 13))
        second = _obs(day, "100.10", market=_stamp(day, 16))
        report = inspect_series((first, second))
        self.assertFalse(report.valid)
        self.assertIn("SESSION_DATE_COLLISION", report.issue_codes())
        result = run_dataset_session(
            _declaration(),
            (first.envelope, second.envelope),
            (first, second),
        )
        self.assertFalse(result.series.valid)
        self.assertIsNone(result.baseline)

    def test_nonfinite_closes_are_refused_before_measurement(self) -> None:
        first = _obs(EXPECTED_SESSIONS[0], "100.00")
        for special in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(close=special):
                second = _obs(EXPECTED_SESSIONS[1], special)
                validation = validate_observation(second)
                self.assertFalse(validation.valid)
                self.assertIn("NON_FINITE_CLOSE", validation.issue_codes())
                result = close_to_close_changes((first, second))
                self.assertEqual(result.status, "INVALID_COMPARISON")
                self.assertEqual(result.claim_level, "NONE")


class RemainingBoundedGapTests(unittest.TestCase):
    def test_missing_expected_session_blocks_level0_measurement(self) -> None:
        observations = tuple(
            _obs(day, f"{100 + index / 100:.2f}")
            for index, day in enumerate(EXPECTED_SESSIONS[:-1])
        )
        result = run_dataset_session(
            _declaration(),
            tuple(item.envelope for item in observations),
            observations,
        )
        self.assertTrue(result.series.valid)
        self.assertEqual(result.kept_observation_count(), 29)
        self.assertIsNotNone(result.baseline)
        assert result.baseline is not None
        self.assertEqual(result.baseline.status, "INSUFFICIENT_EVIDENCE")
        self.assertEqual(result.baseline.claim_level, "NONE")
        self.assertEqual(result.baseline.change_count, 0)
        self.assertIn("expected-session manifest is incomplete", result.baseline.notes)

    def test_complete_expected_session_set_can_measure(self) -> None:
        observations = tuple(
            _obs(day, f"{100 + index / 100:.2f}")
            for index, day in enumerate(EXPECTED_SESSIONS)
        )
        result = run_dataset_session(
            _declaration(),
            tuple(item.envelope for item in observations),
            observations,
        )
        self.assertTrue(result.series.valid)
        self.assertEqual(result.kept_observation_count(), 30)
        self.assertIsNotNone(result.baseline)
        assert result.baseline is not None
        self.assertEqual(result.baseline.status, "MEASURED")
        self.assertEqual(result.baseline.claim_level, "LEVEL 0 — MEASURED")
        self.assertEqual(result.baseline.observation_count, 30)
        self.assertEqual(result.baseline.change_count, 29)

    def test_manifestless_series_still_has_no_general_exchange_calendar(self) -> None:
        valid = _obs(EXPECTED_SESSIONS[0], "100.00")
        holiday = _obs(date(2024, 11, 28), "99.50")
        result = run_dataset_session(
            _declaration(use_manifest=False),
            (valid.envelope, holiday.envelope),
            (valid, holiday),
        )
        self.assertEqual(result.kept_observation_count(), 2)
        self.assertTrue(result.series.valid)
        self.assertIsNotNone(result.baseline)
        self.assertEqual(result.baseline.status, "MEASURED")


if __name__ == "__main__":
    unittest.main()
