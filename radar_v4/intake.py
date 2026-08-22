"""Evidence intake and quarantine. No repair, no market access."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from radar_v4.evidence import EvidenceEnvelope
from radar_v4.validation import ValidationResult, validate_envelope


@dataclass(frozen=True)
class IntakeRecord:
    envelope: EvidenceEnvelope
    validation: ValidationResult


@dataclass(frozen=True)
class IntakeReport:
    accepted: tuple[IntakeRecord, ...]
    quarantined: tuple[IntakeRecord, ...]

    def accepted_count(self) -> int:
        return len(self.accepted)

    def quarantined_count(self) -> int:
        return len(self.quarantined)


def intake_envelopes(envelopes: Sequence[EvidenceEnvelope]) -> IntakeReport:
    """Validate each envelope and partition without mutating inputs.

    Accepted records are identity-valid. Quarantined records remain the
    original objects plus the structured validation issues. Nothing is
    rewritten to become valid.
    """
    accepted: list[IntakeRecord] = []
    quarantined: list[IntakeRecord] = []
    for envelope in envelopes:
        record = IntakeRecord(envelope=envelope, validation=validate_envelope(envelope))
        if record.validation.valid:
            accepted.append(record)
        else:
            quarantined.append(record)
    return IntakeReport(accepted=tuple(accepted), quarantined=tuple(quarantined))
