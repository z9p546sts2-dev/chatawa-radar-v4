"""Bind a source document to a local pack. Does not open HISTORICAL intake."""

from __future__ import annotations

from json import JSONDecodeError, dumps, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.dataset_pack import load_dataset_pack
from radar_v4.fixture_pack import PACK_ALLOWED_PROVENANCE
from radar_v4.integrity import IntegrityCheck, lock_source_details
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.source_lock import source_lock
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


def _dump(document: dict[str, object]) -> str:
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def source_bind(source: Path, pack: Path) -> IntegrityCheck:
    locked = source_lock(source)
    extra = {
        "source_path": str(Path(source).resolve()),
        "pack_path": str(Path(pack).resolve()),
        "source_name": locked.details.get("source_name"),
        "source_provenance": locked.details.get("provenance_class"),
    }
    if not locked.valid:
        extra["failed"] = ["radar_v4.source_lock"]
        return IntegrityCheck(
            "radar_v4.source_bind",
            False,
            locked.error_code,
            ("Source bind failed on the source document.",) + locked.notes,
            lock_source_details(source, extra),
        )
    report = load_dataset_pack(pack)
    declared = None if report.declaration is None else report.declaration.provenance_class
    extra["pack_provenance"] = declared
    extra["failed"] = []
    if report.declaration is None:
        extra["failed"] = ["radar_v4.source_bind"]
        return IntegrityCheck(
            "radar_v4.source_bind",
            False,
            "UNREADABLE_PACK",
            ("Source bind needs a pack declaration.",),
            lock_source_details(source, extra),
        )
    if declared not in PACK_ALLOWED_PROVENANCE:
        extra["failed"] = ["radar_v4.source_bind"]
        return IntegrityCheck(
            "radar_v4.source_bind",
            False,
            "PACK_PROVENANCE_NOT_ALLOWED",
            ("Source bind cannot attach to a HISTORICAL or LIVE pack.",),
            lock_source_details(source, extra),
        )
    matched = declared == locked.details.get("provenance_class")
    return IntegrityCheck(
        "radar_v4.source_bind",
        matched,
        None if matched else "SOURCE_MISMATCH",
        (
            "Source provenance must match the pack declaration.",
            "This does not admit HISTORICAL records.",
        ),
        lock_source_details(source, extra),
    )


def source_bind_determinism(source: Path, pack: Path) -> IntegrityCheck:
    first = source_bind(source, pack)
    second = source_bind(source, pack)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.source_bind_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Source bind ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def write_source_bind_record(
    source: Path, pack: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = source_bind(source, pack)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_source_bind_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.source_bind_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable source-bind record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.source_bind_verify",
            False,
            "UNREADABLE_JSON",
            ("source-bind record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.source_bind_verify",
            False,
            "UNREADABLE_JSON",
            ("source-bind record must be an object",),
            {"path": str(target)},
        )
    details = raw.get("details")
    source = details.get("source_path") if isinstance(details, dict) else None
    pack = details.get("pack_path") if isinstance(details, dict) else None
    if (
        not isinstance(source, str)
        or not source
        or not isinstance(pack, str)
        or not pack
    ):
        return IntegrityCheck(
            "radar_v4.source_bind_verify",
            False,
            "SOURCE_BIND_INVALID",
            ("source-bind record is missing source_path or pack_path; kind+valid is not a verify",),
            {"path": str(target)},
        )
    source_path = Path(source)
    pack_path = Path(pack)
    if not source_path.exists() or not pack_path.exists():
        return IntegrityCheck(
            "radar_v4.source_bind_verify",
            False,
            "UNREADABLE_PACK",
            ("source-bind sources are not present",),
            {"path": str(target), "source_path": source, "pack_path": pack},
        )
    recomputed = source_bind(source_path, pack_path)
    matched = (
        raw.get("document_kind") == "radar_v4.source_bind"
        and raw.get("valid") is True
        and recomputed.valid
        and recomputed.serialize() == _dump(raw)
    )
    if not matched and (
        raw.get("document_kind") != "radar_v4.source_bind" or raw.get("valid") is not True
    ):
        error = "SOURCE_BIND_INVALID"
    elif not matched and not recomputed.valid:
        error = "SOURCE_BIND_INVALID"
    elif not matched:
        error = "RECORD_MISMATCH"
    else:
        error = None
    return IntegrityCheck(
        "radar_v4.source_bind_verify",
        matched,
        error,
        (
            "Verified a source-bind record by recomputing from source and pack.",
            "Not market evidence.",
        ),
        {"path": str(target), "source_path": source, "pack_path": pack},
    )


def source_bind_status(source: Path, pack: Path) -> IntegrityCheck:
    locked = source_bind(source, pack)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
        and status.get("vendor_authorized") is False
    )
    return IntegrityCheck(
        "radar_v4.source_bind_status",
        matched,
        None if matched else "SOURCE_BIND_STATUS_MISMATCH",
        ("Source bind and status share the locked unit. Not a measurement.",),
        {
            "bind_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
