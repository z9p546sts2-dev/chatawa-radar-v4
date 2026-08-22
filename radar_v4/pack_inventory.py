"""List a local pack's files without measuring or admitting them."""

from __future__ import annotations

from dataclasses import dataclass
from json import dumps
from pathlib import Path

from radar_v4.dataset_pack import DECLARATION_FILENAME, SKIP_FILENAMES

DOCUMENT_KIND = "radar_v4.pack_inventory"


@dataclass(frozen=True)
class PackFile:
    name: str
    role: str


@dataclass(frozen=True)
class PackInventory:
    directory: str
    present: bool
    files: tuple[PackFile, ...]
    error_code: str | None

    def observation_names(self) -> tuple[str, ...]:
        return tuple(item.name for item in self.files if item.role == "observation")

    def serialize(self) -> str:
        document = {
            "directory": self.directory,
            "document_kind": DOCUMENT_KIND,
            "error_code": self.error_code,
            "files": [{"name": item.name, "role": item.role} for item in self.files],
            "observation_count": len(self.observation_names()),
            "present": self.present,
        }
        return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _role_for(name: str) -> str:
    if name == DECLARATION_FILENAME:
        return "declaration"
    if name in SKIP_FILENAMES:
        return "artifact"
    if name.endswith(".json"):
        return "observation"
    return "other"


def inventory_pack(directory: str | Path) -> PackInventory:
    """Describe filenames and roles. Does not parse observations or run a session."""
    root = Path(directory)
    if not root.is_dir():
        return PackInventory(
            directory=str(root),
            present=False,
            files=(),
            error_code="UNREADABLE_PACK",
        )
    files = tuple(
        PackFile(name=path.name, role=_role_for(path.name))
        for path in sorted(root.iterdir())
        if path.is_file()
    )
    return PackInventory(
        directory=str(root),
        present=True,
        files=files,
        error_code=None,
    )
