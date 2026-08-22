"""Describe a local pack without measuring close-to-close changes."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from json import dumps
from pathlib import Path

from radar_v4.dataset import admit_to_dataset
from radar_v4.dataset_pack import load_dataset_pack
from radar_v4.declaration_json import intake_declaration_json
from radar_v4.evidence import format_canonical_timestamp
from radar_v4.pack_inventory import inventory_pack
from radar_v4.ruler import declaration_ruler, ruler_checksum


def _dump(document: dict[str, object]) -> str:
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


@dataclass(frozen=True)
class PackLayout:
    directory: str
    declaration_present: bool
    observation_files: int
    manifest_present: bool
    ready_to_load: bool
    issues: tuple[str, ...]

    def serialize(self) -> str:
        return _dump(
            {
                "declaration_present": self.declaration_present,
                "directory": self.directory,
                "document_kind": "radar_v4.pack_layout",
                "issues": list(self.issues),
                "manifest_present": self.manifest_present,
                "observation_files": self.observation_files,
                "ready_to_load": self.ready_to_load,
            }
        )


def inspect_pack_layout(directory: str | Path) -> PackLayout:
    inventory = inventory_pack(directory)
    if not inventory.present:
        return PackLayout(
            directory=str(Path(directory)),
            declaration_present=False,
            observation_files=0,
            manifest_present=False,
            ready_to_load=False,
            issues=("UNREADABLE_PACK",),
        )
    declaration_present = any(item.role == "declaration" for item in inventory.files)
    observation_files = len(inventory.observation_names())
    manifest_present = any(item.name == "manifest.json" for item in inventory.files)
    issues: list[str] = []
    if not declaration_present:
        issues.append("LAYOUT_DECLARATION_MISSING")
    if observation_files == 0:
        issues.append("LAYOUT_NO_OBSERVATIONS")
    return PackLayout(
        directory=inventory.directory,
        declaration_present=declaration_present,
        observation_files=observation_files,
        manifest_present=manifest_present,
        ready_to_load=declaration_present and observation_files > 0,
        issues=tuple(issues),
    )


@dataclass(frozen=True)
class ProvenanceMix:
    directory: str
    counts: dict[str, int]
    error_code: str | None

    def serialize(self) -> str:
        return _dump(
            {
                "counts": dict(sorted(self.counts.items())),
                "directory": self.directory,
                "document_kind": "radar_v4.provenance_mix",
                "error_code": self.error_code,
            }
        )


def provenance_mix(directory: str | Path) -> ProvenanceMix:
    """Count provenance labels after pack intake. Does not compute changes."""
    pack = load_dataset_pack(directory)
    if pack.declaration is None and not pack.observation_intake.accepted:
        return ProvenanceMix(str(Path(directory)), {}, pack.pack_issues[0].code if pack.pack_issues else "PACK_NOT_USABLE")
    counts: Counter[str] = Counter()
    if pack.declaration is not None:
        counts[f"declaration:{pack.declaration.provenance_class}"] += 1
    for item in pack.observation_intake.accepted:
        counts[item.envelope.provenance_class] += 1
    for record in pack.observation_intake.quarantined:
        counts[f"quarantined:{record.observation.envelope.provenance_class}"] += 1
    return ProvenanceMix(str(Path(directory)), dict(counts), None)


@dataclass(frozen=True)
class PackIdentities:
    directory: str
    accepted: tuple[dict[str, str | None], ...]
    quarantined: tuple[dict[str, str | None], ...]
    error_code: str | None

    def serialize(self) -> str:
        return _dump(
            {
                "accepted": [dict(item) for item in self.accepted],
                "directory": self.directory,
                "document_kind": "radar_v4.pack_identities",
                "error_code": self.error_code,
                "quarantined": [dict(item) for item in self.quarantined],
            }
        )


def pack_identities(directory: str | Path) -> PackIdentities:
    """List envelope identities. Does not describe close-to-close changes."""
    pack = load_dataset_pack(directory)
    if not pack.usable() and pack.declaration is None:
        return PackIdentities(str(Path(directory)), (), (), "PACK_NOT_USABLE")

    def _row(item) -> dict[str, str | None]:
        envelope = item.envelope
        return {
            "checksum": envelope.checksum,
            "market_timestamp": format_canonical_timestamp(envelope.market_timestamp)
            if envelope.market_timestamp is not None
            else None,
            "provenance_class": envelope.provenance_class,
            "symbol_or_universe": envelope.symbol_or_universe,
        }

    return PackIdentities(
        str(Path(directory)),
        tuple(_row(item) for item in pack.observation_intake.accepted),
        tuple(_row(record.observation) for record in pack.observation_intake.quarantined),
        None if pack.usable() else "PACK_NOT_USABLE",
    )


@dataclass(frozen=True)
class PackReadiness:
    directory: str
    usable_pack: bool
    accepted_observations: int
    admitted_observations: int
    enough_for_close_to_close: bool
    notes: tuple[str, ...]

    def serialize(self) -> str:
        return _dump(
            {
                "accepted_observations": self.accepted_observations,
                "admitted_observations": self.admitted_observations,
                "directory": self.directory,
                "document_kind": "radar_v4.pack_readiness",
                "enough_for_close_to_close": self.enough_for_close_to_close,
                "notes": list(self.notes),
                "usable_pack": self.usable_pack,
            }
        )


def pack_readiness(directory: str | Path) -> PackReadiness:
    """Say whether declaration-admitted observations could be measured.

    Pack-loader acceptance is not admission. This does not measure.
    """
    pack = load_dataset_pack(directory)
    accepted = pack.observation_intake.accepted_count()
    admitted = 0
    if pack.declaration is not None:
        envelopes = tuple(item.envelope for item in pack.observation_intake.accepted)
        admitted = admit_to_dataset(pack.declaration, envelopes).accepted_count()
    notes = [
        "readiness is not a measurement",
        "enough_for_close_to_close requires two declaration-admitted observations",
        "pack-accepted files are not automatically admitted",
        "SYNTHETIC and FIXTURE numbers are not HISTORICAL evidence",
    ]
    if pack.declaration is not None and pack.declaration.provenance_class in {
        "SYNTHETIC",
        "FIXTURE",
    }:
        notes.append("declared provenance is not HISTORICAL")
    return PackReadiness(
        directory=str(Path(directory)),
        usable_pack=pack.usable(),
        accepted_observations=accepted,
        admitted_observations=admitted,
        enough_for_close_to_close=pack.usable() and admitted >= 2,
        notes=tuple(notes),
    )


@dataclass(frozen=True)
class PackDescription:
    layout: PackLayout
    readiness: PackReadiness
    ruler_checksum: str | None

    def serialize(self) -> str:
        ruler = None
        path = Path(self.layout.directory) / "declaration.json"
        if path.is_file():
            parsed = intake_declaration_json(path.read_text(encoding="utf-8"))
            if parsed.declaration is not None:
                ruler = {
                    "ruler": declaration_ruler(parsed.declaration),
                    "ruler_checksum": ruler_checksum(parsed.declaration),
                }
        return _dump(
            {
                "document_kind": "radar_v4.pack_describe",
                "layout": _loads(self.layout.serialize()),
                "readiness": _loads(self.readiness.serialize()),
                "ruler": ruler,
            }
        )


def describe_pack(directory: str | Path) -> PackDescription:
    return PackDescription(
        layout=inspect_pack_layout(directory),
        readiness=pack_readiness(directory),
        ruler_checksum=None,
    )


def _loads(text: str) -> dict[str, object]:
    from json import loads

    parsed = loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("expected a JSON object")
    return parsed
