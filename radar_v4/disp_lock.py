"""Human-disposition identity checks. Not a trade approval."""

from __future__ import annotations

from json import loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.integrity import (
    IntegrityCheck,
    lock_source_details,
    verify_recomputed_lock_record,
)
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import read_disposition


def disposition_lock(path: Path) -> IntegrityCheck:
    inner = read_disposition(path)
    if not inner.valid:
        return IntegrityCheck(
            "radar_v4.disposition_lock",
            False,
            inner.error_code,
            ("Disposition lock failed.",) + inner.notes,
            lock_source_details(path, {"failed": [inner.document_kind]}),
        )
    return IntegrityCheck(
        "radar_v4.disposition_lock",
        True,
        None,
        ("Disposition lock passed. Not a trade approval.",),
        lock_source_details(path, {"failed": []}),
    )


def disposition_lock_determinism(path: Path) -> IntegrityCheck:
    first = disposition_lock(path)
    second = disposition_lock(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.disposition_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Disposition lock ran twice. Equality is not a ranking.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_disposition_lock(left: Path, right: Path) -> IntegrityCheck:
    first = disposition_lock(left)
    second = disposition_lock(right)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.compare_disposition",
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared disposition-lock records. Equality is not usefulness.",),
        {"equal": equal},
    )


def write_disposition_record(
    source: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = disposition_lock(source)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_disposition_record(path: Path) -> IntegrityCheck:
    return verify_recomputed_lock_record(
        path,
        expected_kind="radar_v4.disposition_lock",
        verify_kind="radar_v4.disposition_verify",
        invalid_code="DISPOSITION_RECORD_INVALID",
        recompute=disposition_lock,
    )


def disposition_status_bind(path: Path) -> IntegrityCheck:
    locked = disposition_lock(path)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.disposition_status_bind",
        matched,
        None if matched else "DISPOSITION_STATUS_MISMATCH",
        ("Disposition lock and status share the locked unit. Not a measurement.",),
        {
            "disposition_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
