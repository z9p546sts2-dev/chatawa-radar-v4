"""Workshop stamp and name-record binds. Not a research result."""

from __future__ import annotations

from json import JSONDecodeError, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.integrity import IntegrityCheck
from radar_v4.kind_lock import kind_lock
from radar_v4.local_session import run_session_from_pack
from radar_v4.name_lock import name_lock
from radar_v4.pack_export import PackExportError, export_snapshot_to_pack
from radar_v4.record_eq import snapshot_count_bind
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


def workshop_stamp(directory: Path) -> IntegrityCheck:
    parts = [
        name_lock(directory),
        kind_lock(directory),
        snapshot_count_bind(directory),
    ]
    failed = [part for part in parts if not part.valid]
    if failed:
        first = failed[0]
        return IntegrityCheck(
            "radar_v4.workshop_stamp",
            False,
            first.error_code or "STAMP_FAILED",
            ("Workshop stamp failed.",) + first.notes,
            {"failed": [part.document_kind for part in failed]},
        )
    return IntegrityCheck(
        "radar_v4.workshop_stamp",
        True,
        None,
        ("Workshop stamp passed. Not a research result.",),
        {"failed": []},
    )


def stamp_determinism(directory: Path) -> IntegrityCheck:
    first = workshop_stamp(directory)
    second = workshop_stamp(directory)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.stamp_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Stamp ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_stamp(left_dir: Path, right_dir: Path) -> IntegrityCheck:
    left = workshop_stamp(left_dir)
    right = workshop_stamp(right_dir)
    equal = left.serialize() == right.serialize()
    return IntegrityCheck(
        "radar_v4.compare_stamp",
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared workshop stamps. Equality is not market evidence.",),
        {"equal": equal},
    )


def write_stamp_record(
    directory: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = workshop_stamp(directory)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_stamp_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.stamp_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable stamp record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.stamp_verify",
            False,
            "UNREADABLE_JSON",
            ("stamp record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.stamp_verify",
            False,
            "UNREADABLE_JSON",
            ("stamp record must be an object",),
            {"path": str(target)},
        )
    ok = raw.get("document_kind") == "radar_v4.workshop_stamp" and raw.get("valid") is True
    return IntegrityCheck(
        "radar_v4.stamp_verify",
        ok,
        None if ok else "STAMP_RECORD_INVALID",
        ("Verified a local stamp record. Not market evidence.",),
        {"path": str(target)},
    )


def name_status_bind(directory: Path) -> IntegrityCheck:
    locked = name_lock(directory)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.name_status_bind",
        matched,
        None if matched else "NAME_STATUS_MISMATCH",
        ("Name lock and status share the locked unit. Not a measurement.",),
        {
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "name_valid": locked.valid,
            "status_unit": status_unit,
        },
    )


def export_name_check(directory: Path, destination: Path) -> IntegrityCheck:
    first = run_session_from_pack(directory)
    if first.session is None:
        return IntegrityCheck(
            "radar_v4.export_name",
            False,
            first.error_code or "PACK_NOT_USABLE",
            ("Export name-check needs a usable pack.",),
            {},
        )
    try:
        written = export_snapshot_to_pack(first.session.snapshot, destination)
    except PackExportError as exc:
        return IntegrityCheck(
            "radar_v4.export_name",
            False,
            exc.code,
            (exc.reason,),
            {},
        )
    parts = [name_lock(written), kind_lock(written)]
    failed = [part for part in parts if not part.valid]
    if failed:
        first_fail = failed[0]
        return IntegrityCheck(
            "radar_v4.export_name",
            False,
            first_fail.error_code,
            ("Exported pack failed portable name/kind checks.",) + first_fail.notes,
            {"failed": [part.document_kind for part in failed], "directory": str(written)},
        )
    return IntegrityCheck(
        "radar_v4.export_name",
        True,
        None,
        (
            "Exported pack passed portable name and kind checks.",
            "Export filenames are not fixture obs_YYYY-MM-DD names.",
            "Not market evidence.",
        ),
        {"failed": [], "directory": str(written)},
    )


def kind_lock_determinism(directory: Path) -> IntegrityCheck:
    first = kind_lock(directory)
    second = kind_lock(directory)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.kind_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Kind lock ran twice. Equality is not a taxonomy score.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_kind_lock(left_dir: Path, right_dir: Path) -> IntegrityCheck:
    left = kind_lock(left_dir)
    right = kind_lock(right_dir)
    equal = left.serialize() == right.serialize()
    return IntegrityCheck(
        "radar_v4.compare_kind_lock",
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared kind-lock records. Equality is not a method.",),
        {"equal": equal},
    )


def write_kind_record(
    directory: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = kind_lock(directory)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_kind_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.kind_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable kind-lock record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.kind_verify",
            False,
            "UNREADABLE_JSON",
            ("kind-lock record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.kind_verify",
            False,
            "UNREADABLE_JSON",
            ("kind-lock record must be an object",),
            {"path": str(target)},
        )
    ok = raw.get("document_kind") == "radar_v4.kind_lock" and raw.get("valid") is True
    return IntegrityCheck(
        "radar_v4.kind_verify",
        ok,
        None if ok else "KIND_RECORD_INVALID",
        ("Verified a local kind-lock record. Not market evidence.",),
        {"path": str(target)},
    )


def stamp_status_bind(directory: Path) -> IntegrityCheck:
    stamped = workshop_stamp(directory)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        stamped.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.stamp_status_bind",
        matched,
        None if matched else "STAMP_STATUS_MISMATCH",
        ("Stamp and status share the locked unit. Not a measurement.",),
        {
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "stamp_valid": stamped.valid,
            "status_unit": status_unit,
        },
    )
