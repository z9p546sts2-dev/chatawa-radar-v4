"""Bind a need document to a local pack. Does not buy data."""

from __future__ import annotations

from json import JSONDecodeError, dumps, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.dataset_pack import load_dataset_pack
from radar_v4.integrity import IntegrityCheck, lock_source_details
from radar_v4.need_lock import need_lock
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


def _dump(document: dict[str, object]) -> str:
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _pack_staleness(value: str | None) -> str:
    if value is None or value.strip() == "":
        return "NONE"
    return value


def need_bind(need: Path, pack: Path) -> IntegrityCheck:
    locked = need_lock(need)
    extra = {
        "need_path": str(Path(need).resolve()),
        "pack_path": str(Path(pack).resolve()),
        "need_adjustment": locked.details.get("adjustment_policy"),
        "need_staleness": locked.details.get("max_staleness"),
    }
    if not locked.valid:
        extra["failed"] = ["radar_v4.need_lock"]
        return IntegrityCheck(
            "radar_v4.need_bind",
            False,
            locked.error_code,
            ("Need bind failed on the need document.",) + locked.notes,
            lock_source_details(need, extra),
        )
    report = load_dataset_pack(pack)
    extra["failed"] = []
    if report.declaration is None:
        extra["failed"] = ["radar_v4.need_bind"]
        return IntegrityCheck(
            "radar_v4.need_bind",
            False,
            "UNREADABLE_PACK",
            ("Need bind needs a pack declaration.",),
            lock_source_details(need, extra),
        )
    declared_adjustment = report.declaration.adjustment_policy
    declared_staleness = _pack_staleness(report.declaration.max_staleness)
    extra["pack_adjustment"] = declared_adjustment
    extra["pack_staleness"] = declared_staleness
    if declared_adjustment != locked.details.get("adjustment_policy"):
        extra["failed"] = ["radar_v4.need_bind"]
        return IntegrityCheck(
            "radar_v4.need_bind",
            False,
            "ADJUSTMENT_MISMATCH",
            (
                "Need adjustment_policy must match the pack declaration.",
                "This does not change the adjustment.",
            ),
            lock_source_details(need, extra),
        )
    matched = declared_staleness == locked.details.get("max_staleness")
    return IntegrityCheck(
        "radar_v4.need_bind",
        matched,
        None if matched else "NEED_MISMATCH",
        (
            "Need max_staleness must match the pack declaration.",
            "NONE means the pack declared no live freshness SLA.",
        ),
        lock_source_details(need, extra),
    )


def need_bind_determinism(need: Path, pack: Path) -> IntegrityCheck:
    first = need_bind(need, pack)
    second = need_bind(need, pack)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.need_bind_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Need bind ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def write_need_bind_record(
    need: Path, pack: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = need_bind(need, pack)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_need_bind_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.need_bind_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable need-bind record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.need_bind_verify",
            False,
            "UNREADABLE_JSON",
            ("need-bind record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.need_bind_verify",
            False,
            "UNREADABLE_JSON",
            ("need-bind record must be an object",),
            {"path": str(target)},
        )
    details = raw.get("details")
    need = details.get("need_path") if isinstance(details, dict) else None
    pack = details.get("pack_path") if isinstance(details, dict) else None
    if not isinstance(need, str) or not need or not isinstance(pack, str) or not pack:
        return IntegrityCheck(
            "radar_v4.need_bind_verify",
            False,
            "NEED_BIND_INVALID",
            ("need-bind record is missing need_path or pack_path; kind+valid is not a verify",),
            {"path": str(target)},
        )
    need_path = Path(need)
    pack_path = Path(pack)
    if not need_path.exists() or not pack_path.exists():
        return IntegrityCheck(
            "radar_v4.need_bind_verify",
            False,
            "UNREADABLE_PACK",
            ("need-bind sources are not present",),
            {"path": str(target), "need_path": need, "pack_path": pack},
        )
    recomputed = need_bind(need_path, pack_path)
    matched = (
        raw.get("document_kind") == "radar_v4.need_bind"
        and raw.get("valid") is True
        and recomputed.valid
        and recomputed.serialize() == _dump(raw)
    )
    if not matched and (
        raw.get("document_kind") != "radar_v4.need_bind" or raw.get("valid") is not True
    ):
        error = "NEED_BIND_INVALID"
    elif not matched and not recomputed.valid:
        error = "NEED_BIND_INVALID"
    elif not matched:
        error = "RECORD_MISMATCH"
    else:
        error = None
    return IntegrityCheck(
        "radar_v4.need_bind_verify",
        matched,
        error,
        (
            "Verified a need-bind record by recomputing from need and pack.",
            "Not market evidence.",
        ),
        {"path": str(target), "need_path": need, "pack_path": pack},
    )


def need_bind_status(need: Path, pack: Path) -> IntegrityCheck:
    locked = need_bind(need, pack)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
        and status.get("vendor_authorized") is False
    )
    return IntegrityCheck(
        "radar_v4.need_bind_status",
        matched,
        None if matched else "NEED_BIND_STATUS_MISMATCH",
        ("Need bind and status share the locked unit. Not a measurement.",),
        {
            "bind_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
