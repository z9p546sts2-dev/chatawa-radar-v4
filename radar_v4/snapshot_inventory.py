"""List identities stored in a snapshot. Does not compute changes."""

from __future__ import annotations

from dataclasses import dataclass
from json import dumps
from pathlib import Path

from radar_v4.evidence import format_canonical_timestamp
from radar_v4.snapshot_files import read_snapshot_file


@dataclass(frozen=True)
class SnapshotInventory:
    dataset_id: str
    observation_count: int
    items: tuple[dict[str, str | None], ...]

    def serialize(self) -> str:
        return dumps(
            {
                "dataset_id": self.dataset_id,
                "document_kind": "radar_v4.snapshot_inventory",
                "items": [dict(item) for item in self.items],
                "observation_count": self.observation_count,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )


def snapshot_inventory(path: str | Path) -> SnapshotInventory:
    snapshot = read_snapshot_file(path)
    items = tuple(
        {
            "checksum": item.envelope.checksum,
            "close": item.payload.close,
            "market_timestamp": format_canonical_timestamp(item.envelope.market_timestamp)
            if item.envelope.market_timestamp is not None
            else None,
            "provenance_class": item.envelope.provenance_class,
            "symbol_or_universe": item.envelope.symbol_or_universe,
        }
        for item in snapshot.observations
    )
    return SnapshotInventory(
        dataset_id=snapshot.declaration.dataset_id,
        observation_count=len(items),
        items=items,
    )
