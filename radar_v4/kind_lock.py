"""Document-kind identity checks. Not a taxonomy score."""

from __future__ import annotations

from pathlib import Path

from radar_v4.document_kind import detect_document_kind
from radar_v4.integrity import IntegrityCheck


def _json_files(directory: Path) -> list[Path]:
    root = Path(directory)
    if not root.is_dir():
        return []
    return [
        path
        for path in sorted(root.iterdir())
        if path.is_file() and path.suffix.casefold() == ".json"
    ]


def unreadable_kind_scan(directory: Path) -> IntegrityCheck:
    root = Path(directory)
    if not root.is_dir():
        return IntegrityCheck(
            "radar_v4.unreadable_kind",
            False,
            "UNREADABLE_PACK",
            ("pack is not a directory",),
            {},
        )
    hits = [
        path.name
        for path in _json_files(root)
        if detect_document_kind(path).error_code == "UNREADABLE_JSON"
    ]
    if hits:
        return IntegrityCheck(
            "radar_v4.unreadable_kind",
            False,
            "UNREADABLE_JSON",
            ("Unreadable JSON is not repaired into a document kind.",),
            {"hits": hits},
        )
    return IntegrityCheck(
        "radar_v4.unreadable_kind",
        True,
        None,
        ("JSON files are readable. Not a measurement.",),
        {"hits": []},
    )


def unlabeled_kind_scan(directory: Path) -> IntegrityCheck:
    hits = []
    for path in _json_files(directory):
        detected = detect_document_kind(path)
        if detected.document_kind is None and detected.error_code == "UNKNOWN_DOCUMENT_KIND":
            hits.append(path.name)
    if hits:
        return IntegrityCheck(
            "radar_v4.unlabeled_kind",
            False,
            "UNLABELED_KIND_REFUSED",
            ("Unlabeled JSON is not inferred beyond the locked local kinds.",),
            {"hits": hits},
        )
    return IntegrityCheck(
        "radar_v4.unlabeled_kind",
        True,
        None,
        ("JSON files are labeled or inferred. Not a taxonomy score.",),
        {"hits": []},
    )


def unknown_kind_scan(directory: Path) -> IntegrityCheck:
    hits = []
    for path in _json_files(directory):
        detected = detect_document_kind(path)
        if detected.document_kind is not None and not detected.known:
            hits.append({"name": path.name, "kind": detected.document_kind})
    if hits:
        return IntegrityCheck(
            "radar_v4.unknown_kind",
            False,
            "UNKNOWN_DOCUMENT_KIND",
            ("An unknown document_kind is refused, not repaired.",),
            {"hits": hits},
        )
    return IntegrityCheck(
        "radar_v4.unknown_kind",
        True,
        None,
        ("Document kinds are in the catalog. Not a method.",),
        {"hits": []},
    )


def kind_describe(directory: Path) -> IntegrityCheck:
    files = []
    for path in _json_files(directory):
        detected = detect_document_kind(path)
        files.append(
            {
                "inferred": detected.inferred,
                "kind": detected.document_kind,
                "known": detected.known,
                "name": path.name,
            }
        )
    return IntegrityCheck(
        "radar_v4.kind_describe",
        True,
        None,
        ("Document kinds described. Description is not a score.",),
        {"files": files},
    )


def kind_lock(directory: Path) -> IntegrityCheck:
    parts = [
        unreadable_kind_scan(directory),
        unlabeled_kind_scan(directory),
        unknown_kind_scan(directory),
    ]
    failed = [part for part in parts if not part.valid]
    if failed:
        first = failed[0]
        return IntegrityCheck(
            "radar_v4.kind_lock",
            False,
            first.error_code,
            ("Kind lock failed.",) + first.notes,
            {"failed": [part.document_kind for part in failed]},
        )
    return IntegrityCheck(
        "radar_v4.kind_lock",
        True,
        None,
        ("Kind lock passed. Not a taxonomy score.",),
        {"failed": []},
    )
