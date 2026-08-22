"""Radar V4 evidence identity and intake.

This package does not implement market methods, features, signals,
thresholds, data access, or trading.
"""

from radar_v4.evidence import (
    ALLOWED_PROVENANCE_CLASSES,
    EvidenceEnvelope,
    ProvenanceClass,
)
from radar_v4.intake import IntakeRecord, IntakeReport, intake_envelopes
from radar_v4.validation import ValidationIssue, ValidationResult, validate_envelope

__all__ = [
    "ALLOWED_PROVENANCE_CLASSES",
    "EvidenceEnvelope",
    "IntakeRecord",
    "IntakeReport",
    "ProvenanceClass",
    "ValidationIssue",
    "ValidationResult",
    "intake_envelopes",
    "validate_envelope",
]
