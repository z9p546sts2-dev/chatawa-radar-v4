"""Bind two lock records by named members. Digest alone is not enough."""

from __future__ import annotations

from json import JSONDecodeError, dumps, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.integrity import IntegrityCheck, lock_source_details
from radar_v4.lock_bind import lock_identity
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


def _dump(document: dict[str, object]) -> str:
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _members_of(path: Path) -> tuple[IntegrityCheck, dict[str, str] | None]:
    identity = lock_identity(path)
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
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


def member_bind(left: Path, right: Path) -> IntegrityCheck:
    first, left_members = _members_of(left)
    second, right_members = _members_of(right)
    extra = {
        "left_path": str(Path(left).resolve()),
        "right_path": str(Path(right).resolve()),
        "left_kind": first.details.get("record_kind"),
        "right_kind": second.details.get("record_kind"),
        "record_source_digest": first.details.get("record_source_digest"),
    }
    if not first.valid:
        return IntegrityCheck(
            "radar_v4.member_bind",
            False,
            first.error_code,
            ("Member bind failed on the left record.",) + first.notes,
            lock_source_details(left, extra),
        )
    if not second.valid:
        return IntegrityCheck(
            "radar_v4.member_bind",
            False,
            second.error_code,
            ("Member bind failed on the right record.",) + second.notes,
            lock_source_details(left, extra),
        )
    if left_members is None or right_members is None:
        extra["failed"] = ["radar_v4.member_bind"]
        return IntegrityCheck(
            "radar_v4.member_bind",
            False,
            "MEMBER_BIND_INVALID",
            ("Member bind needs a members map on both records.",),
            lock_source_details(left, extra),
        )
    matched = left_members == right_members
    extra["left_members"] = sorted(left_members)
    extra["right_members"] = sorted(right_members)
    return IntegrityCheck(
        "radar_v4.member_bind",
        matched,
        None if matched else "MEMBER_BIND_MISMATCH",
        (
            "Two lock records must share the named member map.",
            "source_digest alone is not member identity.",
        ),
        lock_source_details(left, extra),
    )


def member_bind_determinism(left: Path, right: Path) -> IntegrityCheck:
    first = member_bind(left, right)
    second = member_bind(left, right)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.member_bind_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Member bind ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def write_member_bind_record(
    left: Path, right: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = member_bind(left, right)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_member_bind_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.member_bind_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable member-bind record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.member_bind_verify",
            False,
            "UNREADABLE_JSON",
            ("member-bind record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.member_bind_verify",
            False,
            "UNREADABLE_JSON",
            ("member-bind record must be an object",),
            {"path": str(target)},
        )
    details = raw.get("details")
    left = details.get("left_path") if isinstance(details, dict) else None
    right = details.get("right_path") if isinstance(details, dict) else None
    if not isinstance(left, str) or not left or not isinstance(right, str) or not right:
        return IntegrityCheck(
            "radar_v4.member_bind_verify",
            False,
            "MEMBER_BIND_INVALID",
            ("member-bind record is missing left_path or right_path; kind+valid is not a verify",),
            {"path": str(target)},
        )
    left_path = Path(left)
    right_path = Path(right)
    if not left_path.exists() or not right_path.exists():
        return IntegrityCheck(
            "radar_v4.member_bind_verify",
            False,
            "UNREADABLE_PACK",
            ("member-bind source records are not present",),
            {"path": str(target), "left_path": left, "right_path": right},
        )
    recomputed = member_bind(left_path, right_path)
    matched = (
        raw.get("document_kind") == "radar_v4.member_bind"
        and raw.get("valid") is True
        and recomputed.valid
        and recomputed.serialize() == _dump(raw)
    )
    if not matched and (
        raw.get("document_kind") != "radar_v4.member_bind" or raw.get("valid") is not True
    ):
        error = "MEMBER_BIND_INVALID"
    elif not matched and not recomputed.valid:
        error = "MEMBER_BIND_INVALID"
    elif not matched:
        error = "RECORD_MISMATCH"
    else:
        error = None
    return IntegrityCheck(
        "radar_v4.member_bind_verify",
        matched,
        error,
        (
            "Verified a member-bind record by recomputing from both lock files.",
            "Not market evidence.",
        ),
        {"path": str(target), "left_path": left, "right_path": right},
    )


def member_bind_status(left: Path, right: Path) -> IntegrityCheck:
    locked = member_bind(left, right)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.member_bind_status",
        matched,
        None if matched else "MEMBER_BIND_STATUS_MISMATCH",
        ("Member bind and status share the locked unit. Not a measurement.",),
        {
            "bind_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
