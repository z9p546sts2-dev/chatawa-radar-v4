"""Pack-manifest identity checks. Not market evidence."""

from __future__ import annotations

from json import JSONDecodeError, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.integrity import IntegrityCheck
from radar_v4.pack_manifest import (
    MANIFEST_FILENAME,
    PackManifestError,
    verify_pack_manifest,
)
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status

MANIFEST_KIND = "radar_v4.pack_manifest"
_HEX = frozenset("0123456789abcdef")


def _load_manifest(path: Path) -> tuple[dict[str, object] | None, IntegrityCheck | None]:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return None, IntegrityCheck(
            "radar_v4.manifest_readable",
            False,
            "MANIFEST_MISSING",
            ("unreadable pack manifest",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return None, IntegrityCheck(
            "radar_v4.manifest_readable",
            False,
            "UNREADABLE_MANIFEST",
            ("pack manifest is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return None, IntegrityCheck(
            "radar_v4.manifest_readable",
            False,
            "UNREADABLE_MANIFEST",
            ("pack manifest must be an object",),
            {"path": str(target)},
        )
    return raw, None


def _manifest_path(target: Path) -> Path:
    path = Path(target)
    if path.is_dir():
        return path / MANIFEST_FILENAME
    return path


def manifest_kind_scan(path: Path) -> IntegrityCheck:
    raw, error = _load_manifest(_manifest_path(path))
    if error is not None:
        return error
    assert raw is not None
    if raw.get("document_kind") != MANIFEST_KIND:
        return IntegrityCheck(
            "radar_v4.manifest_kind",
            False,
            "MANIFEST_KIND_REFUSED",
            ("A manifest must name radar_v4.pack_manifest. Not repaired.",),
            {"path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.manifest_kind",
        True,
        None,
        ("Manifest kind is locked. Not a measurement.",),
        {"path": str(path)},
    )


def manifest_files_scan(path: Path) -> IntegrityCheck:
    raw, error = _load_manifest(_manifest_path(path))
    if error is not None:
        return error
    assert raw is not None
    files = raw.get("files")
    if not isinstance(files, dict) or not files:
        return IntegrityCheck(
            "radar_v4.manifest_files",
            False,
            "MANIFEST_EMPTY_REFUSED",
            ("A manifest must list files. An empty object is not a pack.",),
            {"path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.manifest_files",
        True,
        None,
        ("Manifest files are present. Not market evidence.",),
        {"count": len(files), "path": str(path)},
    )


def manifest_digest_scan(path: Path) -> IntegrityCheck:
    raw, error = _load_manifest(_manifest_path(path))
    if error is not None:
        return error
    assert raw is not None
    files = raw.get("files")
    if not isinstance(files, dict):
        return IntegrityCheck(
            "radar_v4.manifest_digest",
            False,
            "MANIFEST_EMPTY_REFUSED",
            ("Manifest files must be an object before digests are checked.",),
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
            "radar_v4.manifest_digest",
            False,
            "MANIFEST_DIGEST_REFUSED",
            ("A manifest digest must be a 64-character SHA-256 hex string.",),
            {"hits": hits, "path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.manifest_digest",
        True,
        None,
        ("Manifest digests are hex SHA-256. Not a score.",),
        {"hits": [], "path": str(path)},
    )


def manifest_lock(target: Path) -> IntegrityCheck:
    path = Path(target)
    parts = [
        manifest_kind_scan(path),
        manifest_files_scan(path),
        manifest_digest_scan(path),
    ]
    if path.is_dir() and all(part.valid for part in parts):
        try:
            verify_pack_manifest(path)
        except PackManifestError as exc:
            parts.append(
                IntegrityCheck(
                    "radar_v4.manifest_verify_pack",
                    False,
                    exc.code,
                    (exc.reason,),
                    {"path": str(path)},
                )
            )
        else:
            parts.append(
                IntegrityCheck(
                    "radar_v4.manifest_verify_pack",
                    True,
                    None,
                    ("Stored manifest matches pack files. Not a method.",),
                    {"path": str(path)},
                )
            )
    failed = [part for part in parts if not part.valid]
    if failed:
        first = failed[0]
        return IntegrityCheck(
            "radar_v4.manifest_lock",
            False,
            first.error_code,
            ("Manifest lock failed.",) + first.notes,
            {"failed": [part.document_kind for part in failed]},
        )
    return IntegrityCheck(
        "radar_v4.manifest_lock",
        True,
        None,
        ("Manifest lock passed. Not market evidence.",),
        {"failed": []},
    )


def manifest_lock_determinism(target: Path) -> IntegrityCheck:
    first = manifest_lock(target)
    second = manifest_lock(target)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.manifest_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Manifest lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_manifest_lock(left: Path, right: Path) -> IntegrityCheck:
    first = manifest_lock(left)
    second = manifest_lock(right)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.compare_manifest_lock",
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared manifest-lock records. Equality is not a score.",),
        {"equal": equal},
    )


def write_manifest_record(
    target: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = manifest_lock(target)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_manifest_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.manifest_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable manifest-lock record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.manifest_verify",
            False,
            "UNREADABLE_JSON",
            ("manifest-lock record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.manifest_verify",
            False,
            "UNREADABLE_JSON",
            ("manifest-lock record must be an object",),
            {"path": str(target)},
        )
    ok = raw.get("document_kind") == "radar_v4.manifest_lock" and raw.get("valid") is True
    return IntegrityCheck(
        "radar_v4.manifest_verify",
        ok,
        None if ok else "MANIFEST_RECORD_INVALID",
        ("Verified a local manifest-lock record. Not market evidence.",),
        {"path": str(target)},
    )


def manifest_status_bind(target: Path) -> IntegrityCheck:
    locked = manifest_lock(target)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.manifest_status_bind",
        matched,
        None if matched else "MANIFEST_STATUS_MISMATCH",
        ("Manifest lock and status share the locked unit. Not a measurement.",),
        {
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "manifest_valid": locked.valid,
            "status_unit": status_unit,
        },
    )
