"""Path and leftover identity checks. Not market evidence."""

from __future__ import annotations

from pathlib import Path

from radar_v4.integrity import IntegrityCheck, lock_source_details

BACKUP_SUFFIXES = frozenset({".bak", ".orig", ".rej", ".swp"})


def backup_leftover_scan(directory: Path) -> IntegrityCheck:
    hits: list[str] = []
    for path in sorted(Path(directory).iterdir()):
        if not path.is_file():
            continue
        name = path.name
        if name.endswith("~") or path.suffix.casefold() in BACKUP_SUFFIXES:
            hits.append(name)
    if hits:
        return IntegrityCheck(
            "radar_v4.backup_leftovers",
            False,
            "BACKUP_LEFTOVER",
            ("Editor backup files are not workshop evidence.",),
            {"hits": hits},
        )
    return IntegrityCheck(
        "radar_v4.backup_leftovers",
        True,
        None,
        ("No editor backup leftovers.",),
        {"hits": []},
    )


def ascii_name_scan(directory: Path) -> IntegrityCheck:
    hits = [
        path.name
        for path in sorted(Path(directory).iterdir())
        if path.is_file() and not path.name.isascii()
    ]
    if hits:
        return IntegrityCheck(
            "radar_v4.ascii_names",
            False,
            "NON_ASCII_NAME",
            ("Pack filenames must be ASCII. Names are not repaired.",),
            {"hits": hits},
        )
    return IntegrityCheck(
        "radar_v4.ascii_names",
        True,
        None,
        ("Pack filenames are ASCII.",),
        {"hits": []},
    )


def space_name_scan(directory: Path) -> IntegrityCheck:
    hits = [
        path.name
        for path in sorted(Path(directory).iterdir())
        if path.is_file() and (" " in path.name or path.name != path.name.strip())
    ]
    if hits:
        return IntegrityCheck(
            "radar_v4.space_names",
            False,
            "SPACE_IN_NAME",
            ("A space in a filename is not a workshop pack name.",),
            {"hits": hits},
        )
    return IntegrityCheck(
        "radar_v4.space_names",
        True,
        None,
        ("Pack filenames have no spaces.",),
        {"hits": []},
    )


def path_lock(directory: Path) -> IntegrityCheck:
    parts = [
        backup_leftover_scan(directory),
        ascii_name_scan(directory),
        space_name_scan(directory),
    ]
    failed = [part for part in parts if not part.valid]
    if failed:
        first = failed[0]
        return IntegrityCheck(
            "radar_v4.path_lock",
            False,
            first.error_code,
            ("Path lock failed.",) + first.notes,
            lock_source_details(
                directory, {"failed": [part.document_kind for part in failed]}
            ),
        )
    return IntegrityCheck(
        "radar_v4.path_lock",
        True,
        None,
        ("Path lock passed. Not market evidence.",),
        lock_source_details(directory, {"failed": []}),
    )
