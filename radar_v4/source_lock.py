"""A JSON flag cannot authorize historical admission. Not a vendor client."""

from __future__ import annotations

from json import JSONDecodeError, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.fixture_pack import PACK_ALLOWED_PROVENANCE
from radar_v4.integrity import (
    IntegrityCheck,
    lock_source_details,
    verify_recomputed_lock_record,
)
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status

SOURCE_FILENAME = "source.json"
SOURCE_KIND = "radar_v4.source"


def _source_path(path: Path) -> Path:
    root = Path(path)
    if root.is_dir():
        return root / SOURCE_FILENAME
    return root


def _load_source(path: Path) -> tuple[dict[str, object] | None, IntegrityCheck | None]:
    target = _source_path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return None, IntegrityCheck(
            "radar_v4.source_lock",
            False,
            "SOURCE_MISSING",
            ("Source lock needs a present source document.",),
            lock_source_details(target),
        )
    except JSONDecodeError:
        return None, IntegrityCheck(
            "radar_v4.source_lock",
            False,
            "UNREADABLE_JSON",
            ("Source document is not JSON.",),
            lock_source_details(target),
        )
    if not isinstance(raw, dict):
        return None, IntegrityCheck(
            "radar_v4.source_lock",
            False,
            "SOURCE_RECORD_INVALID",
            ("Source document must be an object.",),
            lock_source_details(target),
        )
    return raw, None


def source_lock(path: Path) -> IntegrityCheck:
    """Refuse unnamed, self-authorized, HISTORICAL, or LIVE workshop sources."""
    target = _source_path(path)
    raw, error = _load_source(path)
    if error is not None:
        return error
    assert raw is not None
    name = raw.get("source_name")
    provenance = raw.get("provenance_class")
    authorized = raw.get("authorized")
    extra: dict[str, object] = {
        "source_name": name if isinstance(name, str) else None,
        "provenance_class": provenance if isinstance(provenance, str) else None,
        "authorized": authorized if isinstance(authorized, bool) else None,
    }
    if raw.get("document_kind") != SOURCE_KIND:
        extra["failed"] = ["radar_v4.source_lock"]
        return IntegrityCheck(
            "radar_v4.source_lock",
            False,
            "SOURCE_RECORD_INVALID",
            ("A source document must name radar_v4.source.",),
            lock_source_details(target, extra),
        )
    if not isinstance(name, str) or name.strip() == "":
        extra["failed"] = ["radar_v4.source_lock"]
        return IntegrityCheck(
            "radar_v4.source_lock",
            False,
            "SOURCE_UNNAMED",
            (
                "A workshop source must be named.",
                "This does not invent a vendor.",
            ),
            lock_source_details(target, extra),
        )
    if not isinstance(provenance, str) or not provenance:
        extra["failed"] = ["radar_v4.source_lock"]
        return IntegrityCheck(
            "radar_v4.source_lock",
            False,
            "SOURCE_RECORD_INVALID",
            ("Source document needs provenance_class.",),
            lock_source_details(target, extra),
        )
    if not isinstance(authorized, bool):
        extra["failed"] = ["radar_v4.source_lock"]
        return IntegrityCheck(
            "radar_v4.source_lock",
            False,
            "SOURCE_RECORD_INVALID",
            ("Source document needs authorized as a boolean.",),
            lock_source_details(target, extra),
        )
    if authorized is True:
        extra["failed"] = ["radar_v4.source_lock"]
        return IntegrityCheck(
            "radar_v4.source_lock",
            False,
            "ADMISSION_CLAIM",
            (
                "A JSON flag is not Todd authorization.",
                "This does not open the pack loader.",
            ),
            lock_source_details(target, extra),
        )
    if provenance == "HISTORICAL":
        extra["failed"] = ["radar_v4.source_lock"]
        return IntegrityCheck(
            "radar_v4.source_lock",
            False,
            "HISTORICAL_ADMISSION_NOT_AUTHORIZED",
            (
                "HISTORICAL admission is not authorized.",
                "Naming a source is not a download.",
            ),
            lock_source_details(target, extra),
        )
    if provenance == "LIVE":
        extra["failed"] = ["radar_v4.source_lock"]
        return IntegrityCheck(
            "radar_v4.source_lock",
            False,
            "LIVE_ADMISSION_NOT_AUTHORIZED",
            (
                "LIVE admission is not authorized.",
                "This is not a market-data client.",
            ),
            lock_source_details(target, extra),
        )
    if provenance not in PACK_ALLOWED_PROVENANCE:
        extra["failed"] = ["radar_v4.source_lock"]
        return IntegrityCheck(
            "radar_v4.source_lock",
            False,
            "PACK_PROVENANCE_NOT_ALLOWED",
            ("Workshop source records may name only FIXTURE or SYNTHETIC.",),
            lock_source_details(target, extra),
        )
    extra["failed"] = []
    return IntegrityCheck(
        "radar_v4.source_lock",
        True,
        None,
        (
            "Named local FIXTURE/SYNTHETIC source. Not a vendor.",
            "authorized false is required. This is not Horizon 2.",
        ),
        lock_source_details(target, extra),
    )


def source_lock_determinism(path: Path) -> IntegrityCheck:
    first = source_lock(path)
    second = source_lock(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.source_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Source lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_source_lock(left: Path, right: Path) -> IntegrityCheck:
    first = source_lock(left)
    second = source_lock(right)
    equal = (
        first.valid
        and second.valid
        and first.details.get("source_name") == second.details.get("source_name")
        and first.details.get("provenance_class") == second.details.get("provenance_class")
        and first.details.get("authorized") == second.details.get("authorized")
    )
    return IntegrityCheck(
        "radar_v4.compare_source_lock",
        equal,
        None if equal else "SOURCE_MISMATCH",
        (
            "Compared source identity only.",
            "A name is not a vendor client.",
        ),
        {
            "equal": equal,
            "left_source_name": first.details.get("source_name"),
            "right_source_name": second.details.get("source_name"),
        },
    )


def write_source_record(
    source: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = source_lock(source)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_source_record(path: Path) -> IntegrityCheck:
    return verify_recomputed_lock_record(
        path,
        expected_kind="radar_v4.source_lock",
        verify_kind="radar_v4.source_verify",
        invalid_code="SOURCE_RECORD_INVALID",
        recompute=source_lock,
    )


def source_status_bind(path: Path) -> IntegrityCheck:
    locked = source_lock(path)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
        and status.get("vendor_authorized") is False
    )
    return IntegrityCheck(
        "radar_v4.source_status_bind",
        matched,
        None if matched else "SOURCE_STATUS_MISMATCH",
        ("Source lock and status share the locked unit. Not a measurement.",),
        {
            "source_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
