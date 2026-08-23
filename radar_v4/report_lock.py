"""Session-report identity checks. Not a measurement claim."""

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

ALLOWED_REPORT_KINDS = frozenset(
    {
        "radar_v4.admission_report",
        "radar_v4.local_session_report",
        "radar_v4.session_report",
    }
)


def _load_report(path: Path) -> tuple[dict[str, object] | None, IntegrityCheck | None]:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return None, IntegrityCheck(
            "radar_v4.report_readable",
            False,
            "UNREADABLE_SESSION_REPORT",
            ("unreadable session report",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return None, IntegrityCheck(
            "radar_v4.report_readable",
            False,
            "UNREADABLE_SESSION_REPORT",
            ("session report is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return None, IntegrityCheck(
            "radar_v4.report_readable",
            False,
            "UNREADABLE_SESSION_REPORT",
            ("session report must be an object",),
            {"path": str(target)},
        )
    return raw, None


def report_kind_scan(path: Path) -> IntegrityCheck:
    raw, error = _load_report(path)
    if error is not None:
        return error
    assert raw is not None
    kind = raw.get("document_kind")
    if kind not in ALLOWED_REPORT_KINDS:
        return IntegrityCheck(
            "radar_v4.report_kind",
            False,
            "REPORT_KIND_REFUSED",
            ("A report must name a locked session-report kind. Not repaired.",),
            {"path": str(path), "kind": kind},
        )
    return IntegrityCheck(
        "radar_v4.report_kind",
        True,
        None,
        ("Report kind is locked. Not a measurement.",),
        {"path": str(path), "kind": kind},
    )


def _session_checksum(raw: dict[str, object]) -> str | None:
    kind = raw.get("document_kind")
    if kind == "radar_v4.session_report":
        value = raw.get("snapshot_checksum")
        return value if isinstance(value, str) and value else None
    if kind == "radar_v4.local_session_report":
        session = raw.get("session")
        if session is None:
            return ""
        if isinstance(session, dict):
            value = session.get("snapshot_checksum")
            return value if isinstance(value, str) and value else None
    if kind == "radar_v4.admission_report":
        return ""
    return None


def report_checksum_scan(path: Path) -> IntegrityCheck:
    raw, error = _load_report(path)
    if error is not None:
        return error
    assert raw is not None
    checksum = _session_checksum(raw)
    if checksum is None:
        return IntegrityCheck(
            "radar_v4.report_checksum",
            False,
            "REPORT_CHECKSUM_MISSING",
            ("A usable session report must carry a snapshot checksum.",),
            {"path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.report_checksum",
        True,
        None,
        ("Report checksum field checked. Not market evidence.",),
        {"path": str(path), "present": bool(checksum)},
    )


def report_measured_scan(path: Path) -> IntegrityCheck:
    raw, error = _load_report(path)
    if error is not None:
        return error
    assert raw is not None
    if raw.get("document_kind") == "radar_v4.admission_report" and raw.get("measured") is not False:
        return IntegrityCheck(
            "radar_v4.report_measured",
            False,
            "REPORT_MEASURED_REFUSED",
            ("An admission report must not claim a measurement.",),
            {"path": str(path)},
        )
    if raw.get("measured") is True and raw.get("document_kind") != "radar_v4.session_report":
        return IntegrityCheck(
            "radar_v4.report_measured",
            False,
            "REPORT_MEASURED_REFUSED",
            ("A local report must not set measured true.",),
            {"path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.report_measured",
        True,
        None,
        ("Report measured field checked. Not a method.",),
        {"path": str(path)},
    )


def report_lock(path: Path) -> IntegrityCheck:
    parts = [
        report_kind_scan(path),
        report_checksum_scan(path),
        report_measured_scan(path),
    ]
    failed = [part for part in parts if not part.valid]
    if failed:
        first = failed[0]
        return IntegrityCheck(
            "radar_v4.report_lock",
            False,
            first.error_code,
            ("Report lock failed.",) + first.notes,
            lock_source_details(
                path, {"failed": [part.document_kind for part in failed]}
            ),
        )
    return IntegrityCheck(
        "radar_v4.report_lock",
        True,
        None,
        ("Report lock passed. Not a measurement claim.",),
        lock_source_details(path, {"failed": []}),
    )


def report_lock_determinism(path: Path) -> IntegrityCheck:
    first = report_lock(path)
    second = report_lock(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.report_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Report lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_report_lock(left: Path, right: Path) -> IntegrityCheck:
    first = report_lock(left)
    second = report_lock(right)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.compare_report_lock",
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared report-lock records. Equality is not market evidence.",),
        {"equal": equal},
    )


def write_report_record(
    report: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = report_lock(report)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_report_record(path: Path) -> IntegrityCheck:
    return verify_recomputed_lock_record(
        path,
        expected_kind="radar_v4.report_lock",
        verify_kind="radar_v4.report_verify",
        invalid_code="REPORT_RECORD_INVALID",
        recompute=report_lock,
    )


def report_status_bind(path: Path) -> IntegrityCheck:
    locked = report_lock(path)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.report_status_bind",
        matched,
        None if matched else "REPORT_STATUS_MISMATCH",
        ("Report lock and status share the locked unit. Not a measurement.",),
        {
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "report_valid": locked.valid,
            "status_unit": status_unit,
        },
    )
