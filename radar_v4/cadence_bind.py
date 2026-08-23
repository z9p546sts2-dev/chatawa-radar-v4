"""Bind a cadence document to a pack declaration. Not a method."""

from __future__ import annotations

from json import JSONDecodeError, dumps, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.cadence_lock import cadence_lock
from radar_v4.dataset_pack import load_dataset_pack
from radar_v4.integrity import IntegrityCheck, lock_source_details
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


def _dump(document: dict[str, object]) -> str:
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def cadence_bind(cadence: Path, pack: Path) -> IntegrityCheck:
    locked = cadence_lock(cadence)
    extra = {
        "cadence_path": str(Path(cadence).resolve()),
        "pack_path": str(Path(pack).resolve()),
        "cadence_interval": locked.details.get("interval"),
        "evaluation_cadence": locked.details.get("evaluation_cadence"),
    }
    if not locked.valid:
        extra["failed"] = ["radar_v4.cadence_lock"]
        return IntegrityCheck(
            "radar_v4.cadence_bind",
            False,
            locked.error_code,
            ("Cadence bind failed on the cadence document.",) + locked.notes,
            lock_source_details(cadence, extra),
        )
    report = load_dataset_pack(pack)
    declared = None if report.declaration is None else report.declaration.interval
    extra["pack_interval"] = declared
    extra["failed"] = []
    if report.declaration is None:
        extra["failed"] = ["radar_v4.cadence_bind"]
        return IntegrityCheck(
            "radar_v4.cadence_bind",
            False,
            "UNREADABLE_PACK",
            ("Cadence bind needs a pack declaration.",),
            lock_source_details(cadence, extra),
        )
    matched = declared == locked.details.get("interval")
    return IntegrityCheck(
        "radar_v4.cadence_bind",
        matched,
        None if matched else "CADENCE_MISMATCH",
        (
            "Cadence interval must match the pack declaration.",
            "This does not invent a calendar or a score.",
        ),
        lock_source_details(cadence, extra),
    )


def cadence_bind_determinism(cadence: Path, pack: Path) -> IntegrityCheck:
    first = cadence_bind(cadence, pack)
    second = cadence_bind(cadence, pack)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.cadence_bind_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Cadence bind ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def write_cadence_bind_record(
    cadence: Path, pack: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = cadence_bind(cadence, pack)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_cadence_bind_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.cadence_bind_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable cadence-bind record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.cadence_bind_verify",
            False,
            "UNREADABLE_JSON",
            ("cadence-bind record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.cadence_bind_verify",
            False,
            "UNREADABLE_JSON",
            ("cadence-bind record must be an object",),
            {"path": str(target)},
        )
    details = raw.get("details")
    cadence = details.get("cadence_path") if isinstance(details, dict) else None
    pack = details.get("pack_path") if isinstance(details, dict) else None
    if not isinstance(cadence, str) or not cadence or not isinstance(pack, str) or not pack:
        return IntegrityCheck(
            "radar_v4.cadence_bind_verify",
            False,
            "CADENCE_BIND_INVALID",
            ("cadence-bind record is missing cadence_path or pack_path; kind+valid is not a verify",),
            {"path": str(target)},
        )
    cadence_path = Path(cadence)
    pack_path = Path(pack)
    if not cadence_path.exists() or not pack_path.exists():
        return IntegrityCheck(
            "radar_v4.cadence_bind_verify",
            False,
            "UNREADABLE_PACK",
            ("cadence-bind sources are not present",),
            {"path": str(target), "cadence_path": cadence, "pack_path": pack},
        )
    recomputed = cadence_bind(cadence_path, pack_path)
    matched = (
        raw.get("document_kind") == "radar_v4.cadence_bind"
        and raw.get("valid") is True
        and recomputed.valid
        and recomputed.serialize() == _dump(raw)
    )
    if not matched and (
        raw.get("document_kind") != "radar_v4.cadence_bind" or raw.get("valid") is not True
    ):
        error = "CADENCE_BIND_INVALID"
    elif not matched and not recomputed.valid:
        error = "CADENCE_BIND_INVALID"
    elif not matched:
        error = "RECORD_MISMATCH"
    else:
        error = None
    return IntegrityCheck(
        "radar_v4.cadence_bind_verify",
        matched,
        error,
        (
            "Verified a cadence-bind record by recomputing from cadence and pack.",
            "Not market evidence.",
        ),
        {"path": str(target), "cadence_path": cadence, "pack_path": pack},
    )


def cadence_bind_status(cadence: Path, pack: Path) -> IntegrityCheck:
    locked = cadence_bind(cadence, pack)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.cadence_bind_status",
        matched,
        None if matched else "CADENCE_BIND_STATUS_MISMATCH",
        ("Cadence bind and status share the locked unit. Not a measurement.",),
        {
            "bind_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
