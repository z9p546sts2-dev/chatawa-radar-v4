"""In-memory evidence registry. No database, no market access."""

from __future__ import annotations

from collections.abc import Sequence

from radar_v4.evidence import EvidenceEnvelope
from radar_v4.intake import IntakeRecord, IntakeReport, intake_envelopes
from radar_v4.validation import ValidationIssue, ValidationResult


class EvidenceRegistry:
    """Store accepted envelopes and detect identity contradictions.

    Collision rule: the same identity_key with a different checksum is
    quarantined as CONTRADICTORY_IDENTITY. The stored record is not
    overwritten. The same checksum is idempotent.
    """

    def __init__(self) -> None:
        self._accepted: dict[tuple[object, ...], EvidenceEnvelope] = {}
        self._quarantined: list[IntakeRecord] = []

    def put(self, envelopes: Sequence[EvidenceEnvelope]) -> IntakeReport:
        intake = intake_envelopes(envelopes)
        accepted: list[IntakeRecord] = []
        quarantined: list[IntakeRecord] = list(intake.quarantined)
        for record in intake.accepted:
            collision = self._collision(record.envelope)
            if collision is not None:
                quarantined.append(collision)
                continue
            self._accepted[record.envelope.identity_key()] = record.envelope
            accepted.append(record)
        self._quarantined.extend(quarantined)
        return IntakeReport(accepted=tuple(accepted), quarantined=tuple(quarantined))

    def get(self, envelope: EvidenceEnvelope) -> EvidenceEnvelope | None:
        return self._accepted.get(envelope.identity_key())

    def accepted_envelopes(self) -> tuple[EvidenceEnvelope, ...]:
        return tuple(self._accepted.values())

    def quarantined_records(self) -> tuple[IntakeRecord, ...]:
        return tuple(self._quarantined)

    def record_quarantine(self, records: Sequence[IntakeRecord]) -> None:
        """Preserve already-quarantined records. Does not repair them."""
        self._quarantined.extend(records)

    def accepted_count(self) -> int:
        return len(self._accepted)

    def quarantined_count(self) -> int:
        return len(self._quarantined)

    def _collision(self, envelope: EvidenceEnvelope) -> IntakeRecord | None:
        existing = self._accepted.get(envelope.identity_key())
        if existing is None:
            return None
        if existing.checksum == envelope.checksum:
            return None
        return IntakeRecord(
            envelope=envelope,
            validation=ValidationResult(
                valid=False,
                issues=(
                    ValidationIssue(
                        "CONTRADICTORY_IDENTITY",
                        "same evidence identity already stored with a different checksum",
                        "checksum",
                    ),
                ),
            ),
        )
