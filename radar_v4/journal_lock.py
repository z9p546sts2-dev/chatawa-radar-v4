"""Quarantine-journal identity checks. Not a scoring system."""

from __future__ import annotations

from json import JSONDecodeError, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.bind_check import journal_code_catalog
from radar_v4.integrity import IntegrityCheck
from radar_v4.snapshot_files import SnapshotFileError

JOURNAL_KIND = "radar_v4.quarantine_journal"
KNOWN_JOURNAL_SOURCES = frozenset(
    {
        "admission",
        "observation",
        "pack",
        "pack_observation",
        "pack_unreadable",
        "series",
    }
)


def _load_journal(path: Path) -> tuple[dict[str, object] | None, IntegrityCheck | None]:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return None, IntegrityCheck(
            "radar_v4.journal_readable",
            False,
            "UNREADABLE_JOURNAL",
            ("unreadable quarantine journal",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return None, IntegrityCheck(
            "radar_v4.journal_readable",
            False,
            "UNREADABLE_JOURNAL",
            ("quarantine journal is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return None, IntegrityCheck(
            "radar_v4.journal_readable",
            False,
            "UNREADABLE_JOURNAL",
            ("quarantine journal must be an object",),
            {"path": str(target)},
        )
    return raw, None


def journal_kind_scan(path: Path) -> IntegrityCheck:
    raw, error = _load_journal(path)
    if error is not None:
        return error
    assert raw is not None
    if raw.get("document_kind") != JOURNAL_KIND:
        return IntegrityCheck(
            "radar_v4.journal_kind",
            False,
            "JOURNAL_KIND_REFUSED",
            ("A journal must name radar_v4.quarantine_journal. Not repaired.",),
            {"path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.journal_kind",
        True,
        None,
        ("Journal kind is locked. Not a score.",),
        {"path": str(path)},
    )


def journal_entries_scan(path: Path) -> IntegrityCheck:
    raw, error = _load_journal(path)
    if error is not None:
        return error
    assert raw is not None
    entries = raw.get("entries")
    if not isinstance(entries, list):
        return IntegrityCheck(
            "radar_v4.journal_entries",
            False,
            "JOURNAL_ENTRY_INVALID",
            ("Journal entries must be an array. An empty array is allowed.",),
            {"path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.journal_entries",
        True,
        None,
        ("Journal entries are an array. Zero refusals is valid.",),
        {"count": len(entries), "path": str(path)},
    )


def journal_entry_shape_scan(path: Path) -> IntegrityCheck:
    raw, error = _load_journal(path)
    if error is not None:
        return error
    assert raw is not None
    entries = raw.get("entries")
    if not isinstance(entries, list):
        return IntegrityCheck(
            "radar_v4.journal_entry_shape",
            False,
            "JOURNAL_ENTRY_INVALID",
            ("Journal entries must be an array before shape is checked.",),
            {"path": str(path)},
        )
    hits = []
    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            hits.append({"index": index, "reason": "not_object"})
            continue
        code = item.get("code")
        if not isinstance(code, str) or not code:
            hits.append({"index": index, "reason": "missing_code"})
    if hits:
        return IntegrityCheck(
            "radar_v4.journal_entry_shape",
            False,
            "JOURNAL_ENTRY_INVALID",
            ("Each journal entry must be an object with a code. Not repaired.",),
            {"hits": hits, "path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.journal_entry_shape",
        True,
        None,
        ("Journal entry shape passed. Not a scoring system.",),
        {"hits": [], "path": str(path)},
    )


def journal_source_scan(path: Path) -> IntegrityCheck:
    raw, error = _load_journal(path)
    if error is not None:
        return error
    assert raw is not None
    entries = raw.get("entries")
    if not isinstance(entries, list):
        return IntegrityCheck(
            "radar_v4.journal_source",
            False,
            "JOURNAL_ENTRY_INVALID",
            ("Journal entries must be an array before sources are checked.",),
            {"path": str(path)},
        )
    hits = []
    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            continue
        source = item.get("source")
        if source is None:
            continue
        if not isinstance(source, str) or source not in KNOWN_JOURNAL_SOURCES:
            hits.append({"index": index, "source": source})
    if hits:
        return IntegrityCheck(
            "radar_v4.journal_source",
            False,
            "JOURNAL_SOURCE_REFUSED",
            ("An unknown journal source is refused, not repaired.",),
            {"hits": hits, "path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.journal_source",
        True,
        None,
        ("Journal sources are in the locked set. Not a method.",),
        {"hits": [], "path": str(path)},
    )


def journal_lock(path: Path) -> IntegrityCheck:
    parts = [
        journal_kind_scan(path),
        journal_entries_scan(path),
        journal_entry_shape_scan(path),
        journal_source_scan(path),
    ]
    if all(part.valid for part in parts):
        try:
            parts.append(journal_code_catalog(path))
        except SnapshotFileError as exc:
            parts.append(
                IntegrityCheck(
                    "radar_v4.journal_codes",
                    False,
                    exc.code,
                    (exc.reason,),
                    {"path": str(path)},
                )
            )
    failed = [part for part in parts if not part.valid]
    if failed:
        first = failed[0]
        return IntegrityCheck(
            "radar_v4.journal_lock",
            False,
            first.error_code,
            ("Journal lock failed.",) + first.notes,
            {"failed": [part.document_kind for part in failed]},
        )
    return IntegrityCheck(
        "radar_v4.journal_lock",
        True,
        None,
        ("Journal lock passed. Not a scoring system.",),
        {"failed": []},
    )


def journal_lock_determinism(path: Path) -> IntegrityCheck:
    first = journal_lock(path)
    second = journal_lock(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.journal_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Journal lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_journal_lock(left: Path, right: Path) -> IntegrityCheck:
    first = journal_lock(left)
    second = journal_lock(right)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.compare_journal_lock",
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared journal-lock records. Equality is not a score.",),
        {"equal": equal},
    )


def write_journal_record(
    journal: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = journal_lock(journal)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_journal_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.journal_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable journal-lock record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.journal_verify",
            False,
            "UNREADABLE_JSON",
            ("journal-lock record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.journal_verify",
            False,
            "UNREADABLE_JSON",
            ("journal-lock record must be an object",),
            {"path": str(target)},
        )
    ok = raw.get("document_kind") == "radar_v4.journal_lock" and raw.get("valid") is True
    return IntegrityCheck(
        "radar_v4.journal_verify",
        ok,
        None if ok else "JOURNAL_RECORD_INVALID",
        ("Verified a local journal-lock record. Not market evidence.",),
        {"path": str(target)},
    )
