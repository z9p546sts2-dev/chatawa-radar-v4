"""Radar V4 evidence identity and intake.

This package does not implement market methods, features, signals,
thresholds, data access, or trading.
"""

from radar_v4.baseline import BaselineReport, CloseToCloseChange, close_to_close_changes
from radar_v4.change_continuity import inspect_change_records
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
from radar_v4.pack_export import PackExportError, export_snapshot_to_pack
from radar_v4.registry import EvidenceRegistry
from radar_v4.registry_files import RegistryFileError, read_registry_file, write_registry_file
from radar_v4.series import SeriesReport, inspect_series
from radar_v4.local_session import (
    LocalSessionResult,
    run_session_from_pack,
    run_session_from_snapshot,
    run_session_from_snapshot_file,
)
from radar_v4.session import SessionResult, run_dataset_session
from radar_v4.reason_codes import REASON_CODES, RESULT_STATUSES
from radar_v4.session_report import (
    serialize_local_session_report,
    serialize_session_report,
    write_local_session_report_file,
    write_session_report_file,
)
from radar_v4.snapshot import DatasetSnapshot, make_snapshot
from radar_v4.snapshot_compare import (
    SnapshotComparison,
    compare_snapshot_files,
    compare_snapshots,
)
from radar_v4.snapshot_verify import SnapshotVerification, verify_snapshot, verify_snapshot_file
from radar_v4.snapshot_files import (
    SnapshotFileError,
    read_snapshot_file,
    write_snapshot_file,
)
from radar_v4.validation import ValidationIssue, ValidationResult, validate_envelope

__all__ = [
    "ALLOWED_PROVENANCE_CLASSES",
    "BaselineReport",
    "CloseToCloseChange",
    "DatasetDeclaration",
    "DatasetPackReport",
    "DatasetSnapshot",
    "DeclarationIntakeReport",
    "SnapshotComparison",
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
    "PackExportError",
    "RegistryFileError",
    "SnapshotVerification",
    "IntakeRecord",
    "IntakeReport",
    "ProvenanceClass",
    "UnreadableDocument",
    "ValidationIssue",
    "ValidationResult",
    "PACK_ALLOWED_PROVENANCE",
    "REASON_CODES",
    "RESULT_STATUSES",
    "admit_to_dataset",
    "close_to_close_changes",
    "compare_snapshot_files",
    "compare_snapshots",
    "export_snapshot_to_pack",
    "inspect_change_records",
    "inspect_series",
    "intake_declaration_json",
    "intake_observation_json",
    "load_dataset_pack",
    "make_snapshot",
    "read_registry_file",
    "read_snapshot_file",
    "run_dataset_session",
    "run_session_from_pack",
    "run_session_from_snapshot",
    "run_session_from_snapshot_file",
    "serialize_local_session_report",
    "serialize_session_report",
    "write_local_session_report_file",
    "write_session_report_file",
    "write_snapshot_file",
    "intake_envelopes",
    "intake_json_text",
    "load_fixture_pack",
    "validate_envelope",
    "validate_observation",
    "verify_snapshot",
    "verify_snapshot_file",
    "write_registry_file",
]
