"""A folder of lock records must share one member map. Digest is not enough."""

from __future__ import annotations

from json import JSONDecodeError, loads
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


def _members_map(path: Path) -> dict[str, str] | None:
    try:
        raw = loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, JSONDecodeError):
        return None
    if not isinstance(raw, dict):
        return None
    details = raw.get("details")
    members = details.get("members") if isinstance(details, dict) else None
    if not isinstance(members, dict):
        return None
    cleaned: dict[str, str] = {}
    for key, value in members.items():
        if not isinstance(key, str) or not isinstance(value, str):
            return None
        cleaned[key] = value
    return cleaned


def _lock_records(directory: Path) -> list[tuple[IntegrityCheck, dict[str, str] | None]]:
    records: list[tuple[IntegrityCheck, dict[str, str] | None]] = []
    for child in sorted(directory.iterdir()):
        if not child.is_file() or child.suffix != ".json" or child.is_symlink():
            continue
        records.append((lock_identity(child), _members_map(child)))
    return records


def member_set(path: Path) -> IntegrityCheck:
    root = Path(path)
    if not root.is_dir():
        return IntegrityCheck(
            "radar_v4.member_set",
            False,
            "UNREADABLE_PACK",
            ("Member set needs a present directory of lock records.",),
            lock_source_details(root, {"failed": ["radar_v4.lock_identity"]}),
        )
    records = _lock_records(root)
    listing = [
        {
            "path": item.details.get("source_path"),
            "record_kind": item.details.get("record_kind"),
            "record_source_digest": item.details.get("record_source_digest"),
            "has_members": members is not None,
            "valid": item.valid,
        }
        for item, members in records
    ]
    extra: dict[str, object] = {"records": listing, "count": len(records)}
    if not records:
        return IntegrityCheck(
            "radar_v4.member_set",
            False,
            "MEMBER_SET_EMPTY",
            ("Member set needs lock records. An empty folder is not custody.",),
            lock_source_details(root, extra),
        )
    bad = next((item for item, _members in records if not item.valid), None)
    if bad is not None:
        extra["failed"] = [bad.document_kind]
        return IntegrityCheck(
            "radar_v4.member_set",
            False,
            bad.error_code,
            ("Member set refused an invalid lock record.",) + bad.notes,
            lock_source_details(root, extra),
        )
    missing = next((item for item, members in records if members is None), None)
    if missing is not None:
        extra["failed"] = ["radar_v4.member_set"]
        return IntegrityCheck(
            "radar_v4.member_set",
            False,
            "MEMBER_SET_RECORD_INVALID",
            ("Member set needs a members map on every record.",),
            lock_source_details(root, extra),
        )
    if len(records) < 2:
        extra["failed"] = ["radar_v4.lock_identity"]
        return IntegrityCheck(
            "radar_v4.member_set",
            False,
            "MEMBER_SET_TOO_SMALL",
            ("Member set needs at least two records to agree.",),
            lock_source_details(root, extra),
        )
    members = records[0][1]
    assert members is not None
    matched = all(item_members == members for _item, item_members in records)
    extra["failed"] = []
    extra["members"] = members
    extra["member_names"] = sorted(members)
    extra["paths_may_differ"] = True
    return IntegrityCheck(
        "radar_v4.member_set",
        matched,
        None if matched else "MEMBER_BIND_MISMATCH",
        (
            "Every lock record in the folder must share the named member map.",
            "source_digest alone is not member identity.",
        ),
        lock_source_details(root, extra),
    )


def member_set_determinism(path: Path) -> IntegrityCheck:
    first = member_set(path)
    second = member_set(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.member_set_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Member set ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_member_set(left: Path, right: Path) -> IntegrityCheck:
    first = member_set(left)
    second = member_set(right)
    equal = (
        first.valid
        and second.valid
        and first.details.get("members") == second.details.get("members")
    )
    return IntegrityCheck(
        "radar_v4.compare_member_set",
        equal,
        None if equal else "MEMBER_SET_MISMATCH",
        (
            "Compared member-set maps.",
            "The set folder path is not identity.",
        ),
        {
            "equal": equal,
            "left_members": first.details.get("member_names"),
            "right_members": second.details.get("member_names"),
        },
    )


def write_member_set_record(
    source: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = member_set(source)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_member_set_record(path: Path) -> IntegrityCheck:
    return verify_recomputed_lock_record(
        path,
        expected_kind="radar_v4.member_set",
        verify_kind="radar_v4.member_set_verify",
        invalid_code="MEMBER_SET_RECORD_INVALID",
        recompute=member_set,
    )


def member_set_status(path: Path) -> IntegrityCheck:
    locked = member_set(path)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.member_set_status",
        matched,
        None if matched else "MEMBER_SET_STATUS_MISMATCH",
        ("Member set and status share the locked unit. Not a measurement.",),
        {
            "set_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
