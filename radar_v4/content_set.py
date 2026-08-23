"""A folder of lock records must share one digest. Paths may differ."""

from __future__ import annotations

from json import loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.integrity import (
    IntegrityCheck,
    lock_source_details,
    verify_recomputed_lock_record,
)
from radar_v4.lock_bind import lock_identity
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


def _lock_records(directory: Path) -> list[IntegrityCheck]:
    records: list[IntegrityCheck] = []
    for child in sorted(directory.iterdir()):
        if not child.is_file() or child.suffix != ".json" or child.is_symlink():
            continue
        records.append(lock_identity(child))
    return records


def content_set(path: Path) -> IntegrityCheck:
    root = Path(path)
    if not root.is_dir():
        return IntegrityCheck(
            "radar_v4.content_set",
            False,
            "UNREADABLE_PACK",
            ("Content set needs a present directory of lock records.",),
            lock_source_details(root, {"failed": ["radar_v4.lock_identity"]}),
        )
    records = _lock_records(root)
    listing = [
        {
            "path": item.details.get("source_path"),
            "record_kind": item.details.get("record_kind"),
            "record_source_path": item.details.get("record_source_path"),
            "record_source_digest": item.details.get("record_source_digest"),
            "valid": item.valid,
        }
        for item in records
    ]
    extra: dict[str, object] = {"records": listing, "count": len(records)}
    if not records:
        return IntegrityCheck(
            "radar_v4.content_set",
            False,
            "CONTENT_SET_EMPTY",
            ("Content set needs lock records. An empty folder is not custody.",),
            lock_source_details(root, extra),
        )
    bad = next((item for item in records if not item.valid), None)
    if bad is not None:
        extra["failed"] = [bad.document_kind]
        return IntegrityCheck(
            "radar_v4.content_set",
            False,
            bad.error_code,
            ("Content set refused an invalid lock record.",) + bad.notes,
            lock_source_details(root, extra),
        )
    if len(records) < 2:
        extra["failed"] = ["radar_v4.lock_identity"]
        return IntegrityCheck(
            "radar_v4.content_set",
            False,
            "CONTENT_SET_TOO_SMALL",
            ("Content set needs at least two records to agree.",),
            lock_source_details(root, extra),
        )
    digest = records[0].details.get("record_source_digest")
    matched = all(item.details.get("record_source_digest") == digest for item in records)
    extra["failed"] = []
    extra["record_source_digest"] = digest
    extra["paths_may_differ"] = True
    return IntegrityCheck(
        "radar_v4.content_set",
        matched,
        None if matched else "CONTENT_BIND_MISMATCH",
        (
            "Every lock record in the folder must share source_digest.",
            "Copied packs may differ in path.",
        ),
        lock_source_details(root, extra),
    )


def content_set_determinism(path: Path) -> IntegrityCheck:
    first = content_set(path)
    second = content_set(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.content_set_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Content set ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_content_set(left: Path, right: Path) -> IntegrityCheck:
    first = content_set(left)
    second = content_set(right)
    equal = (
        first.valid
        and second.valid
        and first.details.get("record_source_digest") == second.details.get("record_source_digest")
    )
    return IntegrityCheck(
        "radar_v4.compare_content_set",
        equal,
        None if equal else "CONTENT_SET_MISMATCH",
        (
            "Compared content-set digest only.",
            "The set folder path is not identity.",
        ),
        {
            "equal": equal,
            "left_digest": first.details.get("record_source_digest"),
            "right_digest": second.details.get("record_source_digest"),
        },
    )


def write_content_set_record(
    source: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = content_set(source)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_content_set_record(path: Path) -> IntegrityCheck:
    return verify_recomputed_lock_record(
        path,
        expected_kind="radar_v4.content_set",
        verify_kind="radar_v4.content_set_verify",
        invalid_code="CONTENT_SET_RECORD_INVALID",
        recompute=content_set,
    )


def content_set_status(path: Path) -> IntegrityCheck:
    locked = content_set(path)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.content_set_status",
        matched,
        None if matched else "CONTENT_SET_STATUS_MISMATCH",
        ("Content set and status share the locked unit. Not a measurement.",),
        {
            "set_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
