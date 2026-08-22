"""Write a snapshot back to a local FIXTURE/SYNTHETIC pack. No vendor."""

from __future__ import annotations

from dataclasses import asdict
from json import dumps
from pathlib import Path

from radar_v4.dataset_pack import DECLARATION_FILENAME
from radar_v4.fixture_pack import PACK_ALLOWED_PROVENANCE
from radar_v4.pack_manifest import write_pack_manifest
from radar_v4.snapshot import DatasetSnapshot


class PackExportError(ValueError):
    def __init__(self, code: str, reason: str) -> None:
        self.code = code
        self.reason = reason
        super().__init__(reason)


def export_snapshot_to_pack(snapshot: DatasetSnapshot, directory: str | Path) -> Path:
    """Write declaration.json and observation files. Refuse HISTORICAL/LIVE."""
    if snapshot.declaration.provenance_class not in PACK_ALLOWED_PROVENANCE:
        raise PackExportError(
            "PACK_PROVENANCE_NOT_ALLOWED",
            "pack export may write only FIXTURE or SYNTHETIC declarations",
        )
    for item in snapshot.observations:
        if item.envelope.provenance_class not in PACK_ALLOWED_PROVENANCE:
            raise PackExportError(
                "PACK_PROVENANCE_NOT_ALLOWED",
                "pack export may write only FIXTURE or SYNTHETIC observations",
            )

    target = Path(directory)
    if target.exists() and target.is_file():
        raise PackExportError(
            "PACK_EXPORT_PATH_IS_FILE",
            f"{target} is a file, not a pack directory",
        )
    if target.exists() and any(target.iterdir()):
        raise PackExportError(
            "PACK_EXPORT_DIRECTORY_NOT_EMPTY",
            f"{target} already contains files; export will not merge or repair",
        )
    target.mkdir(parents=True, exist_ok=True)
    (target / DECLARATION_FILENAME).write_text(
        dumps(asdict(snapshot.declaration), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for index, item in enumerate(snapshot.observations, start=1):
        document = {
            "envelope": item.envelope.serialize(),
            "payload": item.payload.canonical_payload(),
            "payload_checksum": item.payload_checksum,
        }
        name = f"obs_{index:04d}.json"
        (target / name).write_text(
            dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    write_pack_manifest(target)
    return target
