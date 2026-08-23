"""Pack-safety identity checks. Not a measurement."""

from __future__ import annotations

from json import JSONDecodeError, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.integrity import IntegrityCheck
from radar_v4.pack_safety import inspect_pack_safety
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


def safety_readable_scan(path: Path) -> IntegrityCheck:
    root = Path(path)
    if not root.is_dir():
        return IntegrityCheck(
            "radar_v4.safety_readable",
            False,
            "UNREADABLE_PACK",
            ("Safety lock needs a pack directory. Not invented.",),
            {"path": str(root)},
        )
    return IntegrityCheck(
        "radar_v4.safety_readable",
        True,
        None,
        ("Pack directory is readable. Not a measurement.",),
        {"path": str(root)},
    )


def safety_lock(path: Path) -> IntegrityCheck:
    readable = safety_readable_scan(path)
    if not readable.valid:
        return IntegrityCheck(
            "radar_v4.safety_lock",
            False,
            readable.error_code,
            ("Safety lock failed.",) + readable.notes,
            {"failed": [readable.document_kind], "issue_codes": []},
        )
    report = inspect_pack_safety(path)
    if not report.safe:
        first = report.issues[0] if report.issues else "PACK_NOT_USABLE"
        return IntegrityCheck(
            "radar_v4.safety_lock",
            False,
            first,
            ("Safety lock failed. Unsafe pack files are not repaired.",),
            {
                "failed": ["radar_v4.pack_safety"],
                "issue_codes": list(report.issues),
            },
        )
    return IntegrityCheck(
        "radar_v4.safety_lock",
        True,
        None,
        ("Safety lock passed. Not market evidence.",),
        {"failed": [], "issue_codes": []},
    )


def safety_lock_determinism(path: Path) -> IntegrityCheck:
    first = safety_lock(path)
    second = safety_lock(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.safety_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Safety lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_safety_lock(left: Path, right: Path) -> IntegrityCheck:
    first = safety_lock(left)
    second = safety_lock(right)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.compare_safety_lock",
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared safety-lock records. Equality is not a score.",),
        {"equal": equal},
    )


def write_safety_record(
    source: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = safety_lock(source)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_safety_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.safety_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable safety-lock record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.safety_verify",
            False,
            "UNREADABLE_JSON",
            ("safety-lock record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.safety_verify",
            False,
            "UNREADABLE_JSON",
            ("safety-lock record must be an object",),
            {"path": str(target)},
        )
    ok = raw.get("document_kind") == "radar_v4.safety_lock" and raw.get("valid") is True
    return IntegrityCheck(
        "radar_v4.safety_verify",
        ok,
        None if ok else "SAFETY_RECORD_INVALID",
        ("Verified a local safety-lock record. Not market evidence.",),
        {"path": str(target)},
    )


def safety_status_bind(path: Path) -> IntegrityCheck:
    locked = safety_lock(path)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.safety_status_bind",
        matched,
        None if matched else "SAFETY_STATUS_MISMATCH",
        ("Safety lock and status share the locked unit. Not a measurement.",),
        {
            "safety_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
