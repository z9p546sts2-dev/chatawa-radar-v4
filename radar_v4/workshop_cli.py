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
from radar_v4.workshop_bounds import scan_package_network_imports, workshop_bounds
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
    return None


def _print(text: str, code: int) -> int:
    sys.stdout.write(text + "\n")
    return code


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
