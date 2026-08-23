"""Checksum-sidecar identity checks. Not a repair."""

from __future__ import annotations

from json import JSONDecodeError, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.checksum_sidecar import sidecar_path, verify_checksum_sidecar
from radar_v4.integrity import IntegrityCheck
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status

_HEX = frozenset("0123456789abcdef")


def _read_sidecar_text(path: Path) -> tuple[str | None, IntegrityCheck | None]:
    target = Path(path)
    try:
        text = target.read_text(encoding="utf-8").strip()
    except OSError:
        return None, IntegrityCheck(
            "radar_v4.sidecar_readable",
            False,
            "UNREADABLE_SIDECAR",
            ("unreadable checksum sidecar",),
            {"path": str(target)},
        )
    return text, None


def sidecar_digest_scan(path: Path) -> IntegrityCheck:
    text, error = _read_sidecar_text(path)
    if error is not None:
        return error
    assert text is not None
    ok = len(text) == 64 and all(char in _HEX for char in text)
    if not ok:
        return IntegrityCheck(
            "radar_v4.sidecar_digest",
            False,
            "SIDECAR_DIGEST_REFUSED",
            ("A sidecar must be a 64-character SHA-256 hex digest. Not repaired.",),
            {"path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.sidecar_digest",
        True,
        None,
        ("Sidecar digest shape passed. Not market evidence.",),
        {"path": str(path)},
    )


def sidecar_lock(path: Path) -> IntegrityCheck:
    digest = sidecar_digest_scan(path)
    if not digest.valid:
        return IntegrityCheck(
            "radar_v4.sidecar_lock",
            False,
            digest.error_code,
            ("Sidecar lock failed.",) + digest.notes,
            {"failed": [digest.document_kind]},
        )
    return IntegrityCheck(
        "radar_v4.sidecar_lock",
        True,
        None,
        ("Sidecar lock passed. Not a repair.",),
        {"failed": []},
    )


def sidecar_snapshot_bind(snapshot: Path) -> IntegrityCheck:
    sidecar = sidecar_path(snapshot)
    locked = sidecar_lock(sidecar)
    if not locked.valid:
        return IntegrityCheck(
            "radar_v4.sidecar_snapshot_bind",
            False,
            locked.error_code,
            ("Sidecar-snapshot bind needs a locked sidecar.",) + locked.notes,
            {"path": str(sidecar)},
        )
    try:
        verification = verify_checksum_sidecar(snapshot)
    except SnapshotFileError as exc:
        return IntegrityCheck(
            "radar_v4.sidecar_snapshot_bind",
            False,
            exc.code,
            (exc.reason,),
            {"path": str(snapshot)},
        )
    return IntegrityCheck(
        "radar_v4.sidecar_snapshot_bind",
        verification.matched,
        None if verification.matched else "SIDECAR_SNAPSHOT_MISMATCH",
        ("Sidecar digest bound to snapshot checksum. Not a method.",),
        {"matched": verification.matched, "path": str(snapshot)},
    )


def sidecar_lock_any(target: Path, snapshot: bool = False) -> IntegrityCheck:
    path = Path(target)
    if snapshot:
        return sidecar_snapshot_bind(path)
    return sidecar_lock(path)


def sidecar_lock_determinism(target: Path, snapshot: bool = False) -> IntegrityCheck:
    first = sidecar_lock_any(target, snapshot=snapshot)
    second = sidecar_lock_any(target, snapshot=snapshot)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.sidecar_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Sidecar lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_sidecar_lock(left: Path, right: Path) -> IntegrityCheck:
    first = sidecar_lock(left)
    second = sidecar_lock(right)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.compare_sidecar_lock",
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared sidecar-lock records. Equality is not a score.",),
        {"equal": equal},
    )


def write_sidecar_record(
    target: Path, destination: Path, replace: bool = False, snapshot: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    path = sidecar_path(target) if snapshot else Path(target)
    record = sidecar_lock(path)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_sidecar_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.sidecar_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable sidecar-lock record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.sidecar_verify",
            False,
            "UNREADABLE_JSON",
            ("sidecar-lock record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.sidecar_verify",
            False,
            "UNREADABLE_JSON",
            ("sidecar-lock record must be an object",),
            {"path": str(target)},
        )
    ok = raw.get("document_kind") == "radar_v4.sidecar_lock" and raw.get("valid") is True
    return IntegrityCheck(
        "radar_v4.sidecar_verify",
        ok,
        None if ok else "SIDECAR_RECORD_INVALID",
        ("Verified a local sidecar-lock record. Not market evidence.",),
        {"path": str(target)},
    )


def sidecar_status_bind(target: Path, snapshot: bool = False) -> IntegrityCheck:
    locked = sidecar_lock_any(target, snapshot=snapshot)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.sidecar_status_bind",
        matched,
        None if matched else "SIDECAR_STATUS_MISMATCH",
        ("Sidecar lock and status share the locked unit. Not a measurement.",),
        {
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "sidecar_valid": locked.valid,
            "status_unit": status_unit,
        },
    )
