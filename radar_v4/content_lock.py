"""Path-independent content identity. Not a measurement."""

from __future__ import annotations

from json import loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.integrity import (
    IntegrityCheck,
    lock_source_details,
    source_digest,
    verify_recomputed_lock_record,
)
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status

_HEX = frozenset("0123456789abcdef")


def content_lock(path: Path) -> IntegrityCheck:
    root = Path(path)
    digest = source_digest(root)
    if not root.exists():
        return IntegrityCheck(
            "radar_v4.content_lock",
            False,
            "UNREADABLE_PACK",
            ("Content lock needs a present file or directory.",),
            lock_source_details(root),
        )
    ok = len(digest) == 64 and all(char in _HEX for char in digest)
    return IntegrityCheck(
        "radar_v4.content_lock",
        ok,
        None if ok else "SOURCE_DIGEST_REFUSED",
        (
            "Content lock is SHA-256 identity.",
            "Path is recorded, but equality ignores path.",
        ),
        lock_source_details(root, {"algorithm": "sha256"}),
    )


def content_lock_determinism(path: Path) -> IntegrityCheck:
    first = content_lock(path)
    second = content_lock(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.content_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Content lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_content_lock(left: Path, right: Path) -> IntegrityCheck:
    first = content_lock(left)
    second = content_lock(right)
    equal = (
        first.valid
        and second.valid
        and first.details.get("source_digest") == second.details.get("source_digest")
    )
    return IntegrityCheck(
        "radar_v4.compare_content_lock",
        equal,
        None if equal else "CONTENT_MISMATCH",
        (
            "Compared content identity only.",
            "Path is not identity.",
        ),
        {
            "equal": equal,
            "left_digest": first.details.get("source_digest"),
            "right_digest": second.details.get("source_digest"),
        },
    )


def write_content_record(
    source: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = content_lock(source)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_content_record(path: Path) -> IntegrityCheck:
    return verify_recomputed_lock_record(
        path,
        expected_kind="radar_v4.content_lock",
        verify_kind="radar_v4.content_verify",
        invalid_code="CONTENT_RECORD_INVALID",
        recompute=content_lock,
    )


def content_status_bind(path: Path) -> IntegrityCheck:
    locked = content_lock(path)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.content_status_bind",
        matched,
        None if matched else "CONTENT_STATUS_MISMATCH",
        ("Content lock and status share the locked unit. Not a measurement.",),
        {
            "content_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
