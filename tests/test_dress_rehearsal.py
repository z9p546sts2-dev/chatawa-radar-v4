"""SOFTWARE and DATA CORRECTNESS — SYNTHETIC pre-HISTORICAL dress rehearsal.

These tests exercise first-cycle shape on invented SYNTHETIC bars.
They are not HISTORICAL evidence, method validity, usefulness, or edge.
"""

from __future__ import annotations

import json
import shutil
import unittest
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

from radar_v4.baseline import close_to_close_changes
from radar_v4.dataset import DatasetDeclaration
from radar_v4.dataset_pack import load_dataset_pack
from radar_v4.evidence import EvidenceEnvelope, ProvenanceClass
from radar_v4.horizon_bind import horizon_bind
from radar_v4.horizon_lock import horizon_lock
from radar_v4.local_session import run_session_from_pack
from radar_v4.observation import Observation, ObservationPayload
from radar_v4.observation_json import intake_observation_json
from radar_v4.observation_validation import validate_observation
from radar_v4.pack_describe import pack_readiness
from radar_v4.record_check import describe_adjustment_policy
from radar_v4.ruler import declaration_ruler, ruler_checksum
from radar_v4.series import inspect_series
from radar_v4.session import run_dataset_session
from radar_v4.session_report import serialize_session_report
from radar_v4.validation import validate_envelope
from radar_v4.workshop_check import check_pack_determinism

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "fixtures" / "synthetic_dress_rehearsal_1d"
UTC_FIXTURE = ROOT / "fixtures" / "synthetic_one_symbol_1d"
NY = ZoneInfo("America/New_York")
WINDOW_START = date(2024, 1, 2)
WINDOW_END = date(2024, 12, 31)
# Comment-only holiday example for the calendar-gap probe. Not a holiday API.
# 2024-07-04 is a Thursday weekday and is included by SYNTHETIC_WEEKDAY_SPAN.
HOLIDAY_SHAPED_WEEKDAY = date(2024, 7, 4)
CALENDAR_GAP_STILL_OPEN = "CALENDAR_GAP_STILL_OPEN"
DATE_WINDOW_GAP_STILL_OPEN = "DATE_WINDOW_GAP_STILL_OPEN"
SESSION_DATE_COLLISION_GAP_STILL_OPEN = "SESSION_DATE_COLLISION_GAP_STILL_OPEN"
DECIMAL_SPECIAL_VALUE_GAP_STILL_OPEN = "DECIMAL_SPECIAL_VALUE_GAP_STILL_OPEN"
DISPOSITION = "LOCAL FIXTURE/SYNTHETIC DRESS REHEARSAL PASSED WITH KNOWN GAPS"
CALENDAR_CODE_FRAGMENTS = (
    "CALENDAR",
    "HOLIDAY",
    "WEEKEND",
    "MISSING_SESSION",
    "EXCHANGE",
)


def _ny_close(day: date, hour: int = 16) -> datetime:
    return datetime(day.year, day.month, day.day, hour, 0, 0, tzinfo=NY)


def _synthetic_obs(
    day: date,
    close: str,
    *,
    symbol: str = "SYN:ONE",
    interval: str = "1d",
    provenance: ProvenanceClass | str = ProvenanceClass.SYNTHETIC,
    timezone_name: str = "America/New_York",
    market: datetime | None = None,
    retrieval: datetime | None = None,
    transformation_version: str = "phase5-v1",
) -> Observation:
    stamp = market if market is not None else _ny_close(day)
    retrieved = retrieval if retrieval is not None else _ny_close(day, 17)
    return Observation.create(
        EvidenceEnvelope.create(
            provenance_class=provenance,
            provider="PHASE5_SOURCE",
            symbol_or_universe=symbol,
            market_timestamp=stamp,
            retrieval_timestamp=retrieved,
            interval=interval,
            timezone=timezone_name,
            transformation_version=transformation_version,
        ),
        ObservationPayload(close=close),
    )


def _declaration(**overrides: object) -> dict[str, object]:
    document: dict[str, object] = {
        "dataset_id": "synthetic.dress-rehearsal.1d",
        "provenance_class": "SYNTHETIC",
        "provider": "PHASE5_SOURCE",
        "universe": "SYN:ONE",
        "interval": "1d",
        "timezone": "America/New_York",
        "transformation_version": "phase5-v1",
        "adjustment_policy": "UNADJUSTED",
        "locked_question": "ordinary close-to-close changes for one symbol",
        "primary_metric": "close-to-close difference",
        "max_staleness": "NONE",
    }
    document.update(overrides)
    return document


def _declaration_object(**overrides: object) -> DatasetDeclaration:
    raw = _declaration(**overrides)
    return DatasetDeclaration(
        dataset_id=str(raw["dataset_id"]),
        provenance_class=str(raw["provenance_class"]),
        provider=str(raw["provider"]),
        universe=str(raw["universe"]),
        interval=str(raw["interval"]),
        timezone=str(raw["timezone"]),
        transformation_version=str(raw["transformation_version"]),
        adjustment_policy=str(raw["adjustment_policy"]),
        locked_question=str(raw["locked_question"]),
        primary_metric=str(raw["primary_metric"]),
        max_staleness=None if raw.get("max_staleness") is None else str(raw["max_staleness"]),
    )


def _write_obs(path: Path, item: Observation) -> None:
    path.write_text(
        json.dumps(
            {
                "envelope": item.envelope.serialize(),
                "payload": item.payload.canonical_payload(),
                "payload_checksum": item.payload_checksum,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _weekday_span() -> list[date]:
    days: list[date] = []
    cursor = WINDOW_START
    while cursor <= WINDOW_END:
        if cursor.weekday() < 5:
            days.append(cursor)
        cursor += timedelta(days=1)
    return days


def _invented_close(index: int) -> str:
    return str(Decimal("100") + Decimal(index % 7) * Decimal("0.01"))


def _write_year_shaped_pack(root: Path, omit: date | None = None) -> list[date]:
    (root / "declaration.json").write_text(
        json.dumps(_declaration(), indent=2) + "\n",
        encoding="utf-8",
    )
    kept: list[date] = []
    for index, day in enumerate(_weekday_span()):
        if omit is not None and day == omit:
            continue
        kept.append(day)
        _write_obs(
            root / f"obs_{day.isoformat()}.json",
            _synthetic_obs(day, _invented_close(index)),
        )
    return kept


def _issue_codes(series_or_validation: object) -> tuple[str, ...]:
    if hasattr(series_or_validation, "issue_codes"):
        return series_or_validation.issue_codes()
    issues = getattr(series_or_validation, "issues", ())
    return tuple(issue.code for issue in issues)


def _has_calendar_code(codes: tuple[str, ...]) -> bool:
    joined = " ".join(codes)
    return any(fragment in joined for fragment in CALENDAR_CODE_FRAGMENTS)


class DressRehearsalGoldenTests(unittest.TestCase):
    def test_golden_pack_is_usable_synthetic(self) -> None:
        report = load_dataset_pack(GOLDEN)
        self.assertTrue(report.usable())
        assert report.declaration is not None
        self.assertEqual(report.declaration.provenance_class, "SYNTHETIC")
        self.assertEqual(report.declaration.universe, "SYN:ONE")
        self.assertEqual(report.declaration.interval, "1d")
        self.assertEqual(report.declaration.timezone, "America/New_York")
        self.assertEqual(report.declaration.adjustment_policy, "UNADJUSTED")
        self.assertEqual(report.declaration.max_staleness, "NONE")
        self.assertEqual(report.observation_intake.accepted_count(), 3)

    def test_golden_envelope_offsets_match_new_york(self) -> None:
        report = load_dataset_pack(GOLDEN)
        self.assertTrue(report.usable())
        for item in report.observation_intake.accepted:
            result = validate_envelope(item.envelope)
            self.assertTrue(result.valid, result.issue_codes())
            self.assertNotIn("TIMEZONE_MISMATCH", result.issue_codes())
            self.assertEqual(item.envelope.timezone, "America/New_York")
            stamp = item.envelope.market_timestamp
            assert stamp is not None
            self.assertEqual(stamp.utcoffset(), _ny_close(stamp.date()).utcoffset())

    def test_golden_close_to_close_arithmetic(self) -> None:
        result = run_session_from_pack(GOLDEN)
        self.assertIsNone(result.error_code)
        assert result.session is not None
        assert result.session.baseline is not None
        self.assertEqual(result.session.baseline.status, "MEASURED")
        self.assertEqual(result.session.baseline.claim_level, "LEVEL 0 — MEASURED")
        self.assertEqual(result.session.baseline.changes, ("0.25", "-0.50"))

    def test_golden_is_not_historical(self) -> None:
        report = load_dataset_pack(GOLDEN)
        assert report.declaration is not None
        self.assertNotEqual(report.declaration.provenance_class, "HISTORICAL")
        readiness = pack_readiness(GOLDEN)
        notes = " ".join(readiness.notes)
        self.assertIn("SYNTHETIC and FIXTURE numbers are not HISTORICAL evidence", notes)
        self.assertIn("declared provenance is not HISTORICAL", notes)

    def test_existing_utc_fixture_pack_still_measures(self) -> None:
        result = run_session_from_pack(UTC_FIXTURE)
        self.assertIsNone(result.error_code)
        assert result.session is not None
        assert result.session.baseline is not None
        self.assertEqual(result.session.baseline.status, "MEASURED")
        self.assertEqual(result.session.baseline.changes, ("0.50", "-0.50"))


class DressRehearsalYearShapedTests(unittest.TestCase):
    def test_year_shaped_pack_measures(self) -> None:
        with self._temp_year() as (root, days):
            result = run_session_from_pack(root)
            self.assertIsNone(result.error_code)
            assert result.session is not None
            assert result.session.baseline is not None
            self.assertEqual(result.session.baseline.status, "MEASURED")
            self.assertEqual(
                result.session.baseline.change_count,
                result.session.baseline.observation_count - 1,
            )
            stamps = [
                item.envelope.market_timestamp
                for item in result.session.observations
                if item.envelope.market_timestamp is not None
            ]
            self.assertGreaterEqual(min(stamps).date(), WINDOW_START)
            self.assertLessEqual(max(stamps).date(), WINDOW_END)
            self.assertNotIn(date(2024, 1, 1), [stamp.date() for stamp in stamps])
            self.assertEqual(len(days), len(stamps))

    def test_year_shaped_is_one_symbol_1d(self) -> None:
        with self._temp_year() as (root, _days):
            report = load_dataset_pack(root)
            assert report.declaration is not None
            for item in report.observation_intake.accepted:
                self.assertEqual(item.envelope.symbol_or_universe, "SYN:ONE")
                self.assertEqual(item.envelope.interval, "1d")
                self.assertEqual(item.envelope.timezone, "America/New_York")
                self.assertEqual(item.envelope.transformation_version, "phase5-v1")
            self.assertEqual(report.declaration.adjustment_policy, "UNADJUSTED")
            self.assertEqual(report.declaration.universe, "SYN:ONE")

    def test_year_shaped_has_no_intraday_rows(self) -> None:
        with self._temp_year() as (root, _days):
            report = load_dataset_pack(root)
            intervals = {item.envelope.interval for item in report.observation_intake.accepted}
            self.assertEqual(intervals, {"1d"})

    def test_year_shaped_is_not_an_exchange_calendar(self) -> None:
        days = _weekday_span()
        self.assertIn(HOLIDAY_SHAPED_WEEKDAY, days)
        self.assertGreater(len(days), 250)
        self.assertLess(len(days), 270)
        # SYNTHETIC_WEEKDAY_SPAN includes a holiday-shaped weekday. That is
        # the documented gap: weekday span is not an NYSE session list.

    def _temp_year(self):
        from tempfile import TemporaryDirectory

        class _Guard:
            def __enter__(self_inner):
                self_inner._ctx = TemporaryDirectory()
                root = Path(self_inner._ctx.__enter__())
                days = _write_year_shaped_pack(root)
                return root, days

            def __exit__(self_inner, *args):
                return self_inner._ctx.__exit__(*args)

        return _Guard()


class DressRehearsalRefusalTests(unittest.TestCase):
    def test_historical_label_still_refused(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "declaration.json").write_text(
                json.dumps(_declaration(provenance_class="HISTORICAL"), indent=2) + "\n",
                encoding="utf-8",
            )
            _write_obs(root / "obs.json", _synthetic_obs(WINDOW_START, "100.00"))
            report = load_dataset_pack(root)
        self.assertFalse(report.usable())
        self.assertIn(
            "PACK_PROVENANCE_NOT_ALLOWED",
            [issue.code for issue in report.pack_issues],
        )

    def test_live_baseline_refused(self) -> None:
        report = close_to_close_changes(
            (
                _synthetic_obs(
                    WINDOW_START, "100.00", provenance=ProvenanceClass.LIVE, symbol="LIVE:ONE"
                ),
                _synthetic_obs(
                    date(2024, 1, 3),
                    "100.25",
                    provenance=ProvenanceClass.LIVE,
                    symbol="LIVE:ONE",
                ),
            )
        )
        self.assertEqual(report.status, "INVALID_COMPARISON")
        self.assertEqual(report.claim_level, "NONE")

    def test_utc_offset_refused_on_new_york_declaration(self) -> None:
        utc = timezone.utc
        item = _synthetic_obs(
            WINDOW_START,
            "100.00",
            market=datetime(2024, 1, 2, 16, 0, 0, tzinfo=utc),
            retrieval=datetime(2024, 1, 2, 17, 0, 0, tzinfo=utc),
        )
        result = validate_envelope(item.envelope)
        self.assertFalse(result.valid)
        self.assertIn("TIMEZONE_MISMATCH", result.issue_codes())
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "declaration.json").write_text(
                json.dumps(_declaration(), indent=2) + "\n", encoding="utf-8"
            )
            _write_obs(root / "obs.json", item)
            report = load_dataset_pack(root)
        self.assertEqual(report.observation_intake.accepted_count(), 0)
        self.assertIn(
            "TIMEZONE_MISMATCH",
            report.observation_intake.quarantined[0].validation.issue_codes(),
        )

    def test_transformation_version_mismatch_refused(self) -> None:
        first = _synthetic_obs(date(2024, 1, 2), "100.00")
        second = _synthetic_obs(
            date(2024, 1, 3),
            "100.25",
            transformation_version="phase5-v1-mutated",
        )
        self.assertNotEqual(
            first.envelope.transformation_version,
            second.envelope.transformation_version,
        )
        mixed = close_to_close_changes((first, second))
        self.assertEqual(mixed.status, "INVALID_COMPARISON")
        self.assertEqual(mixed.claim_level, "NONE")
        self.assertNotEqual(mixed.claim_level, "LEVEL 0 — MEASURED")
        result = run_dataset_session(
            _declaration_object(),
            (first.envelope, second.envelope),
            (first, second),
        )
        codes = [
            code
            for record in result.admission.quarantined
            for code in record.validation.issue_codes()
        ]
        self.assertIn("DATASET_DECLARATION_MISMATCH", codes)
        if result.baseline is None:
            self.assertIsNone(result.baseline)
        else:
            self.assertNotEqual(result.baseline.status, "MEASURED")
            self.assertNotEqual(result.baseline.claim_level, "LEVEL 0 — MEASURED")

    def test_interval_mismatch_quarantined(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "declaration.json").write_text(
                json.dumps(_declaration(), indent=2) + "\n", encoding="utf-8"
            )
            _write_obs(root / "a.json", _synthetic_obs(WINDOW_START, "100.00"))
            _write_obs(
                root / "b.json",
                _synthetic_obs(date(2024, 1, 3), "100.25", interval="1h"),
            )
            report = load_dataset_pack(root)
            result = run_session_from_pack(root)
        codes: list[str] = []
        for record in report.observation_intake.quarantined:
            codes.extend(record.validation.issue_codes())
        if result.session is not None:
            for record in result.session.admission.quarantined:
                codes.extend(record.validation.issue_codes())
            codes.extend(
                issue.code
                for _item, validation in result.session.rejected_observations
                for issue in validation.issues
            )
            if result.session.baseline is not None:
                baseline_status = result.session.baseline.status
            else:
                baseline_status = None
        else:
            baseline_status = None
        self.assertTrue(
            "DATASET_DECLARATION_MISMATCH" in codes
            or baseline_status == "INVALID_COMPARISON",
            codes,
        )

    def test_second_symbol_is_invalid_comparison(self) -> None:
        report = close_to_close_changes(
            (
                _synthetic_obs(WINDOW_START, "100.00", symbol="SYN:ONE"),
                _synthetic_obs(date(2024, 1, 3), "100.25", symbol="SYN:TWO"),
            )
        )
        self.assertEqual(report.status, "INVALID_COMPARISON")
        self.assertEqual(report.claim_level, "NONE")

    def test_duplicate_session_timestamp_refused(self) -> None:
        first = _synthetic_obs(WINDOW_START, "100.00")
        second = _synthetic_obs(WINDOW_START, "100.25")
        self.assertNotEqual(first.payload.close, second.payload.close)
        series = inspect_series((first, second))
        self.assertFalse(series.valid)
        self.assertIn("DUPLICATE_MARKET_TIMESTAMP", series.issue_codes())
        # Series lock is the refusal. Pack identity-gate may drop the second
        # file earlier; session composition is the DUPLICATE_MARKET_TIMESTAMP path.
        result = run_dataset_session(
            _declaration_object(),
            (first.envelope, second.envelope),
            (first, second),
        )
        self.assertFalse(result.series.valid)
        self.assertIsNone(result.baseline)
        self.assertIn("DUPLICATE_MARKET_TIMESTAMP", result.series.issue_codes())
        # Conflicting closes are not averaged or repaired into a MEASURED row.
        self.assertNotEqual(first.payload.close, second.payload.close)

    def test_single_bar_insufficient(self) -> None:
        report = close_to_close_changes((_synthetic_obs(WINDOW_START, "100.00"),))
        self.assertEqual(report.status, "INSUFFICIENT_EVIDENCE")
        self.assertEqual(report.claim_level, "NONE")

    def test_naive_timestamp_refused(self) -> None:
        naive = datetime(2024, 1, 2, 16, 0, 0)
        envelope = EvidenceEnvelope(
            provenance_class="SYNTHETIC",
            provider="PHASE5_SOURCE",
            symbol_or_universe="SYN:ONE",
            market_timestamp=naive,
            retrieval_timestamp=_ny_close(WINDOW_START, 17),
            interval="1d",
            timezone="America/New_York",
            transformation_version="phase5-v1",
            checksum=None,
        )
        result = validate_envelope(envelope)
        self.assertFalse(result.valid)
        self.assertIn("INVALID_MARKET_TIMESTAMP", result.issue_codes())


class DressRehearsalDeterminismTests(unittest.TestCase):
    def test_golden_pack_determinism(self) -> None:
        report = check_pack_determinism(GOLDEN)
        self.assertTrue(report.equal)
        self.assertEqual(report.left, report.right)
        self.assertIsNotNone(report.left)

    def test_year_shaped_pack_determinism(self) -> None:
        from tempfile import TemporaryDirectory

        checksums: list[str] = []
        for _ in range(2):
            with TemporaryDirectory() as raw:
                root = Path(raw)
                _write_year_shaped_pack(root)
                result = run_session_from_pack(root)
                assert result.session is not None
                checksums.append(result.session.snapshot.integrity_checksum())
        self.assertEqual(checksums[0], checksums[1])


class DressRehearsalMutationTests(unittest.TestCase):
    def test_one_close_change_changes_checksum(self) -> None:
        original = run_session_from_pack(GOLDEN)
        assert original.session is not None
        assert original.session.baseline is not None
        left = original.session.snapshot.integrity_checksum()
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw:
            copy = Path(raw) / "pack"
            shutil.copytree(GOLDEN, copy)
            target = copy / "obs_2024-01-03.json"
            parsed = intake_observation_json(target.read_text(encoding="utf-8"))
            self.assertEqual(parsed.accepted_count(), 1)
            old = parsed.accepted[0]
            mutated = Observation.create(old.envelope, ObservationPayload(close="100.26"))
            _write_obs(target, mutated)
            # Stale golden manifest would refuse the edited file.
            (copy / "manifest.json").unlink(missing_ok=True)
            changed = run_session_from_pack(copy)
        assert changed.session is not None
        assert changed.session.baseline is not None
        self.assertEqual(original.session.baseline.status, "MEASURED")
        self.assertEqual(changed.session.baseline.status, "MEASURED")
        self.assertNotEqual(left, changed.session.snapshot.integrity_checksum())
        self.assertEqual(changed.session.baseline.changes, ("0.26", "-0.51"))

    def test_unchanged_copy_keeps_checksum(self) -> None:
        first = run_session_from_pack(GOLDEN)
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw:
            copy = Path(raw) / "pack"
            shutil.copytree(GOLDEN, copy)
            second = run_session_from_pack(copy)
        assert first.session is not None
        assert second.session is not None
        self.assertEqual(
            first.session.snapshot.integrity_checksum(),
            second.session.snapshot.integrity_checksum(),
        )


class DressRehearsalCalendarGapTests(unittest.TestCase):
    def test_gap_weekend_bar_is_not_calendar_refused(self) -> None:
        # Decision #4: weekends produce no bar. Software does not enforce that.
        saturday = _synthetic_obs(date(2024, 1, 6), "99.00")
        self.assertEqual(saturday.envelope.market_timestamp.weekday(), 5)
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw:
            root = Path(raw)
            shutil.copytree(GOLDEN, root, dirs_exist_ok=True)
            _write_obs(root / "obs_2024-01-06.json", saturday)
            # Stale golden manifest would refuse the added weekend file.
            (root / "manifest.json").unlink(missing_ok=True)
            report = load_dataset_pack(root)
            result = run_session_from_pack(root)
        self.assertEqual(report.observation_intake.accepted_count(), 4)
        assert result.session is not None
        self.assertTrue(result.session.series.valid)
        self.assertFalse(_has_calendar_code(result.session.series.issue_codes()))
        assert result.session.baseline is not None
        self.assertEqual(result.session.baseline.status, "MEASURED")
        self.assertEqual(result.session.baseline.observation_count, 4)
        self.assertEqual(result.session.baseline.change_count, 3)
        self.assertEqual(CALENDAR_GAP_STILL_OPEN, "CALENDAR_GAP_STILL_OPEN")

    def test_gap_missing_weekday_is_not_flagged(self) -> None:
        # Decision #4: unexplained missing expected sessions must be flagged.
        # Software does not yet flag them.
        omitted = date(2024, 6, 12)
        self.assertEqual(omitted.weekday(), 2)
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw:
            root = Path(raw)
            full = _weekday_span()
            kept = _write_year_shaped_pack(root, omit=omitted)
            result = run_session_from_pack(root)
        self.assertEqual(len(kept), len(full) - 1)
        assert result.session is not None
        self.assertTrue(result.session.series.valid)
        self.assertFalse(_has_calendar_code(result.session.series.issue_codes()))
        assert result.session.baseline is not None
        self.assertEqual(result.session.baseline.status, "MEASURED")
        self.assertEqual(result.session.baseline.change_count, len(kept) - 1)
        self.assertEqual(CALENDAR_GAP_STILL_OPEN, "CALENDAR_GAP_STILL_OPEN")

    def test_gap_weekday_holiday_shaped_bar_is_accepted(self) -> None:
        # 2024-07-04 is used only as a comment-labeled holiday-shaped weekday.
        # No holiday API. SYNTHETIC_WEEKDAY_SPAN includes it. Software cannot know.
        self.assertEqual(HOLIDAY_SHAPED_WEEKDAY.weekday(), 3)
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw:
            root = Path(raw)
            days = _write_year_shaped_pack(root)
            result = run_session_from_pack(root)
        self.assertIn(HOLIDAY_SHAPED_WEEKDAY, days)
        assert result.session is not None
        self.assertTrue(result.session.series.valid)
        self.assertFalse(_has_calendar_code(result.session.series.issue_codes()))
        stamps = [
            item.envelope.market_timestamp.date()
            for item in result.session.observations
            if item.envelope.market_timestamp is not None
        ]
        self.assertIn(HOLIDAY_SHAPED_WEEKDAY, stamps)
        self.assertEqual(CALENDAR_GAP_STILL_OPEN, "CALENDAR_GAP_STILL_OPEN")


class DressRehearsalRedTeamTests(unittest.TestCase):
    def test_authoritative_market_timestamp_ordering(self) -> None:
        reversed_bars = (
            _synthetic_obs(date(2024, 1, 4), "99.75"),
            _synthetic_obs(date(2024, 1, 2), "100.00"),
            _synthetic_obs(date(2024, 1, 3), "100.25"),
        )
        series = inspect_series(reversed_bars)
        stamps = [
            item.envelope.market_timestamp
            for item in series.ordered
            if item.envelope.market_timestamp is not None
        ]
        self.assertEqual(stamps, sorted(stamps))
        report = close_to_close_changes(reversed_bars)
        self.assertEqual(report.status, "MEASURED")
        self.assertEqual(report.changes, ("0.25", "-0.50"))

    def test_order_sensitive_adversarial_sorting(self) -> None:
        from tempfile import TemporaryDirectory

        bars = (
            _synthetic_obs(date(2024, 1, 4), "99.75"),
            _synthetic_obs(date(2024, 1, 2), "100.00"),
            _synthetic_obs(date(2024, 1, 3), "100.25"),
        )
        by_close = tuple(sorted(bars, key=lambda item: Decimal(item.payload.close), reverse=True))
        self.assertEqual(
            [item.payload.close for item in by_close],
            ["100.25", "100.00", "99.75"],
        )
        report = close_to_close_changes(by_close)
        self.assertEqual(report.changes, ("0.25", "-0.50"))
        with TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "declaration.json").write_text(
                json.dumps(_declaration(), indent=2) + "\n", encoding="utf-8"
            )
            _write_obs(root / "a_late.json", bars[0])
            _write_obs(root / "z_early.json", bars[1])
            _write_obs(root / "m_mid.json", bars[2])
            result = run_session_from_pack(root)
        assert result.session is not None
        assert result.session.baseline is not None
        self.assertEqual(result.session.baseline.changes, ("0.25", "-0.50"))

    def test_duplicate_timestamp_with_conflicting_closes(self) -> None:
        first = _synthetic_obs(WINDOW_START, "100.00")
        second = _synthetic_obs(WINDOW_START, "100.25")
        self.assertEqual(first.envelope.market_timestamp, second.envelope.market_timestamp)
        self.assertNotEqual(first.payload.close, second.payload.close)
        result = run_dataset_session(
            _declaration_object(),
            (first.envelope, second.envelope),
            (first, second),
        )
        self.assertIn("DUPLICATE_MARKET_TIMESTAMP", result.series.issue_codes())
        self.assertIsNone(result.baseline)
        self.assertNotIn("100.125", "".join((first.payload.close, second.payload.close)))

    def test_same_session_date_different_timestamp_is_refused(self) -> None:
        # Authorized pre-extract hardening: one completed 1d session, one bar.
        first = _synthetic_obs(WINDOW_START, "100.00")
        second = _synthetic_obs(
            WINDOW_START,
            "100.25",
            market=_ny_close(WINDOW_START, 16).replace(minute=1),
            retrieval=_ny_close(WINDOW_START, 17).replace(minute=1),
        )
        self.assertEqual(first.envelope.market_timestamp.date(), second.envelope.market_timestamp.date())
        self.assertNotEqual(first.envelope.market_timestamp, second.envelope.market_timestamp)
        series = inspect_series((first, second))
        self.assertFalse(series.valid)
        self.assertIn("SESSION_DATE_COLLISION", series.issue_codes())
        result = run_dataset_session(
            _declaration_object(),
            (first.envelope, second.envelope),
            (first, second),
        )
        self.assertIsNone(result.baseline)

    def test_decimal_adversary_cases(self) -> None:
        exact = close_to_close_changes(
            (
                _synthetic_obs(date(2024, 1, 2), "100.10"),
                _synthetic_obs(date(2024, 1, 3), "100.20"),
                _synthetic_obs(date(2024, 1, 4), "100.30"),
            )
        )
        self.assertEqual(exact.status, "MEASURED")
        self.assertEqual(exact.changes, ("0.10", "0.10"))
        self.assertEqual(exact.changes[0], str(Decimal("100.20") - Decimal("100.10")))
        malformed = Observation.create(
            _synthetic_obs(WINDOW_START, "100.00").envelope,
            ObservationPayload(close="100.2.5"),
        )
        refused = validate_observation(malformed)
        self.assertFalse(refused.valid)
        self.assertIn("INVALID_CLOSE", refused.issue_codes())
        baseline = close_to_close_changes(
            (_synthetic_obs(date(2024, 1, 2), "100.00"), malformed)
        )
        self.assertEqual(baseline.status, "INVALID_COMPARISON")
        self.assertEqual(baseline.claim_level, "NONE")

    def test_decimal_special_values_are_refused(self) -> None:
        # Authorized pre-extract hardening: non-finite closes are invalid.
        later = _synthetic_obs(date(2024, 1, 3), "100.00")
        for special in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(close=special):
                item = Observation.create(
                    _synthetic_obs(WINDOW_START, "100.00").envelope,
                    ObservationPayload(close=special),
                )
                validation = validate_observation(item)
                self.assertFalse(validation.valid)
                self.assertIn("NON_FINITE_CLOSE", validation.issue_codes())
                report = close_to_close_changes((item, later))
                self.assertEqual(report.status, "INVALID_COMPARISON")
                self.assertEqual(report.claim_level, "NONE")

    def test_durable_synthetic_rehearsal_artifact_identity(self) -> None:
        identity = (GOLDEN / "IDENTITY.txt").read_text(encoding="utf-8")
        readme = (GOLDEN / "README.md").read_text(encoding="utf-8")
        declaration = json.loads((GOLDEN / "declaration.json").read_text(encoding="utf-8"))
        self.assertIn("ARTIFACT_KIND=PRE_HISTORICAL_DRESS_REHEARSAL", identity)
        self.assertIn("PROVENANCE_CLASS=SYNTHETIC", identity)
        self.assertIn("PRE_HISTORICAL_DRESS_REHEARSAL", readme)
        self.assertEqual(declaration["provenance_class"], "SYNTHETIC")
        self.assertEqual(declaration["universe"], "SYN:ONE")
        self.assertEqual(declaration["dataset_id"], "synthetic.dress-rehearsal.1d")
        self.assertNotEqual(declaration["universe"], "SPY")
        self.assertNotEqual(declaration["provenance_class"], "HISTORICAL")
        report = load_dataset_pack(GOLDEN)
        assert report.declaration is not None
        self.assertEqual(report.declaration.provenance_class, "SYNTHETIC")
        self.assertEqual(report.declaration.universe, "SYN:ONE")

    def test_before_after_date_window_probes(self) -> None:
        # Decision #3 names 2024-01-01..2024-12-31. Date range is not a ruler field.
        before = _synthetic_obs(date(2023, 12, 29), "99.00")
        bound = _synthetic_obs(date(2024, 1, 1), "99.50")
        after = _synthetic_obs(date(2025, 1, 2), "101.00")
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "declaration.json").write_text(
                json.dumps(_declaration(), indent=2) + "\n", encoding="utf-8"
            )
            _write_obs(root / "obs_before.json", before)
            _write_obs(root / "obs_bound.json", bound)
            _write_obs(root / "obs_after.json", after)
            report = load_dataset_pack(root)
            result = run_session_from_pack(root)
        self.assertEqual(report.observation_intake.accepted_count(), 3)
        assert result.session is not None
        self.assertTrue(result.session.series.valid)
        assert result.session.baseline is not None
        self.assertEqual(result.session.baseline.status, "MEASURED")
        stamps = {
            item.envelope.market_timestamp.date()
            for item in result.session.observations
            if item.envelope.market_timestamp is not None
        }
        self.assertEqual(stamps, {date(2023, 12, 29), date(2024, 1, 1), date(2025, 1, 2)})
        self.assertEqual(DATE_WINDOW_GAP_STILL_OPEN, "DATE_WINDOW_GAP_STILL_OPEN")

    def test_lookahead_bar_rehearsal(self) -> None:
        from tempfile import TemporaryDirectory

        last = "2024-01-04T16:00:00.000000-05:00"
        early = "2024-01-03T16:00:00.000000-05:00"
        with TemporaryDirectory() as raw:
            root = Path(raw)
            honest = root / "honest.json"
            early_path = root / "early.json"
            honest.write_text(
                json.dumps(
                    {
                        "as_of": last,
                        "document_kind": "radar_v4.horizon",
                        "include_through": last,
                    },
                    separators=(",", ":"),
                )
                + "\n",
                encoding="utf-8",
            )
            early_path.write_text(
                json.dumps(
                    {
                        "as_of": early,
                        "document_kind": "radar_v4.horizon",
                        "include_through": early,
                    },
                    separators=(",", ":"),
                )
                + "\n",
                encoding="utf-8",
            )
            self.assertTrue(horizon_lock(honest).valid)
            self.assertTrue(horizon_bind(honest, GOLDEN).valid)
            refused = horizon_bind(early_path, GOLDEN)
        self.assertFalse(refused.valid)
        self.assertEqual(refused.error_code, "LOOKAHEAD_BAR")

    def test_deterministic_canonical_measurement_output(self) -> None:
        first = run_session_from_pack(GOLDEN)
        second = run_session_from_pack(GOLDEN)
        assert first.session is not None
        assert second.session is not None
        left = serialize_session_report(first.session)
        right = serialize_session_report(second.session)
        self.assertEqual(left, right)
        parsed = json.loads(left)
        self.assertEqual(parsed["baseline"]["changes"], ["0.25", "-0.50"])
        self.assertEqual(parsed["baseline"]["status"], "MEASURED")
        self.assertEqual(parsed["snapshot_checksum"], first.session.snapshot.integrity_checksum())

    def test_new_measurement_artifact_identity_after_mutation(self) -> None:
        original = run_session_from_pack(GOLDEN)
        assert original.session is not None
        left_report = serialize_session_report(original.session)
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw:
            copy = Path(raw) / "pack"
            shutil.copytree(GOLDEN, copy)
            target = copy / "obs_2024-01-03.json"
            parsed = intake_observation_json(target.read_text(encoding="utf-8"))
            old = parsed.accepted[0]
            _write_obs(
                target,
                Observation.create(old.envelope, ObservationPayload(close="100.26")),
            )
            (copy / "manifest.json").unlink(missing_ok=True)
            changed = run_session_from_pack(copy)
        assert changed.session is not None
        right_report = serialize_session_report(changed.session)
        left = json.loads(left_report)
        right = json.loads(right_report)
        self.assertNotEqual(left["snapshot_checksum"], right["snapshot_checksum"])
        self.assertEqual(left["ruler_checksum"], right["ruler_checksum"])
        self.assertEqual(left["dataset_id"], right["dataset_id"])
        self.assertEqual(right["baseline"]["changes"], ["0.26", "-0.51"])

    def test_preserved_original_measurement_after_mutation(self) -> None:
        before = run_session_from_pack(GOLDEN)
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as raw:
            copy = Path(raw) / "pack"
            shutil.copytree(GOLDEN, copy)
            target = copy / "obs_2024-01-03.json"
            parsed = intake_observation_json(target.read_text(encoding="utf-8"))
            old = parsed.accepted[0]
            _write_obs(
                target,
                Observation.create(old.envelope, ObservationPayload(close="100.26")),
            )
            (copy / "manifest.json").unlink(missing_ok=True)
            mutated = run_session_from_pack(copy)
        after = run_session_from_pack(GOLDEN)
        assert before.session is not None
        assert after.session is not None
        assert mutated.session is not None
        assert before.session.baseline is not None
        assert after.session.baseline is not None
        self.assertEqual(
            before.session.snapshot.integrity_checksum(),
            after.session.snapshot.integrity_checksum(),
        )
        self.assertEqual(before.session.baseline.changes, ("0.25", "-0.50"))
        self.assertEqual(after.session.baseline.changes, ("0.25", "-0.50"))
        self.assertEqual(
            serialize_session_report(before.session),
            serialize_session_report(after.session),
        )
        self.assertNotEqual(
            before.session.snapshot.integrity_checksum(),
            mutated.session.snapshot.integrity_checksum(),
        )

    def test_adjustment_policy_ruler_consistency(self) -> None:
        report = load_dataset_pack(GOLDEN)
        assert report.declaration is not None
        ruler = declaration_ruler(report.declaration)
        self.assertEqual(ruler["adjustment_policy"], "UNADJUSTED")
        echoed = describe_adjustment_policy(GOLDEN)
        self.assertTrue(echoed.valid)
        self.assertEqual(echoed.details["adjustment_policy"], "UNADJUSTED")
        self.assertEqual(report.declaration.adjustment_policy, "UNADJUSTED")
        altered = _declaration_object(adjustment_policy="SPLIT_ADJUSTED")
        self.assertNotEqual(ruler_checksum(report.declaration), ruler_checksum(altered))
        self.assertEqual(DISPOSITION, "LOCAL FIXTURE/SYNTHETIC DRESS REHEARSAL PASSED WITH KNOWN GAPS")


if __name__ == "__main__":
    unittest.main()
