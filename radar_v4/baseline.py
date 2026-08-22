"""Ordinary close-to-close description. Not a method, signal, or edge."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from radar_v4.evidence import format_canonical_timestamp
from radar_v4.observation import Observation, parse_decimal
from radar_v4.observation_validation import validate_observation

LIVE_PROVENANCE = "LIVE"


@dataclass(frozen=True)
class CloseToCloseChange:
    """One ordinary close-to-close difference. Not a signal."""

    from_market_timestamp: str
    to_market_timestamp: str
    from_close: str
    to_close: str
    difference: str

    def to_json_dict(self) -> dict[str, str]:
        return {
            "difference": self.difference,
            "from_close": self.from_close,
            "from_market_timestamp": self.from_market_timestamp,
            "to_close": self.to_close,
            "to_market_timestamp": self.to_market_timestamp,
        }


@dataclass(frozen=True)
class BaselineReport:
    claim_level: str
    status: str
    symbol_or_universe: str | None
    interval: str | None
    timezone: str | None
    observation_count: int
    change_count: int
    changes: tuple[str, ...]
    notes: tuple[str, ...]
    change_records: tuple[CloseToCloseChange, ...] = ()


def close_to_close_changes(observations: Sequence[Observation]) -> BaselineReport:
    """Describe ordinary close-to-close differences.

    This is LEVEL 0 — MEASURED. It is not usefulness, prediction, or a
    trading rule. LIVE records are refused. Invalid observations are
    refused rather than repaired.
    """
    notes: list[str] = []
    if len(observations) < 2:
        return BaselineReport(
            claim_level="LEVEL 0 — MEASURED",
            status="INSUFFICIENT_EVIDENCE",
            symbol_or_universe=None,
            interval=None,
            timezone=None,
            observation_count=len(observations),
            change_count=0,
            changes=(),
            notes=("fewer than two observations",),
        )

    for item in observations:
        if item.envelope.provenance_class == LIVE_PROVENANCE:
            return BaselineReport(
                claim_level="LEVEL 0 — MEASURED",
                status="INVALID_COMPARISON",
                symbol_or_universe=item.envelope.symbol_or_universe,
                interval=item.envelope.interval,
                timezone=item.envelope.timezone,
                observation_count=len(observations),
                change_count=0,
                changes=(),
                notes=("LIVE provenance is not allowed in this baseline",),
            )
        if not validate_observation(item).valid:
            return BaselineReport(
                claim_level="LEVEL 0 — MEASURED",
                status="INVALID_COMPARISON",
                symbol_or_universe=item.envelope.symbol_or_universe,
                interval=item.envelope.interval,
                timezone=item.envelope.timezone,
                observation_count=len(observations),
                change_count=0,
                changes=(),
                notes=("one or more observations failed validation",),
            )

    first = observations[0].envelope
    for item in observations[1:]:
        envelope = item.envelope
        if (
            envelope.symbol_or_universe != first.symbol_or_universe
            or envelope.interval != first.interval
            or envelope.timezone != first.timezone
            or envelope.transformation_version != first.transformation_version
        ):
            return BaselineReport(
                claim_level="LEVEL 0 — MEASURED",
                status="INVALID_COMPARISON",
                symbol_or_universe=first.symbol_or_universe,
                interval=first.interval,
                timezone=first.timezone,
                observation_count=len(observations),
                change_count=0,
                changes=(),
                notes=("observations do not share the same ruler",),
            )

    ordered = sorted(
        observations,
        key=lambda item: item.envelope.market_timestamp or datetime(1, 1, 1),
    )
    closes = [parse_decimal(item.payload.close, "close") for item in ordered]
    records: list[CloseToCloseChange] = []
    for index in range(1, len(ordered)):
        previous_close = closes[index - 1]
        current_close = closes[index]
        previous_stamp = ordered[index - 1].envelope.market_timestamp
        current_stamp = ordered[index].envelope.market_timestamp
        if (
            previous_close is None
            or current_close is None
            or previous_stamp is None
            or current_stamp is None
        ):
            continue
        difference = str(current_close - previous_close)
        records.append(
            CloseToCloseChange(
                from_market_timestamp=format_canonical_timestamp(previous_stamp),
                to_market_timestamp=format_canonical_timestamp(current_stamp),
                from_close=ordered[index - 1].payload.close,
                to_close=ordered[index].payload.close,
                difference=difference,
            )
        )
    changes = tuple(item.difference for item in records)
    notes.append("descriptive close-to-close differences only")
    notes.append("not a threshold, signal, or edge")
    return BaselineReport(
        claim_level="LEVEL 0 — MEASURED",
        status="MEASURED",
        symbol_or_universe=first.symbol_or_universe,
        interval=first.interval,
        timezone=first.timezone,
        observation_count=len(ordered),
        change_count=len(changes),
        changes=changes,
        notes=tuple(notes),
        change_records=tuple(records),
    )
