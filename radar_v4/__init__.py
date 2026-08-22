"""Radar V4 evidence identity and intake.

This package does not implement market methods, features, signals,
thresholds, data access, or trading.
"""

from radar_v4.baseline import BaselineReport, close_to_close_changes
from radar_v4.dataset import DatasetDeclaration, admit_to_dataset
from radar_v4.evidence import (
    ALLOWED_PROVENANCE_CLASSES,
    EvidenceEnvelope,
    ProvenanceClass,
)
from radar_v4.fixture_pack import PACK_ALLOWED_PROVENANCE, load_fixture_pack
from radar_v4.intake import IntakeRecord, IntakeReport, intake_envelopes
from radar_v4.json_intake import (
    DocumentIntakeReport,
    UnreadableDocument,
    intake_json_text,
)
from radar_v4.observation import Observation, ObservationPayload
from radar_v4.observation_validation import validate_observation
from radar_v4.registry import EvidenceRegistry
from radar_v4.validation import ValidationIssue, ValidationResult, validate_envelope

__all__ = [
    "ALLOWED_PROVENANCE_CLASSES",
    "BaselineReport",
    "DatasetDeclaration",
    "Observation",
    "ObservationPayload",
    "DocumentIntakeReport",
    "EvidenceEnvelope",
    "EvidenceRegistry",
    "IntakeRecord",
    "IntakeReport",
    "ProvenanceClass",
    "UnreadableDocument",
    "ValidationIssue",
    "ValidationResult",
    "PACK_ALLOWED_PROVENANCE",
    "admit_to_dataset",
    "close_to_close_changes",
    "intake_envelopes",
    "intake_json_text",
    "load_fixture_pack",
    "validate_envelope",
    "validate_observation",
]
