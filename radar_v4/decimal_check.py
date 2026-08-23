"""Close-value representation checks. Not market evidence."""

from __future__ import annotations

import json
import re
from pathlib import Path

from radar_v4.dataset_pack import SKIP_FILENAMES
from radar_v4.integrity import IntegrityCheck

SCIENTIFIC_RE = re.compile(r"[eE]")
NON_FINITE = frozenset({"nan", "infinity", "+infinity", "-infinity"})


def _close_from_raw_json(text: str) -> object | None:
    raw = json.loads(text)
    if not isinstance(raw, dict):
        return None
    payload = raw.get("payload")
    if not isinstance(payload, dict):
        return None
    if "close" not in payload:
        return None
    return payload["close"]


def decimal_check_text(text: str, *, path: str = "") -> IntegrityCheck:
    close = _close_from_raw_json(text)
    if close is None:
        return IntegrityCheck(
            "radar_v4.decimal_check",
            True,
            None,
            ("No close field to check.",),
            {"path": path},
        )
    if isinstance(close, bool) or isinstance(close, (int, float)):
        return IntegrityCheck(
            "radar_v4.decimal_check",
            False,
            "JSON_NUMBER_NOT_STRING",
            ("Close is a JSON number. Workshop closes are decimal strings.",),
            {"path": path, "close_type": type(close).__name__},
        )
    if not isinstance(close, str):
        return IntegrityCheck(
            "radar_v4.decimal_check",
            False,
            "JSON_NUMBER_NOT_STRING",
            ("Close is not a decimal string.",),
            {"path": path, "close_type": type(close).__name__},
        )
    if close.strip().lower() in NON_FINITE:
        return IntegrityCheck(
            "radar_v4.decimal_check",
            False,
            "NON_FINITE_CLOSE",
            ("Close is not a finite decimal.",),
            {"path": path, "close": close},
        )
    if SCIENTIFIC_RE.search(close):
        return IntegrityCheck(
            "radar_v4.decimal_check",
            True,
            "SCIENTIFIC_NOTATION_DESCRIBE",
            ("Close uses scientific notation. Described only. Not a measurement.",),
            {"path": path, "close": close},
        )
    return IntegrityCheck(
        "radar_v4.decimal_check",
        True,
        None,
        ("Close is a finite decimal string.",),
        {"path": path, "close": close},
    )


def decimal_check_directory(directory: Path) -> IntegrityCheck:
    failures: list[dict[str, object]] = []
    describes: list[str] = []
    for path in sorted(Path(directory).glob("*.json")):
        if path.name in SKIP_FILENAMES:
            continue
        result = decimal_check_text(path.read_text(encoding="utf-8"), path=path.name)
        if not result.valid:
            failures.append({"path": path.name, "error_code": result.error_code})
        elif result.error_code == "SCIENTIFIC_NOTATION_DESCRIBE":
            describes.append(path.name)
    if failures:
        return IntegrityCheck(
            "radar_v4.decimal_check",
            False,
            str(failures[0]["error_code"]),
            ("A close value is not a finite decimal string.",),
            {"failures": failures, "describes": describes},
        )
    return IntegrityCheck(
        "radar_v4.decimal_check",
        True,
        "SCIENTIFIC_NOTATION_DESCRIBE" if describes else None,
        ("Close values are decimal strings. Not market evidence.",),
        {"failures": [], "describes": describes},
    )
