"""Bind two lock records to one source. Not a measurement."""

from __future__ import annotations

from json import JSONDecodeError, dumps, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.integrity import IntegrityCheck, lock_source_details
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status

_HEX = frozenset("0123456789abcdef")


def _dump(document: dict[str, object]) -> str:
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def lock_identity(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.lock_identity",
            False,
            "UNREADABLE_JSON",
            ("Lock identity needs a readable JSON file.",),
            lock_source_details(target),
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.lock_identity",
            False,
            "UNREADABLE_JSON",
            ("Lock identity needs JSON.",),
            lock_source_details(target),
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.lock_identity",
            False,
            "LOCK_RECORD_INVALID",
            ("Lock identity needs a JSON object.",),
            lock_source_details(target),
        )
    kind = raw.get("document_kind")
    details = raw.get("details")
    source = details.get("source_path") if isinstance(details, dict) else None
    digest = details.get("source_digest") if isinstance(details, dict) else None
    ok = (
        isinstance(kind, str)
        and kind.startswith("radar_v4.")
        and isinstance(source, str)
        and bool(source)
        and isinstance(digest, str)
        and len(digest) == 64
        and all(char in _HEX for char in digest)
    )
    return IntegrityCheck(
        "radar_v4.lock_identity",
        ok,
        None if ok else "LOCK_RECORD_INVALID",
        (
            "Lock identity needs source_path and source_digest.",
            "This is custody, not a score.",
        ),
        lock_source_details(
            target,
            {
                "record_kind": kind if isinstance(kind, str) else None,
                "record_source_path": source if isinstance(source, str) else None,
                "record_source_digest": digest if isinstance(digest, str) else None,
            },
        ),
    )


def bind_lock_records(left: Path, right: Path) -> IntegrityCheck:
    first = lock_identity(left)
    second = lock_identity(right)
    extra = {
        "left_path": str(Path(left).resolve()),
        "right_path": str(Path(right).resolve()),
        "left_kind": first.details.get("record_kind"),
        "right_kind": second.details.get("record_kind"),
        "record_source_path": first.details.get("record_source_path"),
        "record_source_digest": first.details.get("record_source_digest"),
    }
    if not first.valid:
        return IntegrityCheck(
            "radar_v4.lock_bind",
            False,
            first.error_code,
            ("Lock bind failed on the left record.",) + first.notes,
            lock_source_details(left, extra),
        )
    if not second.valid:
        return IntegrityCheck(
            "radar_v4.lock_bind",
            False,
            second.error_code,
            ("Lock bind failed on the right record.",) + second.notes,
            lock_source_details(left, extra),
        )
    matched = (
        first.details.get("record_source_path") == second.details.get("record_source_path")
        and first.details.get("record_source_digest")
        == second.details.get("record_source_digest")
    )
    return IntegrityCheck(
        "radar_v4.lock_bind",
        matched,
        None if matched else "LOCK_BIND_MISMATCH",
        (
            "Two lock records must name the same source.",
            "Agreement is not a method.",
        ),
        lock_source_details(left, extra),
    )


def lock_bind_determinism(left: Path, right: Path) -> IntegrityCheck:
    first = bind_lock_records(left, right)
    second = bind_lock_records(left, right)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.lock_bind_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Lock bind ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def write_lock_bind_record(
    left: Path, right: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = bind_lock_records(left, right)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_lock_bind_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.lock_bind_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable lock-bind record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.lock_bind_verify",
            False,
            "UNREADABLE_JSON",
            ("lock-bind record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.lock_bind_verify",
            False,
            "UNREADABLE_JSON",
            ("lock-bind record must be an object",),
            {"path": str(target)},
        )
    details = raw.get("details")
    left = details.get("left_path") if isinstance(details, dict) else None
    right = details.get("right_path") if isinstance(details, dict) else None
    if not isinstance(left, str) or not left or not isinstance(right, str) or not right:
        return IntegrityCheck(
            "radar_v4.lock_bind_verify",
            False,
            "LOCK_BIND_INVALID",
            ("lock-bind record is missing left_path or right_path; kind+valid is not a verify",),
            {"path": str(target)},
        )
    left_path = Path(left)
    right_path = Path(right)
    if not left_path.exists() or not right_path.exists():
        return IntegrityCheck(
            "radar_v4.lock_bind_verify",
            False,
            "UNREADABLE_PACK",
            ("lock-bind source records are not present",),
            {"path": str(target), "left_path": left, "right_path": right},
        )
    recomputed = bind_lock_records(left_path, right_path)
    matched = (
        raw.get("document_kind") == "radar_v4.lock_bind"
        and raw.get("valid") is True
        and recomputed.valid
        and recomputed.serialize() == _dump(raw)
    )
    if not matched and (
        raw.get("document_kind") != "radar_v4.lock_bind" or raw.get("valid") is not True
    ):
        error = "LOCK_BIND_INVALID"
    elif not matched and not recomputed.valid:
        error = "LOCK_BIND_INVALID"
    elif not matched:
        error = "RECORD_MISMATCH"
    else:
        error = None
    return IntegrityCheck(
        "radar_v4.lock_bind_verify",
        matched,
        error,
        (
            "Verified a lock-bind record by recomputing from both lock files.",
            "Not market evidence.",
        ),
        {"path": str(target), "left_path": left, "right_path": right},
    )


def lock_bind_status(left: Path, right: Path) -> IntegrityCheck:
    locked = bind_lock_records(left, right)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.lock_bind_status",
        matched,
        None if matched else "LOCK_BIND_STATUS_MISMATCH",
        ("Lock bind and status share the locked unit. Not a measurement.",),
        {
            "bind_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
