"""Observation-series integrity. No calendar fill, no market hours."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from radar_v4.observation import Observation
from radar_v4.observation_validation import validate_observation
from radar_v4.validation import ValidationIssue


@dataclass(frozen=True)
class SeriesReport:
    valid: bool
    ordered: tuple[Observation, ...]
    issues: tuple[ValidationIssue, ...]

    def issue_codes(self) -> tuple[str, ...]:
        return tuple(issue.code for issue in self.issues)


def inspect_series(observations: Sequence[Observation]) -> SeriesReport:
    """Check timestamp uniqueness and produce a time-ordered copy.

    Missing bars are not invented. Exchange calendars are not applied.
    """
    issues: list[ValidationIssue] = []
    for index, item in enumerate(observations):
        result = validate_observation(item)
        if not result.valid:
            issues.append(
                ValidationIssue(
                    "INVALID_OBSERVATION",
                    f"observation {index} failed validation",
                    "observation",
                )
            )

    timestamps: list[datetime | None] = [
        item.envelope.market_timestamp for item in observations
    ]
    seen: dict[datetime, int] = {}
    for index, stamp in enumerate(timestamps):
        if stamp is None:
            issues.append(
                ValidationIssue(
                    "MISSING_MARKET_TIMESTAMP",
                    f"observation {index} has no market timestamp",
                    "market_timestamp",
                )
            )
            continue
        if stamp in seen:
            issues.append(
                ValidationIssue(
                    "DUPLICATE_MARKET_TIMESTAMP",
                    f"observations {seen[stamp]} and {index} share {stamp.isoformat()}",
                    "market_timestamp",
                )
            )
        else:
            seen[stamp] = index

    ordered = tuple(
        sorted(
            (item for item in observations if item.envelope.market_timestamp is not None),
            key=lambda item: item.envelope.market_timestamp or datetime(1, 1, 1),
        )
    )
    issues.sort(key=lambda item: (item.code, item.field or "", item.reason))
    return SeriesReport(valid=len(issues) == 0, ordered=ordered, issues=tuple(issues))
