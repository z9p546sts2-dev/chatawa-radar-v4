"""A folder of pack copies must share one digest. Not a measurement."""

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


def _copies(directory: Path) -> list[Path]:
    copies: list[Path] = []
    for child in sorted(directory.iterdir()):
        if child.is_dir() and not child.is_symlink():
            copies.append(child)
    return copies


def copy_set(path: Path) -> IntegrityCheck:
    root = Path(path)
    if not root.is_dir():
        return IntegrityCheck(
            "radar_v4.copy_set",
            False,
            "UNREADABLE_PACK",
            ("Copy set needs a present directory of pack copies.",),
            lock_source_details(root, {"failed": ["radar_v4.copy_set"]}),
        )
    copies = _copies(root)
    listing = [
        {"path": str(item.resolve()), "source_digest": source_digest(item)} for item in copies
    ]
    extra: dict[str, object] = {"copies": listing, "count": len(copies)}
    if not copies:
        return IntegrityCheck(
            "radar_v4.copy_set",
            False,
            "COPY_SET_EMPTY",
            (
                "Copy set needs pack directories.",
                "A folder of lock records is not a copy set.",
            ),
            lock_source_details(root, extra),
        )
    digest = listing[0]["source_digest"]
    digest_ok = isinstance(digest, str) and len(digest) == 64 and all(
        char in _HEX for char in digest
    )
    if not digest_ok:
        extra["failed"] = ["radar_v4.copy_set"]
        return IntegrityCheck(
            "radar_v4.copy_set",
            False,
            "SOURCE_DIGEST_REFUSED",
            ("Copy set refused a copy without a SHA-256 digest.",),
            lock_source_details(root, extra),
        )
    if len(copies) < 2:
        extra["failed"] = ["radar_v4.copy_set"]
        extra["record_source_digest"] = digest
        return IntegrityCheck(
            "radar_v4.copy_set",
            False,
            "COPY_SET_TOO_SMALL",
            ("Copy set needs at least two pack directories to agree.",),
            lock_source_details(root, extra),
        )
    matched = all(item["source_digest"] == digest for item in listing)
    extra["failed"] = []
    extra["record_source_digest"] = digest
    extra["paths_may_differ"] = True
    return IntegrityCheck(
        "radar_v4.copy_set",
        matched,
        None if matched else "CONTENT_MISMATCH",
        (
            "Every pack copy in the folder must share source_digest.",
            "Agreement is not a method.",
        ),
        lock_source_details(root, extra),
    )


def copy_set_determinism(path: Path) -> IntegrityCheck:
    first = copy_set(path)
    second = copy_set(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.copy_set_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Copy set ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_copy_set(left: Path, right: Path) -> IntegrityCheck:
    first = copy_set(left)
    second = copy_set(right)
    equal = (
        first.valid
        and second.valid
        and first.details.get("record_source_digest") == second.details.get("record_source_digest")
    )
    return IntegrityCheck(
        "radar_v4.compare_copy_set",
        equal,
        None if equal else "COPY_SET_MISMATCH",
        (
            "Compared copy-set digest only.",
            "The set folder path is not identity.",
        ),
        {
            "equal": equal,
            "left_digest": first.details.get("record_source_digest"),
            "right_digest": second.details.get("record_source_digest"),
        },
    )


def write_copy_set_record(
    source: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = copy_set(source)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_copy_set_record(path: Path) -> IntegrityCheck:
    return verify_recomputed_lock_record(
        path,
        expected_kind="radar_v4.copy_set",
        verify_kind="radar_v4.copy_set_verify",
        invalid_code="COPY_SET_RECORD_INVALID",
        recompute=copy_set,
    )


def copy_set_status(path: Path) -> IntegrityCheck:
    locked = copy_set(path)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.copy_set_status",
        matched,
        None if matched else "COPY_SET_STATUS_MISMATCH",
        ("Copy set and status share the locked unit. Not a measurement.",),
        {
            "set_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
