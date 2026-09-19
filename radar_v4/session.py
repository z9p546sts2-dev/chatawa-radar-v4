"""Compose Phase 5 admission, series checks, snapshot, and baseline.

This is a session runner, not a method, vendor client, or trading loop.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from radar_v4.baseline import BaselineReport, close_to_close_changes
from radar_v4.dataset import DatasetDeclaration, admit_to_dataset
from radar_v4.evidence import EvidenceEnvelope
from radar_v4.intake import IntakeReport
from radar_v4.observation import Observation
from radar_v4.observation_validation import validate_observation
from radar_v4.series import SeriesReport, inspect_series
from radar_v4.snapshot import DatasetSnapshot, make_snapshot
from radar_v4.validation import ValidationIssue, ValidationResult


@dataclass(frozen=True)
class SessionResult:
    admission: IntakeReport
    observations: tuple[Observation, ...]
    rejected_observations: tuple[tuple[Observation, ValidationResult], ...]
    series: SeriesReport
    snapshot: DatasetSnapshot
    baseline: BaselineReport | None

    def kept_observation_count(self) -> int:
        return len(self.observations)

    def rejected_observation_count(self) -> int:
        return len(self.rejected_observations)


def run_dataset_session(
    declaration: DatasetDeclaration,
    envelopes: Sequence[EvidenceEnvelope],
    observations: Sequence[Observation],
    measure: bool = True,
) -> SessionResult:
    """Admit envelopes, keep matching valid observations, then inspect.

    Baseline runs only when measure is true and the series is valid.
    Unit 9 still reports LEVEL 0 description only. Nothing is repaired.
    """
    admission = admit_to_dataset(declaration, envelopes)
    admitted_checksums = {
        record.envelope.checksum for record in admission.accepted
    }
    kept: list[Observation] = []
    rejected: list[tuple[Observation, ValidationResult]] = []
    for item in observations:
        validation = validate_observation(item)
        if not validation.valid:
            rejected.append((item, validation))
            continue
        if item.envelope.checksum not in admitted_checksums:
            rejected.append(
                (
                    item,
                    ValidationResult(
                        valid=False,
                        issues=(
                            ValidationIssue(
                                "OBSERVATION_NOT_ADMITTED",
                                "observation envelope was not admitted to the dataset",
                                "envelope",
                            ),
                        ),
                    ),
                )
            )
            continue
        kept.append(item)

    series = inspect_series(kept)
    snapshot = make_snapshot(declaration, series.ordered)
    baseline: BaselineReport | None = None
    if measure and series.valid:
        if declaration.expected_session_dates:
            expected = set(declaration.expected_session_dates)
            actual = {
                item.envelope.market_timestamp.date().isoformat()
                for item in series.ordered
                if item.envelope.market_timestamp is not None
            }
            if actual != expected:
                baseline = BaselineReport(
                    claim_level="NONE",
                    status="INSUFFICIENT_EVIDENCE",
                    symbol_or_universe=declaration.universe,
                    interval=declaration.interval,
                    timezone=declaration.timezone,
                    observation_count=len(series.ordered),
                    change_count=0,
                    changes=(),
                    notes=(
                        "expected-session manifest is incomplete",
                        f"expected {len(expected)} unique session dates; admitted {len(actual)}",
                        "no missing bar was synthesized or bridged",
                    ),
                )
            else:
                baseline = close_to_close_changes(series.ordered)
        else:
            baseline = close_to_close_changes(series.ordered)
    return SessionResult(
        admission=admission,
        observations=tuple(kept),
        rejected_observations=tuple(rejected),
        series=series,
        snapshot=snapshot,
        baseline=baseline,
    )
