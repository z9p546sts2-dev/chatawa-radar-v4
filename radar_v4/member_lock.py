"""Named file-member identity. A digest alone does not name the file."""

from __future__ import annotations

from hashlib import sha256
from json import loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.integrity import (
    IntegrityCheck,
    lock_source_details,
    source_digest,
    verify_recomputed_lock_record,
)
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status

_HEX = frozenset("0123456789abcdef")


def source_members(path: Path) -> dict[str, str]:
    """Relative-path map of SHA-256 members. Symlinks are not followed."""
    root = Path(path)
    if root.is_file() and not root.is_symlink():
        return {root.name: sha256(root.read_bytes()).hexdigest()}
    if not root.is_dir():
        return {}
    listing: dict[str, str] = {}
    for child in sorted(root.rglob("*")):
        rel = child.relative_to(root).as_posix()
        if child.is_symlink():
            listing[rel] = "SYMLINK"
        elif child.is_file():
            listing[rel] = sha256(child.read_bytes()).hexdigest()
    return listing


def member_lock(path: Path) -> IntegrityCheck:
    root = Path(path)
    members = source_members(root)
    digest = source_digest(root)
    if not root.exists():
        return IntegrityCheck(
            "radar_v4.member_lock",
            False,
            "UNREADABLE_PACK",
            ("Member lock needs a present file or directory.",),
            lock_source_details(root, {"members": members}),
        )
    ok = bool(members) and len(digest) == 64 and all(char in _HEX for char in digest)
    return IntegrityCheck(
        "radar_v4.member_lock",
        ok,
        None if ok else "SOURCE_DIGEST_REFUSED",
        (
            "Member lock names each relative path.",
            "A pack digest does not name the changed file.",
        ),
        lock_source_details(root, {"algorithm": "sha256", "members": members}),
    )


def member_lock_determinism(path: Path) -> IntegrityCheck:
    first = member_lock(path)
    second = member_lock(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.member_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Member lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def _member_diff(
    left: dict[str, str], right: dict[str, str]
) -> tuple[list[str], list[str], list[str]]:
    missing = sorted(name for name in left if name not in right)
    extra = sorted(name for name in right if name not in left)
    changed = sorted(
        name for name in left if name in right and left[name] != right[name]
    )
    return missing, extra, changed


def compare_member_lock(left: Path, right: Path) -> IntegrityCheck:
    first = member_lock(left)
    second = member_lock(right)
    left_members = first.details.get("members")
    right_members = second.details.get("members")
    left_map = left_members if isinstance(left_members, dict) else {}
    right_map = right_members if isinstance(right_members, dict) else {}
    missing, extra, changed = _member_diff(
        {str(key): str(value) for key, value in left_map.items()},
        {str(key): str(value) for key, value in right_map.items()},
    )
    equal = first.valid and second.valid and not missing and not extra and not changed
    if equal:
        error = None
    elif missing and not extra and not changed:
        error = "MEMBER_ABSENT"
    elif extra and not missing and not changed:
        error = "MEMBER_EXTRA"
    else:
        error = "MEMBER_MISMATCH"
    return IntegrityCheck(
        "radar_v4.compare_member_lock",
        equal,
        error,
        (
            "Compared named members.",
            "Digest-only compare does not name the file.",
        ),
        {
            "equal": equal,
            "changed": changed,
            "extra": extra,
            "missing": missing,
        },
    )


def write_member_record(
    source: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = member_lock(source)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_member_record(path: Path) -> IntegrityCheck:
    return verify_recomputed_lock_record(
        path,
        expected_kind="radar_v4.member_lock",
        verify_kind="radar_v4.member_verify",
        invalid_code="MEMBER_RECORD_INVALID",
        recompute=member_lock,
    )


def member_status_bind(path: Path) -> IntegrityCheck:
    locked = member_lock(path)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.member_status_bind",
        matched,
        None if matched else "MEMBER_STATUS_MISMATCH",
        ("Member lock and status share the locked unit. Not a measurement.",),
        {
            "member_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
