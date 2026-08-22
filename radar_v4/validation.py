"""Validate evidence-envelope identity. Do not repair invalid records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from radar_v4.evidence import (
    ALLOWED_PROVENANCE_CLASSES,
    EvidenceEnvelope,
    is_known_timezone,
    timezone_offset_matches,
)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    reason: str
    field: str | None = None


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    issues: tuple[ValidationIssue, ...]

    def issue_codes(self) -> tuple[str, ...]:
        return tuple(issue.code for issue in self.issues)


def _blank(value: object) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def validate_envelope(envelope: EvidenceEnvelope) -> ValidationResult:
    """Return a structured accept/reject result. Never mutates the envelope."""
    issues: list[ValidationIssue] = []

    if _blank(envelope.provenance_class):
        issues.append(
            ValidationIssue(
                "MISSING_PROVENANCE_CLASS",
                "provenance class is required",
                "provenance_class",
            )
        )
    elif envelope.provenance_class not in ALLOWED_PROVENANCE_CLASSES:
        issues.append(
            ValidationIssue(
                "UNKNOWN_PROVENANCE_CLASS",
                "provenance class is not an allowed identity",
                "provenance_class",
            )
        )

    if _blank(envelope.provider):
        issues.append(
            ValidationIssue(
                "MISSING_PROVIDER",
                "provider/source is required",
                "provider",
            )
        )

    if _blank(envelope.symbol_or_universe):
        issues.append(
            ValidationIssue(
                "MISSING_SYMBOL_OR_UNIVERSE",
                "symbol or universe identity is required",
                "symbol_or_universe",
            )
        )

    _check_timestamp(issues, envelope.market_timestamp, "market_timestamp")
    _check_timestamp(issues, envelope.retrieval_timestamp, "retrieval_timestamp")

    if _blank(envelope.interval):
        issues.append(
            ValidationIssue(
                "MISSING_INTERVAL",
                "interval is required",
                "interval",
            )
        )

    if _blank(envelope.timezone):
        issues.append(
            ValidationIssue(
                "MISSING_TIMEZONE",
                "timezone is required and is not defaulted to UTC",
                "timezone",
            )
        )
    elif not is_known_timezone(str(envelope.timezone)):
        issues.append(
            ValidationIssue(
                "UNKNOWN_TIMEZONE",
                "timezone is not a known IANA name or UTC",
                "timezone",
            )
        )
    else:
        declared = str(envelope.timezone)
        if (
            isinstance(envelope.market_timestamp, datetime)
            and envelope.market_timestamp.tzinfo is not None
            and not timezone_offset_matches(envelope.market_timestamp, declared)
        ):
            issues.append(
                ValidationIssue(
                    "TIMEZONE_MISMATCH",
                    "market timestamp offset does not match the declared timezone",
                    "market_timestamp",
                )
            )
        if (
            isinstance(envelope.retrieval_timestamp, datetime)
            and envelope.retrieval_timestamp.tzinfo is not None
            and not timezone_offset_matches(envelope.retrieval_timestamp, declared)
        ):
            issues.append(
                ValidationIssue(
                    "TIMEZONE_MISMATCH",
                    "retrieval timestamp offset does not match the declared timezone",
                    "retrieval_timestamp",
                )
            )

    if _blank(envelope.transformation_version):
        issues.append(
            ValidationIssue(
                "MISSING_TRANSFORMATION_VERSION",
                "transformation version is required",
                "transformation_version",
            )
        )

    if envelope.context_decision_use_tag is not None and _blank(
        envelope.context_decision_use_tag
    ):
        issues.append(
            ValidationIssue(
                "MALFORMED_CONTEXT_DECISION_USE_TAG",
                "optional context/decision-use tag must be omitted, not empty",
                "context_decision_use_tag",
            )
        )

    if _blank(envelope.checksum):
        issues.append(
            ValidationIssue(
                "MISSING_CHECKSUM",
                "integrity checksum is required",
                "checksum",
            )
        )
    elif not _is_sha256_hex(envelope.checksum):
        issues.append(
            ValidationIssue(
                "MALFORMED_CHECKSUM",
                "checksum must be a 64-character SHA-256 hex digest",
                "checksum",
            )
        )
    else:
        expected = envelope.compute_checksum()
        if envelope.checksum != expected:
            issues.append(
                ValidationIssue(
                    "CHECKSUM_MISMATCH",
                    "supplied checksum does not match the canonical payload",
                    "checksum",
                )
            )

    issues.sort(key=lambda item: (item.code, item.field or "", item.reason))
    return ValidationResult(valid=len(issues) == 0, issues=tuple(issues))


def _check_timestamp(
    issues: list[ValidationIssue], value: object, field: str
) -> None:
    if value is None:
        issues.append(
            ValidationIssue(
                f"INVALID_{field.upper()}",
                f"{field} is required and must be parseable",
                field,
            )
        )
        return
    if not isinstance(value, datetime):
        issues.append(
            ValidationIssue(
                f"INVALID_{field.upper()}",
                f"{field} is not a datetime",
                field,
            )
        )
        return
    if value.tzinfo is None:
        issues.append(
            ValidationIssue(
                f"INVALID_{field.upper()}",
                f"{field} must be timezone-aware; UTC is not inferred",
                field,
            )
        )


def _is_sha256_hex(value: object) -> bool:
    if not isinstance(value, str):
        return False
    if len(value) != 64:
        return False
    return all(char in "0123456789abcdef" for char in value)
