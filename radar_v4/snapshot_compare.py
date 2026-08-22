"""Compare two dataset snapshots. No method, no ranking."""

from __future__ import annotations

from dataclasses import dataclass, fields
from json import dumps
from pathlib import Path

from radar_v4.snapshot import DatasetSnapshot
from radar_v4.snapshot_files import read_snapshot_file


@dataclass(frozen=True)
class SnapshotComparison:
    equal: bool
    declaration_mismatches: tuple[str, ...]
    left_only_envelope_checksums: tuple[str, ...]
    right_only_envelope_checksums: tuple[str, ...]
    payload_conflicts: tuple[str, ...]

    def serialize(self) -> str:
        document = {
            "declaration_mismatches": list(self.declaration_mismatches),
            "equal": self.equal,
            "left_only_envelope_checksums": list(self.left_only_envelope_checksums),
            "payload_conflicts": list(self.payload_conflicts),
            "right_only_envelope_checksums": list(self.right_only_envelope_checksums),
        }
        return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compare_snapshots(
    left: DatasetSnapshot, right: DatasetSnapshot
) -> SnapshotComparison:
    """Describe identity differences. Does not repair or merge."""
    mismatches = tuple(
        field.name
        for field in fields(left.declaration)
        if getattr(left.declaration, field.name)
        != getattr(right.declaration, field.name)
    )
    left_map = {
        item.envelope.checksum or "": item for item in left.observations
    }
    right_map = {
        item.envelope.checksum or "": item for item in right.observations
    }
    left_only = tuple(sorted(set(left_map) - set(right_map)))
    right_only = tuple(sorted(set(right_map) - set(left_map)))
    conflicts = tuple(
        sorted(
            checksum
            for checksum in set(left_map) & set(right_map)
            if left_map[checksum].payload_checksum
            != right_map[checksum].payload_checksum
        )
    )
    equal = not mismatches and not left_only and not right_only and not conflicts
    return SnapshotComparison(
        equal=equal,
        declaration_mismatches=mismatches,
        left_only_envelope_checksums=left_only,
        right_only_envelope_checksums=right_only,
        payload_conflicts=conflicts,
    )


def compare_snapshot_files(left: str | Path, right: str | Path) -> SnapshotComparison:
    return compare_snapshots(read_snapshot_file(left), read_snapshot_file(right))
