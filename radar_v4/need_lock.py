"""A bounded local file is still sufficient. Purchase is not earned."""

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

NEED_FILENAME = "need.json"
NEED_KIND = "radar_v4.need"


def _need_path(path: Path) -> Path:
    root = Path(path)
    if root.is_dir():
        return root / NEED_FILENAME
    return root


def _load_need(path: Path) -> tuple[dict[str, object] | None, IntegrityCheck | None]:
    target = _need_path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return None, IntegrityCheck(
            "radar_v4.need_lock",
            False,
            "NEED_MISSING",
            ("Need lock needs a present need document.",),
            lock_source_details(target),
        )
    except JSONDecodeError:
        return None, IntegrityCheck(
            "radar_v4.need_lock",
            False,
            "UNREADABLE_JSON",
            ("Need document is not JSON.",),
            lock_source_details(target),
        )
    if not isinstance(raw, dict):
        return None, IntegrityCheck(
            "radar_v4.need_lock",
            False,
            "NEED_RECORD_INVALID",
            ("Need document must be an object.",),
            lock_source_details(target),
        )
    return raw, None


def need_lock(path: Path) -> IntegrityCheck:
    """Refuse skipping the bounded file, purchase claims, and undeclared rulers."""
    target = _need_path(path)
    raw, error = _load_need(path)
    if error is not None:
        return error
    assert raw is not None
    sufficient = raw.get("bounded_file_sufficient")
    purchase = raw.get("purchase_authorized")
    adjustment = raw.get("adjustment_policy")
    staleness = raw.get("max_staleness")
    extra: dict[str, object] = {
        "bounded_file_sufficient": sufficient if isinstance(sufficient, bool) else None,
        "purchase_authorized": purchase if isinstance(purchase, bool) else None,
        "adjustment_policy": adjustment if isinstance(adjustment, str) else None,
        "max_staleness": staleness if isinstance(staleness, str) else None,
    }
    if raw.get("document_kind") != NEED_KIND:
        extra["failed"] = ["radar_v4.need_lock"]
        return IntegrityCheck(
            "radar_v4.need_lock",
            False,
            "NEED_RECORD_INVALID",
            ("A need document must name radar_v4.need.",),
            lock_source_details(target, extra),
        )
    if not isinstance(sufficient, bool) or not isinstance(purchase, bool):
        extra["failed"] = ["radar_v4.need_lock"]
        return IntegrityCheck(
            "radar_v4.need_lock",
            False,
            "NEED_RECORD_INVALID",
            ("Need document needs bounded_file_sufficient and purchase_authorized.",),
            lock_source_details(target, extra),
        )
    if not isinstance(adjustment, str) or adjustment.strip() == "":
        extra["failed"] = ["radar_v4.need_lock"]
        return IntegrityCheck(
            "radar_v4.need_lock",
            False,
            "ADJUSTMENT_UNDECLARED",
            (
                "Adjustment policy must be declared before a later source class.",
                "This does not invent a calendar.",
            ),
            lock_source_details(target, extra),
        )
    if not isinstance(staleness, str) or staleness.strip() == "":
        extra["failed"] = ["radar_v4.need_lock"]
        return IntegrityCheck(
            "radar_v4.need_lock",
            False,
            "STALENESS_UNDECLARED",
            (
                "Maximum staleness must be declared before a later source class.",
                "NONE means no live freshness SLA.",
            ),
            lock_source_details(target, extra),
        )
    if sufficient is False:
        extra["failed"] = ["radar_v4.need_lock"]
        return IntegrityCheck(
            "radar_v4.need_lock",
            False,
            "BOUNDED_FILE_SKIPPED",
            (
                "The bounded local file is still sufficient for this class of work.",
                "Skipping it does not earn a vendor.",
            ),
            lock_source_details(target, extra),
        )
    if purchase is True:
        extra["failed"] = ["radar_v4.need_lock"]
        return IntegrityCheck(
            "radar_v4.need_lock",
            False,
            "PURCHASE_CLAIM",
            (
                "A JSON flag is not a data purchase.",
                "Learning and earning it does not buy an API.",
            ),
            lock_source_details(target, extra),
        )
    extra["failed"] = []
    return IntegrityCheck(
        "radar_v4.need_lock",
        True,
        None,
        (
            "Bounded file is sufficient. Purchase is not authorized.",
            "This is inspectability, not Horizon 2.",
        ),
        lock_source_details(target, extra),
    )


def need_lock_determinism(path: Path) -> IntegrityCheck:
    first = need_lock(path)
    second = need_lock(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.need_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Need lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_need_lock(left: Path, right: Path) -> IntegrityCheck:
    first = need_lock(left)
    second = need_lock(right)
    equal = (
        first.valid
        and second.valid
        and first.details.get("bounded_file_sufficient")
        == second.details.get("bounded_file_sufficient")
        and first.details.get("purchase_authorized")
        == second.details.get("purchase_authorized")
        and first.details.get("adjustment_policy") == second.details.get("adjustment_policy")
        and first.details.get("max_staleness") == second.details.get("max_staleness")
    )
    return IntegrityCheck(
        "radar_v4.compare_need_lock",
        equal,
        None if equal else "NEED_MISMATCH",
        (
            "Compared need identity only.",
            "A need record is not a purchase.",
        ),
        {
            "equal": equal,
            "left_adjustment_policy": first.details.get("adjustment_policy"),
            "right_adjustment_policy": second.details.get("adjustment_policy"),
        },
    )


def write_need_record(
    source: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = need_lock(source)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_need_record(path: Path) -> IntegrityCheck:
    return verify_recomputed_lock_record(
        path,
        expected_kind="radar_v4.need_lock",
        verify_kind="radar_v4.need_verify",
        invalid_code="NEED_RECORD_INVALID",
        recompute=need_lock,
    )


def need_status_bind(path: Path) -> IntegrityCheck:
    locked = need_lock(path)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
        and status.get("vendor_authorized") is False
    )
    return IntegrityCheck(
        "radar_v4.need_status_bind",
        matched,
        None if matched else "NEED_STATUS_MISMATCH",
        ("Need lock and status share the locked unit. Not a measurement.",),
        {
            "need_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
