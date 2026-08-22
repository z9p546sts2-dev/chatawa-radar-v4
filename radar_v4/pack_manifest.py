"""Integrity manifest for a local dataset pack. No vendor. No repair."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
from json import JSONDecodeError, dumps, loads
from pathlib import Path

from radar_v4.dataset_pack import SKIP_FILENAMES

MANIFEST_FILENAME = "manifest.json"
DOCUMENT_KIND = "radar_v4.pack_manifest"


class PackManifestError(ValueError):
    def __init__(self, code: str, reason: str) -> None:
        self.code = code
        self.reason = reason
        super().__init__(reason)


@dataclass(frozen=True)
class PackManifest:
    files: dict[str, str]

    def serialize(self) -> str:
        document = {
            "document_kind": DOCUMENT_KIND,
            "files": dict(sorted(self.files.items())),
        }
        return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _file_digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _pack_json_files(root: Path) -> list[Path]:
    return [
        path
        for path in sorted(root.glob("*.json"))
        if path.name not in SKIP_FILENAMES and path.name != MANIFEST_FILENAME
    ]


def build_pack_manifest(directory: str | Path) -> PackManifest:
    root = Path(directory)
    if not root.is_dir():
        raise PackManifestError(
            "UNREADABLE_PACK",
            f"{root} is not a pack directory",
        )
    files = {path.name: _file_digest(path) for path in _pack_json_files(root)}
    declaration = root / "declaration.json"
    if declaration.is_file():
        files["declaration.json"] = _file_digest(declaration)
    return PackManifest(files=files)


def write_pack_manifest(directory: str | Path) -> Path:
    root = Path(directory)
    manifest = build_pack_manifest(root)
    target = root / MANIFEST_FILENAME
    target.write_text(manifest.serialize() + "\n", encoding="utf-8")
    return target


def read_pack_manifest(directory: str | Path) -> PackManifest:
    target = Path(directory) / MANIFEST_FILENAME
    try:
        text = target.read_text(encoding="utf-8")
    except OSError as exc:
        raise PackManifestError(
            "MANIFEST_MISSING",
            f"pack manifest could not be read: {exc}",
        ) from exc
    try:
        raw = loads(text)
    except JSONDecodeError as exc:
        raise PackManifestError(
            "UNREADABLE_MANIFEST",
            f"pack manifest is not readable JSON: {exc.msg}",
        ) from exc
    if not isinstance(raw, Mapping):
        raise PackManifestError(
            "UNREADABLE_MANIFEST",
            "pack manifest must be a JSON object",
        )
    kind = raw.get("document_kind")
    if kind is not None and kind != DOCUMENT_KIND:
        raise PackManifestError(
            "UNREADABLE_MANIFEST",
            f"document_kind {kind!r} is not {DOCUMENT_KIND}",
        )
    files_raw = raw.get("files")
    if not isinstance(files_raw, Mapping):
        raise PackManifestError(
            "UNREADABLE_MANIFEST",
            "pack manifest files must be an object",
        )
    files = {str(name): str(digest) for name, digest in files_raw.items()}
    return PackManifest(files=files)


def verify_pack_manifest(directory: str | Path) -> PackManifest:
    """Refuse a pack whose files do not match the stored manifest."""
    root = Path(directory)
    expected = read_pack_manifest(root)
    actual = build_pack_manifest(root)
    expected_names = set(expected.files)
    actual_names = set(actual.files)
    missing = sorted(expected_names - actual_names)
    unexpected = sorted(actual_names - expected_names)
    if missing:
        raise PackManifestError(
            "MANIFEST_FILE_MISSING",
            f"pack is missing manifest files: {', '.join(missing)}",
        )
    if unexpected:
        raise PackManifestError(
            "MANIFEST_UNEXPECTED_FILE",
            f"pack has files not in the manifest: {', '.join(unexpected)}",
        )
    mismatches = sorted(
        name
        for name, digest in expected.files.items()
        if actual.files.get(name) != digest
    )
    if mismatches:
        raise PackManifestError(
            "MANIFEST_CHECKSUM_MISMATCH",
            f"pack file checksums do not match: {', '.join(mismatches)}",
        )
    return expected
