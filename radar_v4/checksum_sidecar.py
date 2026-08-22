"""Write and verify a SHA-256 sidecar next to a snapshot file. No repair."""

from __future__ import annotations

from pathlib import Path

from radar_v4.atomic_write import write_text_atomic
from radar_v4.snapshot_files import SnapshotFileError, read_snapshot_file
from radar_v4.snapshot_verify import SnapshotVerification, verify_snapshot


def sidecar_path(snapshot_path: str | Path) -> Path:
    return Path(str(Path(snapshot_path)) + ".sha256")


def write_checksum_sidecar(snapshot_path: str | Path, checksum: str | None = None) -> Path:
    snapshot_file = Path(snapshot_path)
    if checksum is None:
        checksum = read_snapshot_file(snapshot_file).integrity_checksum()
    target = sidecar_path(snapshot_file)
    if target.exists() and target.is_dir():
        raise SnapshotFileError(
            "SIDECAR_PATH_IS_DIRECTORY",
            f"{target} is a directory, not a checksum sidecar",
        )
    return write_text_atomic(target, checksum + "\n")


def read_checksum_sidecar(snapshot_path: str | Path) -> str:
    target = sidecar_path(snapshot_path)
    try:
        text = target.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise SnapshotFileError(
            "UNREADABLE_SIDECAR",
            f"checksum sidecar could not be read: {exc}",
        ) from exc
    if len(text) != 64 or any(char not in "0123456789abcdef" for char in text):
        raise SnapshotFileError(
            "UNREADABLE_SIDECAR",
            "checksum sidecar must be a 64-character SHA-256 hex digest",
        )
    return text


def verify_checksum_sidecar(snapshot_path: str | Path) -> SnapshotVerification:
    expected = read_checksum_sidecar(snapshot_path)
    snapshot = read_snapshot_file(snapshot_path)
    return verify_snapshot(snapshot, expected)
