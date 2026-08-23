"""Leftover-file identity checks. Not a method."""

from __future__ import annotations

from json import JSONDecodeError, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.integrity import IntegrityCheck
from radar_v4.record_check import inspect_leftovers
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


def leftover_lock(path: Path) -> IntegrityCheck:
    leftovers = inspect_leftovers(path)
    if not leftovers.valid:
        return IntegrityCheck(
            "radar_v4.leftover_lock",
            False,
            leftovers.error_code,
            ("Leftover lock failed. Leftovers are not repaired.",) + leftovers.notes,
            leftovers.details,
        )
    return IntegrityCheck(
        "radar_v4.leftover_lock",
        True,
        None,
        ("Leftover lock passed. Not market evidence.",),
        leftovers.details,
    )


def leftover_lock_determinism(path: Path) -> IntegrityCheck:
    first = leftover_lock(path)
    second = leftover_lock(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.leftover_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Leftover lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_leftover_lock(left: Path, right: Path) -> IntegrityCheck:
    first = leftover_lock(left)
    second = leftover_lock(right)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.compare_leftover_lock",
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared leftover-lock records. Equality is not a score.",),
        {"equal": equal},
    )


def write_leftover_record(
    source: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = leftover_lock(source)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_leftover_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.leftover_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable leftover-lock record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.leftover_verify",
            False,
            "UNREADABLE_JSON",
            ("leftover-lock record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.leftover_verify",
            False,
            "UNREADABLE_JSON",
            ("leftover-lock record must be an object",),
            {"path": str(target)},
        )
    ok = raw.get("document_kind") == "radar_v4.leftover_lock" and raw.get("valid") is True
    return IntegrityCheck(
        "radar_v4.leftover_verify",
        ok,
        None if ok else "LEFTOVER_RECORD_INVALID",
        ("Verified a local leftover-lock record. Not market evidence.",),
        {"path": str(target)},
    )


def leftover_status_bind(path: Path) -> IntegrityCheck:
    locked = leftover_lock(path)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.leftover_status_bind",
        matched,
        None if matched else "LEFTOVER_STATUS_MISMATCH",
        ("Leftover lock and status share the locked unit. Not a measurement.",),
        {
            "leftover_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
