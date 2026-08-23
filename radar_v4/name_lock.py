"""Filename identity checks. Not market evidence."""

from __future__ import annotations

from pathlib import Path

from radar_v4.integrity import IntegrityCheck
from radar_v4.path_lock import path_lock

RESERVED_STEMS = frozenset(
    {
        "aux",
        "com1",
        "com2",
        "com3",
        "com4",
        "con",
        "lpt1",
        "lpt2",
        "lpt3",
        "nul",
        "prn",
    }
)


def reserved_stem_scan(directory: Path) -> IntegrityCheck:
    hits = [
        path.name
        for path in sorted(Path(directory).iterdir())
        if path.is_file() and path.stem.casefold() in RESERVED_STEMS
    ]
    if hits:
        return IntegrityCheck(
            "radar_v4.reserved_stems",
            False,
            "RESERVED_STEM_REFUSED",
            ("A reserved device stem is not a workshop filename.",),
            {"hits": hits},
        )
    return IntegrityCheck(
        "radar_v4.reserved_stems",
        True,
        None,
        ("No reserved device stems.",),
        {"hits": []},
    )


def leading_hyphen_scan(directory: Path) -> IntegrityCheck:
    hits = [
        path.name
        for path in sorted(Path(directory).iterdir())
        if path.is_file() and path.name.startswith("-")
    ]
    if hits:
        return IntegrityCheck(
            "radar_v4.leading_hyphen",
            False,
            "LEADING_HYPHEN_REFUSED",
            ("A leading hyphen is not a workshop filename.",),
            {"hits": hits},
        )
    return IntegrityCheck(
        "radar_v4.leading_hyphen",
        True,
        None,
        ("No leading-hyphen filenames.",),
        {"hits": []},
    )


def double_json_scan(directory: Path) -> IntegrityCheck:
    hits = [
        path.name
        for path in sorted(Path(directory).iterdir())
        if path.is_file() and path.name.casefold().endswith(".json.json")
    ]
    if hits:
        return IntegrityCheck(
            "radar_v4.double_json",
            False,
            "DOUBLE_JSON_REFUSED",
            ("A double .json extension is not a workshop name.",),
            {"hits": hits},
        )
    return IntegrityCheck(
        "radar_v4.double_json",
        True,
        None,
        ("No double .json filenames.",),
        {"hits": []},
    )


def empty_pack_scan(directory: Path) -> IntegrityCheck:
    root = Path(directory)
    if not root.is_dir():
        return IntegrityCheck(
            "radar_v4.empty_pack",
            False,
            "UNREADABLE_PACK",
            ("pack is not a directory",),
            {},
        )
    files = [path.name for path in sorted(root.iterdir()) if path.is_file()]
    if not files:
        return IntegrityCheck(
            "radar_v4.empty_pack",
            False,
            "EMPTY_PACK",
            ("An empty directory is not a pack.",),
            {"files": []},
        )
    return IntegrityCheck(
        "radar_v4.empty_pack",
        True,
        None,
        ("Directory contains files. Not a measurement.",),
        {"files": files},
    )


def name_lock(directory: Path) -> IntegrityCheck:
    parts = [
        empty_pack_scan(directory),
        path_lock(directory),
        reserved_stem_scan(directory),
        leading_hyphen_scan(directory),
        double_json_scan(directory),
    ]
    failed = [part for part in parts if not part.valid]
    if failed:
        first = failed[0]
        return IntegrityCheck(
            "radar_v4.name_lock",
            False,
            first.error_code,
            ("Name lock failed.",) + first.notes,
            {"failed": [part.document_kind for part in failed]},
        )
    return IntegrityCheck(
        "radar_v4.name_lock",
        True,
        None,
        ("Name lock passed. Not market evidence.",),
        {"failed": []},
    )
