"""Refuse unsafe or silently-ignored pack files. No repair. No measurement."""

from __future__ import annotations

from dataclasses import dataclass
from json import dumps
from pathlib import Path

from radar_v4.dataset_pack import SKIP_FILENAMES

MAX_PACK_FILE_BYTES = 1_048_576


def _dump(document: dict[str, object]) -> str:
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


@dataclass(frozen=True)
class PackSafety:
    directory: str
    safe: bool
    issues: tuple[str, ...]
    details: dict[str, object]

    def serialize(self) -> str:
        return _dump(
            {
                "details": self.details,
                "directory": self.directory,
                "document_kind": "radar_v4.pack_safety",
                "error_code": None if self.safe else (self.issues[0] if self.issues else "PACK_NOT_USABLE"),
                "issues": list(self.issues),
                "safe": self.safe,
            }
        )


def inspect_pack_safety(directory: str | Path) -> PackSafety:
    """Inspect BOM, symlink, empty, nested, casefold, UTF-8, and size."""
    root = Path(directory)
    if not root.is_dir():
        return PackSafety(str(root), False, ("UNREADABLE_PACK",), {"present": False})
    issues: list[str] = []
    bom_files: list[str] = []
    symlinks: list[str] = []
    empty: list[str] = []
    not_utf8: list[str] = []
    too_large: list[str] = []
    for path in sorted(root.iterdir()):
        if path.is_symlink():
            symlinks.append(path.name)
            issues.append("PACK_SYMLINK")
            continue
        if not path.is_file():
            continue
        data = path.read_bytes()
        if path.suffix == ".json" or path.name in SKIP_FILENAMES:
            if data.startswith(b"\xef\xbb\xbf"):
                bom_files.append(path.name)
                issues.append("PACK_BOM")
            if not data:
                empty.append(path.name)
                issues.append("PACK_EMPTY_FILE")
            if len(data) > MAX_PACK_FILE_BYTES:
                too_large.append(path.name)
                issues.append("PACK_FILE_TOO_LARGE")
            try:
                data.decode("utf-8")
            except UnicodeDecodeError:
                not_utf8.append(path.name)
                issues.append("PACK_NOT_UTF8")
    nested = [
        str(path.relative_to(root))
        for path in sorted(root.rglob("*.json"))
        if path.parent != root
    ]
    if nested:
        issues.append("PACK_NESTED_JSON")
    casefold_groups: dict[str, list[str]] = {}
    for path in root.iterdir():
        if path.is_file() or path.is_symlink():
            casefold_groups.setdefault(path.name.casefold(), []).append(path.name)
    collisions = [names for names in casefold_groups.values() if len(names) > 1]
    if collisions:
        issues.append("PACK_CASEFOLD_COLLISION")
    unique_issues = tuple(dict.fromkeys(issues))
    return PackSafety(
        directory=str(root),
        safe=not unique_issues,
        issues=unique_issues,
        details={
            "bom_files": bom_files,
            "casefold_collisions": collisions,
            "empty_files": empty,
            "nested_json": nested,
            "not_utf8": not_utf8,
            "symlinks": symlinks,
            "too_large": too_large,
        },
    )


def refuse_bom(directory: str | Path) -> PackSafety:
    report = inspect_pack_safety(directory)
    issues = tuple(code for code in report.issues if code == "PACK_BOM")
    return PackSafety(report.directory, not issues, issues, {"bom_files": report.details.get("bom_files")})


def refuse_symlink(directory: str | Path) -> PackSafety:
    report = inspect_pack_safety(directory)
    issues = tuple(code for code in report.issues if code == "PACK_SYMLINK")
    return PackSafety(report.directory, not issues, issues, {"symlinks": report.details.get("symlinks")})


def refuse_empty(directory: str | Path) -> PackSafety:
    report = inspect_pack_safety(directory)
    issues = tuple(code for code in report.issues if code == "PACK_EMPTY_FILE")
    return PackSafety(report.directory, not issues, issues, {"empty_files": report.details.get("empty_files")})
