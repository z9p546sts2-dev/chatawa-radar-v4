"""Write and read a ruler sidecar. Not a method and not a dataset nickname."""

from __future__ import annotations

from collections.abc import Mapping
from json import JSONDecodeError, dumps, loads
from pathlib import Path

from radar_v4.dataset import DatasetDeclaration
from radar_v4.ruler import declaration_ruler, ruler_checksum
from radar_v4.snapshot_files import SnapshotFileError

DOCUMENT_KIND = "radar_v4.ruler"


def ruler_sidecar_path(snapshot_path: str | Path) -> Path:
    return Path(str(Path(snapshot_path)) + ".ruler.json")


def serialize_ruler(declaration: DatasetDeclaration) -> str:
    document = {
        "document_kind": DOCUMENT_KIND,
        "ruler": declaration_ruler(declaration),
        "ruler_checksum": ruler_checksum(declaration),
    }
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def write_ruler_sidecar(snapshot_path: str | Path, declaration: DatasetDeclaration) -> Path:
    target = ruler_sidecar_path(snapshot_path)
    if target.exists() and target.is_dir():
        raise SnapshotFileError(
            "RULER_SIDECAR_PATH_IS_DIRECTORY",
            f"{target} is a directory, not a ruler sidecar",
        )
    target.write_text(serialize_ruler(declaration) + "\n", encoding="utf-8")
    return target


def read_ruler_sidecar(snapshot_path: str | Path) -> dict[str, object]:
    target = ruler_sidecar_path(snapshot_path)
    try:
        text = target.read_text(encoding="utf-8")
    except OSError as exc:
        raise SnapshotFileError(
            "UNREADABLE_RULER_SIDECAR",
            f"ruler sidecar could not be read: {exc}",
        ) from exc
    try:
        raw = loads(text)
    except JSONDecodeError as exc:
        raise SnapshotFileError(
            "UNREADABLE_RULER_SIDECAR",
            f"ruler sidecar is not readable JSON: {exc.msg}",
        ) from exc
    if not isinstance(raw, Mapping):
        raise SnapshotFileError(
            "UNREADABLE_RULER_SIDECAR",
            "ruler sidecar must be a JSON object",
        )
    kind = raw.get("document_kind")
    if kind is not None and kind != DOCUMENT_KIND:
        raise SnapshotFileError(
            "UNREADABLE_RULER_SIDECAR",
            f"document_kind {kind!r} is not {DOCUMENT_KIND}",
        )
    return dict(raw)
