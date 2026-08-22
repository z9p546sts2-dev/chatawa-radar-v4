"""Radar V4 Build Unit 1 — evidence identity only.

This package does not implement market methods, features, signals,
thresholds, data access, or trading.
"""

from radar_v4.evidence import (
    ALLOWED_PROVENANCE_CLASSES,
    EvidenceEnvelope,
    ProvenanceClass,
)
from radar_v4.validation import ValidationIssue, ValidationResult, validate_envelope

__all__ = [
    "ALLOWED_PROVENANCE_CLASSES",
    "EvidenceEnvelope",
    "ProvenanceClass",
    "ValidationIssue",
    "ValidationResult",
    "validate_envelope",
]
