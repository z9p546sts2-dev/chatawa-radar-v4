"""Radar V4 evidence identity and intake.

This package does not implement market methods, features, signals,
thresholds, data access, or trading.
"""

from radar_v4.baseline import BaselineReport, close_to_close_changes
from radar_v4.dataset import DatasetDeclaration, admit_to_dataset
from radar_v4.dataset_pack import DatasetPackReport, load_dataset_pack
from radar_v4.declaration_json import DeclarationIntakeReport, intake_declaration_json
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
from radar_v4.observation_json import (
    ObservationIntakeRecord,
    ObservationIntakeReport,
    intake_observation_json,
)
from radar_v4.observation_validation import validate_observation
from radar_v4.registry import EvidenceRegistry
from radar_v4.series import SeriesReport, inspect_series
from radar_v4.local_session import (
    LocalSessionResult,
    run_session_from_pack,
    run_session_from_snapshot,
    run_session_from_snapshot_file,
)
from radar_v4.session import SessionResult, run_dataset_session
from radar_v4.session_report import serialize_session_report, write_session_report_file
from radar_v4.snapshot import DatasetSnapshot, make_snapshot
from radar_v4.snapshot_files import (
    SnapshotFileError,
    read_snapshot_file,
    write_snapshot_file,
)
from radar_v4.validation import ValidationIssue, ValidationResult, validate_envelope

__all__ = [
    "ALLOWED_PROVENANCE_CLASSES",
    "BaselineReport",
    "DatasetDeclaration",
    "DatasetPackReport",
    "DatasetSnapshot",
    "DeclarationIntakeReport",
    "LocalSessionResult",
    "SeriesReport",
    "Observation",
    "ObservationIntakeRecord",
    "ObservationIntakeReport",
    "ObservationPayload",
    "SessionResult",
    "SnapshotFileError",
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
    "inspect_series",
    "intake_declaration_json",
    "intake_observation_json",
    "load_dataset_pack",
    "make_snapshot",
    "read_snapshot_file",
    "run_dataset_session",
    "run_session_from_pack",
    "run_session_from_snapshot",
    "run_session_from_snapshot_file",
    "serialize_session_report",
    "write_session_report_file",
    "write_snapshot_file",
    "intake_envelopes",
    "intake_json_text",
    "load_fixture_pack",
    "validate_envelope",
    "validate_observation",
]
