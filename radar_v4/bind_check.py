"""Bind freeze, journal, and byte records. Not market evidence."""

from __future__ import annotations

from collections import Counter
from json import JSONDecodeError, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.byte_check import (
    byte_check,
    null_byte_scan,
    payload_checksum_required,
    shebang_scan,
    tab_scan,
    trailing_whitespace_scan,
)
from radar_v4.dataset_pack import load_dataset_pack
from radar_v4.freeze import workshop_freeze
from radar_v4.integrity import IntegrityCheck
from radar_v4.local_session import run_session_from_pack
from radar_v4.pack_export import PackExportError, export_snapshot_to_pack
from radar_v4.path_lock import path_lock
from radar_v4.quarantine_journal import read_quarantine_journal_file
from radar_v4.reason_codes import REASON_CODES, RESULT_STATUSES
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


def journal_code_catalog(path: Path) -> IntegrityCheck:
    raw = read_quarantine_journal_file(path)
    entries = raw.get("entries")
    if not isinstance(entries, list):
        return IntegrityCheck(
            "radar_v4.journal_codes",
            False,
            "UNREADABLE_JOURNAL",
            ("Journal entries must be an array.",),
            {"path": str(path)},
        )
    allowed = REASON_CODES | RESULT_STATUSES
    unknown: list[str] = []
    codes: list[str] = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        code = item.get("code")
        if not isinstance(code, str) or not code:
            continue
        codes.append(code)
        if code not in allowed:
            unknown.append(code)
    if unknown:
        return IntegrityCheck(
            "radar_v4.journal_codes",
            False,
            "CODE_UNKNOWN",
            ("A journal code is not in the refusal catalog.",),
            {"unknown": unknown, "codes": codes},
        )
    return IntegrityCheck(
        "radar_v4.journal_codes",
        True,
        None,
        ("Journal codes are in the catalog. Not a scoring system.",),
        {"unknown": [], "codes": codes},
    )


def freeze_status_bind(directory: Path | None = None) -> IntegrityCheck:
    status = loads(workshop_status())
    freeze = workshop_freeze(directory)
    status_unit = int(status.get("highest_unit") or 0)
    freeze_unit = int(freeze.details.get("highest_unit") or 0)
    matched = (
        status_unit == PHASE5_HIGHEST_UNIT
        and freeze_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
        and freeze.valid
    )
    return IntegrityCheck(
        "radar_v4.freeze_status_bind",
        matched,
        None if matched else "FREEZE_STATUS_MISMATCH",
        ("Freeze and status share the locked unit. Not a measurement.",),
        {
            "freeze_unit": freeze_unit,
            "status_unit": status_unit,
            "locked_unit": PHASE5_HIGHEST_UNIT,
        },
    )


def write_byte_record(
    directory: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = byte_check(directory)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_byte_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.byte_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable byte record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.byte_verify",
            False,
            "UNREADABLE_JSON",
            ("byte record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.byte_verify",
            False,
            "UNREADABLE_JSON",
            ("byte record must be an object",),
            {"path": str(target)},
        )
    ok = raw.get("document_kind") == "radar_v4.byte_check" and raw.get("valid") is True
    return IntegrityCheck(
        "radar_v4.byte_verify",
        ok,
        None if ok else "BYTE_RECORD_INVALID",
        ("Verified a local byte-check record. Not market evidence.",),
        {"path": str(target)},
    )


def close_sign_describe(directory: Path) -> IntegrityCheck:
    negatives = 0
    zeros = 0
    checked = 0
    for item in load_dataset_pack(directory).observation_intake.accepted:
        close = item.payload.close
        checked += 1
        if close.startswith("-"):
            negatives += 1
        if close in {"0", "0.0", "0.00"}:
            zeros += 1
    return IntegrityCheck(
        "radar_v4.close_sign",
        True,
        None,
        ("Close signs described. Not a threshold or signal.",),
        {"checked": checked, "negatives": negatives, "zeros": zeros},
    )


def retrieval_unique_describe(directory: Path) -> IntegrityCheck:
    stamps = [
        item.envelope.retrieval_timestamp.isoformat()
        for item in load_dataset_pack(directory).observation_intake.accepted
        if item.envelope.retrieval_timestamp is not None
    ]
    counts = Counter(stamps)
    dups = {key: count for key, count in counts.items() if count > 1}
    return IntegrityCheck(
        "radar_v4.retrieval_unique",
        True,
        None,
        ("Duplicate retrieval times described. Not a trading clock.",),
        {"duplicates": dups, "count": len(dups)},
    )


def export_byte_check(directory: Path, destination: Path) -> IntegrityCheck:
    first = run_session_from_pack(directory)
    if first.session is None:
        return IntegrityCheck(
            "radar_v4.export_byte",
            False,
            first.error_code or "PACK_NOT_USABLE",
            ("Export byte-check needs a usable pack.",),
            {},
        )
    try:
        written = export_snapshot_to_pack(first.session.snapshot, destination)
    except PackExportError as exc:
        return IntegrityCheck(
            "radar_v4.export_byte",
            False,
            exc.code,
            (exc.reason,),
            {},
        )
    parts = [
        trailing_whitespace_scan(written),
        null_byte_scan(written),
        shebang_scan(written),
        tab_scan(written),
        payload_checksum_required(written),
        path_lock(written),
    ]
    failed = [part for part in parts if not part.valid]
    if failed:
        first_fail = failed[0]
        return IntegrityCheck(
            "radar_v4.export_byte",
            False,
            first_fail.error_code,
            ("Exported pack failed portable byte checks.",) + first_fail.notes,
            {"failed": [part.document_kind for part in failed], "directory": str(written)},
        )
    return IntegrityCheck(
        "radar_v4.export_byte",
        True,
        None,
        (
            "Exported pack passed portable byte checks.",
            "Export filenames are not fixture obs_YYYY-MM-DD names.",
            "Not market evidence.",
        ),
        {"failed": [], "directory": str(written)},
    )
