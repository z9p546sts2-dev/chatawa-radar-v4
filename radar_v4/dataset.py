"""Dataset declaration and admission. No vendor download, no method."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from radar_v4.evidence import EvidenceEnvelope
from radar_v4.intake import IntakeRecord, IntakeReport, intake_envelopes
from radar_v4.validation import ValidationIssue, ValidationResult


@dataclass(frozen=True)
class DatasetDeclaration:
    """Identity of one dataset that may later hold admitted evidence."""

    dataset_id: str
    provenance_class: str
    provider: str
    universe: str
    interval: str
    timezone: str
    transformation_version: str
    adjustment_policy: str
    locked_question: str
    primary_metric: str
    max_staleness: str | None = None


def admit_to_dataset(
    declaration: DatasetDeclaration,
    envelopes: Sequence[EvidenceEnvelope],
) -> IntakeReport:
    """Admit envelopes that match the dataset declaration.

    Identity-invalid envelopes are quarantined first. Declaration mismatches
    are quarantined even if the envelope would otherwise be valid.
    """
    intake = intake_envelopes(envelopes)
    accepted: list[IntakeRecord] = []
    quarantined: list[IntakeRecord] = list(intake.quarantined)
    for record in intake.accepted:
        mismatch = _declaration_mismatch(declaration, record.envelope)
        if mismatch is not None:
            quarantined.append(mismatch)
        else:
            accepted.append(record)
    return IntakeReport(accepted=tuple(accepted), quarantined=tuple(quarantined))


def _declaration_mismatch(
    declaration: DatasetDeclaration, envelope: EvidenceEnvelope
) -> IntakeRecord | None:
    issues: list[ValidationIssue] = []
    checks = (
        ("provenance_class", declaration.provenance_class, envelope.provenance_class),
        ("provider", declaration.provider, envelope.provider),
        ("symbol_or_universe", declaration.universe, envelope.symbol_or_universe),
        ("interval", declaration.interval, envelope.interval),
        ("timezone", declaration.timezone, envelope.timezone),
        (
            "transformation_version",
            declaration.transformation_version,
            envelope.transformation_version,
        ),
    )
    for field, expected, actual in checks:
        if actual != expected:
            issues.append(
                ValidationIssue(
                    "DATASET_DECLARATION_MISMATCH",
                    f"{field} {actual!r} does not match dataset {expected!r}",
                    field,
                )
            )
    if not issues:
        return None
    issues.sort(key=lambda item: (item.code, item.field or "", item.reason))
    return IntakeRecord(
        envelope=envelope,
        validation=ValidationResult(valid=False, issues=tuple(issues)),
    )
