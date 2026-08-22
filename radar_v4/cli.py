"""Local command-line entry. No network. Not a trading interface."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from json import dumps
from pathlib import Path

from radar_v4.checksum_sidecar import verify_checksum_sidecar, write_checksum_sidecar
from radar_v4.declaration_json import intake_declaration_json
from radar_v4.local_session import run_session_from_pack, run_session_from_snapshot_file
from radar_v4.pack_export import PackExportError, export_snapshot_to_pack
from radar_v4.pack_manifest import PackManifestError, verify_pack_manifest, write_pack_manifest
from radar_v4.quarantine_journal import write_quarantine_journal_file
from radar_v4.reason_codes import REASON_CODES
from radar_v4.registry import EvidenceRegistry
from radar_v4.registry_files import RegistryFileError, write_registry_file
from radar_v4.ruler import RulerMismatchError
from radar_v4.ruler_file import serialize_ruler, write_ruler_sidecar
from radar_v4.session_report import (
    serialize_local_session_report,
    serialize_session_report,
    write_local_session_report_file,
    write_session_report_file,
)
from radar_v4.snapshot_compare import compare_snapshot_files
from radar_v4.snapshot_files import SnapshotFileError, read_snapshot_file, write_snapshot_file
from radar_v4.snapshot_verify import verify_snapshot_file


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="radar_v4",
        description="Radar V4 local evidence commands. No vendor. No method.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    session = sub.add_parser("session", help="run a FIXTURE/SYNTHETIC pack session")
    session.add_argument("--pack", required=True, help="local dataset pack directory")
    session.add_argument("--snapshot", help="optional snapshot output path")
    session.add_argument("--report", help="optional session report output path")
    session.add_argument("--journal", help="optional quarantine journal output path")
    session.add_argument(
        "--sidecar",
        action="store_true",
        help="write a .sha256 sidecar next to --snapshot",
    )

    replay = sub.add_parser("replay", help="replay a local snapshot file")
    replay.add_argument("--snapshot", required=True, help="snapshot file to replay")
    replay.add_argument("--report", help="optional session report output path")
    replay.add_argument("--expect-ruler", help="optional ruler checksum to require")

    compare = sub.add_parser("compare", help="compare two local snapshot files")
    compare.add_argument("--left", required=True, help="left snapshot file")
    compare.add_argument("--right", required=True, help="right snapshot file")

    verify = sub.add_parser("verify", help="verify a snapshot integrity checksum")
    verify.add_argument("--snapshot", required=True, help="snapshot file")
    verify.add_argument(
        "--expect-checksum",
        help="optional SHA-256 hex digest to compare",
    )
    verify.add_argument(
        "--sidecar",
        action="store_true",
        help="verify or write using the .sha256 sidecar",
    )
    verify.add_argument(
        "--write-sidecar",
        action="store_true",
        help="write a .sha256 sidecar for this snapshot",
    )

    export_pack = sub.add_parser(
        "export-pack", help="write a FIXTURE/SYNTHETIC pack from a snapshot"
    )
    export_pack.add_argument("--snapshot", required=True, help="snapshot file")
    export_pack.add_argument("--out", required=True, help="empty output directory")

    sub.add_parser("codes", help="print the refusal-code catalog")

    quarantine = sub.add_parser("quarantine", help="write a pack quarantine journal")
    quarantine.add_argument("--pack", required=True, help="local dataset pack directory")
    quarantine.add_argument("--out", required=True, help="journal output path")

    registry_write = sub.add_parser(
        "registry-write", help="write accepted snapshot envelopes to a registry file"
    )
    registry_write.add_argument("--snapshot", required=True, help="snapshot file")
    registry_write.add_argument("--out", required=True, help="registry output path")

    manifest = sub.add_parser("pack-manifest", help="write a pack integrity manifest")
    manifest.add_argument("--pack", required=True, help="local dataset pack directory")

    pack_verify = sub.add_parser("pack-verify", help="verify a pack against its manifest")
    pack_verify.add_argument("--pack", required=True, help="local dataset pack directory")

    show_ruler = sub.add_parser("show-ruler", help="print a pack or snapshot ruler")
    show_ruler.add_argument("--pack", help="local dataset pack directory")
    show_ruler.add_argument("--snapshot", help="snapshot file")

    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.command == "session":
        return _run_session(
            args.pack, args.snapshot, args.report, args.journal, args.sidecar
        )
    if args.command == "replay":
        return _run_replay(args.snapshot, args.report, args.expect_ruler)
    if args.command == "compare":
        return _run_compare(args.left, args.right)
    if args.command == "verify":
        return _run_verify(
            args.snapshot, args.expect_checksum, args.sidecar, args.write_sidecar
        )
    if args.command == "export-pack":
        return _run_export_pack(args.snapshot, args.out)
    if args.command == "codes":
        return _run_codes()
    if args.command == "quarantine":
        return _run_quarantine(args.pack, args.out)
    if args.command == "registry-write":
        return _run_registry_write(args.snapshot, args.out)
    if args.command == "pack-manifest":
        return _run_pack_manifest(args.pack)
    if args.command == "pack-verify":
        return _run_pack_verify(args.pack)
    return _run_show_ruler(args.pack, args.snapshot)


def _run_session(
    pack: str,
    snapshot_path: str | None,
    report_path: str | None,
    journal_path: str | None,
    write_sidecar: bool,
) -> int:
    result = run_session_from_pack(pack)
    if result.session is None:
        sys.stderr.write(f"{result.error_code or 'PACK_NOT_USABLE'}\n")
        if result.pack is not None:
            for issue in result.pack.pack_issues:
                sys.stderr.write(f"{issue.code}: {issue.reason}\n")
            for item in result.pack.unreadable:
                sys.stderr.write(f"{item.code}: {item.reason}\n")
        if journal_path:
            try:
                write_quarantine_journal_file(journal_path, local=result)
            except SnapshotFileError as exc:
                sys.stderr.write(f"{exc.code}: {exc.reason}\n")
                return 2
        return 2
    text = serialize_local_session_report(result)
    try:
        if snapshot_path:
            write_snapshot_file(snapshot_path, result.session.snapshot)
            write_ruler_sidecar(snapshot_path, result.session.snapshot.declaration)
            if write_sidecar:
                write_checksum_sidecar(
                    snapshot_path, result.session.snapshot.integrity_checksum()
                )
        elif write_sidecar:
            sys.stderr.write("SIDECAR requires --snapshot\n")
            return 2
        if report_path:
            write_local_session_report_file(report_path, result)
        if journal_path:
            write_quarantine_journal_file(journal_path, local=result)
    except SnapshotFileError as exc:
        sys.stderr.write(f"{exc.code}: {exc.reason}\n")
        return 2
    sys.stdout.write(text + "\n")
    return 0


def _run_replay(
    snapshot_path: str, report_path: str | None, expected_ruler: str | None
) -> int:
    try:
        session = run_session_from_snapshot_file(snapshot_path, expected_ruler)
        if report_path:
            write_session_report_file(report_path, session)
    except SnapshotFileError as exc:
        sys.stderr.write(f"{exc.code}: {exc.reason}\n")
        return 2
    except RulerMismatchError as exc:
        sys.stderr.write(f"{exc.code}: {exc.reason}\n")
        return 1
    sys.stdout.write(serialize_session_report(session) + "\n")
    return 0


def _run_verify(
    snapshot_path: str,
    expected: str | None,
    use_sidecar: bool,
    write_sidecar: bool,
) -> int:
    try:
        if write_sidecar:
            write_checksum_sidecar(snapshot_path)
        if use_sidecar:
            verification = verify_checksum_sidecar(snapshot_path)
        else:
            verification = verify_snapshot_file(snapshot_path, expected)
    except SnapshotFileError as exc:
        sys.stderr.write(f"{exc.code}: {exc.reason}\n")
        return 2
    sys.stdout.write(verification.serialize() + "\n")
    if verification.matched is False:
        sys.stderr.write("SNAPSHOT_CHECKSUM_MISMATCH\n")
        return 1
    return 0


def _run_export_pack(snapshot_path: str, out_dir: str) -> int:
    try:
        snapshot = read_snapshot_file(snapshot_path)
        written = export_snapshot_to_pack(snapshot, out_dir)
    except SnapshotFileError as exc:
        sys.stderr.write(f"{exc.code}: {exc.reason}\n")
        return 2
    except PackExportError as exc:
        sys.stderr.write(f"{exc.code}: {exc.reason}\n")
        return 2
    sys.stdout.write(f"{written}\n")
    return 0


def _run_compare(left: str, right: str) -> int:
    try:
        comparison = compare_snapshot_files(left, right)
    except SnapshotFileError as exc:
        sys.stderr.write(f"{exc.code}: {exc.reason}\n")
        return 2
    sys.stdout.write(comparison.serialize() + "\n")
    return 0


def _run_codes() -> int:
    sys.stdout.write(
        dumps(sorted(REASON_CODES), separators=(",", ":"), ensure_ascii=True) + "\n"
    )
    return 0


def _run_quarantine(pack: str, out_path: str) -> int:
    result = run_session_from_pack(pack)
    try:
        write_quarantine_journal_file(out_path, local=result)
    except SnapshotFileError as exc:
        sys.stderr.write(f"{exc.code}: {exc.reason}\n")
        return 2
    if result.session is None:
        sys.stderr.write(f"{result.error_code or 'PACK_NOT_USABLE'}\n")
        return 2
    sys.stdout.write(out_path + "\n")
    return 0


def _run_registry_write(snapshot_path: str, out_path: str) -> int:
    try:
        snapshot = read_snapshot_file(snapshot_path)
        registry = EvidenceRegistry()
        registry.put(tuple(item.envelope for item in snapshot.observations))
        write_registry_file(out_path, registry)
    except SnapshotFileError as exc:
        sys.stderr.write(f"{exc.code}: {exc.reason}\n")
        return 2
    except RegistryFileError as exc:
        sys.stderr.write(f"{exc.code}: {exc.reason}\n")
        return 2
    sys.stdout.write(out_path + "\n")
    return 0


def _run_pack_manifest(pack: str) -> int:
    try:
        written = write_pack_manifest(pack)
    except PackManifestError as exc:
        sys.stderr.write(f"{exc.code}: {exc.reason}\n")
        return 2
    sys.stdout.write(str(written) + "\n")
    return 0


def _run_pack_verify(pack: str) -> int:
    try:
        manifest = verify_pack_manifest(pack)
    except PackManifestError as exc:
        sys.stderr.write(f"{exc.code}: {exc.reason}\n")
        return 1 if exc.code == "MANIFEST_CHECKSUM_MISMATCH" else 2
    sys.stdout.write(manifest.serialize() + "\n")
    return 0


def _run_show_ruler(pack: str | None, snapshot_path: str | None) -> int:
    if bool(pack) == bool(snapshot_path):
        sys.stderr.write("show-ruler requires exactly one of --pack or --snapshot\n")
        return 2
    if snapshot_path:
        try:
            snapshot = read_snapshot_file(snapshot_path)
        except SnapshotFileError as exc:
            sys.stderr.write(f"{exc.code}: {exc.reason}\n")
            return 2
        sys.stdout.write(serialize_ruler(snapshot.declaration) + "\n")
        return 0
    assert pack is not None
    declaration_path = Path(pack) / "declaration.json"
    if not declaration_path.is_file():
        sys.stderr.write("UNREADABLE_DECLARATION: pack has no usable declaration.json\n")
        return 2
    parsed = intake_declaration_json(declaration_path.read_text(encoding="utf-8"))
    if parsed.declaration is None:
        sys.stderr.write("UNREADABLE_DECLARATION: pack has no usable declaration.json\n")
        return 2
    sys.stdout.write(serialize_ruler(parsed.declaration) + "\n")
    return 0
