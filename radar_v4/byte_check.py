"""Byte-level pack identity checks. Not market evidence."""

from __future__ import annotations

import re
from json import JSONDecodeError, loads
from pathlib import Path

from radar_v4.dataset_pack import SKIP_FILENAMES, load_dataset_pack
from radar_v4.integrity import IntegrityCheck
from radar_v4.pack_describe import pack_readiness

OBS_DATE_RE = re.compile(r"obs_(\d{4}-\d{2}-\d{2})")
CLAIM_WORDS = frozenset(
    {
        "best_trades",
        "buy",
        "edge",
        "paper",
        "sell",
        "signal",
        "trade",
    }
)


def _json_files(directory: Path) -> list[Path]:
    return [path for path in sorted(Path(directory).iterdir()) if path.is_file()]


def trailing_whitespace_scan(directory: Path) -> IntegrityCheck:
    hits: list[str] = []
    for path in _json_files(directory):
        if path.suffix.casefold() != ".json":
            continue
        text = path.read_text(encoding="utf-8")
        if not text.endswith("\n") or text.endswith("\n\n"):
            hits.append(path.name)
            continue
        for line in text.splitlines():
            if line != line.rstrip(" \t"):
                hits.append(path.name)
                break
    if hits:
        return IntegrityCheck(
            "radar_v4.trailing_whitespace",
            False,
            "TRAILING_WHITESPACE",
            ("JSON files must end with one newline and no trailing spaces.",),
            {"hits": hits},
        )
    return IntegrityCheck(
        "radar_v4.trailing_whitespace",
        True,
        None,
        ("JSON files have one trailing newline and no trailing spaces.",),
        {"hits": []},
    )


def null_byte_scan(directory: Path) -> IntegrityCheck:
    hits = [path.name for path in _json_files(directory) if b"\x00" in path.read_bytes()]
    if hits:
        return IntegrityCheck(
            "radar_v4.null_byte",
            False,
            "NULL_BYTE_REFUSED",
            ("A null byte is not a workshop encoding.",),
            {"hits": hits},
        )
    return IntegrityCheck(
        "radar_v4.null_byte",
        True,
        None,
        ("No null bytes in pack files.",),
        {"hits": []},
    )


def shebang_scan(directory: Path) -> IntegrityCheck:
    hits = [path.name for path in _json_files(directory) if path.read_bytes().startswith(b"#!")]
    if hits:
        return IntegrityCheck(
            "radar_v4.shebang_scan",
            False,
            "SHEBANG_REFUSED",
            ("A shebang is not an evidence file.",),
            {"hits": hits},
        )
    return IntegrityCheck(
        "radar_v4.shebang_scan",
        True,
        None,
        ("No shebang in pack files.",),
        {"hits": []},
    )


def tab_scan(directory: Path) -> IntegrityCheck:
    hits: list[str] = []
    for path in _json_files(directory):
        if path.suffix.casefold() != ".json":
            continue
        if b"\t" in path.read_bytes():
            hits.append(path.name)
    if hits:
        return IntegrityCheck(
            "radar_v4.tab_scan",
            False,
            "TAB_CHARACTER_REFUSED",
            ("Canonical JSON does not use tab characters.",),
            {"hits": hits},
        )
    return IntegrityCheck(
        "radar_v4.tab_scan",
        True,
        None,
        ("No tab characters in pack JSON.",),
        {"hits": []},
    )


def filename_date_check(directory: Path) -> IntegrityCheck:
    mismatches: list[dict[str, str]] = []
    pack = load_dataset_pack(directory)
    by_date: dict[str, str] = {}
    for item in pack.observation_intake.accepted:
        stamp = item.envelope.market_timestamp
        if stamp is None:
            continue
        by_date[stamp.date().isoformat()] = item.envelope.symbol_or_universe or ""
    for path in Path(directory).glob("obs_*.json"):
        matched = OBS_DATE_RE.fullmatch(path.stem)
        if matched is None:
            mismatches.append({"file": path.name, "reason": "name is not obs_YYYY-MM-DD"})
            continue
        day = matched.group(1)
        if day not in by_date:
            mismatches.append({"file": path.name, "reason": "no admitted observation on that date"})
    if mismatches:
        return IntegrityCheck(
            "radar_v4.filename_date",
            False,
            "FILENAME_DATE_REFUSED",
            ("Observation filenames must match an admitted market date.",),
            {"mismatches": mismatches},
        )
    return IntegrityCheck(
        "radar_v4.filename_date",
        True,
        None,
        ("Observation filenames match admitted market dates.",),
        {"mismatches": []},
    )


def count_check(directory: Path) -> IntegrityCheck:
    readiness = pack_readiness(directory)
    files = [
        path.name
        for path in Path(directory).glob("*.json")
        if path.name not in SKIP_FILENAMES
    ]
    if len(files) != readiness.admitted_observations:
        return IntegrityCheck(
            "radar_v4.count_check",
            False,
            "COUNT_MISMATCH",
            ("Observation file count must match declaration-admitted count.",),
            {
                "files": len(files),
                "admitted": readiness.admitted_observations,
            },
        )
    return IntegrityCheck(
        "radar_v4.count_check",
        True,
        None,
        ("Observation file count matches admitted count. Not a quality score.",),
        {"files": len(files), "admitted": readiness.admitted_observations},
    )


def payload_checksum_required(directory: Path) -> IntegrityCheck:
    missing: list[str] = []
    for path in Path(directory).glob("*.json"):
        if path.name in SKIP_FILENAMES:
            continue
        try:
            raw = loads(path.read_text(encoding="utf-8"))
        except (OSError, JSONDecodeError):
            continue
        if not isinstance(raw, dict):
            continue
        if "envelope" in raw and "payload" in raw and "payload_checksum" not in raw:
            missing.append(path.name)
    if missing:
        return IntegrityCheck(
            "radar_v4.payload_checksum_required",
            False,
            "MISSING_PAYLOAD_CHECKSUM",
            ("An observation is missing payload_checksum. Nothing is repaired.",),
            {"missing": missing},
        )
    return IntegrityCheck(
        "radar_v4.payload_checksum_required",
        True,
        None,
        ("Observation files carry payload_checksum.",),
        {"missing": []},
    )


def _walk_strings(value: object, found: set[str]) -> None:
    if isinstance(value, str):
        if value.casefold() in CLAIM_WORDS:
            found.add(value.casefold())
        return
    if isinstance(value, dict):
        for child in value.values():
            _walk_strings(child, found)
        return
    if isinstance(value, list):
        for child in value:
            _walk_strings(child, found)


def claim_word_scan(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.claim_words",
            False,
            "UNREADABLE_JSON",
            ("unreadable path",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.claim_words",
            False,
            "UNREADABLE_JSON",
            ("unreadable JSON",),
            {"path": str(target)},
        )
    found: set[str] = set()
    _walk_strings(raw, found)
    if found:
        return IntegrityCheck(
            "radar_v4.claim_words",
            False,
            "CLAIM_WORD_REFUSED",
            ("Claim words are not workshop values.",),
            {"found": sorted(found), "path": str(target)},
        )
    return IntegrityCheck(
        "radar_v4.claim_words",
        True,
        None,
        ("No claim-word values in this document.",),
        {"found": [], "path": str(target)},
    )


def byte_check(directory: Path) -> IntegrityCheck:
    parts = [
        trailing_whitespace_scan(directory),
        null_byte_scan(directory),
        shebang_scan(directory),
        tab_scan(directory),
        filename_date_check(directory),
        count_check(directory),
        payload_checksum_required(directory),
    ]
    failed = [part for part in parts if not part.valid]
    if failed:
        first = failed[0]
        return IntegrityCheck(
            "radar_v4.byte_check",
            False,
            first.error_code,
            ("Byte-level pack checks failed.",) + first.notes,
            {"failed": [part.document_kind for part in failed]},
        )
    return IntegrityCheck(
        "radar_v4.byte_check",
        True,
        None,
        ("Byte-level pack checks passed. Not market evidence.",),
        {"failed": []},
    )
