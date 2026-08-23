"""Evaluation cadence may not outrun bar interval. Not a score."""

from __future__ import annotations

from json import JSONDecodeError, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.integrity import (
    IntegrityCheck,
    lock_source_details,
    verify_recomputed_lock_record,
)
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status

CADENCE_FILENAME = "cadence.json"
CADENCE_KIND = "radar_v4.cadence"
CADENCE_ORDER = ("1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w")


def _cadence_path(path: Path) -> Path:
    root = Path(path)
    if root.is_dir():
        return root / CADENCE_FILENAME
    return root


def _rank(value: str) -> int | None:
    try:
        return CADENCE_ORDER.index(value)
    except ValueError:
        return None


def _load_cadence(path: Path) -> tuple[dict[str, object] | None, IntegrityCheck | None]:
    target = _cadence_path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return None, IntegrityCheck(
            "radar_v4.cadence_lock",
            False,
            "CADENCE_MISSING",
            ("Cadence lock needs a present cadence document.",),
            lock_source_details(target),
        )
    except JSONDecodeError:
        return None, IntegrityCheck(
            "radar_v4.cadence_lock",
            False,
            "UNREADABLE_JSON",
            ("Cadence document is not JSON.",),
            lock_source_details(target),
        )
    if not isinstance(raw, dict):
        return None, IntegrityCheck(
            "radar_v4.cadence_lock",
            False,
            "CADENCE_RECORD_INVALID",
            ("Cadence document must be an object.",),
            lock_source_details(target),
        )
    return raw, None


def cadence_lock(path: Path) -> IntegrityCheck:
    target = _cadence_path(path)
    raw, error = _load_cadence(path)
    if error is not None:
        return error
    assert raw is not None
    interval = raw.get("interval")
    evaluation = raw.get("evaluation_cadence")
    extra = {
        "interval": interval if isinstance(interval, str) else None,
        "evaluation_cadence": evaluation if isinstance(evaluation, str) else None,
    }
    if raw.get("document_kind") != CADENCE_KIND:
        extra["failed"] = ["radar_v4.cadence_lock"]
        return IntegrityCheck(
            "radar_v4.cadence_lock",
            False,
            "CADENCE_RECORD_INVALID",
            ("A cadence document must name radar_v4.cadence.",),
            lock_source_details(target, extra),
        )
    if not isinstance(interval, str) or not interval or not isinstance(evaluation, str) or not evaluation:
        extra["failed"] = ["radar_v4.cadence_lock"]
        return IntegrityCheck(
            "radar_v4.cadence_lock",
            False,
            "CADENCE_RECORD_INVALID",
            ("Cadence document needs interval and evaluation_cadence.",),
            lock_source_details(target, extra),
        )
    bar_rank = _rank(interval)
    eval_rank = _rank(evaluation)
    if bar_rank is None or eval_rank is None:
        extra["failed"] = ["radar_v4.cadence_lock"]
        return IntegrityCheck(
            "radar_v4.cadence_lock",
            False,
            "CADENCE_UNKNOWN",
            ("Cadence values must be a known interval token.",),
            lock_source_details(target, extra),
        )
    if eval_rank < bar_rank:
        extra["failed"] = ["radar_v4.cadence_lock"]
        return IntegrityCheck(
            "radar_v4.cadence_lock",
            False,
            "CADENCE_OVERRUN",
            (
                "Evaluation cadence may not outrun bar interval.",
                "That reuse produced flat scores in V1 and V2.",
            ),
            lock_source_details(target, extra),
        )
    extra["failed"] = []
    return IntegrityCheck(
        "radar_v4.cadence_lock",
        True,
        None,
        (
            "Evaluation cadence does not outrun the bars.",
            "This is not a score and not a method.",
        ),
        lock_source_details(target, extra),
    )


def cadence_lock_determinism(path: Path) -> IntegrityCheck:
    first = cadence_lock(path)
    second = cadence_lock(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.cadence_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Cadence lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_cadence_lock(left: Path, right: Path) -> IntegrityCheck:
    first = cadence_lock(left)
    second = cadence_lock(right)
    equal = (
        first.valid
        and second.valid
        and first.details.get("interval") == second.details.get("interval")
        and first.details.get("evaluation_cadence") == second.details.get("evaluation_cadence")
    )
    return IntegrityCheck(
        "radar_v4.compare_cadence_lock",
        equal,
        None if equal else "CADENCE_MISMATCH",
        (
            "Compared cadence identity only.",
            "Path is not cadence.",
        ),
        {
            "equal": equal,
            "left_interval": first.details.get("interval"),
            "right_interval": second.details.get("interval"),
        },
    )


def write_cadence_record(
    source: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = cadence_lock(source)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_cadence_record(path: Path) -> IntegrityCheck:
    return verify_recomputed_lock_record(
        path,
        expected_kind="radar_v4.cadence_lock",
        verify_kind="radar_v4.cadence_verify",
        invalid_code="CADENCE_RECORD_INVALID",
        recompute=cadence_lock,
    )


def cadence_status_bind(path: Path) -> IntegrityCheck:
    locked = cadence_lock(path)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.cadence_status_bind",
        matched,
        None if matched else "CADENCE_STATUS_MISMATCH",
        ("Cadence lock and status share the locked unit. Not a measurement.",),
        {
            "cadence_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
