"""Parse a dataset declaration from JSON. No defaults. No repair."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from json import JSONDecodeError, loads

from radar_v4.dataset import DatasetDeclaration
from radar_v4.evidence import ALLOWED_PROVENANCE_CLASSES
from radar_v4.json_intake import UnreadableDocument
from radar_v4.validation import ValidationIssue, ValidationResult

REQUIRED_DECLARATION_FIELDS = (
    "dataset_id",
    "provenance_class",
    "provider",
    "universe",
    "interval",
    "timezone",
    "transformation_version",
    "adjustment_policy",
    "locked_question",
    "primary_metric",
)


@dataclass(frozen=True)
class DeclarationIntakeReport:
    declaration: DatasetDeclaration | None
    validation: ValidationResult | None
    unreadable: UnreadableDocument | None


def intake_declaration_json(text: str) -> DeclarationIntakeReport:
    """Parse one declaration object. Partial records are not emitted."""
    try:
        raw = loads(text)
    except JSONDecodeError as exc:
        return DeclarationIntakeReport(
            declaration=None,
            validation=None,
            unreadable=UnreadableDocument(
                index=0,
                raw=text,
                code="UNREADABLE_JSON",
                reason=f"JSON could not be parsed: {exc.msg}",
            ),
        )
    if not isinstance(raw, Mapping):
        return DeclarationIntakeReport(
            declaration=None,
            validation=None,
            unreadable=UnreadableDocument(
                index=0,
                raw=text,
                code="UNREADABLE_JSON",
                reason="declaration JSON root must be an object",
            ),
        )

    issues: list[ValidationIssue] = []
    values: dict[str, str] = {}
    for field in REQUIRED_DECLARATION_FIELDS:
        value = raw.get(field)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            issues.append(
                ValidationIssue(
                    "MISSING_DECLARATION_FIELD",
                    f"{field} is required",
                    field,
                )
            )
        else:
            values[field] = str(value)

    provenance = values.get("provenance_class")
    if provenance is not None and provenance not in ALLOWED_PROVENANCE_CLASSES:
        issues.append(
            ValidationIssue(
                "UNKNOWN_PROVENANCE_CLASS",
                "provenance class is not an allowed identity",
                "provenance_class",
            )
        )

    issues.sort(key=lambda item: (item.code, item.field or "", item.reason))
    if issues:
        return DeclarationIntakeReport(
            declaration=None,
            validation=ValidationResult(valid=False, issues=tuple(issues)),
            unreadable=None,
        )

    staleness = raw.get("max_staleness")
    declaration = DatasetDeclaration(
        dataset_id=values["dataset_id"],
        provenance_class=values["provenance_class"],
        provider=values["provider"],
        universe=values["universe"],
        interval=values["interval"],
        timezone=values["timezone"],
        transformation_version=values["transformation_version"],
        adjustment_policy=values["adjustment_policy"],
        locked_question=values["locked_question"],
        primary_metric=values["primary_metric"],
        max_staleness=None if staleness is None else str(staleness),
    )
    return DeclarationIntakeReport(
        declaration=declaration,
        validation=ValidationResult(valid=True, issues=()),
        unreadable=None,
    )
