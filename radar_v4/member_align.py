"""Align a stored member map to a live path. Verify stays on source_path."""

from __future__ import annotations

from json import JSONDecodeError, dumps, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.integrity import IntegrityCheck, lock_source_details
from radar_v4.lock_bind import lock_identity
from radar_v4.member_lock import source_members
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


def _dump(document: dict[str, object]) -> str:
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _record_members(path: Path) -> tuple[IntegrityCheck, dict[str, str] | None]:
    identity = lock_identity(path)
    try:
        raw = loads(Path(path).read_text(encoding="utf-8"))
    except OSError:
        return identity, None
    except JSONDecodeError:
        return identity, None
    if not isinstance(raw, dict):
        return identity, None
    details = raw.get("details")
    members = details.get("members") if isinstance(details, dict) else None
    if not isinstance(members, dict):
        return identity, None
    cleaned: dict[str, str] = {}
    for key, value in members.items():
        if not isinstance(key, str) or not isinstance(value, str):
            return identity, None
        cleaned[key] = value
    return identity, cleaned


def member_align(record: Path, live: Path) -> IntegrityCheck:
    identity, members = _record_members(record)
    live_root = Path(live)
    extra = {
        "record_path": str(Path(record).resolve()),
        "live_path": str(live_root.resolve()),
        "record_kind": identity.details.get("record_kind"),
        "record_source_path": identity.details.get("record_source_path"),
        "record_source_digest": identity.details.get("record_source_digest"),
    }
    if not identity.valid:
        return IntegrityCheck(
            "radar_v4.member_align",
            False,
            identity.error_code,
            ("Member align failed on the stored record.",) + identity.notes,
            lock_source_details(record, extra),
        )
    if members is None:
        extra["failed"] = ["radar_v4.member_align"]
        return IntegrityCheck(
            "radar_v4.member_align",
            False,
            "MEMBER_ALIGN_INVALID",
            ("Member align needs a members map on the stored record.",),
            lock_source_details(record, extra),
        )
    if not live_root.exists():
        extra["failed"] = ["radar_v4.member_align"]
        return IntegrityCheck(
            "radar_v4.member_align",
            False,
            "UNREADABLE_PACK",
            ("Member align needs a present live path.",),
            lock_source_details(record, extra),
        )
    live_members = source_members(live_root)
    matched = members == live_members
    extra["failed"] = []
    extra["member_names"] = sorted(members)
    extra["live_names"] = sorted(live_members)
    extra["paths_may_differ"] = True
    return IntegrityCheck(
        "radar_v4.member_align",
        matched,
        None if matched else "MEMBER_ALIGN_MISMATCH",
        (
            "The stored member map must match the live path.",
            "Verify still uses source_path. Align may use a copy.",
        ),
        lock_source_details(record, extra),
    )


def member_align_determinism(record: Path, live: Path) -> IntegrityCheck:
    first = member_align(record, live)
    second = member_align(record, live)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.member_align_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Member align ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def write_member_align_record(
    record: Path, live: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    locked = member_align(record, live)
    write_text_atomic(destination, locked.serialize() + "\n")
    return locked


def verify_member_align_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.member_align_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable member-align record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.member_align_verify",
            False,
            "UNREADABLE_JSON",
            ("member-align record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.member_align_verify",
            False,
            "UNREADABLE_JSON",
            ("member-align record must be an object",),
            {"path": str(target)},
        )
    details = raw.get("details")
    record = details.get("record_path") if isinstance(details, dict) else None
    live = details.get("live_path") if isinstance(details, dict) else None
    if not isinstance(record, str) or not record or not isinstance(live, str) or not live:
        return IntegrityCheck(
            "radar_v4.member_align_verify",
            False,
            "MEMBER_ALIGN_INVALID",
            ("member-align record is missing record_path or live_path; kind+valid is not a verify",),
            {"path": str(target)},
        )
    record_path = Path(record)
    live_path = Path(live)
    if not record_path.exists() or not live_path.exists():
        return IntegrityCheck(
            "radar_v4.member_align_verify",
            False,
            "UNREADABLE_PACK",
            ("member-align sources are not present",),
            {"path": str(target), "record_path": record, "live_path": live},
        )
    recomputed = member_align(record_path, live_path)
    matched = (
        raw.get("document_kind") == "radar_v4.member_align"
        and raw.get("valid") is True
        and recomputed.valid
        and recomputed.serialize() == _dump(raw)
    )
    if not matched and (
        raw.get("document_kind") != "radar_v4.member_align" or raw.get("valid") is not True
    ):
        error = "MEMBER_ALIGN_INVALID"
    elif not matched and not recomputed.valid:
        error = "MEMBER_ALIGN_INVALID"
    elif not matched:
        error = "RECORD_MISMATCH"
    else:
        error = None
    return IntegrityCheck(
        "radar_v4.member_align_verify",
        matched,
        error,
        (
            "Verified a member-align record by recomputing from record and live path.",
            "Not market evidence.",
        ),
        {"path": str(target), "record_path": record, "live_path": live},
    )


def member_align_status(record: Path, live: Path) -> IntegrityCheck:
    locked = member_align(record, live)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.member_align_status",
        matched,
        None if matched else "MEMBER_ALIGN_STATUS_MISMATCH",
        ("Member align and status share the locked unit. Not a measurement.",),
        {
            "align_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
