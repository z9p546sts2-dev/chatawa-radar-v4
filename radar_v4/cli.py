"""Local command-line entry. No network. Not a trading interface."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from radar_v4.local_session import run_session_from_pack, run_session_from_snapshot_file
from radar_v4.pack_export import PackExportError, export_snapshot_to_pack
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

    replay = sub.add_parser("replay", help="replay a local snapshot file")
    replay.add_argument("--snapshot", required=True, help="snapshot file to replay")
    replay.add_argument("--report", help="optional session report output path")

    compare = sub.add_parser("compare", help="compare two local snapshot files")
    compare.add_argument("--left", required=True, help="left snapshot file")
    compare.add_argument("--right", required=True, help="right snapshot file")

    verify = sub.add_parser("verify", help="verify a snapshot integrity checksum")
    verify.add_argument("--snapshot", required=True, help="snapshot file")
    verify.add_argument(
        "--expect-checksum",
        help="optional SHA-256 hex digest to compare",
    )

    export_pack = sub.add_parser(
        "export-pack", help="write a FIXTURE/SYNTHETIC pack from a snapshot"
    )
    export_pack.add_argument("--snapshot", required=True, help="snapshot file")
    export_pack.add_argument("--out", required=True, help="empty output directory")

    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.command == "session":
        return _run_session(args.pack, args.snapshot, args.report)
    if args.command == "replay":
        return _run_replay(args.snapshot, args.report)
    if args.command == "compare":
        return _run_compare(args.left, args.right)
    if args.command == "verify":
        return _run_verify(args.snapshot, args.expect_checksum)
    return _run_export_pack(args.snapshot, args.out)


def _run_session(pack: str, snapshot_path: str | None, report_path: str | None) -> int:
    result = run_session_from_pack(pack)
    if result.session is None:
        sys.stderr.write(f"{result.error_code or 'PACK_NOT_USABLE'}\n")
        if result.pack is not None:
            for issue in result.pack.pack_issues:
                sys.stderr.write(f"{issue.code}: {issue.reason}\n")
            for item in result.pack.unreadable:
                sys.stderr.write(f"{item.code}: {item.reason}\n")
        return 2
    text = serialize_local_session_report(result)
    try:
        if snapshot_path:
            write_snapshot_file(snapshot_path, result.session.snapshot)
        if report_path:
            write_local_session_report_file(report_path, result)
    except SnapshotFileError as exc:
        sys.stderr.write(f"{exc.code}: {exc.reason}\n")
        return 2
    sys.stdout.write(text + "\n")
    return 0


def _run_replay(snapshot_path: str, report_path: str | None) -> int:
    try:
        session = run_session_from_snapshot_file(snapshot_path)
        if report_path:
            write_session_report_file(report_path, session)
    except SnapshotFileError as exc:
        sys.stderr.write(f"{exc.code}: {exc.reason}\n")
        return 2
    sys.stdout.write(serialize_session_report(session) + "\n")
    return 0


def _run_verify(snapshot_path: str, expected: str | None) -> int:
    try:
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
