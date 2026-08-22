"""Compare local evidence artifacts. No merge. No method."""

from __future__ import annotations

from dataclasses import dataclass
from json import dumps
from pathlib import Path

from radar_v4.declaration_json import intake_declaration_json
from radar_v4.pack_inventory import inventory_pack
from radar_v4.pack_manifest import PackManifestError, read_pack_manifest
from radar_v4.ruler import declaration_ruler, ruler_checksum
from radar_v4.session_report import read_session_report_file
from radar_v4.snapshot_files import SnapshotFileError, read_snapshot_file


def _dump(document: dict[str, object]) -> str:
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _ruler_from_path(path: str | Path) -> tuple[str, dict[str, str]]:
    target = Path(path)
    if target.is_dir():
        declaration_path = target / "declaration.json"
        if not declaration_path.is_file():
            raise SnapshotFileError(
                "UNREADABLE_DECLARATION",
                f"{target} has no declaration.json",
            )
        parsed = intake_declaration_json(declaration_path.read_text(encoding="utf-8"))
        if parsed.declaration is None:
            raise SnapshotFileError(
                "UNREADABLE_DECLARATION",
                f"{target} has no usable declaration.json",
            )
        declaration = parsed.declaration
    else:
        declaration = read_snapshot_file(target).declaration
    return ruler_checksum(declaration), declaration_ruler(declaration)


@dataclass(frozen=True)
class RulerComparison:
    equal: bool
    left: str
    right: str

    def serialize(self) -> str:
        return _dump(
            {
                "document_kind": "radar_v4.ruler_comparison",
                "equal": self.equal,
                "left": self.left,
                "right": self.right,
            }
        )


def compare_rulers(left_path: str | Path, right_path: str | Path) -> RulerComparison:
    left, _ = _ruler_from_path(left_path)
    right, _ = _ruler_from_path(right_path)
    return RulerComparison(equal=left == right, left=left, right=right)


def _report_checksums(document: dict[str, object]) -> dict[str, object]:
    session = document.get("session")
    if isinstance(session, dict):
        return {
            "dataset_id": session.get("dataset_id"),
            "ruler_checksum": session.get("ruler_checksum"),
            "snapshot_checksum": session.get("snapshot_checksum"),
            "baseline_status": (session.get("baseline") or {}).get("status")
            if isinstance(session.get("baseline"), dict)
            else None,
        }
    baseline = document.get("baseline")
    return {
        "dataset_id": document.get("dataset_id"),
        "ruler_checksum": document.get("ruler_checksum"),
        "snapshot_checksum": document.get("snapshot_checksum"),
        "baseline_status": baseline.get("status") if isinstance(baseline, dict) else None,
    }


@dataclass(frozen=True)
class ReportComparison:
    equal: bool
    left: dict[str, object]
    right: dict[str, object]

    def serialize(self) -> str:
        return _dump(
            {
                "document_kind": "radar_v4.report_comparison",
                "equal": self.equal,
                "left": self.left,
                "right": self.right,
            }
        )


def compare_session_reports(
    left_path: str | Path, right_path: str | Path
) -> ReportComparison:
    left = _report_checksums(read_session_report_file(left_path))
    right = _report_checksums(read_session_report_file(right_path))
    return ReportComparison(equal=left == right, left=left, right=right)


@dataclass(frozen=True)
class InventoryComparison:
    equal: bool
    left_only: tuple[str, ...]
    right_only: tuple[str, ...]
    digest_mismatches: tuple[str, ...]

    def serialize(self) -> str:
        return _dump(
            {
                "digest_mismatches": list(self.digest_mismatches),
                "document_kind": "radar_v4.inventory_comparison",
                "equal": self.equal,
                "left_only": list(self.left_only),
                "right_only": list(self.right_only),
            }
        )


def compare_inventories(
    left_directory: str | Path, right_directory: str | Path
) -> InventoryComparison:
    left = {item.name: item.digest for item in inventory_pack(left_directory).files}
    right = {item.name: item.digest for item in inventory_pack(right_directory).files}
    left_only = tuple(sorted(set(left) - set(right)))
    right_only = tuple(sorted(set(right) - set(left)))
    mismatches = tuple(
        sorted(name for name in set(left) & set(right) if left[name] != right[name])
    )
    return InventoryComparison(
        equal=not left_only and not right_only and not mismatches,
        left_only=left_only,
        right_only=right_only,
        digest_mismatches=mismatches,
    )


@dataclass(frozen=True)
class InventoryManifestCheck:
    matched: bool
    missing_from_inventory: tuple[str, ...]
    digest_mismatches: tuple[str, ...]
    error_code: str | None

    def serialize(self) -> str:
        return _dump(
            {
                "digest_mismatches": list(self.digest_mismatches),
                "document_kind": "radar_v4.inventory_comparison",
                "error_code": self.error_code,
                "matched": self.matched,
                "missing_from_inventory": list(self.missing_from_inventory),
            }
        )


def inventory_vs_manifest(directory: str | Path) -> InventoryManifestCheck:
    """Compare live file digests with a stored manifest. Does not repair."""
    root = Path(directory)
    try:
        manifest = read_pack_manifest(root)
    except PackManifestError as exc:
        return InventoryManifestCheck(False, (), (), exc.code)
    inventory = {item.name: item.digest for item in inventory_pack(root).files}
    missing = tuple(sorted(name for name in manifest.files if name not in inventory))
    mismatches = tuple(
        sorted(
            name
            for name, digest in manifest.files.items()
            if name in inventory and inventory[name] != digest
        )
    )
    return InventoryManifestCheck(
        matched=not missing and not mismatches,
        missing_from_inventory=missing,
        digest_mismatches=mismatches,
        error_code=None,
    )
