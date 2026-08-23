"""Source-digest identity checks. Not a measurement."""

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


def source_digest_scan(path: Path) -> IntegrityCheck:
    root = Path(path)
    digest = source_digest(root)
    if not root.exists():
        return IntegrityCheck(
            "radar_v4.source_digest",
            False,
            "UNREADABLE_PACK",
            ("Source digest needs a present file or directory. Not invented.",),
            lock_source_details(root),
        )
    ok = len(digest) == 64 and all(char in _HEX for char in digest)
    return IntegrityCheck(
        "radar_v4.source_digest",
        ok,
        None if ok else "SOURCE_DIGEST_REFUSED",
        (
            "Source digest is SHA-256 of file bytes or a sorted listing.",
            "This is identity, not a score.",
        ),
        lock_source_details(root, {"algorithm": "sha256"}),
    )


def digest_lock(path: Path) -> IntegrityCheck:
    scanned = source_digest_scan(path)
    if not scanned.valid:
        return IntegrityCheck(
            "radar_v4.digest_lock",
            False,
            scanned.error_code,
            ("Digest lock failed.",) + scanned.notes,
            lock_source_details(path, {"failed": [scanned.document_kind]}),
        )
    return IntegrityCheck(
        "radar_v4.digest_lock",
        True,
        None,
        ("Digest lock passed. Path alone is not identity.",),
        lock_source_details(path, {"failed": []}),
    )


def digest_lock_determinism(path: Path) -> IntegrityCheck:
    first = digest_lock(path)
    second = digest_lock(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.digest_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Digest lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_digest_lock(left: Path, right: Path) -> IntegrityCheck:
    first = digest_lock(left)
    second = digest_lock(right)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.compare_digest_lock",
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared digest-lock records. Equality is not a score.",),
        {"equal": equal},
    )


def write_digest_record(
    source: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = digest_lock(source)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_digest_record(path: Path) -> IntegrityCheck:
    return verify_recomputed_lock_record(
        path,
        expected_kind="radar_v4.digest_lock",
        verify_kind="radar_v4.digest_verify",
        invalid_code="DIGEST_RECORD_INVALID",
        recompute=digest_lock,
    )


def digest_status_bind(path: Path) -> IntegrityCheck:
    locked = digest_lock(path)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.digest_status_bind",
        matched,
        None if matched else "DIGEST_STATUS_MISMATCH",
        ("Digest lock and status share the locked unit. Not a measurement.",),
        {
            "digest_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
