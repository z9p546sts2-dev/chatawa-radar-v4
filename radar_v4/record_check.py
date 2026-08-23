"""Record-level inspectability: OHLC, timestamps, files, and text safety.

These checks do not invent calendars, fill bars, or define a method.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from json import JSONDecoder, JSONDecodeError, loads
from pathlib import Path
from stat import S_IXGRP, S_IXOTH, S_IXUSR
from urllib.parse import urlparse

from radar_v4.dataset_pack import load_dataset_pack
from radar_v4.integrity import IntegrityCheck
from radar_v4.observation_validation import validate_observation


PERCENT_FIELD_NAMES = frozenset(
    {
        "log_return",
        "pct",
        "pct_change",
        "percent",
        "percent_change",
        "return",
        "returns",
    }
)
UNEXPECTED_SUFFIXES = frozenset(
    {".arrow", ".csv", ".feather", ".parquet", ".pkl", ".xlsx"}
)
ALLOWED_PRIMARY_METRICS = frozenset(
    {
        "close-to-close difference",
        "close to close difference",
    }
)


def inspect_ohlc(directory: str | Path) -> IntegrityCheck:
    """Report OHLC contradictions already refused by observation validation."""
    pack = load_dataset_pack(directory)
    issues: list[dict[str, str]] = []
    for item in pack.observation_intake.accepted:
        validation = validate_observation(item)
        for issue in validation.issues:
            if issue.code == "OHLC_CONTRADICTION":
                issues.append(
                    {
                        "code": issue.code,
                        "reason": issue.reason,
                        "symbol": item.envelope.symbol_or_universe or "",
                    }
                )
    valid = not issues
    return IntegrityCheck(
        "radar_v4.ohlc_check",
        valid,
        None if valid else "OHLC_CONTRADICTION",
        ("OHLC inspect does not repair highs, lows, or closes",),
        {"contradictions": issues, "checked": pack.observation_intake.accepted_count()},
    )


def inspect_retrieval_order(directory: str | Path) -> IntegrityCheck:
    """Flag retrieval timestamps that precede market timestamps."""
    pack = load_dataset_pack(directory)
    early: list[str] = []
    checked = 0
    for item in pack.observation_intake.accepted:
        market = item.envelope.market_timestamp
        retrieval = item.envelope.retrieval_timestamp
        if market is None or retrieval is None:
            continue
        checked += 1
        if retrieval < market:
            early.append(item.envelope.symbol_or_universe or "unknown")
    valid = not early
    return IntegrityCheck(
        "radar_v4.retrieval_order",
        valid,
        None if valid else "RETRIEVAL_BEFORE_MARKET",
        (
            "retrieval time is not a market timestamp",
            "this does not invent exchange hours",
        ),
        {"checked": checked, "early": early},
    )


def inspect_ruler_fields(directory: str | Path) -> IntegrityCheck:
    """Require accepted observations to share declaration provider and transform."""
    pack = load_dataset_pack(directory)
    declaration = pack.declaration
    mismatches: list[dict[str, str]] = []
    if declaration is None:
        return IntegrityCheck(
            "radar_v4.ruler_fields",
            False,
            "LOCKED_SCOPE_VIOLATION",
            ("pack has no usable declaration",),
            {"mismatches": []},
        )
    for item in pack.observation_intake.accepted:
        envelope = item.envelope
        if envelope.provider != declaration.provider:
            mismatches.append({"field": "provider", "actual": envelope.provider or ""})
        if envelope.transformation_version != declaration.transformation_version:
            mismatches.append(
                {
                    "field": "transformation_version",
                    "actual": envelope.transformation_version or "",
                }
            )
        if envelope.timezone != declaration.timezone:
            mismatches.append({"field": "timezone", "actual": envelope.timezone or ""})
    valid = not mismatches
    return IntegrityCheck(
        "radar_v4.ruler_fields",
        valid,
        None if valid else "DATASET_DECLARATION_MISMATCH",
        ("ruler fields are not a method",),
        {
            "declared_provider": declaration.provider,
            "declared_timezone": declaration.timezone,
            "declared_transformation": declaration.transformation_version,
            "mismatches": mismatches,
        },
    )


def _walk_keys(value: object, found: set[str], names: frozenset[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if isinstance(key, str) and key.casefold() in names:
                found.add(key.casefold())
            _walk_keys(child, found, names)
    elif isinstance(value, list):
        for child in value:
            _walk_keys(child, found, names)


def scan_percent_fields(path: str | Path) -> IntegrityCheck:
    """Refuse percent/return field names that are not the locked difference."""
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.percent_fields",
            False,
            "UNREADABLE_JSON",
            ("unreadable path",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.percent_fields",
            False,
            "UNREADABLE_JSON",
            ("unreadable JSON",),
            {"path": str(target)},
        )
    found: set[str] = set()
    _walk_keys(raw, found, PERCENT_FIELD_NAMES)
    valid = not found
    return IntegrityCheck(
        "radar_v4.percent_fields",
        valid,
        None if valid else "PERCENT_FIELD",
        ("locked metric is close-to-close difference, not percent",),
        {"found": sorted(found), "path": str(target)},
    )


def inspect_unexpected_files(directory: str | Path) -> IntegrityCheck:
    """Refuse market-looking binary/tabular files inside a pack."""
    root = Path(directory)
    if not root.is_dir():
        return IntegrityCheck(
            "radar_v4.unexpected_files",
            False,
            "UNREADABLE_PACK",
            ("pack is not a directory",),
            {"files": []},
        )
    unexpected = [
        path.name
        for path in sorted(root.iterdir())
        if path.is_file() and path.suffix.casefold() in UNEXPECTED_SUFFIXES
    ]
    valid = not unexpected
    return IntegrityCheck(
        "radar_v4.unexpected_files",
        valid,
        None if valid else "UNEXPECTED_PACK_FILE",
        ("a pack is JSON evidence, not a vendor extract",),
        {"files": unexpected},
    )


def inspect_leftovers(directory: str | Path) -> IntegrityCheck:
    """Refuse temp siblings and orphan checksum sidecars."""
    root = Path(directory)
    if not root.is_dir():
        return IntegrityCheck(
            "radar_v4.leftovers",
            False,
            "UNREADABLE_PACK",
            ("pack is not a directory",),
            {},
        )
    temps = [path.name for path in sorted(root.iterdir()) if path.name.endswith(".tmp")]
    orphans = [
        path.name
        for path in sorted(root.iterdir())
        if path.name.endswith(".sha256") and not (root / path.name[: -len(".sha256")]).is_file()
    ]
    issues: list[str] = []
    if temps:
        issues.append("PACK_TMP_LEFTOVER")
    if orphans:
        issues.append("SIDECAR_ORPHAN")
    return IntegrityCheck(
        "radar_v4.leftovers",
        not issues,
        None if not issues else issues[0],
        ("leftovers are not repaired into evidence",),
        {"orphans": orphans, "tmp_files": temps},
    )


def inspect_text_safety(path: str | Path) -> IntegrityCheck:
    """Refuse CRLF, control bytes, and duplicate JSON keys."""
    target = Path(path)
    try:
        data = target.read_bytes()
    except OSError:
        return IntegrityCheck(
            "radar_v4.text_safety",
            False,
            "UNREADABLE_JSON",
            ("unreadable path",),
            {"path": str(target)},
        )
    issues: list[str] = []
    if b"\r\n" in data or b"\r" in data:
        issues.append("CRLF_LINE_ENDING")
    if any(byte < 32 and byte not in {9, 10} for byte in data):
        issues.append("CONTROL_CHARACTER")
    decoder = JSONDecoder()
    try:
        decoder.decode(data.decode("utf-8"))
    except (UnicodeDecodeError, JSONDecodeError):
        issues.append("UNREADABLE_JSON")
    else:
        duplicates: list[str] = []

        def _hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
            seen: set[str] = set()
            for key, _value in pairs:
                if key in seen:
                    duplicates.append(key)
                seen.add(key)
            return dict(pairs)

        loads(data.decode("utf-8"), object_pairs_hook=_hook)
        if duplicates:
            issues.append("DUPLICATE_JSON_KEY")
    valid = not issues
    return IntegrityCheck(
        "radar_v4.text_safety",
        valid,
        None if valid else issues[0],
        ("canonical JSON is UTF-8 with one trailing newline",),
        {"issues": issues, "path": str(target)},
    )


def inspect_file_modes(directory: str | Path) -> IntegrityCheck:
    """Refuse executable bits on pack evidence files."""
    root = Path(directory)
    if not root.is_dir():
        return IntegrityCheck(
            "radar_v4.file_modes",
            False,
            "UNREADABLE_PACK",
            ("pack is not a directory",),
            {"executable": []},
        )
    executable = []
    for path in sorted(root.iterdir()):
        if not path.is_file():
            continue
        mode = path.stat().st_mode
        if mode & (S_IXUSR | S_IXGRP | S_IXOTH):
            executable.append(path.name)
    valid = not executable
    return IntegrityCheck(
        "radar_v4.file_modes",
        valid,
        None if valid else "EXECUTABLE_PACK_FILE",
        ("evidence files are data, not programs",),
        {"executable": executable},
    )


def inspect_pack_urls(directory: str | Path) -> IntegrityCheck:
    """Refuse http(s) URLs inside pack JSON values. This is not a download."""
    root = Path(directory)
    if not root.is_dir():
        return IntegrityCheck(
            "radar_v4.url_scan",
            False,
            "UNREADABLE_PACK",
            ("pack is not a directory",),
            {"urls": []},
        )
    found: list[str] = []
    for path in sorted(root.glob("*.json")):
        try:
            raw = loads(path.read_text(encoding="utf-8"))
        except (OSError, JSONDecodeError):
            continue
        found.extend(f"{path.name}:{url}" for url in _collect_urls(raw))
    valid = not found
    return IntegrityCheck(
        "radar_v4.url_scan",
        valid,
        None if valid else "NETWORK_URL",
        ("a local pack must not point at a vendor or live download",),
        {"urls": found},
    )


def _collect_urls(value: object) -> list[str]:
    found: list[str] = []
    if isinstance(value, str):
        if value.startswith("http://") or value.startswith("https://"):
            parsed = urlparse(value)
            if parsed.scheme in {"http", "https"} and parsed.netloc:
                found.append(value)
    elif isinstance(value, Mapping):
        for child in value.values():
            found.extend(_collect_urls(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_collect_urls(child))
    return found


def describe_close_zeros(directory: str | Path) -> IntegrityCheck:
    """Count zero closes. Not a threshold and not a signal."""
    pack = load_dataset_pack(directory)
    zeros = 0
    checked = 0
    for item in pack.observation_intake.accepted:
        try:
            close = Decimal(item.payload.close)
        except Exception:
            continue
        checked += 1
        if close == 0:
            zeros += 1
    return IntegrityCheck(
        "radar_v4.close_zeros",
        True,
        None,
        ("zero closes are described, not scored", "this is not a filter"),
        {"checked": checked, "zeros": zeros},
    )


def describe_adjustment_policy(directory: str | Path) -> IntegrityCheck:
    """Echo the declared adjustment policy. Does not invent corporate actions."""
    pack = load_dataset_pack(directory)
    if pack.declaration is None:
        return IntegrityCheck(
            "radar_v4.adjustment_policy",
            False,
            "UNREADABLE_DECLARATION",
            ("pack has no usable declaration",),
            {},
        )
    return IntegrityCheck(
        "radar_v4.adjustment_policy",
        True,
        None,
        ("adjustment policy is declared, not computed",),
        {"adjustment_policy": pack.declaration.adjustment_policy},
    )


def inspect_primary_metric(directory: str | Path) -> IntegrityCheck:
    pack = load_dataset_pack(directory)
    if pack.declaration is None:
        return IntegrityCheck(
            "radar_v4.primary_metric",
            False,
            "UNREADABLE_DECLARATION",
            ("pack has no usable declaration",),
            {},
        )
    metric = pack.declaration.primary_metric.casefold().replace("_", " ")
    valid = metric in ALLOWED_PRIMARY_METRICS
    return IntegrityCheck(
        "radar_v4.primary_metric",
        valid,
        None if valid else "LOCKED_SCOPE_VIOLATION",
        ("primary metric remains close-to-close difference",),
        {"primary_metric": pack.declaration.primary_metric},
    )


def inspect_status_taxonomy(report_path: str | Path) -> IntegrityCheck:
    """Allow only the locked Phase 5 result statuses on a baseline."""
    from radar_v4.session_report import read_session_report_file

    document = read_session_report_file(report_path)
    session = document.get("session")
    baseline = session.get("baseline") if isinstance(session, Mapping) else document.get("baseline")
    if not isinstance(baseline, Mapping):
        return IntegrityCheck(
            "radar_v4.status_taxonomy",
            True,
            None,
            ("no baseline present",),
            {"status": None},
        )
    status = str(baseline.get("status") or "")
    allowed = {"MEASURED", "INSUFFICIENT_EVIDENCE", "INVALID_COMPARISON", "UNCLEAR"}
    valid = status in allowed
    return IntegrityCheck(
        "radar_v4.status_taxonomy",
        valid,
        None if valid else "UNKNOWN_RESULT_STATUS",
        ("result language is descriptive, not an edge claim",),
        {"status": status},
    )
