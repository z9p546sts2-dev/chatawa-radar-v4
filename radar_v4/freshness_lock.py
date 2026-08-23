"""A freshness stamp is not a current series. Not a score."""

from __future__ import annotations

from json import JSONDecodeError, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.evidence import parse_canonical_timestamp
from radar_v4.integrity import (
    IntegrityCheck,
    lock_source_details,
    verify_recomputed_lock_record,
)
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status

FRESHNESS_FILENAME = "freshness.json"
FRESHNESS_KIND = "radar_v4.freshness"


def _freshness_path(path: Path) -> Path:
    root = Path(path)
    if root.is_dir():
        return root / FRESHNESS_FILENAME
    return root


def _load_freshness(path: Path) -> tuple[dict[str, object] | None, IntegrityCheck | None]:
    target = _freshness_path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return None, IntegrityCheck(
            "radar_v4.freshness_lock",
            False,
            "FRESHNESS_MISSING",
            ("Freshness lock needs a present freshness document.",),
            lock_source_details(target),
        )
    except JSONDecodeError:
        return None, IntegrityCheck(
            "radar_v4.freshness_lock",
            False,
            "UNREADABLE_JSON",
            ("Freshness document is not JSON.",),
            lock_source_details(target),
        )
    if not isinstance(raw, dict):
        return None, IntegrityCheck(
            "radar_v4.freshness_lock",
            False,
            "FRESHNESS_RECORD_INVALID",
            ("Freshness document must be an object.",),
            lock_source_details(target),
        )
    return raw, None


def freshness_lock(path: Path) -> IntegrityCheck:
    target = _freshness_path(path)
    raw, error = _load_freshness(path)
    if error is not None:
        return error
    assert raw is not None
    as_of = raw.get("as_of")
    claim = raw.get("claim_current")
    extra: dict[str, object] = {
        "as_of": as_of if isinstance(as_of, str) else None,
        "claim_current": claim if isinstance(claim, bool) else None,
    }
    if raw.get("document_kind") != FRESHNESS_KIND:
        extra["failed"] = ["radar_v4.freshness_lock"]
        return IntegrityCheck(
            "radar_v4.freshness_lock",
            False,
            "FRESHNESS_RECORD_INVALID",
            ("A freshness document must name radar_v4.freshness.",),
            lock_source_details(target, extra),
        )
    if not isinstance(as_of, str) or not as_of or not isinstance(claim, bool):
        extra["failed"] = ["radar_v4.freshness_lock"]
        return IntegrityCheck(
            "radar_v4.freshness_lock",
            False,
            "FRESHNESS_RECORD_INVALID",
            ("Freshness document needs as_of and claim_current.",),
            lock_source_details(target, extra),
        )
    try:
        parse_canonical_timestamp(as_of)
    except ValueError:
        extra["failed"] = ["radar_v4.freshness_lock"]
        return IntegrityCheck(
            "radar_v4.freshness_lock",
            False,
            "FRESHNESS_RECORD_INVALID",
            ("as_of must be a timezone-aware timestamp.",),
            lock_source_details(target, extra),
        )
    extra["failed"] = []
    return IntegrityCheck(
        "radar_v4.freshness_lock",
        True,
        None,
        (
            "Freshness document is readable.",
            "A stamp is not a current series.",
        ),
        lock_source_details(target, extra),
    )


def freshness_lock_determinism(path: Path) -> IntegrityCheck:
    first = freshness_lock(path)
    second = freshness_lock(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.freshness_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Freshness lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_freshness_lock(left: Path, right: Path) -> IntegrityCheck:
    first = freshness_lock(left)
    second = freshness_lock(right)
    equal = (
        first.valid
        and second.valid
        and first.details.get("as_of") == second.details.get("as_of")
        and first.details.get("claim_current") == second.details.get("claim_current")
    )
    return IntegrityCheck(
        "radar_v4.compare_freshness_lock",
        equal,
        None if equal else "FRESHNESS_MISMATCH",
        (
            "Compared freshness identity only.",
            "Path is not freshness.",
        ),
        {
            "equal": equal,
            "left_as_of": first.details.get("as_of"),
            "right_as_of": second.details.get("as_of"),
        },
    )


def write_freshness_record(
    source: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = freshness_lock(source)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_freshness_record(path: Path) -> IntegrityCheck:
    return verify_recomputed_lock_record(
        path,
        expected_kind="radar_v4.freshness_lock",
        verify_kind="radar_v4.freshness_verify",
        invalid_code="FRESHNESS_RECORD_INVALID",
        recompute=freshness_lock,
    )


def freshness_status_bind(path: Path) -> IntegrityCheck:
    locked = freshness_lock(path)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.freshness_status_bind",
        matched,
        None if matched else "FRESHNESS_STATUS_MISMATCH",
        ("Freshness lock and status share the locked unit. Not a measurement.",),
        {
            "freshness_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
