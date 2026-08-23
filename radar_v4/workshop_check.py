"""Bind, determinism, canonical, journal, and status checks. No method."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from json import JSONDecodeError, dumps, loads
from pathlib import Path

from radar_v4.local_session import run_session_from_pack
from radar_v4.quarantine_journal import read_quarantine_journal_file
from radar_v4.reason_codes import REASON_CODES, RESULT_STATUSES
from radar_v4.session_report import read_session_report_file
from radar_v4.snapshot_files import read_snapshot_file


def _dump(document: dict[str, object]) -> str:
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


@dataclass(frozen=True)
class ReportBind:
    matched: bool
    claimed: str | None
    actual: str
    error_code: str | None

    def serialize(self) -> str:
        return _dump(
            {
                "actual": self.actual,
                "claimed": self.claimed,
                "document_kind": "radar_v4.report_bind",
                "error_code": self.error_code,
                "matched": self.matched,
            }
        )


def bind_report_to_snapshot(report_path: str | Path, snapshot_path: str | Path) -> ReportBind:
    report = read_session_report_file(report_path)
    snapshot = read_snapshot_file(snapshot_path)
    actual = snapshot.integrity_checksum()
    claimed = report.get("snapshot_checksum")
    session = report.get("session")
    if claimed is None and isinstance(session, dict):
        claimed = session.get("snapshot_checksum")
    claimed_text = None if claimed is None else str(claimed)
    matched = claimed_text == actual
    return ReportBind(
        matched=matched,
        claimed=claimed_text,
        actual=actual,
        error_code=None if matched else "REPORT_SNAPSHOT_MISMATCH",
    )


@dataclass(frozen=True)
class DeterminismReport:
    equal: bool
    left: str | None
    right: str | None
    error_code: str | None

    def serialize(self) -> str:
        return _dump(
            {
                "document_kind": "radar_v4.determinism_report",
                "equal": self.equal,
                "error_code": self.error_code,
                "left": self.left,
                "right": self.right,
            }
        )


def check_pack_determinism(directory: str | Path) -> DeterminismReport:
    """Run the same local pack twice. Equal checksums are not market evidence."""
    first = run_session_from_pack(directory)
    second = run_session_from_pack(directory)
    if first.session is None or second.session is None:
        return DeterminismReport(
            False,
            None,
            None,
            first.error_code or second.error_code or "PACK_NOT_USABLE",
        )
    left = first.session.snapshot.integrity_checksum()
    right = second.session.snapshot.integrity_checksum()
    equal = left == right
    return DeterminismReport(
        equal=equal,
        left=left,
        right=right,
        error_code=None if equal else "DETERMINISM_MISMATCH",
    )


@dataclass(frozen=True)
class CanonicalCheck:
    canonical: bool
    error_code: str | None

    def serialize(self) -> str:
        return _dump(
            {
                "canonical": self.canonical,
                "document_kind": "radar_v4.canonical_check",
                "error_code": self.error_code,
            }
        )


def check_canonical_json(path: str | Path) -> CanonicalCheck:
    """Refuse a file whose bytes are not sorted-key compact JSON plus newline."""
    target = Path(path)
    try:
        text = target.read_text(encoding="utf-8")
        raw = loads(text)
    except OSError:
        return CanonicalCheck(False, "UNREADABLE_JSON")
    except JSONDecodeError:
        return CanonicalCheck(False, "UNREADABLE_JSON")
    expected = dumps(raw, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    if text == expected + "\n":
        return CanonicalCheck(True, None)
    return CanonicalCheck(False, "NOT_CANONICAL_JSON")


@dataclass(frozen=True)
class JournalSummary:
    refusal_count: int
    by_code: dict[str, int]
    by_source: dict[str, int]
    error_code: str | None

    def serialize(self) -> str:
        return _dump(
            {
                "by_code": dict(sorted(self.by_code.items())),
                "by_source": dict(sorted(self.by_source.items())),
                "document_kind": "radar_v4.journal_summary",
                "error_code": self.error_code,
                "refusal_count": self.refusal_count,
            }
        )


def summarize_journal(path: str | Path) -> JournalSummary:
    document = read_quarantine_journal_file(path)
    entries = document.get("entries")
    if not isinstance(entries, list):
        return JournalSummary(0, {}, {}, "UNREADABLE_JOURNAL")
    codes: Counter[str] = Counter()
    sources: Counter[str] = Counter()
    for item in entries:
        if not isinstance(item, dict):
            continue
        codes[str(item.get("code") or "UNKNOWN")] += 1
        sources[str(item.get("source") or "UNKNOWN")] += 1
    return JournalSummary(len(entries), dict(codes), dict(sources), None)


@dataclass(frozen=True)
class CodeLookup:
    code: str
    known: bool
    family: str

    def serialize(self) -> str:
        return _dump(
            {
                "code": self.code,
                "document_kind": "radar_v4.reason_code",
                "family": self.family,
                "known": self.known,
            }
        )


def lookup_reason_code(code: str) -> CodeLookup:
    if code in REASON_CODES:
        family = "reason"
        known = True
    elif code in RESULT_STATUSES:
        family = "result"
        known = True
    else:
        family = "unknown"
        known = False
    return CodeLookup(code=code, known=known, family=family)


def serialize_reason_catalog() -> str:
    return _dump(
        {
            "codes": sorted(REASON_CODES),
            "document_kind": "radar_v4.reason_codes",
            "result_statuses": sorted(RESULT_STATUSES),
        }
    )


PHASE5_HIGHEST_UNIT = 250


def workshop_status() -> str:
    """Workshop capability statement. Does not measure a dataset."""
    return _dump(
        {
            "available_claim_level": "LEVEL 0 — MEASURED",
            "document_kind": "radar_v4.workshop_status",
            "fixture_is_market_evidence": False,
            "historical_evidence": False,
            "highest_unit": PHASE5_HIGHEST_UNIT,
            "measured": False,
            "method_defined": False,
            "notes": [
                "status is a workshop capability statement, not a measurement",
                "software correctness is not data correctness",
                "data correctness is not method validity",
                "method validity is not usefulness",
                "SYNTHETIC and FIXTURE numbers are not HISTORICAL evidence",
                "units 201-250 are inspectability, not a research result",
            ],
            "paper_trading_authorized": False,
            "phase": 5,
            "units_complete": f"1-6 / 7-{PHASE5_HIGHEST_UNIT}",
            "vendor_authorized": False,
        }
    )
