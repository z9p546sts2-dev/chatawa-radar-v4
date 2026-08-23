"""Additional local inspect/compare commands. No vendor. No method."""

from __future__ import annotations

import argparse
import sys
from json import dumps, loads
from pathlib import Path

from radar_v4.audit_bundle import (
    AuditBundleError,
    verify_audit_bundle,
    write_audit_bundle,
)
from radar_v4.declaration_json import intake_declaration_json
from radar_v4.document_kind import detect_document_kind
from radar_v4.evidence_chain import (
    inspect_evidence_chain,
    reconcile_journal_to_pack,
    three_way_pack,
)
from radar_v4.integrity import (
    check_claim_level,
    check_readiness_semantics,
    inspect_close_scale,
    inspect_gaps,
    inspect_locked_scope,
    inspect_payload_keys,
    inspect_timestamps,
    recompute_change_records,
    recompute_from_snapshot,
    require_document_kind,
    scan_forbidden_fields,
)
from radar_v4.local_session import run_session_from_pack
from radar_v4.observation_json import intake_observation_json
from radar_v4.pack_describe import (
    describe_pack,
    inspect_pack_layout,
    pack_identities,
    pack_readiness,
    provenance_mix,
)
from radar_v4.pack_safety import inspect_pack_safety
from radar_v4.session_report import serialize_admission_report
from radar_v4.snapshot_files import SnapshotFileError, read_snapshot_file
from radar_v4.snapshot_inventory import snapshot_inventory
from radar_v4.catalog_audit import audit_document_kinds, audit_reason_catalog
from radar_v4.record_check import (
    describe_adjustment_policy,
    describe_close_zeros,
    inspect_file_modes,
    inspect_leftovers,
    inspect_ohlc,
    inspect_pack_urls,
    inspect_primary_metric,
    inspect_retrieval_order,
    inspect_ruler_fields,
    inspect_status_taxonomy,
    inspect_text_safety,
    inspect_unexpected_files,
    scan_percent_fields,
)
from radar_v4.roundtrip_check import check_export_roundtrip, check_replay_equality
from radar_v4.workshop_bounds import scan_package_network_imports, workshop_bounds
from radar_v4.certify import (
    certify_pack,
    command_catalog,
    compare_stops,
    fixture_label_check,
    name_vs_ruler,
    reserved_name_scan,
    self_test,
    utf16_scan,
    write_certify_record,
)
from radar_v4.decimal_check import decimal_check_directory
from radar_v4.hygiene import pack_hygiene, scan_python_source, scan_workshop_tree
from radar_v4.lineage import (
    admission_vs_kept,
    clock_skew_describe,
    snapshot_order_check,
    volume_describe,
    write_lineage_record,
)
from radar_v4.bind_check import (
    close_sign_describe,
    export_byte_check,
    freeze_status_bind,
    journal_code_catalog,
    retrieval_unique_describe,
    verify_byte_record,
    write_byte_record,
)
from radar_v4.byte_check import byte_check, claim_word_scan, count_check, filename_date_check
from radar_v4.journal_lock import (
    compare_journal_lock,
    journal_lock,
    journal_lock_determinism,
    verify_journal_record,
    write_journal_record,
)
from radar_v4.report_lock import (
    compare_report_lock,
    report_lock,
    report_lock_determinism,
    report_status_bind,
    verify_report_record,
    write_report_record,
)
from radar_v4.ruler_lock import (
    compare_ruler_lock,
    report_ruler_bind,
    ruler_lock_any,
    ruler_lock_determinism,
    verify_ruler_record,
    write_ruler_record,
)
from radar_v4.disp_lock import (
    compare_disposition_lock,
    disposition_lock,
    disposition_lock_determinism,
    disposition_status_bind,
    verify_disposition_record,
    write_disposition_record,
)
from radar_v4.audit_lock import (
    audit_lock,
    audit_lock_determinism,
    audit_status_bind,
    compare_audit_lock,
    verify_audit_record,
    write_audit_record,
)
from radar_v4.bundle_lock import (
    bundle_lock,
    bundle_lock_determinism,
    bundle_status_bind,
    compare_bundle_lock,
    verify_bundle_record,
    write_bundle_record,
)
from radar_v4.chain_lock import (
    chain_lock,
    chain_lock_determinism,
    chain_status_bind,
    compare_chain_lock,
    verify_chain_record,
    write_chain_record,
)
from radar_v4.inventory_lock import (
    compare_inventory_lock,
    inventory_lock,
    inventory_lock_determinism,
    inventory_status_bind,
    verify_inventory_record,
    write_inventory_record,
)
from radar_v4.layout_lock import (
    compare_layout_lock,
    layout_lock,
    layout_lock_determinism,
    layout_status_bind,
    verify_layout_record,
    write_layout_record,
)
from radar_v4.content_bind import (
    content_bind,
    content_bind_determinism,
    content_bind_status,
    verify_content_bind_record,
    write_content_bind_record,
)
from radar_v4.content_lock import (
    compare_content_lock,
    content_lock,
    content_lock_determinism,
    content_status_bind,
    verify_content_record,
    write_content_record,
)
from radar_v4.content_set import (
    compare_content_set,
    content_set,
    content_set_determinism,
    content_set_status,
    verify_content_set_record,
    write_content_set_record,
)
from radar_v4.copy_set import (
    compare_copy_set,
    copy_set,
    copy_set_determinism,
    copy_set_status,
    verify_copy_set_record,
    write_copy_set_record,
)
from radar_v4.digest_lock import (
    compare_digest_lock,
    digest_lock,
    digest_lock_determinism,
    digest_status_bind,
    verify_digest_record,
    write_digest_record,
)
from radar_v4.lock_bind import (
    bind_lock_records,
    lock_bind_determinism,
    lock_bind_status,
    verify_lock_bind_record,
    write_lock_bind_record,
)
from radar_v4.lock_set import (
    compare_lock_set,
    lock_set,
    lock_set_determinism,
    lock_set_status,
    verify_lock_set_record,
    write_lock_set_record,
)
from radar_v4.leftover_lock import (
    compare_leftover_lock,
    leftover_lock,
    leftover_lock_determinism,
    leftover_status_bind,
    verify_leftover_record,
    write_leftover_record,
)
from radar_v4.safety_lock import (
    compare_safety_lock,
    safety_lock,
    safety_lock_determinism,
    safety_status_bind,
    verify_safety_record,
    write_safety_record,
)
from radar_v4.export_lock import (
    compare_export_lock,
    export_lock,
    export_lock_determinism,
    export_status_bind,
    verify_export_record,
    write_export_record,
)
from radar_v4.manifest_lock import (
    compare_manifest_lock,
    manifest_lock,
    manifest_lock_determinism,
    manifest_status_bind,
    verify_manifest_record,
    write_manifest_record,
)
from radar_v4.sidecar_lock import (
    compare_sidecar_lock,
    sidecar_lock_any,
    sidecar_lock_determinism,
    sidecar_status_bind,
    verify_sidecar_record,
    write_sidecar_record,
)
from radar_v4.snapshot_lock import (
    compare_snapshot_lock,
    snapshot_lock_any,
    snapshot_lock_determinism,
    snapshot_status_bind,
    verify_snapshot_record,
    write_snapshot_record,
)
from radar_v4.kind_lock import kind_describe, kind_lock
from radar_v4.name_lock import name_lock
from radar_v4.path_lock import path_lock
from radar_v4.record_eq import (
    compare_name_lock,
    compare_path_lock,
    freeze_determinism,
    name_lock_determinism,
    package_identity_determinism,
    path_lock_determinism,
    snapshot_count_bind,
    verify_name_record,
    verify_path_record,
    write_name_record,
    write_path_record,
)
from radar_v4.stamp import (
    compare_kind_lock,
    compare_stamp,
    export_name_check,
    kind_lock_determinism,
    name_status_bind,
    stamp_determinism,
    stamp_status_bind,
    verify_kind_record,
    verify_stamp_record,
    workshop_stamp,
    write_kind_record,
    write_stamp_record,
)
from radar_v4.freeze import (
    certify_determinism,
    command_catalog_determinism,
    compare_certify,
    compare_freeze,
    compare_lineage,
    readme_unit_lock,
    self_test_determinism,
    verify_freeze_record,
    workshop_freeze,
    write_freeze_record,
)
from radar_v4.workshop_record import (
    inspect_question_lock,
    package_source_identity,
    read_disposition,
    workshop_stop_record,
    write_disposition,
)
from radar_v4.workshop_check import (
    bind_report_to_snapshot,
    check_canonical_json,
    check_pack_determinism,
    lookup_reason_code,
    serialize_reason_catalog,
    summarize_journal,
    workshop_status,
)
from radar_v4.workshop_compare import (
    compare_inventories,
    compare_rulers,
    compare_session_reports,
    inventory_vs_manifest,
)


def register_workshop_commands(sub: argparse._SubParsersAction) -> None:
    detect = sub.add_parser("detect-kind", help="identify a local JSON document kind")
    detect.add_argument("--path", required=True)

    show_declaration = sub.add_parser("show-declaration", help="print a declaration file")
    show_declaration.add_argument("--path", required=True)

    show_snapshot = sub.add_parser("show-snapshot", help="print a snapshot without re-running")
    show_snapshot.add_argument("--snapshot", required=True)

    show_observation = sub.add_parser("show-observation", help="print one observation file")
    show_observation.add_argument("--path", required=True)

    mix = sub.add_parser("provenance-mix", help="count provenance labels in a pack")
    mix.add_argument("--pack", required=True)

    admission = sub.add_parser("admission", help="admit a pack without measuring")
    admission.add_argument("--pack", required=True)

    compare_ruler = sub.add_parser("compare-rulers", help="compare two pack or snapshot rulers")
    compare_ruler.add_argument("--left", required=True)
    compare_ruler.add_argument("--right", required=True)

    compare_report = sub.add_parser("compare-reports", help="compare two session reports")
    compare_report.add_argument("--left", required=True)
    compare_report.add_argument("--right", required=True)

    journal_summary = sub.add_parser("journal-summary", help="count journal refusals by code")
    journal_summary.add_argument("--journal", required=True)

    report_bind = sub.add_parser("report-bind", help="bind a report checksum to a snapshot")
    report_bind.add_argument("--report", required=True)
    report_bind.add_argument("--snapshot", required=True)

    determinism = sub.add_parser("determinism", help="run the same pack twice and compare")
    determinism.add_argument("--pack", required=True)

    snap_inv = sub.add_parser("snapshot-inventory", help="list identities in a snapshot")
    snap_inv.add_argument("--snapshot", required=True)

    layout = sub.add_parser("pack-layout", help="check required pack files")
    layout.add_argument("--pack", required=True)

    canonical = sub.add_parser(
        "canonical-check",
        help="require exact sorted-key compact JSON plus one newline",
    )
    canonical.add_argument("--path", required=True)

    identities = sub.add_parser("pack-identities", help="list pack envelope identities")
    identities.add_argument("--pack", required=True)

    describe = sub.add_parser("pack-describe", help="describe a pack without measuring")
    describe.add_argument("--pack", required=True)

    code = sub.add_parser("code", help="look up one refusal or result code")
    code.add_argument("--name", required=True)

    compare_inv = sub.add_parser("compare-inventories", help="compare two pack inventories")
    compare_inv.add_argument("--left", required=True)
    compare_inv.add_argument("--right", required=True)

    inv_manifest = sub.add_parser(
        "inventory-manifest", help="compare inventory digests to a pack manifest"
    )
    inv_manifest.add_argument("--pack", required=True)

    sub.add_parser(
        "status",
        help="print workshop capability statement; does not measure a dataset",
    )

    readiness = sub.add_parser(
        "readiness",
        help="count declaration-admitted observations; not a measurement",
    )
    readiness.add_argument("--pack", required=True)

    claim = sub.add_parser(
        "claim-check",
        help="require MEASURED claim-level only on measured baselines",
    )
    claim.add_argument("--report", required=True)

    recompute = sub.add_parser(
        "recompute",
        help="recompute stored close-to-close differences",
    )
    recompute.add_argument("--report", required=True)
    recompute.add_argument("--snapshot", help="optional snapshot to recompute from")

    locked = sub.add_parser(
        "locked-scope",
        help="check the locked one-symbol daily question",
    )
    locked.add_argument("--pack", required=True)

    forbidden = sub.add_parser(
        "forbidden",
        help="refuse signal, score, threshold, or edge field names",
    )
    forbidden.add_argument("--path", required=True)

    gaps = sub.add_parser("gaps", help="list timestamp deltas without filling bars")
    gaps.add_argument("--pack", required=True)

    timestamps = sub.add_parser(
        "timestamps",
        help="require timezone offsets; file mtime is not market time",
    )
    timestamps.add_argument("--pack", required=True)

    safety = sub.add_parser(
        "pack-safety",
        help="refuse BOM, symlink, empty, nested, and non-UTF-8 pack files",
    )
    safety.add_argument("--pack", required=True)

    chain = sub.add_parser("chain", help="bind pack, snapshot, and report identities")
    chain.add_argument("--pack", required=True)
    chain.add_argument("--snapshot")
    chain.add_argument("--report")

    three = sub.add_parser(
        "three-way",
        help="compare filesystem, inventory, and manifest names",
    )
    three.add_argument("--pack", required=True)

    reconcile = sub.add_parser(
        "reconcile-journal",
        help="require journal codes to remain in current pack refusals",
    )
    reconcile.add_argument("--pack", required=True)
    reconcile.add_argument("--journal", required=True)

    write_audit = sub.add_parser(
        "write-audit",
        help="copy a local pack into an audit directory",
    )
    write_audit.add_argument("--pack", required=True)
    write_audit.add_argument("--out", required=True)

    verify_audit = sub.add_parser("verify-audit", help="verify a local audit copy")
    verify_audit.add_argument("--dir", required=True)

    close_scale = sub.add_parser(
        "close-scale",
        help="describe close decimal places; not a threshold",
    )
    close_scale.add_argument("--pack", required=True)

    sub.add_parser("bounds", help="print authorized workshop bounds; does not measure")
    sub.add_parser("no-network", help="scan the package for vendor-style imports")

    kind_required = sub.add_parser(
        "require-kind",
        help="require document_kind or a known inferred kind",
    )
    kind_required.add_argument("--path", required=True)

    payload_keys = sub.add_parser(
        "payload-keys",
        help="flag extra observation payload keys",
    )
    payload_keys.add_argument("--pack", required=True)

    readiness_check = sub.add_parser(
        "readiness-check",
        help="refuse readiness that claims enough without two admitted observations",
    )
    readiness_check.add_argument("--pack", required=True)

    ohlc = sub.add_parser("ohlc-check", help="report high/low/close contradictions")
    ohlc.add_argument("--pack", required=True)

    retrieval = sub.add_parser(
        "retrieval-order",
        help="flag retrieval timestamps that precede market timestamps",
    )
    retrieval.add_argument("--pack", required=True)

    ruler_fields = sub.add_parser(
        "ruler-fields",
        help="require provider, timezone, and transformation to match the declaration",
    )
    ruler_fields.add_argument("--pack", required=True)

    percent = sub.add_parser(
        "percent-fields",
        help="refuse percent/return field names",
    )
    percent.add_argument("--path", required=True)

    unexpected = sub.add_parser(
        "unexpected-files",
        help="refuse csv/parquet/xlsx files inside a pack",
    )
    unexpected.add_argument("--pack", required=True)

    leftovers = sub.add_parser("leftovers", help="refuse tmp files and orphan sidecars")
    leftovers.add_argument("--pack", required=True)

    text_safety = sub.add_parser(
        "text-safety",
        help="refuse CRLF, control bytes, and duplicate JSON keys",
    )
    text_safety.add_argument("--path", required=True)

    modes = sub.add_parser("file-modes", help="refuse executable bits on pack files")
    modes.add_argument("--pack", required=True)

    urls = sub.add_parser("url-scan", help="refuse http(s) URLs inside pack JSON")
    urls.add_argument("--pack", required=True)

    zeros = sub.add_parser("close-zeros", help="count zero closes; not a threshold")
    zeros.add_argument("--pack", required=True)

    adjustment = sub.add_parser(
        "adjustment",
        help="echo the declared adjustment policy; does not invent actions",
    )
    adjustment.add_argument("--pack", required=True)

    metric = sub.add_parser("primary-metric", help="require close-to-close difference")
    metric.add_argument("--pack", required=True)

    taxonomy = sub.add_parser(
        "taxonomy",
        help="allow only locked Phase 5 result statuses",
    )
    taxonomy.add_argument("--report", required=True)

    replay_eq = sub.add_parser("replay-eq", help="replay a pack snapshot and compare changes")
    replay_eq.add_argument("--pack", required=True)

    export_rt = sub.add_parser(
        "export-roundtrip",
        help="export a snapshot to a new pack and compare identity",
    )
    export_rt.add_argument("--pack", required=True)
    export_rt.add_argument("--out", required=True)

    sub.add_parser("catalog-audit", help="compare CODE literals to the reason catalog")
    sub.add_parser("kind-audit", help="compare document_kind literals to the kind catalog")
    sub.add_parser("package-identity", help="hash local package files; not market evidence")

    question = sub.add_parser(
        "question-lock",
        help="bind a pack declaration to the locked Phase 5 question",
    )
    question.add_argument("--pack", required=True)

    write_disp = sub.add_parser(
        "write-disposition",
        help="write UNREVIEWED, ACKNOWLEDGED, or NEEDS_REVIEW; not a trade",
    )
    write_disp.add_argument("--out", required=True)
    write_disp.add_argument("--disposition", required=True)
    write_disp.add_argument("--note")
    write_disp.add_argument("--replace", action="store_true")

    show_disp = sub.add_parser("show-disposition", help="read a human disposition file")
    show_disp.add_argument("--path", required=True)

    sub.add_parser("stop-record", help="print a workshop capability freeze; does not measure")

    hygiene = sub.add_parser(
        "hygiene-scan",
        help="refuse eval/exec/subprocess/socket/os.system names in workshop Python",
    )
    hygiene.add_argument("--path", help="optional single Python file; default is radar_v4")

    pack_hyg = sub.add_parser(
        "pack-hygiene",
        help="hidden files, NFC names, duplicate digests, checksums, identity uniqueness",
    )
    pack_hyg.add_argument("--pack", required=True)

    decimal = sub.add_parser(
        "decimal-check",
        help="require close values to be finite decimal strings",
    )
    decimal.add_argument("--pack", required=True)

    lineage = sub.add_parser(
        "lineage",
        help="describe admission versus kept counts; not a quality score",
    )
    lineage.add_argument("--pack", required=True)

    write_lineage = sub.add_parser(
        "write-lineage",
        help="write a local lineage description; not market evidence",
    )
    write_lineage.add_argument("--pack", required=True)
    write_lineage.add_argument("--out", required=True)
    write_lineage.add_argument("--replace", action="store_true")

    volume = sub.add_parser(
        "volume-describe",
        help="describe unused volume fields; not a signal",
    )
    volume.add_argument("--pack", required=True)

    reserved = sub.add_parser(
        "reserved-names",
        help="refuse live/trade/edge filenames in a pack",
    )
    reserved.add_argument("--pack", required=True)

    name_ruler = sub.add_parser(
        "name-vs-ruler",
        help="require observation symbols to match the declaration universe",
    )
    name_ruler.add_argument("--pack", required=True)

    encoding = sub.add_parser(
        "text-encoding",
        help="refuse UTF-16 BOM in pack files",
    )
    encoding.add_argument("--pack", required=True)

    fixture = sub.add_parser(
        "fixture-label",
        help="require a SYNTHETIC fixture label",
    )
    fixture.add_argument("--pack", required=True)

    stops = sub.add_parser(
        "compare-stops",
        help="compare two stop records; same freeze is not a method",
    )
    stops.add_argument("--left", required=True)
    stops.add_argument("--right", required=True)

    snap_order = sub.add_parser(
        "snapshot-order",
        help="require snapshot observation timestamps to be sorted",
    )
    snap_order.add_argument("--snapshot", required=True)

    span = sub.add_parser(
        "span-describe",
        help="describe first-to-last timestamp span; not a trading clock",
    )
    span.add_argument("--pack", required=True)

    certify = sub.add_parser(
        "certify",
        help="compose local pack checks; passing is not market evidence",
    )
    certify.add_argument("--pack", required=True)

    write_cert = sub.add_parser(
        "write-certify",
        help="write a local certify record; not a method",
    )
    write_cert.add_argument("--pack", required=True)
    write_cert.add_argument("--out", required=True)
    write_cert.add_argument("--replace", action="store_true")

    sub.add_parser("commands", help="list local CLI commands; a command is not a method")
    sub.add_parser("self-test", help="check local workshop invariants; not market evidence")

    byte = sub.add_parser(
        "byte-check",
        help="refuse trailing whitespace, null bytes, shebang, tabs, and count mismatch",
    )
    byte.add_argument("--pack", required=True)

    filename = sub.add_parser(
        "filename-date",
        help="require obs_YYYY-MM-DD filenames to match admitted market dates",
    )
    filename.add_argument("--pack", required=True)

    counts = sub.add_parser(
        "count-check",
        help="require observation file count to match admitted count",
    )
    counts.add_argument("--pack", required=True)

    claim_words = sub.add_parser(
        "claim-words",
        help="refuse edge/buy/sell/paper values in a JSON document",
    )
    claim_words.add_argument("--path", required=True)

    cmp_cert = sub.add_parser(
        "compare-certify",
        help="compare certify results of two packs; equality is not a method",
    )
    cmp_cert.add_argument("--left", required=True)
    cmp_cert.add_argument("--right", required=True)

    cmp_lineage = sub.add_parser(
        "compare-lineage",
        help="compare admission lineage of two packs",
    )
    cmp_lineage.add_argument("--left", required=True)
    cmp_lineage.add_argument("--right", required=True)

    cert_eq = sub.add_parser(
        "certify-eq",
        help="certify the same pack twice; equality is not market evidence",
    )
    cert_eq.add_argument("--pack", required=True)

    sub.add_parser("self-test-eq", help="run self-test twice; equality is not a result")
    sub.add_parser("commands-eq", help="list commands twice; a command is not a method")
    sub.add_parser("readme-lock", help="require README to name the locked highest unit")

    freeze = sub.add_parser(
        "freeze",
        help="print a workshop capability freeze; does not measure",
    )
    freeze.add_argument("--pack", help="optional pack for certify/byte checks")

    write_freeze = sub.add_parser(
        "write-freeze",
        help="write a local freeze record; not a method",
    )
    write_freeze.add_argument("--out", required=True)
    write_freeze.add_argument("--pack")
    write_freeze.add_argument("--replace", action="store_true")

    verify_freeze = sub.add_parser(
        "verify-freeze",
        help="verify a local freeze record; not market evidence",
    )
    verify_freeze.add_argument("--path", required=True)

    cmp_freeze = sub.add_parser(
        "compare-freeze",
        help="compare two freeze records; same freeze is not a method",
    )
    cmp_freeze.add_argument("--left", required=True)
    cmp_freeze.add_argument("--right", required=True)

    pathlock = sub.add_parser(
        "path-lock",
        help="refuse backup leftovers, non-ASCII names, and spaces in filenames",
    )
    pathlock.add_argument("--pack", required=True)

    journal_codes = sub.add_parser(
        "journal-codes",
        help="require journal codes to remain in the refusal catalog",
    )
    journal_codes.add_argument("--journal", required=True)

    freeze_bind = sub.add_parser(
        "freeze-bind",
        help="bind freeze highest-unit to status; not a measurement",
    )
    freeze_bind.add_argument("--pack", help="optional pack for freeze compose")

    write_byte = sub.add_parser(
        "write-byte",
        help="write a local byte-check record; not market evidence",
    )
    write_byte.add_argument("--pack", required=True)
    write_byte.add_argument("--out", required=True)
    write_byte.add_argument("--replace", action="store_true")

    verify_byte = sub.add_parser(
        "verify-byte",
        help="verify a local byte-check record",
    )
    verify_byte.add_argument("--path", required=True)

    close_sign = sub.add_parser(
        "close-sign",
        help="describe negative and zero closes; not a threshold",
    )
    close_sign.add_argument("--pack", required=True)

    retrieval_unique = sub.add_parser(
        "retrieval-unique",
        help="describe duplicate retrieval timestamps; not a trading clock",
    )
    retrieval_unique.add_argument("--pack", required=True)

    export_byte = sub.add_parser(
        "export-byte",
        help="export a snapshot and run portable byte checks",
    )
    export_byte.add_argument("--pack", required=True)
    export_byte.add_argument("--out", required=True)

    namelock = sub.add_parser(
        "name-lock",
        help="refuse reserved stems, leading hyphens, double .json, and empty packs",
    )
    namelock.add_argument("--pack", required=True)

    path_eq = sub.add_parser(
        "path-lock-eq",
        help="run path-lock twice; equality is not a method",
    )
    path_eq.add_argument("--pack", required=True)

    name_eq = sub.add_parser(
        "name-lock-eq",
        help="run name-lock twice; equality is not market evidence",
    )
    name_eq.add_argument("--pack", required=True)

    freeze_eq = sub.add_parser(
        "freeze-eq",
        help="run freeze twice; equality is not a research result",
    )
    freeze_eq.add_argument("--pack", help="optional pack for freeze compose")

    sub.add_parser(
        "package-eq",
        help="hash package identity twice; software identity only",
    )

    cmp_path = sub.add_parser(
        "compare-path-lock",
        help="compare path-lock of two packs",
    )
    cmp_path.add_argument("--left", required=True)
    cmp_path.add_argument("--right", required=True)

    snap_count = sub.add_parser(
        "snapshot-count",
        help="require snapshot kept count to match admitted count",
    )
    snap_count.add_argument("--pack", required=True)

    write_path = sub.add_parser(
        "write-path",
        help="write a local path-lock record; not market evidence",
    )
    write_path.add_argument("--pack", required=True)
    write_path.add_argument("--out", required=True)
    write_path.add_argument("--replace", action="store_true")

    verify_path = sub.add_parser(
        "verify-path",
        help="verify a local path-lock record",
    )
    verify_path.add_argument("--path", required=True)

    write_name = sub.add_parser(
        "write-name",
        help="write a local name-lock record; not a method",
    )
    write_name.add_argument("--pack", required=True)
    write_name.add_argument("--out", required=True)
    write_name.add_argument("--replace", action="store_true")

    verify_name = sub.add_parser(
        "verify-name",
        help="verify a local name-lock record",
    )
    verify_name.add_argument("--path", required=True)

    cmp_name = sub.add_parser(
        "compare-name-lock",
        help="compare name-lock of two packs",
    )
    cmp_name.add_argument("--left", required=True)
    cmp_name.add_argument("--right", required=True)

    kindlock = sub.add_parser(
        "kind-lock",
        help="refuse unlabeled, unknown, or unreadable JSON kinds",
    )
    kindlock.add_argument("--pack", required=True)

    kinddesc = sub.add_parser(
        "kind-describe",
        help="describe JSON document kinds; not a score",
    )
    kinddesc.add_argument("--pack", required=True)

    stamp = sub.add_parser(
        "stamp",
        help="compose name-lock, kind-lock, and snapshot-count; not a result",
    )
    stamp.add_argument("--pack", required=True)

    stamp_eq = sub.add_parser(
        "stamp-eq",
        help="run stamp twice; equality is not a method",
    )
    stamp_eq.add_argument("--pack", required=True)

    cmp_stamp = sub.add_parser(
        "compare-stamp",
        help="compare workshop stamps of two packs",
    )
    cmp_stamp.add_argument("--left", required=True)
    cmp_stamp.add_argument("--right", required=True)

    write_stamp = sub.add_parser(
        "write-stamp",
        help="write a local stamp record; not market evidence",
    )
    write_stamp.add_argument("--pack", required=True)
    write_stamp.add_argument("--out", required=True)
    write_stamp.add_argument("--replace", action="store_true")

    verify_stamp = sub.add_parser(
        "verify-stamp",
        help="verify a local stamp record",
    )
    verify_stamp.add_argument("--path", required=True)

    name_bind = sub.add_parser(
        "name-bind",
        help="bind name-lock to status highest-unit; not a measurement",
    )
    name_bind.add_argument("--pack", required=True)

    export_name = sub.add_parser(
        "export-name",
        help="export a snapshot and run portable name/kind checks",
    )
    export_name.add_argument("--pack", required=True)
    export_name.add_argument("--out", required=True)

    journallock = sub.add_parser(
        "journal-lock",
        help="lock journal kind, entries, sources, and catalog codes",
    )
    journallock.add_argument("--journal", required=True)

    journal_eq = sub.add_parser(
        "journal-eq",
        help="run journal-lock twice; equality is not a score",
    )
    journal_eq.add_argument("--journal", required=True)

    cmp_journal = sub.add_parser(
        "compare-journal-lock",
        help="compare journal-lock of two journals",
    )
    cmp_journal.add_argument("--left", required=True)
    cmp_journal.add_argument("--right", required=True)

    write_journal = sub.add_parser(
        "write-journal",
        help="write a local journal-lock record; not a method",
    )
    write_journal.add_argument("--journal", required=True)
    write_journal.add_argument("--out", required=True)
    write_journal.add_argument("--replace", action="store_true")

    verify_journal = sub.add_parser(
        "verify-journal",
        help="verify a local journal-lock record",
    )
    verify_journal.add_argument("--path", required=True)

    kind_eq = sub.add_parser(
        "kind-lock-eq",
        help="run kind-lock twice; equality is not a taxonomy score",
    )
    kind_eq.add_argument("--pack", required=True)

    cmp_kind = sub.add_parser(
        "compare-kind-lock",
        help="compare kind-lock of two packs",
    )
    cmp_kind.add_argument("--left", required=True)
    cmp_kind.add_argument("--right", required=True)

    write_kind = sub.add_parser(
        "write-kind",
        help="write a local kind-lock record; not market evidence",
    )
    write_kind.add_argument("--pack", required=True)
    write_kind.add_argument("--out", required=True)
    write_kind.add_argument("--replace", action="store_true")

    verify_kind = sub.add_parser(
        "verify-kind",
        help="verify a local kind-lock record",
    )
    verify_kind.add_argument("--path", required=True)

    stamp_bind = sub.add_parser(
        "stamp-bind",
        help="bind stamp to status highest-unit; not a measurement",
    )
    stamp_bind.add_argument("--pack", required=True)

    reportlock = sub.add_parser(
        "report-lock",
        help="lock session-report kind, checksum, and measured field",
    )
    reportlock.add_argument("--report", required=True)

    report_eq = sub.add_parser(
        "report-eq",
        help="run report-lock twice; equality is not a method",
    )
    report_eq.add_argument("--report", required=True)

    cmp_report_lock = sub.add_parser(
        "compare-report-lock",
        help="compare report-lock of two reports",
    )
    cmp_report_lock.add_argument("--left", required=True)
    cmp_report_lock.add_argument("--right", required=True)

    write_report = sub.add_parser(
        "write-report",
        help="write a local report-lock record; not a measurement",
    )
    write_report.add_argument("--report", required=True)
    write_report.add_argument("--out", required=True)
    write_report.add_argument("--replace", action="store_true")

    verify_report = sub.add_parser(
        "verify-report",
        help="verify a local report-lock record",
    )
    verify_report.add_argument("--path", required=True)

    rulerlock = sub.add_parser(
        "ruler-lock",
        help="lock a ruler sidecar or pack-derived ruler; not a calendar",
    )
    rulerlock.add_argument("--pack")
    rulerlock.add_argument("--ruler")

    ruler_eq = sub.add_parser(
        "ruler-eq",
        help="run ruler-lock twice; equality is not a method",
    )
    ruler_eq.add_argument("--pack")
    ruler_eq.add_argument("--ruler")

    cmp_ruler_lock = sub.add_parser(
        "compare-ruler-lock",
        help="compare ruler-lock of two packs or ruler files",
    )
    cmp_ruler_lock.add_argument("--left", required=True)
    cmp_ruler_lock.add_argument("--right", required=True)

    write_ruler = sub.add_parser(
        "write-ruler",
        help="write a local ruler-lock record; not a calendar",
    )
    write_ruler.add_argument("--pack")
    write_ruler.add_argument("--ruler")
    write_ruler.add_argument("--out", required=True)
    write_ruler.add_argument("--replace", action="store_true")

    verify_ruler = sub.add_parser(
        "verify-ruler",
        help="verify a local ruler-lock record",
    )
    verify_ruler.add_argument("--path", required=True)

    report_ruler = sub.add_parser(
        "report-ruler",
        help="bind a report ruler checksum to a pack declaration",
    )
    report_ruler.add_argument("--report", required=True)
    report_ruler.add_argument("--pack", required=True)

    report_status = sub.add_parser(
        "report-status",
        help="bind report-lock to status highest-unit; not a measurement",
    )
    report_status.add_argument("--report", required=True)

    snaplock = sub.add_parser(
        "snapshot-lock",
        help="lock snapshot shape, rows, and FIXTURE/SYNTHETIC provenance",
    )
    snaplock.add_argument("--pack")
    snaplock.add_argument("--snapshot")

    snap_eq = sub.add_parser(
        "snapshot-eq",
        help="run snapshot-lock twice; equality is not a method",
    )
    snap_eq.add_argument("--pack")
    snap_eq.add_argument("--snapshot")

    cmp_snap = sub.add_parser(
        "compare-snapshot-lock",
        help="compare snapshot-lock of two packs or snapshot files",
    )
    cmp_snap.add_argument("--left", required=True)
    cmp_snap.add_argument("--right", required=True)

    write_snap = sub.add_parser(
        "write-snap",
        help="write a local snapshot-lock record; not market evidence",
    )
    write_snap.add_argument("--pack")
    write_snap.add_argument("--snapshot")
    write_snap.add_argument("--out", required=True)
    write_snap.add_argument("--replace", action="store_true")

    verify_snap = sub.add_parser(
        "verify-snap",
        help="verify a local snapshot-lock record",
    )
    verify_snap.add_argument("--path", required=True)

    snap_status = sub.add_parser(
        "snapshot-status",
        help="bind snapshot-lock to status highest-unit; not a measurement",
    )
    snap_status.add_argument("--pack")
    snap_status.add_argument("--snapshot")

    displock = sub.add_parser(
        "disp-lock",
        help="lock a human disposition; not a trade approval",
    )
    displock.add_argument("--path", required=True)

    disp_eq = sub.add_parser(
        "disp-eq",
        help="run disp-lock twice; equality is not a ranking",
    )
    disp_eq.add_argument("--path", required=True)

    cmp_disp = sub.add_parser(
        "compare-disp-lock",
        help="compare disposition-lock of two files",
    )
    cmp_disp.add_argument("--left", required=True)
    cmp_disp.add_argument("--right", required=True)

    write_disp_lock = sub.add_parser(
        "write-disp-lock",
        help="write a local disposition-lock record; not a trade approval",
    )
    write_disp_lock.add_argument("--path", required=True)
    write_disp_lock.add_argument("--out", required=True)
    write_disp_lock.add_argument("--replace", action="store_true")

    verify_disp = sub.add_parser(
        "verify-disp",
        help="verify a local disposition-lock record",
    )
    verify_disp.add_argument("--path", required=True)

    disp_status = sub.add_parser(
        "disp-status",
        help="bind disposition-lock to status highest-unit; not a measurement",
    )
    disp_status.add_argument("--path", required=True)

    manifest_lock_cmd = sub.add_parser(
        "manifest-lock",
        help="lock a pack manifest; not market evidence",
    )
    manifest_lock_cmd.add_argument("--pack", required=True)

    manifest_eq = sub.add_parser(
        "manifest-eq",
        help="run manifest-lock twice; equality is not a method",
    )
    manifest_eq.add_argument("--pack", required=True)

    cmp_manifest = sub.add_parser(
        "compare-manifest-lock",
        help="compare manifest-lock of two packs or files",
    )
    cmp_manifest.add_argument("--left", required=True)
    cmp_manifest.add_argument("--right", required=True)

    write_manifest = sub.add_parser(
        "write-manifest",
        help="write a local pack-manifest lock record; not market evidence",
    )
    write_manifest.add_argument("--pack", required=True)
    write_manifest.add_argument("--out", required=True)
    write_manifest.add_argument("--replace", action="store_true")

    verify_manifest = sub.add_parser(
        "verify-manifest",
        help="verify a local pack-manifest lock record",
    )
    verify_manifest.add_argument("--path", required=True)

    manifest_status = sub.add_parser(
        "manifest-status",
        help="bind manifest-lock to status highest-unit; not a measurement",
    )
    manifest_status.add_argument("--pack", required=True)

    sidecar_lock_cmd = sub.add_parser(
        "sidecar-lock",
        help="lock a checksum sidecar; not a repair",
    )
    sidecar_lock_cmd.add_argument("--path")
    sidecar_lock_cmd.add_argument("--snapshot")

    sidecar_eq = sub.add_parser(
        "sidecar-eq",
        help="run sidecar-lock twice; equality is not a method",
    )
    sidecar_eq.add_argument("--path")
    sidecar_eq.add_argument("--snapshot")

    cmp_sidecar = sub.add_parser(
        "compare-sidecar-lock",
        help="compare sidecar-lock of two .sha256 files",
    )
    cmp_sidecar.add_argument("--left", required=True)
    cmp_sidecar.add_argument("--right", required=True)

    write_sidecar = sub.add_parser(
        "write-sidecar-lock",
        help="write a local checksum-sidecar lock record; not a repair",
    )
    write_sidecar.add_argument("--path")
    write_sidecar.add_argument("--snapshot")
    write_sidecar.add_argument("--out", required=True)
    write_sidecar.add_argument("--replace", action="store_true")

    verify_sidecar = sub.add_parser(
        "verify-sidecar",
        help="verify a local checksum-sidecar lock record",
    )
    verify_sidecar.add_argument("--path", required=True)

    sidecar_status = sub.add_parser(
        "sidecar-status",
        help="bind sidecar-lock to status highest-unit; not a measurement",
    )
    sidecar_status.add_argument("--path")
    sidecar_status.add_argument("--snapshot")

    bundle_lock_cmd = sub.add_parser(
        "bundle-lock",
        help="lock a snapshot bundle with sidecar and ruler; not market evidence",
    )
    bundle_lock_cmd.add_argument("--snapshot", required=True)

    bundle_eq = sub.add_parser(
        "bundle-eq",
        help="run bundle-lock twice; equality is not a method",
    )
    bundle_eq.add_argument("--snapshot", required=True)

    cmp_bundle = sub.add_parser(
        "compare-bundle-lock",
        help="compare bundle-lock of two snapshots",
    )
    cmp_bundle.add_argument("--left", required=True)
    cmp_bundle.add_argument("--right", required=True)

    write_bundle_lock = sub.add_parser(
        "write-bundle-lock",
        help="write a local bundle-lock record; not market evidence",
    )
    write_bundle_lock.add_argument("--snapshot", required=True)
    write_bundle_lock.add_argument("--out", required=True)
    write_bundle_lock.add_argument("--replace", action="store_true")

    verify_bundle = sub.add_parser(
        "verify-bundle",
        help="verify a local bundle-lock record",
    )
    verify_bundle.add_argument("--path", required=True)

    bundle_status = sub.add_parser(
        "bundle-status",
        help="bind bundle-lock to status highest-unit; not a measurement",
    )
    bundle_status.add_argument("--snapshot", required=True)

    export_lock_cmd = sub.add_parser(
        "export-lock",
        help="lock a portable FIXTURE/SYNTHETIC pack; not market evidence",
    )
    export_lock_cmd.add_argument("--pack", required=True)

    export_eq = sub.add_parser(
        "export-eq",
        help="run export-lock twice; equality is not a method",
    )
    export_eq.add_argument("--pack", required=True)

    cmp_export = sub.add_parser(
        "compare-export-lock",
        help="compare export-lock of two packs",
    )
    cmp_export.add_argument("--left", required=True)
    cmp_export.add_argument("--right", required=True)

    write_export = sub.add_parser(
        "write-export-lock",
        help="write a local export-lock record; not market evidence",
    )
    write_export.add_argument("--pack", required=True)
    write_export.add_argument("--out", required=True)
    write_export.add_argument("--replace", action="store_true")

    verify_export = sub.add_parser(
        "verify-export",
        help="verify a local export-lock record",
    )
    verify_export.add_argument("--path", required=True)

    export_status = sub.add_parser(
        "export-status",
        help="bind export-lock to status highest-unit; not a measurement",
    )
    export_status.add_argument("--pack", required=True)

    audit_lock_cmd = sub.add_parser(
        "audit-lock",
        help="lock a local audit copy; not market evidence",
    )
    audit_lock_cmd.add_argument("--path", required=True)

    audit_eq = sub.add_parser(
        "audit-eq",
        help="run audit-lock twice; equality is not a method",
    )
    audit_eq.add_argument("--path", required=True)

    cmp_audit = sub.add_parser(
        "compare-audit-lock",
        help="compare audit-lock of two audit copies",
    )
    cmp_audit.add_argument("--left", required=True)
    cmp_audit.add_argument("--right", required=True)

    write_audit_lock = sub.add_parser(
        "write-audit-lock",
        help="write a local audit-lock record; not market evidence",
    )
    write_audit_lock.add_argument("--path", required=True)
    write_audit_lock.add_argument("--out", required=True)
    write_audit_lock.add_argument("--replace", action="store_true")

    verify_audit_lock = sub.add_parser(
        "verify-audit-lock",
        help="verify a local audit-lock record",
    )
    verify_audit_lock.add_argument("--path", required=True)

    audit_status = sub.add_parser(
        "audit-status",
        help="bind audit-lock to status highest-unit; not a measurement",
    )
    audit_status.add_argument("--path", required=True)

    chain_lock_cmd = sub.add_parser(
        "chain-lock",
        help="lock pack filesystem/inventory/manifest identity; not a method",
    )
    chain_lock_cmd.add_argument("--pack", required=True)

    chain_eq = sub.add_parser(
        "chain-eq",
        help="run chain-lock twice; equality is not a method",
    )
    chain_eq.add_argument("--pack", required=True)

    cmp_chain = sub.add_parser(
        "compare-chain-lock",
        help="compare chain-lock of two packs",
    )
    cmp_chain.add_argument("--left", required=True)
    cmp_chain.add_argument("--right", required=True)

    write_chain = sub.add_parser(
        "write-chain-lock",
        help="write a local chain-lock record; not a method",
    )
    write_chain.add_argument("--pack", required=True)
    write_chain.add_argument("--out", required=True)
    write_chain.add_argument("--replace", action="store_true")

    verify_chain = sub.add_parser(
        "verify-chain",
        help="verify a local chain-lock record",
    )
    verify_chain.add_argument("--path", required=True)

    chain_status = sub.add_parser(
        "chain-status",
        help="bind chain-lock to status highest-unit; not a measurement",
    )
    chain_status.add_argument("--pack", required=True)

    inventory_lock_cmd = sub.add_parser(
        "inventory-lock",
        help="lock pack inventory roles; not a measurement",
    )
    inventory_lock_cmd.add_argument("--pack", required=True)

    inventory_eq = sub.add_parser(
        "inventory-eq",
        help="run inventory-lock twice; equality is not a method",
    )
    inventory_eq.add_argument("--pack", required=True)

    cmp_inventory = sub.add_parser(
        "compare-inventory-lock",
        help="compare inventory-lock of two packs",
    )
    cmp_inventory.add_argument("--left", required=True)
    cmp_inventory.add_argument("--right", required=True)

    write_inventory = sub.add_parser(
        "write-inventory-lock",
        help="write a local inventory-lock record; not market evidence",
    )
    write_inventory.add_argument("--pack", required=True)
    write_inventory.add_argument("--out", required=True)
    write_inventory.add_argument("--replace", action="store_true")

    verify_inventory = sub.add_parser(
        "verify-inventory",
        help="verify a local inventory-lock record",
    )
    verify_inventory.add_argument("--path", required=True)

    inventory_status = sub.add_parser(
        "inventory-status",
        help="bind inventory-lock to status highest-unit; not a measurement",
    )
    inventory_status.add_argument("--pack", required=True)

    layout_lock_cmd = sub.add_parser(
        "layout-lock",
        help="lock pack declaration/observations/manifest layout; not a method",
    )
    layout_lock_cmd.add_argument("--pack", required=True)

    layout_eq = sub.add_parser(
        "layout-eq",
        help="run layout-lock twice; equality is not a method",
    )
    layout_eq.add_argument("--pack", required=True)

    cmp_layout = sub.add_parser(
        "compare-layout-lock",
        help="compare layout-lock of two packs",
    )
    cmp_layout.add_argument("--left", required=True)
    cmp_layout.add_argument("--right", required=True)

    write_layout = sub.add_parser(
        "write-layout-lock",
        help="write a local layout-lock record; not market evidence",
    )
    write_layout.add_argument("--pack", required=True)
    write_layout.add_argument("--out", required=True)
    write_layout.add_argument("--replace", action="store_true")

    verify_layout = sub.add_parser(
        "verify-layout",
        help="verify a local layout-lock record",
    )
    verify_layout.add_argument("--path", required=True)

    layout_status = sub.add_parser(
        "layout-status",
        help="bind layout-lock to status highest-unit; not a measurement",
    )
    layout_status.add_argument("--pack", required=True)

    safety_lock_cmd = sub.add_parser(
        "safety-lock",
        help="lock pack safety inspectability; not a measurement",
    )
    safety_lock_cmd.add_argument("--pack", required=True)

    safety_eq = sub.add_parser(
        "safety-eq",
        help="repeat safety-lock; equality is not a method",
    )
    safety_eq.add_argument("--pack", required=True)

    cmp_safety = sub.add_parser(
        "compare-safety-lock",
        help="compare safety-lock of two packs",
    )
    cmp_safety.add_argument("--left", required=True)
    cmp_safety.add_argument("--right", required=True)

    write_safety = sub.add_parser(
        "write-safety-lock",
        help="write a local safety-lock record; not market evidence",
    )
    write_safety.add_argument("--pack", required=True)
    write_safety.add_argument("--out", required=True)
    write_safety.add_argument("--replace", action="store_true")

    verify_safety = sub.add_parser(
        "verify-safety",
        help="verify a local safety-lock record",
    )
    verify_safety.add_argument("--path", required=True)

    safety_status = sub.add_parser(
        "safety-status",
        help="bind safety-lock to status highest-unit; not a measurement",
    )
    safety_status.add_argument("--pack", required=True)

    leftover_lock_cmd = sub.add_parser(
        "leftover-lock",
        help="lock leftover inspectability; not a method",
    )
    leftover_lock_cmd.add_argument("--pack", required=True)

    leftover_eq = sub.add_parser(
        "leftover-eq",
        help="repeat leftover-lock; equality is not a method",
    )
    leftover_eq.add_argument("--pack", required=True)

    cmp_leftover = sub.add_parser(
        "compare-leftover-lock",
        help="compare leftover-lock of two packs",
    )
    cmp_leftover.add_argument("--left", required=True)
    cmp_leftover.add_argument("--right", required=True)

    write_leftover = sub.add_parser(
        "write-leftover-lock",
        help="write a local leftover-lock record; not market evidence",
    )
    write_leftover.add_argument("--pack", required=True)
    write_leftover.add_argument("--out", required=True)
    write_leftover.add_argument("--replace", action="store_true")

    verify_leftover = sub.add_parser(
        "verify-leftover",
        help="verify a local leftover-lock record",
    )
    verify_leftover.add_argument("--path", required=True)

    leftover_status = sub.add_parser(
        "leftover-status",
        help="bind leftover-lock to status highest-unit; not a measurement",
    )
    leftover_status.add_argument("--pack", required=True)

    digest_lock_cmd = sub.add_parser(
        "digest-lock",
        help="lock source-digest identity; path alone is not identity",
    )
    digest_lock_cmd.add_argument("--path", required=True)

    digest_eq = sub.add_parser(
        "digest-eq",
        help="repeat digest-lock; equality is not a method",
    )
    digest_eq.add_argument("--path", required=True)

    cmp_digest = sub.add_parser(
        "compare-digest-lock",
        help="compare digest-lock of two paths",
    )
    cmp_digest.add_argument("--left", required=True)
    cmp_digest.add_argument("--right", required=True)

    write_digest = sub.add_parser(
        "write-digest-lock",
        help="write a local digest-lock record; not market evidence",
    )
    write_digest.add_argument("--path", required=True)
    write_digest.add_argument("--out", required=True)
    write_digest.add_argument("--replace", action="store_true")

    verify_digest = sub.add_parser(
        "verify-digest",
        help="verify a local digest-lock record",
    )
    verify_digest.add_argument("--path", required=True)

    digest_status = sub.add_parser(
        "digest-status",
        help="bind digest-lock to status highest-unit; not a measurement",
    )
    digest_status.add_argument("--path", required=True)

    bind_locks = sub.add_parser(
        "bind-locks",
        help="require two lock records to name the same source",
    )
    bind_locks.add_argument("--left", required=True)
    bind_locks.add_argument("--right", required=True)

    bind_eq = sub.add_parser(
        "bind-eq",
        help="repeat bind-locks; equality is not a method",
    )
    bind_eq.add_argument("--left", required=True)
    bind_eq.add_argument("--right", required=True)

    write_bind = sub.add_parser(
        "write-lock-bind",
        help="write a local lock-bind record; not market evidence",
    )
    write_bind.add_argument("--left", required=True)
    write_bind.add_argument("--right", required=True)
    write_bind.add_argument("--out", required=True)
    write_bind.add_argument("--replace", action="store_true")

    verify_bind = sub.add_parser(
        "verify-lock-bind",
        help="verify a local lock-bind record",
    )
    verify_bind.add_argument("--path", required=True)

    bind_status = sub.add_parser(
        "bind-status",
        help="bind lock-bind to status highest-unit; not a measurement",
    )
    bind_status.add_argument("--left", required=True)
    bind_status.add_argument("--right", required=True)

    lock_set_cmd = sub.add_parser(
        "lock-set",
        help="require a folder of lock records to name the same source",
    )
    lock_set_cmd.add_argument("--path", required=True)

    lock_set_eq = sub.add_parser(
        "lock-set-eq",
        help="repeat lock-set; equality is not a method",
    )
    lock_set_eq.add_argument("--path", required=True)

    cmp_lock_set = sub.add_parser(
        "compare-lock-set",
        help="compare lock-set of two folders",
    )
    cmp_lock_set.add_argument("--left", required=True)
    cmp_lock_set.add_argument("--right", required=True)

    write_set = sub.add_parser(
        "write-lock-set",
        help="write a local lock-set record; not market evidence",
    )
    write_set.add_argument("--path", required=True)
    write_set.add_argument("--out", required=True)
    write_set.add_argument("--replace", action="store_true")

    verify_set = sub.add_parser(
        "verify-lock-set",
        help="verify a local lock-set record",
    )
    verify_set.add_argument("--path", required=True)

    set_status = sub.add_parser(
        "lock-set-status",
        help="bind lock-set to status highest-unit; not a measurement",
    )
    set_status.add_argument("--path", required=True)

    content_lock_cmd = sub.add_parser(
        "content-lock",
        help="lock content identity; path is not equality",
    )
    content_lock_cmd.add_argument("--path", required=True)

    content_eq = sub.add_parser(
        "content-eq",
        help="repeat content-lock; equality is not a method",
    )
    content_eq.add_argument("--path", required=True)

    cmp_content = sub.add_parser(
        "compare-content",
        help="compare content identity of two paths; path is ignored",
    )
    cmp_content.add_argument("--left", required=True)
    cmp_content.add_argument("--right", required=True)

    write_content = sub.add_parser(
        "write-content-lock",
        help="write a local content-lock record; not market evidence",
    )
    write_content.add_argument("--path", required=True)
    write_content.add_argument("--out", required=True)
    write_content.add_argument("--replace", action="store_true")

    verify_content = sub.add_parser(
        "verify-content",
        help="verify a local content-lock record",
    )
    verify_content.add_argument("--path", required=True)

    content_status = sub.add_parser(
        "content-status",
        help="bind content-lock to status highest-unit; not a measurement",
    )
    content_status.add_argument("--path", required=True)

    content_bind_cmd = sub.add_parser(
        "content-bind",
        help="require two lock records to share source_digest",
    )
    content_bind_cmd.add_argument("--left", required=True)
    content_bind_cmd.add_argument("--right", required=True)

    content_bind_eq = sub.add_parser(
        "content-bind-eq",
        help="repeat content-bind; equality is not a method",
    )
    content_bind_eq.add_argument("--left", required=True)
    content_bind_eq.add_argument("--right", required=True)

    write_cbind = sub.add_parser(
        "write-content-bind",
        help="write a local content-bind record; not market evidence",
    )
    write_cbind.add_argument("--left", required=True)
    write_cbind.add_argument("--right", required=True)
    write_cbind.add_argument("--out", required=True)
    write_cbind.add_argument("--replace", action="store_true")

    verify_cbind = sub.add_parser(
        "verify-content-bind",
        help="verify a local content-bind record",
    )
    verify_cbind.add_argument("--path", required=True)

    cbind_status = sub.add_parser(
        "content-bind-status",
        help="bind content-bind to status highest-unit; not a measurement",
    )
    cbind_status.add_argument("--left", required=True)
    cbind_status.add_argument("--right", required=True)

    content_set_cmd = sub.add_parser(
        "content-set",
        help="require lock records in a folder to share source_digest",
    )
    content_set_cmd.add_argument("--path", required=True)

    content_set_eq = sub.add_parser(
        "content-set-eq",
        help="repeat content-set; equality is not a method",
    )
    content_set_eq.add_argument("--path", required=True)

    cmp_cset = sub.add_parser(
        "compare-content-set",
        help="compare content-set digest of two folders; path is ignored",
    )
    cmp_cset.add_argument("--left", required=True)
    cmp_cset.add_argument("--right", required=True)

    write_cset = sub.add_parser(
        "write-content-set",
        help="write a local content-set record; not market evidence",
    )
    write_cset.add_argument("--path", required=True)
    write_cset.add_argument("--out", required=True)
    write_cset.add_argument("--replace", action="store_true")

    verify_cset = sub.add_parser(
        "verify-content-set",
        help="verify a local content-set record",
    )
    verify_cset.add_argument("--path", required=True)

    cset_status = sub.add_parser(
        "content-set-status",
        help="bind content-set to status highest-unit; not a measurement",
    )
    cset_status.add_argument("--path", required=True)

    copy_set_cmd = sub.add_parser(
        "copy-set",
        help="require pack directories in a folder to share source_digest",
    )
    copy_set_cmd.add_argument("--path", required=True)

    copy_set_eq = sub.add_parser(
        "copy-set-eq",
        help="repeat copy-set; equality is not a method",
    )
    copy_set_eq.add_argument("--path", required=True)

    cmp_copies = sub.add_parser(
        "compare-copy-set",
        help="compare copy-set digest of two folders; path is ignored",
    )
    cmp_copies.add_argument("--left", required=True)
    cmp_copies.add_argument("--right", required=True)

    write_copies = sub.add_parser(
        "write-copy-set",
        help="write a local copy-set record; not market evidence",
    )
    write_copies.add_argument("--path", required=True)
    write_copies.add_argument("--out", required=True)
    write_copies.add_argument("--replace", action="store_true")

    verify_copies = sub.add_parser(
        "verify-copy-set",
        help="verify a local copy-set record",
    )
    verify_copies.add_argument("--path", required=True)

    copies_status = sub.add_parser(
        "copy-set-status",
        help="bind copy-set to status highest-unit; not a measurement",
    )
    copies_status.add_argument("--path", required=True)


def dispatch_workshop(args: argparse.Namespace) -> int | None:
    command = args.command
    if command == "detect-kind":
        return _print(detect_document_kind(args.path).serialize(), 0)
    if command == "show-declaration":
        return _show_declaration(args.path)
    if command == "show-snapshot":
        return _show_snapshot(args.snapshot)
    if command == "show-observation":
        return _show_observation(args.path)
    if command == "provenance-mix":
        return _print(provenance_mix(args.pack).serialize(), 0)
    if command == "admission":
        return _run_admission(args.pack)
    if command == "compare-rulers":
        try:
            comparison = compare_rulers(args.left, args.right)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(comparison.serialize(), 0 if comparison.equal else 1)
    if command == "compare-reports":
        try:
            comparison = compare_session_reports(args.left, args.right)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(comparison.serialize(), 0 if comparison.equal else 1)
    if command == "journal-summary":
        try:
            return _print(summarize_journal(args.journal).serialize(), 0)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
    if command == "report-bind":
        try:
            bind = bind_report_to_snapshot(args.report, args.snapshot)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(bind.serialize(), 0 if bind.matched else 1)
    if command == "determinism":
        report = check_pack_determinism(args.pack)
        return _print(report.serialize(), 0 if report.equal else 1 if report.error_code is None or report.error_code == "DETERMINISM_MISMATCH" else 2)
    if command == "snapshot-inventory":
        try:
            return _print(snapshot_inventory(args.snapshot).serialize(), 0)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
    if command == "pack-layout":
        layout = inspect_pack_layout(args.pack)
        return _print(layout.serialize(), 0 if layout.ready_to_load else 2)
    if command == "canonical-check":
        check = check_canonical_json(args.path)
        return _print(check.serialize(), 0 if check.canonical else 1)
    if command == "pack-identities":
        return _print(pack_identities(args.pack).serialize(), 0)
    if command == "pack-describe":
        return _print(describe_pack(args.pack).serialize(), 0)
    if command == "code":
        lookup = lookup_reason_code(args.name)
        return _print(lookup.serialize(), 0 if lookup.known else 1)
    if command == "compare-inventories":
        comparison = compare_inventories(args.left, args.right)
        return _print(comparison.serialize(), 0 if comparison.equal else 1)
    if command == "inventory-manifest":
        check = inventory_vs_manifest(args.pack)
        return _print(check.serialize(), 0 if check.matched else 1)
    if command == "status":
        return _print(workshop_status(), 0)
    if command == "readiness":
        return _print(pack_readiness(args.pack).serialize(), 0)
    if command == "claim-check":
        try:
            check = check_claim_level(args.report)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "recompute":
        try:
            if args.snapshot:
                check = recompute_from_snapshot(args.report, args.snapshot)
            else:
                check = recompute_change_records(args.report)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "locked-scope":
        check = inspect_locked_scope(args.pack)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "forbidden":
        check = scan_forbidden_fields(args.path)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "gaps":
        return _print(inspect_gaps(args.pack).serialize(), 0)
    if command == "timestamps":
        check = inspect_timestamps(args.pack)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "pack-safety":
        report = inspect_pack_safety(args.pack)
        return _print(report.serialize(), 0 if report.safe else 1)
    if command == "chain":
        try:
            check = inspect_evidence_chain(args.pack, args.snapshot, args.report)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(check.serialize(), 0 if check.matched else 1)
    if command == "three-way":
        check = three_way_pack(args.pack)
        return _print(check.serialize(), 0 if check.matched else 1)
    if command == "reconcile-journal":
        try:
            check = reconcile_journal_to_pack(args.pack, args.journal)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(check.serialize(), 0 if check.matched else 1)
    if command == "write-audit":
        try:
            written = write_audit_bundle(args.pack, args.out)
        except AuditBundleError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(str(written), 0)
    if command == "verify-audit":
        try:
            verification = verify_audit_bundle(args.dir)
        except AuditBundleError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(verification.serialize(), 0 if verification.matched else 1)
    if command == "close-scale":
        return _print(inspect_close_scale(args.pack).serialize(), 0)
    if command == "bounds":
        return _print(workshop_bounds(), 0)
    if command == "no-network":
        text = scan_package_network_imports()
        parsed = loads(text)
        return _print(text, 0 if parsed.get("valid") else 1)
    if command == "require-kind":
        check = require_document_kind(args.path)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "payload-keys":
        check = inspect_payload_keys(args.pack)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "readiness-check":
        check = check_readiness_semantics(args.pack)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "ohlc-check":
        check = inspect_ohlc(args.pack)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "retrieval-order":
        check = inspect_retrieval_order(args.pack)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "ruler-fields":
        check = inspect_ruler_fields(args.pack)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "percent-fields":
        check = scan_percent_fields(args.path)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "unexpected-files":
        check = inspect_unexpected_files(args.pack)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "leftovers":
        check = inspect_leftovers(args.pack)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "text-safety":
        check = inspect_text_safety(args.path)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "file-modes":
        check = inspect_file_modes(args.pack)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "url-scan":
        check = inspect_pack_urls(args.pack)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "close-zeros":
        return _print(describe_close_zeros(args.pack).serialize(), 0)
    if command == "adjustment":
        check = describe_adjustment_policy(args.pack)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "primary-metric":
        check = inspect_primary_metric(args.pack)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "taxonomy":
        try:
            check = inspect_status_taxonomy(args.report)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "replay-eq":
        check = check_replay_equality(args.pack)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "export-roundtrip":
        check = check_export_roundtrip(args.pack, args.out)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "catalog-audit":
        text = audit_reason_catalog()
        return _print(text, 0 if loads(text).get("valid") else 1)
    if command == "kind-audit":
        text = audit_document_kinds()
        return _print(text, 0 if loads(text).get("valid") else 1)
    if command == "package-identity":
        return _print(package_source_identity(), 0)
    if command == "question-lock":
        check = inspect_question_lock(args.pack)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-disposition":
        try:
            written = write_disposition(
                args.out, args.disposition, args.note, args.replace
            )
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(str(written), 0)
    if command == "show-disposition":
        check = read_disposition(args.path)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "stop-record":
        return _print(workshop_stop_record(), 0)
    if command == "hygiene-scan":
        check = scan_python_source(Path(args.path)) if args.path else scan_workshop_tree()
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "pack-hygiene":
        check = pack_hygiene(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "decimal-check":
        check = decimal_check_directory(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "lineage":
        return _print(admission_vs_kept(Path(args.pack)).serialize(), 0)
    if command == "write-lineage":
        try:
            record = write_lineage_record(Path(args.pack), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0)
    if command == "volume-describe":
        return _print(volume_describe(Path(args.pack)).serialize(), 0)
    if command == "reserved-names":
        check = reserved_name_scan(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "name-vs-ruler":
        check = name_vs_ruler(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "text-encoding":
        check = utf16_scan(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "fixture-label":
        check = fixture_label_check(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-stops":
        try:
            left = Path(args.left).read_text(encoding="utf-8")
            right = Path(args.right).read_text(encoding="utf-8")
        except OSError as exc:
            sys.stderr.write(f"UNREADABLE_JSON: {exc}\n")
            return 2
        check = compare_stops(left, right)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "snapshot-order":
        try:
            check = snapshot_order_check(args.snapshot)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "span-describe":
        return _print(clock_skew_describe(Path(args.pack)).serialize(), 0)
    if command == "certify":
        check = certify_pack(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-certify":
        try:
            record = write_certify_record(Path(args.pack), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "commands":
        return _print(command_catalog().serialize(), 0)
    if command == "self-test":
        check = self_test()
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "byte-check":
        check = byte_check(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "filename-date":
        check = filename_date_check(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "count-check":
        check = count_check(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "claim-words":
        check = claim_word_scan(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-certify":
        check = compare_certify(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-lineage":
        check = compare_lineage(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "certify-eq":
        check = certify_determinism(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "self-test-eq":
        check = self_test_determinism()
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "commands-eq":
        check = command_catalog_determinism()
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "readme-lock":
        check = readme_unit_lock()
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "freeze":
        check = workshop_freeze(Path(args.pack) if args.pack else None)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-freeze":
        try:
            record = write_freeze_record(
                Path(args.out),
                Path(args.pack) if args.pack else None,
                args.replace,
            )
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-freeze":
        check = verify_freeze_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-freeze":
        try:
            left = Path(args.left).read_text(encoding="utf-8")
            right = Path(args.right).read_text(encoding="utf-8")
        except OSError as exc:
            sys.stderr.write(f"UNREADABLE_JSON: {exc}\n")
            return 2
        check = compare_freeze(left, right)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "path-lock":
        check = path_lock(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "journal-codes":
        try:
            check = journal_code_catalog(Path(args.journal))
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "freeze-bind":
        check = freeze_status_bind(Path(args.pack) if args.pack else None)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-byte":
        try:
            record = write_byte_record(Path(args.pack), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-byte":
        check = verify_byte_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "close-sign":
        return _print(close_sign_describe(Path(args.pack)).serialize(), 0)
    if command == "retrieval-unique":
        return _print(retrieval_unique_describe(Path(args.pack)).serialize(), 0)
    if command == "export-byte":
        check = export_byte_check(Path(args.pack), Path(args.out))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "name-lock":
        check = name_lock(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "path-lock-eq":
        check = path_lock_determinism(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "name-lock-eq":
        check = name_lock_determinism(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "freeze-eq":
        check = freeze_determinism(Path(args.pack) if args.pack else None)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "package-eq":
        check = package_identity_determinism()
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-path-lock":
        check = compare_path_lock(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "snapshot-count":
        check = snapshot_count_bind(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-path":
        try:
            record = write_path_record(Path(args.pack), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-path":
        check = verify_path_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-name":
        try:
            record = write_name_record(Path(args.pack), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-name":
        check = verify_name_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-name-lock":
        check = compare_name_lock(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "kind-lock":
        check = kind_lock(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "kind-describe":
        return _print(kind_describe(Path(args.pack)).serialize(), 0)
    if command == "stamp":
        check = workshop_stamp(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "stamp-eq":
        check = stamp_determinism(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-stamp":
        check = compare_stamp(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-stamp":
        try:
            record = write_stamp_record(Path(args.pack), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-stamp":
        check = verify_stamp_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "name-bind":
        check = name_status_bind(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "export-name":
        check = export_name_check(Path(args.pack), Path(args.out))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "journal-lock":
        check = journal_lock(Path(args.journal))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "journal-eq":
        check = journal_lock_determinism(Path(args.journal))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-journal-lock":
        check = compare_journal_lock(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-journal":
        try:
            record = write_journal_record(Path(args.journal), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-journal":
        check = verify_journal_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "kind-lock-eq":
        check = kind_lock_determinism(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-kind-lock":
        check = compare_kind_lock(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-kind":
        try:
            record = write_kind_record(Path(args.pack), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-kind":
        check = verify_kind_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "stamp-bind":
        check = stamp_status_bind(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "report-lock":
        check = report_lock(Path(args.report))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "report-eq":
        check = report_lock_determinism(Path(args.report))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-report-lock":
        check = compare_report_lock(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-report":
        try:
            record = write_report_record(Path(args.report), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-report":
        check = verify_report_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "ruler-lock":
        target = _ruler_target(args)
        if target is None:
            return 2
        check = ruler_lock_any(target)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "ruler-eq":
        target = _ruler_target(args)
        if target is None:
            return 2
        check = ruler_lock_determinism(target)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-ruler-lock":
        check = compare_ruler_lock(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-ruler":
        target = _ruler_target(args)
        if target is None:
            return 2
        try:
            record = write_ruler_record(target, Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-ruler":
        check = verify_ruler_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "report-ruler":
        check = report_ruler_bind(Path(args.report), Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "report-status":
        check = report_status_bind(Path(args.report))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "snapshot-lock":
        target = _snapshot_target(args)
        if target is None:
            return 2
        check = snapshot_lock_any(target)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "snapshot-eq":
        target = _snapshot_target(args)
        if target is None:
            return 2
        check = snapshot_lock_determinism(target)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-snapshot-lock":
        check = compare_snapshot_lock(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-snap":
        target = _snapshot_target(args)
        if target is None:
            return 2
        try:
            record = write_snapshot_record(target, Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-snap":
        check = verify_snapshot_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "snapshot-status":
        target = _snapshot_target(args)
        if target is None:
            return 2
        check = snapshot_status_bind(target)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "disp-lock":
        check = disposition_lock(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "disp-eq":
        check = disposition_lock_determinism(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-disp-lock":
        check = compare_disposition_lock(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-disp-lock":
        try:
            record = write_disposition_record(Path(args.path), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-disp":
        check = verify_disposition_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "disp-status":
        check = disposition_status_bind(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "manifest-lock":
        check = manifest_lock(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "manifest-eq":
        check = manifest_lock_determinism(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-manifest-lock":
        check = compare_manifest_lock(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-manifest":
        try:
            record = write_manifest_record(Path(args.pack), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-manifest":
        check = verify_manifest_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "manifest-status":
        check = manifest_status_bind(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "sidecar-lock":
        target = _sidecar_target(args)
        if target is None:
            return 2
        path, snapshot = target
        check = sidecar_lock_any(path, snapshot=snapshot)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "sidecar-eq":
        target = _sidecar_target(args)
        if target is None:
            return 2
        path, snapshot = target
        check = sidecar_lock_determinism(path, snapshot=snapshot)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-sidecar-lock":
        check = compare_sidecar_lock(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-sidecar-lock":
        target = _sidecar_target(args)
        if target is None:
            return 2
        path, snapshot = target
        try:
            record = write_sidecar_record(path, Path(args.out), args.replace, snapshot=snapshot)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-sidecar":
        check = verify_sidecar_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "sidecar-status":
        target = _sidecar_target(args)
        if target is None:
            return 2
        path, snapshot = target
        check = sidecar_status_bind(path, snapshot=snapshot)
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "bundle-lock":
        check = bundle_lock(Path(args.snapshot))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "bundle-eq":
        check = bundle_lock_determinism(Path(args.snapshot))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-bundle-lock":
        check = compare_bundle_lock(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-bundle-lock":
        try:
            record = write_bundle_record(Path(args.snapshot), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-bundle":
        check = verify_bundle_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "bundle-status":
        check = bundle_status_bind(Path(args.snapshot))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "export-lock":
        check = export_lock(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "export-eq":
        check = export_lock_determinism(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-export-lock":
        check = compare_export_lock(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-export-lock":
        try:
            record = write_export_record(Path(args.pack), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-export":
        check = verify_export_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "export-status":
        check = export_status_bind(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "audit-lock":
        check = audit_lock(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "audit-eq":
        check = audit_lock_determinism(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-audit-lock":
        check = compare_audit_lock(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-audit-lock":
        try:
            record = write_audit_record(Path(args.path), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-audit-lock":
        check = verify_audit_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "audit-status":
        check = audit_status_bind(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "chain-lock":
        check = chain_lock(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "chain-eq":
        check = chain_lock_determinism(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-chain-lock":
        check = compare_chain_lock(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-chain-lock":
        try:
            record = write_chain_record(Path(args.pack), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-chain":
        check = verify_chain_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "chain-status":
        check = chain_status_bind(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "inventory-lock":
        check = inventory_lock(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "inventory-eq":
        check = inventory_lock_determinism(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-inventory-lock":
        check = compare_inventory_lock(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-inventory-lock":
        try:
            record = write_inventory_record(Path(args.pack), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-inventory":
        check = verify_inventory_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "inventory-status":
        check = inventory_status_bind(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "layout-lock":
        check = layout_lock(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "layout-eq":
        check = layout_lock_determinism(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-layout-lock":
        check = compare_layout_lock(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-layout-lock":
        try:
            record = write_layout_record(Path(args.pack), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-layout":
        check = verify_layout_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "layout-status":
        check = layout_status_bind(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "safety-lock":
        check = safety_lock(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "safety-eq":
        check = safety_lock_determinism(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-safety-lock":
        check = compare_safety_lock(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-safety-lock":
        try:
            record = write_safety_record(Path(args.pack), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-safety":
        check = verify_safety_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "safety-status":
        check = safety_status_bind(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "leftover-lock":
        check = leftover_lock(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "leftover-eq":
        check = leftover_lock_determinism(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-leftover-lock":
        check = compare_leftover_lock(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-leftover-lock":
        try:
            record = write_leftover_record(Path(args.pack), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-leftover":
        check = verify_leftover_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "leftover-status":
        check = leftover_status_bind(Path(args.pack))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "digest-lock":
        check = digest_lock(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "digest-eq":
        check = digest_lock_determinism(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-digest-lock":
        check = compare_digest_lock(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-digest-lock":
        try:
            record = write_digest_record(Path(args.path), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-digest":
        check = verify_digest_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "digest-status":
        check = digest_status_bind(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "bind-locks":
        check = bind_lock_records(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "bind-eq":
        check = lock_bind_determinism(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-lock-bind":
        try:
            record = write_lock_bind_record(
                Path(args.left), Path(args.right), Path(args.out), args.replace
            )
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-lock-bind":
        check = verify_lock_bind_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "bind-status":
        check = lock_bind_status(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "lock-set":
        check = lock_set(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "lock-set-eq":
        check = lock_set_determinism(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-lock-set":
        check = compare_lock_set(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-lock-set":
        try:
            record = write_lock_set_record(Path(args.path), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-lock-set":
        check = verify_lock_set_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "lock-set-status":
        check = lock_set_status(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "content-lock":
        check = content_lock(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "content-eq":
        check = content_lock_determinism(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-content":
        check = compare_content_lock(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-content-lock":
        try:
            record = write_content_record(Path(args.path), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-content":
        check = verify_content_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "content-status":
        check = content_status_bind(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "content-bind":
        check = content_bind(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "content-bind-eq":
        check = content_bind_determinism(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-content-bind":
        try:
            record = write_content_bind_record(
                Path(args.left), Path(args.right), Path(args.out), args.replace
            )
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-content-bind":
        check = verify_content_bind_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "content-bind-status":
        check = content_bind_status(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "content-set":
        check = content_set(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "content-set-eq":
        check = content_set_determinism(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-content-set":
        check = compare_content_set(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-content-set":
        try:
            record = write_content_set_record(Path(args.path), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-content-set":
        check = verify_content_set_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "content-set-status":
        check = content_set_status(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "copy-set":
        check = copy_set(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "copy-set-eq":
        check = copy_set_determinism(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "compare-copy-set":
        check = compare_copy_set(Path(args.left), Path(args.right))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "write-copy-set":
        try:
            record = write_copy_set_record(Path(args.path), Path(args.out), args.replace)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        return _print(record.serialize(), 0 if record.valid else 1)
    if command == "verify-copy-set":
        check = verify_copy_set_record(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    if command == "copy-set-status":
        check = copy_set_status(Path(args.path))
        return _print(check.serialize(), 0 if check.valid else 1)
    return None


def _print(text: str, code: int) -> int:
    sys.stdout.write(text + "\n")
    return code


def _ruler_target(args: argparse.Namespace) -> Path | None:
    pack = getattr(args, "pack", None)
    ruler = getattr(args, "ruler", None)
    if bool(pack) == bool(ruler):
        sys.stderr.write("UNREADABLE_RULER_SIDECAR: pass exactly one of --pack or --ruler\n")
        return None
    return Path(pack or ruler)


def _snapshot_target(args: argparse.Namespace) -> Path | None:
    pack = getattr(args, "pack", None)
    snapshot = getattr(args, "snapshot", None)
    if bool(pack) == bool(snapshot):
        sys.stderr.write("UNREADABLE_SNAPSHOT_FILE: pass exactly one of --pack or --snapshot\n")
        return None
    return Path(pack or snapshot)


def _sidecar_target(args: argparse.Namespace) -> tuple[Path, bool] | None:
    path = getattr(args, "path", None)
    snapshot = getattr(args, "snapshot", None)
    if bool(path) == bool(snapshot):
        sys.stderr.write("UNREADABLE_SIDECAR: pass exactly one of --path or --snapshot\n")
        return None
    if path:
        return Path(path), False
    return Path(snapshot), True


def _show_declaration(path: str) -> int:
    target = Path(path)
    try:
        text = target.read_text(encoding="utf-8")
    except OSError as exc:
        sys.stderr.write(f"UNREADABLE_DECLARATION: {exc}\n")
        return 2
    parsed = intake_declaration_json(text)
    if parsed.declaration is None:
        sys.stderr.write("UNREADABLE_DECLARATION: declaration is not usable\n")
        return 2
    sys.stdout.write(text if text.endswith("\n") else text + "\n")
    return 0


def _show_snapshot(path: str) -> int:
    try:
        snapshot = read_snapshot_file(path)
    except SnapshotFileError as exc:
        sys.stderr.write(f"{exc.code}: {exc.reason}\n")
        return 2
    sys.stdout.write(snapshot.serialize() + "\n")
    return 0


def _show_observation(path: str) -> int:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        sys.stderr.write(f"UNREADABLE_JSON: {exc}\n")
        return 2
    report = intake_observation_json(text)
    document = {
        "accepted": report.accepted_count(),
        "document_kind": "radar_v4.observation",
        "quarantined": report.quarantined_count(),
        "unreadable": report.unreadable_count(),
    }
    sys.stdout.write(
        dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"
    )
    return 0 if report.accepted_count() else 2


def _run_admission(pack: str) -> int:
    result = run_session_from_pack(pack, measure=False)
    sys.stdout.write(serialize_admission_report(result) + "\n")
    return 0 if result.session is not None else 2
