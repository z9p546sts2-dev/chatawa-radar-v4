"""Read and write dataset snapshots on the local filesystem only.

This is not a vendor client. It does not download, invent, or relabel
records. Failed reads do not produce a fake snapshot.
"""

from __future__ import annotations

from json import JSONDecodeError
from pathlib import Path

from radar_v4.snapshot import DatasetSnapshot


class SnapshotFileError(ValueError):
    def __init__(self, code: str, reason: str) -> None:
        self.code = code
        self.reason = reason
        super().__init__(reason)


def write_snapshot_file(path: str | Path, snapshot: DatasetSnapshot) -> Path:
    target = Path(path)
    if target.exists() and target.is_dir():
        raise SnapshotFileError(
            "SNAPSHOT_PATH_IS_DIRECTORY",
            f"{target} is a directory, not a snapshot file",
        )
    target.write_text(snapshot.serialize() + "\n", encoding="utf-8")
    return target


def read_snapshot_file(path: str | Path) -> DatasetSnapshot:
    target = Path(path)
    if target.exists() and target.is_dir():
        raise SnapshotFileError(
            "SNAPSHOT_PATH_IS_DIRECTORY",
            f"{target} is a directory, not a snapshot file",
        )
    try:
        text = target.read_text(encoding="utf-8")
    except OSError as exc:
        raise SnapshotFileError(
            "UNREADABLE_SNAPSHOT_FILE",
            f"snapshot file could not be read: {exc}",
        ) from exc
    try:
        return DatasetSnapshot.deserialize(text)
    except (JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise SnapshotFileError(
            "UNREADABLE_SNAPSHOT_FILE",
            f"snapshot file is not a readable DatasetSnapshot: {exc}",
        ) from exc
