"""A window may not include bars after as-of. Not a score."""

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

HORIZON_FILENAME = "horizon.json"
HORIZON_KIND = "radar_v4.horizon"


def _horizon_path(path: Path) -> Path:
    root = Path(path)
    if root.is_dir():
        return root / HORIZON_FILENAME
    return root


def _load_horizon(path: Path) -> tuple[dict[str, object] | None, IntegrityCheck | None]:
    target = _horizon_path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return None, IntegrityCheck(
            "radar_v4.horizon_lock",
            False,
            "HORIZON_MISSING",
            ("Horizon lock needs a present horizon document.",),
            lock_source_details(target),
        )
    except JSONDecodeError:
        return None, IntegrityCheck(
            "radar_v4.horizon_lock",
            False,
            "UNREADABLE_JSON",
            ("Horizon document is not JSON.",),
            lock_source_details(target),
        )
    if not isinstance(raw, dict):
        return None, IntegrityCheck(
            "radar_v4.horizon_lock",
            False,
            "HORIZON_RECORD_INVALID",
            ("Horizon document must be an object.",),
            lock_source_details(target),
        )
    return raw, None


def horizon_lock(path: Path) -> IntegrityCheck:
    target = _horizon_path(path)
    raw, error = _load_horizon(path)
    if error is not None:
        return error
    assert raw is not None
    as_of = raw.get("as_of")
    include_through = raw.get("include_through")
    extra: dict[str, object] = {
        "as_of": as_of if isinstance(as_of, str) else None,
        "include_through": include_through if isinstance(include_through, str) else None,
    }
    if raw.get("document_kind") != HORIZON_KIND:
        extra["failed"] = ["radar_v4.horizon_lock"]
        return IntegrityCheck(
            "radar_v4.horizon_lock",
            False,
            "HORIZON_RECORD_INVALID",
            ("A horizon document must name radar_v4.horizon.",),
            lock_source_details(target, extra),
        )
    if (
        not isinstance(as_of, str)
        or not as_of
        or not isinstance(include_through, str)
        or not include_through
    ):
        extra["failed"] = ["radar_v4.horizon_lock"]
        return IntegrityCheck(
            "radar_v4.horizon_lock",
            False,
            "HORIZON_RECORD_INVALID",
            ("Horizon document needs as_of and include_through.",),
            lock_source_details(target, extra),
        )
    try:
        stamp = parse_canonical_timestamp(as_of)
        window = parse_canonical_timestamp(include_through)
    except ValueError:
        extra["failed"] = ["radar_v4.horizon_lock"]
        return IntegrityCheck(
            "radar_v4.horizon_lock",
            False,
            "HORIZON_RECORD_INVALID",
            ("as_of and include_through must be timezone-aware timestamps.",),
            lock_source_details(target, extra),
        )
    if window > stamp:
        extra["failed"] = ["radar_v4.horizon_lock"]
        return IntegrityCheck(
            "radar_v4.horizon_lock",
            False,
            "LOOKAHEAD_WINDOW",
            (
                "include_through may not be after as_of.",
                "A later bar is not known at an earlier clock.",
            ),
            lock_source_details(target, extra),
        )
    extra["failed"] = []
    return IntegrityCheck(
        "radar_v4.horizon_lock",
        True,
        None,
        (
            "Horizon window does not look ahead of as_of.",
            "This is not a score and not a method.",
        ),
        lock_source_details(target, extra),
    )


def horizon_lock_determinism(path: Path) -> IntegrityCheck:
    first = horizon_lock(path)
    second = horizon_lock(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.horizon_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Horizon lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_horizon_lock(left: Path, right: Path) -> IntegrityCheck:
    first = horizon_lock(left)
    second = horizon_lock(right)
    equal = (
        first.valid
        and second.valid
        and first.details.get("as_of") == second.details.get("as_of")
        and first.details.get("include_through") == second.details.get("include_through")
    )
    return IntegrityCheck(
        "radar_v4.compare_horizon_lock",
        equal,
        None if equal else "HORIZON_MISMATCH",
        (
            "Compared horizon identity only.",
            "Path is not horizon.",
        ),
        {
            "equal": equal,
            "left_as_of": first.details.get("as_of"),
            "right_as_of": second.details.get("as_of"),
        },
    )


def write_horizon_record(
    source: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = horizon_lock(source)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_horizon_record(path: Path) -> IntegrityCheck:
    return verify_recomputed_lock_record(
        path,
        expected_kind="radar_v4.horizon_lock",
        verify_kind="radar_v4.horizon_verify",
        invalid_code="HORIZON_RECORD_INVALID",
        recompute=horizon_lock,
    )


def horizon_status_bind(path: Path) -> IntegrityCheck:
    locked = horizon_lock(path)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.horizon_status_bind",
        matched,
        None if matched else "HORIZON_STATUS_MISMATCH",
        ("Horizon lock and status share the locked unit. Not a measurement.",),
        {
            "horizon_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
