"""Leftover-file identity checks. Not a method."""

from __future__ import annotations

from json import loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.integrity import (
    IntegrityCheck,
    lock_source_details,
    verify_recomputed_lock_record,
)
from radar_v4.record_check import inspect_leftovers
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


def leftover_lock(path: Path) -> IntegrityCheck:
    leftovers = inspect_leftovers(path)
    details = lock_source_details(path, leftovers.details)
    if not leftovers.valid:
        return IntegrityCheck(
            "radar_v4.leftover_lock",
            False,
            leftovers.error_code,
            ("Leftover lock failed. Leftovers are not repaired.",) + leftovers.notes,
            details,
        )
    return IntegrityCheck(
        "radar_v4.leftover_lock",
        True,
        None,
        ("Leftover lock passed. Not market evidence.",),
        details,
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
    return verify_recomputed_lock_record(
        path,
        expected_kind="radar_v4.leftover_lock",
        verify_kind="radar_v4.leftover_verify",
        invalid_code="LEFTOVER_RECORD_INVALID",
        recompute=leftover_lock,
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
