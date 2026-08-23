"""Radar V4 evidence identity and intake.

This package does not implement market methods, features, signals,
thresholds, data access, or trading.
"""

from radar_v4.atomic_write import write_text_atomic
from radar_v4.baseline import BaselineReport, CloseToCloseChange, close_to_close_changes
from radar_v4.bundle_verify import (
    BundleVerification,
    BundleWriteResult,
    verify_snapshot_bundle,
    write_bundle_sidecars,
    write_snapshot_bundle,
)
from radar_v4.change_continuity import inspect_change_records
from radar_v4.checksum_sidecar import (
    sidecar_path,
    verify_checksum_sidecar,
    write_checksum_sidecar,
)
from radar_v4.document_kind import KNOWN_DOCUMENT_KINDS, KindDetection, detect_document_kind
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
from radar_v4.pack_describe import (
    PackDescription,
    PackIdentities,
    PackLayout,
    PackReadiness,
    ProvenanceMix,
    describe_pack,
    inspect_pack_layout,
    pack_identities,
    pack_readiness,
    provenance_mix,
)
from radar_v4.pack_inventory import PackFile, PackInventory, inventory_pack
from radar_v4.pack_manifest import (
    ManifestComparison,
    PackManifest,
    PackManifestError,
    compare_pack_manifests,
    verify_pack_manifest,
    write_pack_manifest,
)
from radar_v4.quarantine_journal import (
    read_quarantine_journal_file,
    serialize_quarantine_journal,
    write_quarantine_journal_file,
)
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
from radar_v4.ruler import (
    RulerMismatchError,
    declaration_ruler,
    require_ruler,
    ruler_checksum,
    rulers_match,
)
from radar_v4.ruler_file import (
    read_ruler_sidecar,
    serialize_ruler,
    write_ruler_sidecar,
)
from radar_v4.session_report import (
    read_session_report_file,
    serialize_admission_report,
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
from radar_v4.snapshot_inventory import SnapshotInventory, snapshot_inventory
from radar_v4.validation import ValidationIssue, ValidationResult, validate_envelope
from radar_v4.workshop_check import (
    CanonicalCheck,
    CodeLookup,
    DeterminismReport,
    JournalSummary,
    ReportBind,
    bind_report_to_snapshot,
    check_canonical_json,
    check_pack_determinism,
    lookup_reason_code,
    serialize_reason_catalog,
    summarize_journal,
    workshop_status,
)
from radar_v4.workshop_compare import (
    InventoryComparison,
    InventoryManifestCheck,
    ReportComparison,
    RulerComparison,
    compare_inventories,
    compare_rulers,
    compare_session_reports,
    inventory_vs_manifest,
)
from radar_v4.audit_bundle import (
    AuditBundle,
    AuditVerification,
    verify_audit_bundle,
    write_audit_bundle,
)
from radar_v4.evidence_chain import (
    ChainCheck,
    inspect_evidence_chain,
    reconcile_journal_to_pack,
    three_way_pack,
)
from radar_v4.integrity import (
    IntegrityCheck,
    check_claim_level,
    check_readiness_semantics,
    check_workshop_status_semantics,
    inspect_close_scale,
    inspect_gaps,
    inspect_locked_scope,
    inspect_payload_keys,
    inspect_timestamps,
    recompute_change_records,
    require_document_kind,
    scan_forbidden_fields,
    source_digest,
)
from radar_v4.pack_safety import PackSafety, inspect_pack_safety
from radar_v4.workshop_bounds import scan_package_network_imports, workshop_bounds
from radar_v4.catalog_audit import audit_document_kinds, audit_reason_catalog
from radar_v4.record_check import (
    inspect_ohlc,
    inspect_retrieval_order,
    inspect_ruler_fields,
    inspect_unexpected_files,
)
from radar_v4.roundtrip_check import check_export_roundtrip, check_replay_equality
from radar_v4.workshop_record import (
    inspect_question_lock,
    package_source_identity,
    workshop_stop_record,
)
from radar_v4.certify import certify_pack, command_catalog, self_test
from radar_v4.decimal_check import decimal_check_directory
from radar_v4.hygiene import pack_hygiene, scan_workshop_tree
from radar_v4.lineage import admission_vs_kept, write_lineage_record
from radar_v4.byte_check import byte_check
from radar_v4.freeze import workshop_freeze
from radar_v4.bind_check import freeze_status_bind
from radar_v4.journal_lock import journal_lock
from radar_v4.kind_lock import kind_lock
from radar_v4.name_lock import name_lock
from radar_v4.path_lock import path_lock
from radar_v4.record_eq import snapshot_count_bind
from radar_v4.disp_lock import disposition_lock
from radar_v4.audit_lock import audit_lock
from radar_v4.bundle_lock import bundle_lock
from radar_v4.chain_lock import chain_lock
from radar_v4.export_lock import export_lock
from radar_v4.inventory_lock import inventory_lock
from radar_v4.layout_lock import layout_lock
from radar_v4.digest_lock import digest_lock
from radar_v4.leftover_lock import leftover_lock
from radar_v4.safety_lock import safety_lock
from radar_v4.manifest_lock import manifest_lock
from radar_v4.report_lock import report_lock
from radar_v4.ruler_lock import pack_ruler_lock
from radar_v4.sidecar_lock import sidecar_lock
from radar_v4.snapshot_lock import snapshot_lock
from radar_v4.stamp import stamp_status_bind, workshop_stamp

__all__ = [
    "ALLOWED_PROVENANCE_CLASSES",
    "BaselineReport",
    "BundleVerification",
    "BundleWriteResult",
    "CanonicalCheck",
    "CloseToCloseChange",
    "CodeLookup",
    "DatasetDeclaration",
    "DatasetPackReport",
    "DatasetSnapshot",
    "DeclarationIntakeReport",
    "DeterminismReport",
    "InventoryComparison",
    "InventoryManifestCheck",
    "JournalSummary",
    "KindDetection",
    "KNOWN_DOCUMENT_KINDS",
    "SnapshotComparison",
    "LocalSessionResult",
    "ManifestComparison",
    "PackDescription",
    "PackFile",
    "PackIdentities",
    "PackInventory",
    "PackLayout",
    "PackReadiness",
    "ProvenanceMix",
    "ReportBind",
    "ReportComparison",
    "RulerComparison",
    "SnapshotInventory",
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
    "PackManifest",
    "PackManifestError",
    "RegistryFileError",
    "RulerMismatchError",
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
    "bind_report_to_snapshot",
    "check_canonical_json",
    "check_pack_determinism",
    "close_to_close_changes",
    "compare_inventories",
    "compare_pack_manifests",
    "compare_rulers",
    "compare_session_reports",
    "compare_snapshot_files",
    "compare_snapshots",
    "describe_pack",
    "detect_document_kind",
    "declaration_ruler",
    "export_snapshot_to_pack",
    "inspect_change_records",
    "inspect_pack_layout",
    "inspect_series",
    "inventory_pack",
    "inventory_vs_manifest",
    "intake_declaration_json",
    "intake_observation_json",
    "load_dataset_pack",
    "lookup_reason_code",
    "make_snapshot",
    "pack_identities",
    "pack_readiness",
    "provenance_mix",
    "read_quarantine_journal_file",
    "read_registry_file",
    "read_ruler_sidecar",
    "read_session_report_file",
    "read_snapshot_file",
    "require_ruler",
    "ruler_checksum",
    "rulers_match",
    "run_dataset_session",
    "run_session_from_pack",
    "run_session_from_snapshot",
    "run_session_from_snapshot_file",
    "serialize_admission_report",
    "serialize_local_session_report",
    "serialize_reason_catalog",
    "serialize_ruler",
    "serialize_quarantine_journal",
    "serialize_session_report",
    "sidecar_path",
    "snapshot_inventory",
    "summarize_journal",
    "workshop_status",
    "write_local_session_report_file",
    "write_session_report_file",
    "write_snapshot_file",
    "intake_envelopes",
    "intake_json_text",
    "load_fixture_pack",
    "validate_envelope",
    "validate_observation",
    "verify_checksum_sidecar",
    "verify_pack_manifest",
    "verify_snapshot",
    "verify_snapshot_bundle",
    "verify_snapshot_file",
    "write_bundle_sidecars",
    "write_checksum_sidecar",
    "write_pack_manifest",
    "write_quarantine_journal_file",
    "write_ruler_sidecar",
    "write_registry_file",
    "write_snapshot_bundle",
    "write_text_atomic",
    "AuditBundle",
    "AuditVerification",
    "ChainCheck",
    "IntegrityCheck",
    "PackSafety",
    "check_claim_level",
    "check_readiness_semantics",
    "check_workshop_status_semantics",
    "inspect_close_scale",
    "inspect_evidence_chain",
    "inspect_gaps",
    "inspect_locked_scope",
    "inspect_pack_safety",
    "inspect_payload_keys",
    "inspect_timestamps",
    "recompute_change_records",
    "reconcile_journal_to_pack",
    "require_document_kind",
    "scan_forbidden_fields",
    "scan_package_network_imports",
    "three_way_pack",
    "verify_audit_bundle",
    "workshop_bounds",
    "write_audit_bundle",
    "audit_document_kinds",
    "audit_reason_catalog",
    "check_export_roundtrip",
    "check_replay_equality",
    "inspect_ohlc",
    "inspect_question_lock",
    "inspect_retrieval_order",
    "inspect_ruler_fields",
    "inspect_unexpected_files",
    "package_source_identity",
    "workshop_stop_record",
    "admission_vs_kept",
    "audit_lock",
    "bundle_lock",
    "byte_check",
    "certify_pack",
    "chain_lock",
    "export_lock",
    "freeze_status_bind",
    "inventory_lock",
    "layout_lock",
    "digest_lock",
    "leftover_lock",
    "safety_lock",
    "source_digest",
    "disposition_lock",
    "journal_lock",
    "kind_lock",
    "manifest_lock",
    "name_lock",
    "pack_ruler_lock",
    "path_lock",
    "report_lock",
    "sidecar_lock",
    "snapshot_count_bind",
    "snapshot_lock",
    "stamp_status_bind",
    "workshop_stamp",
    "command_catalog",
    "decimal_check_directory",
    "pack_hygiene",
    "scan_workshop_tree",
    "self_test",
    "workshop_freeze",
    "write_lineage_record",
]
