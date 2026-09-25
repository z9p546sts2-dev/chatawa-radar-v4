"""Validate observation payloads. Do not repair values."""

from __future__ import annotations

from decimal import InvalidOperation

from radar_v4.observation import Observation, parse_decimal
from radar_v4.validation import ValidationIssue, ValidationResult, validate_envelope


def validate_observation(observation: Observation) -> ValidationResult:
    issues: list[ValidationIssue] = list(validate_envelope(observation.envelope).issues)
    payload = observation.payload

    close = None
    if payload.close is None or str(payload.close).strip() == "":
        issues.append(ValidationIssue("MISSING_CLOSE", "close is required", "close"))
    else:
        try:
            close = parse_decimal(payload.close, "close")
            if not close.is_finite():
                raise InvalidOperation("close must be finite")
        except InvalidOperation:
            close = None
            issues.append(
                ValidationIssue(
                    "INVALID_CLOSE", "close must be a decimal string", "close"
                )
            )

    optional = {
        "open": payload.open,
        "high": payload.high,
        "low": payload.low,
        "volume": payload.volume,
    }
    parsed: dict[str, object] = {"close": close}
    for field, raw in optional.items():
        if raw is None:
            continue
        try:
            number = parse_decimal(raw, field)
            if not number.is_finite() or (field == "volume" and number < 0):
                raise InvalidOperation(f"{field} must be finite and volume nonnegative")
            parsed[field] = number
        except InvalidOperation:
            issues.append(
                ValidationIssue(
                    f"INVALID_{field.upper()}",
                    f"{field} must be a decimal string",
                    field,
                )
            )
            parsed[field] = None

    high = parsed.get("high")
    low = parsed.get("low")
    if high is not None and low is not None and high < low:
        issues.append(
            ValidationIssue(
                "OHLC_CONTRADICTION",
                "high is below low",
                "high",
            )
        )
    opening = parsed.get("open")
    if (
        opening is not None
        and high is not None
        and low is not None
        and (opening > high or opening < low)
    ):
        issues.append(
            ValidationIssue(
                "OHLC_CONTRADICTION",
                "open is outside high/low",
                "open",
            )
        )
    if (
        close is not None
        and high is not None
        and low is not None
        and (close > high or close < low)
    ):
        issues.append(
            ValidationIssue(
                "OHLC_CONTRADICTION",
                "close is outside high/low",
                "close",
            )
        )

    if observation.payload_checksum != payload.compute_checksum():
        issues.append(
            ValidationIssue(
                "PAYLOAD_CHECKSUM_MISMATCH",
                "payload checksum does not match the canonical payload",
                "payload_checksum",
            )
        )

    issues.sort(key=lambda item: (item.code, item.field or "", item.reason))
    # Deduplicate identical issues
    unique: list[ValidationIssue] = []
    seen: set[tuple[str, str | None, str]] = set()
    for issue in issues:
        key = (issue.code, issue.field, issue.reason)
        if key in seen:
            continue
        seen.add(key)
        unique.append(issue)
    return ValidationResult(valid=len(unique) == 0, issues=tuple(unique))
