"""Claim, arithmetic, locked-scope, and timestamp inspectability.

These checks do not measure a new question, invent a calendar, or
define a method. SYNTHETIC numbers remain SYNTHETIC.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from json import JSONDecodeError, dumps, loads
from pathlib import Path

from radar_v4.baseline import close_to_close_changes
from radar_v4.dataset_pack import SKIP_FILENAMES, load_dataset_pack
from radar_v4.observation import parse_decimal
from radar_v4.session_report import read_session_report_file
from radar_v4.snapshot_files import read_snapshot_file
from radar_v4.workshop_check import workshop_status
from radar_v4.pack_describe import pack_readiness


def _dump(document: dict[str, object]) -> str:
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


LOCKED_INTERVAL = "1d"
MEASURED_CLAIM = "LEVEL 0 — MEASURED"
REFUSAL_STATUSES = frozenset(
    {"INSUFFICIENT_EVIDENCE", "INVALID_COMPARISON", "UNCLEAR"}
)
ALLOWED_PAYLOAD_KEYS = frozenset({"close", "high", "low", "open", "volume"})
FORBIDDEN_FIELD_NAMES = frozenset(
    {
        "alpha",
        "best_trades",
        "buy",
        "edge",
        "entry",
        "exit",
        "paper",
        "predict",
        "prediction",
        "rank",
        "ranking",
        "score",
        "scores",
        "sell",
        "sharpe",
        "signal",
        "signals",
        "threshold",
        "thresholds",
    }
)


def _baseline_from_report(document: Mapping[str, object]) -> Mapping[str, object] | None:
    session = document.get("session")
    if isinstance(session, Mapping):
        baseline = session.get("baseline")
        if isinstance(baseline, Mapping):
            return baseline
        return None
    baseline = document.get("baseline")
    if isinstance(baseline, Mapping):
        return baseline
    return None


@dataclass(frozen=True)
class IntegrityCheck:
    document_kind: str
    valid: bool
    error_code: str | None
    notes: tuple[str, ...]
    details: dict[str, object]

    def serialize(self) -> str:
        return _dump(
            {
                "details": self.details,
                "document_kind": self.document_kind,
                "error_code": self.error_code,
                "notes": list(self.notes),
                "valid": self.valid,
            }
        )


def lock_source_details(
    path: Path, extra: dict[str, object] | None = None
) -> dict[str, object]:
    """Attach the locked source path. A lock without this is not an identity record."""
    details = dict(extra or {})
    details["source_path"] = str(Path(path).resolve())
    return details


def verify_recomputed_lock_record(
    path: Path,
    *,
    expected_kind: str,
    verify_kind: str,
    invalid_code: str,
    recompute,
) -> IntegrityCheck:
    """Refuse kind+valid-only records. Recompute from source_path and compare bytes."""
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            verify_kind,
            False,
            "UNREADABLE_JSON",
            ("unreadable lock record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            verify_kind,
            False,
            "UNREADABLE_JSON",
            ("lock record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            verify_kind,
            False,
            "UNREADABLE_JSON",
            ("lock record must be an object",),
            {"path": str(target)},
        )
    details = raw.get("details")
    source = details.get("source_path") if isinstance(details, dict) else None
    if not isinstance(source, str) or not source:
        return IntegrityCheck(
            verify_kind,
            False,
            invalid_code,
            ("lock record is missing source_path; kind+valid is not a verify",),
            {"path": str(target)},
        )
    source_path = Path(source)
    if not source_path.exists():
        return IntegrityCheck(
            verify_kind,
            False,
            "UNREADABLE_PACK",
            ("lock source_path is not present",),
            {"path": str(target), "source_path": source},
        )
    recomputed = recompute(source_path)
    matched = (
        raw.get("document_kind") == expected_kind
        and raw.get("valid") is True
        and recomputed.valid
        and recomputed.serialize() == _dump(raw)
    )
    if not matched and (
        raw.get("document_kind") != expected_kind or raw.get("valid") is not True
    ):
        error = invalid_code
    elif not matched and not recomputed.valid:
        error = invalid_code
    elif not matched:
        error = "RECORD_MISMATCH"
    else:
        error = None
    return IntegrityCheck(
        verify_kind,
        matched,
        error,
        (
            "Verified a local lock record by recomputing from source_path.",
            "Not market evidence.",
        ),
        {
            "path": str(target),
            "recomputed_valid": recomputed.valid,
            "source_path": source,
        },
    )


def check_claim_level(report_path: str | Path) -> IntegrityCheck:
    """MEASURED may carry LEVEL 0 — MEASURED. Refusals must use NONE."""
    document = read_session_report_file(report_path)
    baseline = _baseline_from_report(document)
    notes = (
        "claim_level is not usefulness",
        "a missing baseline is not a measurement",
    )
    if baseline is None:
        return IntegrityCheck(
            "radar_v4.claim_check",
            True,
            None,
            notes + ("no baseline present",),
            {"baseline_present": False},
        )
    status = str(baseline.get("status") or "")
    claim = str(baseline.get("claim_level") or "")
    if status == "MEASURED":
        valid = claim == MEASURED_CLAIM
        return IntegrityCheck(
            "radar_v4.claim_check",
            valid,
            None if valid else "CLAIM_LEVEL_MISMATCH",
            notes,
            {"baseline_present": True, "claim_level": claim, "status": status},
        )
    if status in REFUSAL_STATUSES:
        valid = claim == "NONE"
        return IntegrityCheck(
            "radar_v4.claim_check",
            valid,
            None if valid else "CLAIM_LEVEL_MISMATCH",
            notes,
            {"baseline_present": True, "claim_level": claim, "status": status},
        )
    return IntegrityCheck(
        "radar_v4.claim_check",
        False,
        "CLAIM_LEVEL_MISMATCH",
        notes,
        {"baseline_present": True, "claim_level": claim, "status": status},
    )


def check_workshop_status_semantics(status_text: str | None = None) -> IntegrityCheck:
    """status is a capability statement. It must not claim a measurement."""
    raw = loads(status_text or workshop_status())
    if not isinstance(raw, Mapping):
        return IntegrityCheck(
            "radar_v4.status_semantics",
            False,
            "STATUS_OVERCLAIM",
            ("status must be a JSON object",),
            {},
        )
    measured = raw.get("measured") is False
    no_claim = "claim_level" not in raw
    valid = measured and no_claim
    return IntegrityCheck(
        "radar_v4.status_semantics",
        valid,
        None if valid else "STATUS_OVERCLAIM",
        ("status does not measure a dataset",),
        {
            "has_claim_level": "claim_level" in raw,
            "measured": raw.get("measured"),
        },
    )


def check_readiness_semantics(directory: str | Path) -> IntegrityCheck:
    """enough_for_close_to_close requires two declaration-admitted observations."""
    readiness = pack_readiness(directory)
    enough = readiness.enough_for_close_to_close
    admitted = readiness.admitted_observations
    valid = (not enough) or admitted >= 2
    if enough and admitted < 2:
        valid = False
    return IntegrityCheck(
        "radar_v4.readiness_semantics",
        valid,
        None if valid else "READINESS_OVERCLAIM",
        (
            "readiness is not a measurement",
            "pack-accepted files are not automatically admitted",
        ),
        {
            "accepted_observations": readiness.accepted_observations,
            "admitted_observations": admitted,
            "enough_for_close_to_close": enough,
        },
    )


def recompute_change_records(report_path: str | Path) -> IntegrityCheck:
    """Recompute stored close-to-close differences. Does not predict."""
    document = read_session_report_file(report_path)
    baseline = _baseline_from_report(document)
    notes = (
        "ordinary close-to-close difference only",
        "not a percent, score, or signal",
    )
    if baseline is None:
        return IntegrityCheck(
            "radar_v4.recompute",
            True,
            None,
            notes + ("no baseline to recompute",),
            {"checked": 0},
        )
    records = baseline.get("change_records")
    if not isinstance(records, list):
        return IntegrityCheck(
            "radar_v4.recompute",
            False,
            "ARITHMETIC_MISMATCH",
            notes,
            {"checked": 0},
        )
    mismatches: list[dict[str, str]] = []
    for item in records:
        if not isinstance(item, Mapping):
            mismatches.append({"reason": "record is not an object"})
            continue
        try:
            expected = parse_decimal(str(item.get("to_close")), "to_close")
            previous = parse_decimal(str(item.get("from_close")), "from_close")
            stored = parse_decimal(str(item.get("difference")), "difference")
        except (InvalidOperation, TypeError):
            mismatches.append({"reason": "unreadable decimal"})
            continue
        if expected is None or previous is None or stored is None:
            mismatches.append({"reason": "missing decimal"})
            continue
        actual = expected - previous
        if actual != stored:
            mismatches.append(
                {
                    "actual": str(actual),
                    "stored": str(stored),
                }
            )
    valid = not mismatches
    return IntegrityCheck(
        "radar_v4.recompute",
        valid,
        None if valid else "ARITHMETIC_MISMATCH",
        notes,
        {"checked": len(records), "mismatches": mismatches},
    )


def recompute_from_snapshot(
    report_path: str | Path, snapshot_path: str | Path
) -> IntegrityCheck:
    """Compare stored changes to a fresh close-to-close description."""
    document = read_session_report_file(report_path)
    baseline = _baseline_from_report(document)
    snapshot = read_snapshot_file(snapshot_path)
    recomputed = close_to_close_changes(snapshot.observations)
    stored = () if baseline is None else tuple(str(item) for item in baseline.get("changes") or ())
    actual = recomputed.changes
    valid = stored == actual
    return IntegrityCheck(
        "radar_v4.recompute_snapshot",
        valid,
        None if valid else "ARITHMETIC_MISMATCH",
        (
            "snapshot recomputation is not a new method",
            "SYNTHETIC numbers are not HISTORICAL evidence",
        ),
        {"actual": list(actual), "stored": list(stored)},
    )


def inspect_locked_scope(directory: str | Path) -> IntegrityCheck:
    """Describe whether a pack matches the locked one-symbol daily question."""
    pack = load_dataset_pack(directory)
    issues: list[str] = []
    declaration = pack.declaration
    symbols = sorted(
        {
            item.envelope.symbol_or_universe
            for item in pack.observation_intake.accepted
            if item.envelope.symbol_or_universe
        }
    )
    intervals = sorted(
        {
            item.envelope.interval
            for item in pack.observation_intake.accepted
            if item.envelope.interval
        }
    )
    if declaration is None:
        issues.append("LOCKED_SCOPE_VIOLATION")
    else:
        if declaration.interval != LOCKED_INTERVAL:
            issues.append("LOCKED_SCOPE_VIOLATION")
        if declaration.universe and symbols and set(symbols) != {declaration.universe}:
            issues.append("LOCKED_SCOPE_VIOLATION")
        if "close-to-close" not in declaration.primary_metric.replace("_", "-"):
            issues.append("LOCKED_SCOPE_VIOLATION")
    if len(symbols) > 1:
        issues.append("LOCKED_SCOPE_VIOLATION")
    if any(interval != LOCKED_INTERVAL for interval in intervals):
        issues.append("LOCKED_SCOPE_VIOLATION")
    valid = not issues and declaration is not None
    return IntegrityCheck(
        "radar_v4.locked_scope",
        valid,
        None if valid else "LOCKED_SCOPE_VIOLATION",
        (
            "locked question remains ordinary close-to-close difference",
            "this does not authorize a second symbol or interval",
        ),
        {
            "declared_interval": None if declaration is None else declaration.interval,
            "declared_universe": None if declaration is None else declaration.universe,
            "intervals": intervals,
            "symbol_count": len(symbols),
            "symbols": symbols,
        },
    )


def _walk_keys(value: object, found: set[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if isinstance(key, str) and key.casefold() in FORBIDDEN_FIELD_NAMES:
                found.add(key.casefold())
            _walk_keys(child, found)
    elif isinstance(value, list):
        for child in value:
            _walk_keys(child, found)


def scan_forbidden_fields(path: str | Path) -> IntegrityCheck:
    """Refuse documents that carry method/signal/edge field names."""
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.forbidden_fields",
            False,
            "UNREADABLE_JSON",
            ("unreadable path",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.forbidden_fields",
            False,
            "UNREADABLE_JSON",
            ("unreadable JSON",),
            {"path": str(target)},
        )
    found: set[str] = set()
    _walk_keys(raw, found)
    valid = not found
    return IntegrityCheck(
        "radar_v4.forbidden_fields",
        valid,
        None if valid else "FORBIDDEN_FIELD",
        ("forbidden names are not repaired into allowed names",),
        {"found": sorted(found), "path": str(target)},
    )


def inspect_payload_keys(directory: str | Path) -> IntegrityCheck:
    """Flag extra payload keys that intake would otherwise drop silently."""
    root = Path(directory)
    extras: list[dict[str, object]] = []
    if not root.is_dir():
        return IntegrityCheck(
            "radar_v4.payload_keys",
            False,
            "UNREADABLE_PACK",
            ("pack is not a directory",),
            {"extra": []},
        )
    for path in sorted(root.glob("*.json")):
        if path.name in SKIP_FILENAMES:
            continue
        try:
            raw = loads(path.read_text(encoding="utf-8"))
        except (OSError, JSONDecodeError):
            continue
        items = raw if isinstance(raw, list) else [raw]
        for item in items:
            if not isinstance(item, Mapping):
                continue
            payload = item.get("payload")
            if not isinstance(payload, Mapping):
                continue
            unexpected = sorted(
                str(key) for key in payload.keys() if str(key) not in ALLOWED_PAYLOAD_KEYS
            )
            if unexpected:
                extras.append({"file": path.name, "keys": unexpected})
    valid = not extras
    return IntegrityCheck(
        "radar_v4.payload_keys",
        valid,
        None if valid else "EXTRA_PAYLOAD_KEY",
        (
            "allowed payload keys are close, open, high, low, volume",
            "extra keys are not features or scores",
        ),
        {"extra": extras},
    )


def inspect_gaps(directory: str | Path) -> IntegrityCheck:
    """List adjacent timestamp deltas. Does not fill bars or name holidays."""
    pack = load_dataset_pack(directory)
    stamps: list[datetime] = []
    for item in pack.observation_intake.accepted:
        stamp = item.envelope.market_timestamp
        if stamp is not None:
            stamps.append(stamp)
    ordered = sorted(stamps)
    gaps: list[dict[str, str]] = []
    for index in range(1, len(ordered)):
        delta = ordered[index] - ordered[index - 1]
        gaps.append(
            {
                "from": ordered[index - 1].isoformat(timespec="microseconds"),
                "seconds": str(Decimal(str(delta.total_seconds()))),
                "to": ordered[index].isoformat(timespec="microseconds"),
            }
        )
    return IntegrityCheck(
        "radar_v4.gap_inspect",
        True,
        None,
        (
            "gaps are descriptive only",
            "this does not invent a market calendar",
            "this does not fill missing bars",
        ),
        {"gap_count": len(gaps), "gaps": gaps, "observation_count": len(ordered)},
    )


def inspect_timestamps(directory: str | Path) -> IntegrityCheck:
    """Require timezone offsets on raw market_timestamp strings."""
    root = Path(directory)
    naive: list[str] = []
    checked = 0
    if not root.is_dir():
        return IntegrityCheck(
            "radar_v4.timestamps",
            False,
            "UNREADABLE_PACK",
            ("pack is not a directory",),
            {"checked": 0, "naive": []},
        )
    for path in sorted(root.glob("*.json")):
        if path.name in SKIP_FILENAMES and path.name != "declaration.json":
            continue
        try:
            raw = loads(path.read_text(encoding="utf-8"))
        except (OSError, JSONDecodeError):
            continue
        for stamp in _collect_timestamp_strings(raw):
            checked += 1
            if stamp.endswith("Z"):
                continue
            if "+" not in stamp[10:] and stamp.count("-") < 3:
                naive.append(f"{path.name}:{stamp}")
                continue
            try:
                parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            except ValueError:
                naive.append(f"{path.name}:{stamp}")
                continue
            if parsed.tzinfo is None:
                naive.append(f"{path.name}:{stamp}")
    valid = not naive
    return IntegrityCheck(
        "radar_v4.timestamps",
        valid,
        None if valid else "NAIVE_TIMESTAMP",
        (
            "missing timezone is not defaulted to UTC",
            "file mtime is not a market timestamp",
        ),
        {"checked": checked, "naive": naive, "uses_file_mtime": False},
    )


def _collect_timestamp_strings(value: object) -> list[str]:
    found: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in {"market_timestamp", "retrieval_timestamp"} and isinstance(child, str):
                found.append(child)
            else:
                found.extend(_collect_timestamp_strings(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_collect_timestamp_strings(child))
    return found


def inspect_close_scale(directory: str | Path) -> IntegrityCheck:
    """Describe decimal places on close strings. Not a trading threshold."""
    pack = load_dataset_pack(directory)
    scales: list[int] = []
    for item in pack.observation_intake.accepted:
        close = item.payload.close
        if "." in close:
            scales.append(len(close.split(".", 1)[1]))
        else:
            scales.append(0)
    return IntegrityCheck(
        "radar_v4.close_scale",
        True,
        None,
        (
            "scale is descriptive",
            "this is not a precision threshold or signal",
        ),
        {
            "count": len(scales),
            "places": scales,
            "unique_places": sorted(set(scales)),
        },
    )


def require_document_kind(path: str | Path) -> IntegrityCheck:
    """Refuse unlabeled workshop JSON that is not a known inferred kind."""
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.document_kind_required",
            False,
            "UNREADABLE_JSON",
            ("unreadable path",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.document_kind_required",
            False,
            "UNREADABLE_JSON",
            ("unreadable JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, Mapping):
        return IntegrityCheck(
            "radar_v4.document_kind_required",
            False,
            "DOCUMENT_KIND_MISSING",
            ("root must be an object",),
            {"path": str(target)},
        )
    labeled = raw.get("document_kind")
    if isinstance(labeled, str) and labeled:
        return IntegrityCheck(
            "radar_v4.document_kind_required",
            True,
            None,
            ("labeled document",),
            {"document_kind": labeled, "path": str(target)},
        )
    inferred = (
        ("envelope" in raw and "payload" in raw)
        or ("declaration" in raw and "observations" in raw)
        or {"dataset_id", "provenance_class", "universe", "interval"} <= set(raw)
    )
    return IntegrityCheck(
        "radar_v4.document_kind_required",
        inferred,
        None if inferred else "DOCUMENT_KIND_MISSING",
        ("inferred kinds are declaration, observation, or snapshot only",),
        {"inferred": inferred, "path": str(target)},
    )
