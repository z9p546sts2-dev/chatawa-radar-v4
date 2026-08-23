"""Snapshot-bundle identity checks. Not market evidence."""

from __future__ import annotations

from json import JSONDecodeError, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.bundle_verify import verify_snapshot_bundle
from radar_v4.integrity import IntegrityCheck
from radar_v4.snapshot_files import SnapshotFileError, read_snapshot_file
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


def bundle_readable_scan(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        read_snapshot_file(target)
    except SnapshotFileError as exc:
        return IntegrityCheck(
            "radar_v4.bundle_readable",
            False,
            exc.code,
            (exc.reason,),
            {"path": str(target)},
        )
    return IntegrityCheck(
        "radar_v4.bundle_readable",
        True,
        None,
        ("Snapshot file is readable. Not a measurement.",),
        {"path": str(target)},
    )


def bundle_sidecar_scan(path: Path) -> IntegrityCheck:
    readable = bundle_readable_scan(path)
    if not readable.valid:
        return readable
    verification = verify_snapshot_bundle(path, require_sidecar=True, require_ruler=False)
    if not verification.sidecar_present:
        return IntegrityCheck(
            "radar_v4.bundle_sidecar",
            False,
            "BUNDLE_SIDECAR_MISSING",
            ("A locked bundle requires a checksum sidecar. Not repaired.",),
            {"path": str(path)},
        )
    if verification.sidecar_matched is False:
        return IntegrityCheck(
            "radar_v4.bundle_sidecar",
            False,
            "SNAPSHOT_CHECKSUM_MISMATCH",
            ("Sidecar digest does not match the snapshot. Not repaired.",),
            {"path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.bundle_sidecar",
        True,
        None,
        ("Bundle sidecar matches. Not market evidence.",),
        {"path": str(path)},
    )


def bundle_ruler_scan(path: Path) -> IntegrityCheck:
    readable = bundle_readable_scan(path)
    if not readable.valid:
        return readable
    verification = verify_snapshot_bundle(path, require_sidecar=False, require_ruler=True)
    if not verification.ruler_present:
        return IntegrityCheck(
            "radar_v4.bundle_ruler",
            False,
            "BUNDLE_RULER_MISSING",
            ("A locked bundle requires a ruler sidecar. Not a method.",),
            {"path": str(path)},
        )
    if verification.ruler_matched is False:
        return IntegrityCheck(
            "radar_v4.bundle_ruler",
            False,
            "BUNDLE_RULER_MISMATCH",
            ("Ruler sidecar does not match the snapshot ruler. Not repaired.",),
            {"path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.bundle_ruler",
        True,
        None,
        ("Bundle ruler matches. Not a score.",),
        {"path": str(path)},
    )


def bundle_lock(path: Path) -> IntegrityCheck:
    parts = [
        bundle_readable_scan(path),
        bundle_sidecar_scan(path),
        bundle_ruler_scan(path),
    ]
    failed = [part for part in parts if not part.valid]
    if failed:
        first = failed[0]
        return IntegrityCheck(
            "radar_v4.bundle_lock",
            False,
            first.error_code,
            ("Bundle lock failed.",) + first.notes,
            {"failed": [part.document_kind for part in failed]},
        )
    return IntegrityCheck(
        "radar_v4.bundle_lock",
        True,
        None,
        ("Bundle lock passed. Not market evidence.",),
        {"failed": []},
    )


def bundle_lock_determinism(path: Path) -> IntegrityCheck:
    first = bundle_lock(path)
    second = bundle_lock(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.bundle_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Bundle lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_bundle_lock(left: Path, right: Path) -> IntegrityCheck:
    first = bundle_lock(left)
    second = bundle_lock(right)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.compare_bundle_lock",
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared bundle-lock records. Equality is not a score.",),
        {"equal": equal},
    )


def write_bundle_record(
    source: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = bundle_lock(source)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_bundle_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.bundle_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable bundle-lock record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.bundle_verify",
            False,
            "UNREADABLE_JSON",
            ("bundle-lock record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.bundle_verify",
            False,
            "UNREADABLE_JSON",
            ("bundle-lock record must be an object",),
            {"path": str(target)},
        )
    ok = raw.get("document_kind") == "radar_v4.bundle_lock" and raw.get("valid") is True
    return IntegrityCheck(
        "radar_v4.bundle_verify",
        ok,
        None if ok else "BUNDLE_RECORD_INVALID",
        ("Verified a local bundle-lock record. Not market evidence.",),
        {"path": str(target)},
    )


def bundle_status_bind(path: Path) -> IntegrityCheck:
    locked = bundle_lock(path)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.bundle_status_bind",
        matched,
        None if matched else "BUNDLE_STATUS_MISMATCH",
        ("Bundle lock and status share the locked unit. Not a measurement.",),
        {
            "bundle_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
