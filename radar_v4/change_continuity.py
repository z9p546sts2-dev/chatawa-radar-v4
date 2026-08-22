"""Check that close-to-close records form a continuous chain. Not a method."""

from __future__ import annotations

from collections.abc import Sequence

from radar_v4.baseline import CloseToCloseChange
from radar_v4.validation import ValidationIssue, ValidationResult


def inspect_change_records(
    records: Sequence[CloseToCloseChange],
) -> ValidationResult:
    """Refuse broken from/to linkage. Does not invent missing bars."""
    issues: list[ValidationIssue] = []
    for index in range(1, len(records)):
        previous = records[index - 1]
        current = records[index]
        if previous.to_market_timestamp != current.from_market_timestamp:
            issues.append(
                ValidationIssue(
                    "CHANGE_DISCONTINUITY",
                    f"record {index} does not start where record {index - 1} ended",
                    "from_market_timestamp",
                )
            )
        if previous.to_close != current.from_close:
            issues.append(
                ValidationIssue(
                    "CHANGE_DISCONTINUITY",
                    f"record {index} close does not match the previous to_close",
                    "from_close",
                )
            )
    issues.sort(key=lambda item: (item.code, item.field or "", item.reason))
    return ValidationResult(valid=len(issues) == 0, issues=tuple(issues))
