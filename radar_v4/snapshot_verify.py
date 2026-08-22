"""Verify a snapshot's integrity checksum. No repair."""

from __future__ import annotations

from dataclasses import dataclass
from json import dumps
from pathlib import Path

from radar_v4.snapshot import DatasetSnapshot
from radar_v4.snapshot_files import read_snapshot_file


@dataclass(frozen=True)
class SnapshotVerification:
    checksum: str
    expected: str | None
    matched: bool | None

    def serialize(self) -> str:
        document = {
            "checksum": self.checksum,
            "expected": self.expected,
            "matched": self.matched,
        }
        return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def verify_snapshot(
    snapshot: DatasetSnapshot, expected: str | None = None
) -> SnapshotVerification:
    checksum = snapshot.integrity_checksum()
    matched = None if expected is None else checksum == expected
    return SnapshotVerification(
        checksum=checksum, expected=expected, matched=matched
    )


def verify_snapshot_file(
    path: str | Path, expected: str | None = None
) -> SnapshotVerification:
    return verify_snapshot(read_snapshot_file(path), expected)
