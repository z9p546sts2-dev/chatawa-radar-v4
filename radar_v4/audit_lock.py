"""Local audit-copy identity checks. Not market evidence."""

from __future__ import annotations

from json import JSONDecodeError, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.audit_bundle import AUDIT_MANIFEST, verify_audit_bundle
from radar_v4.integrity import IntegrityCheck
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status

AUDIT_KIND = "radar_v4.audit_bundle"
_HEX = frozenset("0123456789abcdef")


def _audit_dir(target: Path) -> Path:
    path = Path(target)
    if path.is_file():
        return path.parent
    return path


def _manifest_path(target: Path) -> Path:
    path = Path(target)
    if path.is_dir():
        return path / AUDIT_MANIFEST
    return path


def _load_audit(path: Path) -> tuple[dict[str, object] | None, IntegrityCheck | None]:
    target = _manifest_path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return None, IntegrityCheck(
            "radar_v4.audit_readable",
            False,
            "UNREADABLE_JSON",
            ("unreadable audit manifest",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return None, IntegrityCheck(
            "radar_v4.audit_readable",
            False,
            "UNREADABLE_JSON",
            ("audit manifest is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return None, IntegrityCheck(
            "radar_v4.audit_readable",
            False,
            "UNREADABLE_JSON",
            ("audit manifest must be an object",),
            {"path": str(target)},
        )
    return raw, None


def audit_kind_scan(path: Path) -> IntegrityCheck:
    raw, error = _load_audit(path)
    if error is not None:
        return error
    assert raw is not None
    if raw.get("document_kind") != AUDIT_KIND:
        return IntegrityCheck(
            "radar_v4.audit_kind",
            False,
            "AUDIT_KIND_REFUSED",
            ("An audit copy must name radar_v4.audit_bundle. Not repaired.",),
            {"path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.audit_kind",
        True,
        None,
        ("Audit kind is locked. Not a measurement.",),
        {"path": str(path)},
    )


def audit_files_scan(path: Path) -> IntegrityCheck:
    raw, error = _load_audit(path)
    if error is not None:
        return error
    assert raw is not None
    files = raw.get("files")
    if not isinstance(files, dict) or not files:
        return IntegrityCheck(
            "radar_v4.audit_files",
            False,
            "AUDIT_EMPTY_REFUSED",
            ("An audit copy must list files. An empty object is not a copy.",),
            {"path": str(path)},
        )
    hits = [
        name
        for name, digest in files.items()
        if not isinstance(digest, str)
        or len(digest) != 64
        or any(char not in _HEX for char in digest)
    ]
    if hits:
        return IntegrityCheck(
            "radar_v4.audit_files",
            False,
            "AUDIT_DIGEST_REFUSED",
            ("An audit digest must be a 64-character SHA-256 hex string.",),
            {"hits": hits, "path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.audit_files",
        True,
        None,
        ("Audit files are present. Not market evidence.",),
        {"count": len(files), "path": str(path)},
    )


def audit_copy_scan(path: Path) -> IntegrityCheck:
    raw, error = _load_audit(path)
    if error is not None:
        return error
    verification = verify_audit_bundle(_audit_dir(path))
    if not verification.matched:
        return IntegrityCheck(
            "radar_v4.audit_copy",
            False,
            verification.error_code or "AUDIT_BUNDLE_MISMATCH",
            ("Stored audit bytes do not match the copy. Not repaired.",),
            {"path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.audit_copy",
        True,
        None,
        ("Audit copy matches its manifest. Not HISTORICAL evidence.",),
        {"path": str(path)},
    )


def audit_lock(target: Path) -> IntegrityCheck:
    parts = [
        audit_kind_scan(target),
        audit_files_scan(target),
        audit_copy_scan(target),
    ]
    failed = [part for part in parts if not part.valid]
    if failed:
        first = failed[0]
        return IntegrityCheck(
            "radar_v4.audit_lock",
            False,
            first.error_code,
            ("Audit lock failed.",) + first.notes,
            {"failed": [part.document_kind for part in failed]},
        )
    return IntegrityCheck(
        "radar_v4.audit_lock",
        True,
        None,
        ("Audit lock passed. Not market evidence.",),
        {"failed": []},
    )


def audit_lock_determinism(target: Path) -> IntegrityCheck:
    first = audit_lock(target)
    second = audit_lock(target)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.audit_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Audit lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_audit_lock(left: Path, right: Path) -> IntegrityCheck:
    first = audit_lock(left)
    second = audit_lock(right)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.compare_audit_lock",
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared audit-lock records. Equality is not a score.",),
        {"equal": equal},
    )


def write_audit_record(
    target: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = audit_lock(target)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_audit_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.audit_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable audit-lock record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.audit_verify",
            False,
            "UNREADABLE_JSON",
            ("audit-lock record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.audit_verify",
            False,
            "UNREADABLE_JSON",
            ("audit-lock record must be an object",),
            {"path": str(target)},
        )
    ok = raw.get("document_kind") == "radar_v4.audit_lock" and raw.get("valid") is True
    return IntegrityCheck(
        "radar_v4.audit_verify",
        ok,
        None if ok else "AUDIT_RECORD_INVALID",
        ("Verified a local audit-lock record. Not market evidence.",),
        {"path": str(target)},
    )


def audit_status_bind(target: Path) -> IntegrityCheck:
    locked = audit_lock(target)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.audit_status_bind",
        matched,
        None if matched else "AUDIT_STATUS_MISMATCH",
        ("Audit lock and status share the locked unit. Not a measurement.",),
        {
            "audit_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
