"""Identify local evidence documents. No repair. No measurement."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from json import JSONDecodeError, dumps, loads
from pathlib import Path

from radar_v4.declaration_json import REQUIRED_DECLARATION_FIELDS

DOCUMENT_KIND = "radar_v4.kind_detection"

KNOWN_DOCUMENT_KINDS = frozenset(
    {
        "radar_v4.admission_report",
        "radar_v4.bundle_verification",
        "radar_v4.canonical_check",
        "radar_v4.declaration",
        "radar_v4.determinism_report",
        "radar_v4.inventory_comparison",
        "radar_v4.journal_summary",
        "radar_v4.kind_detection",
        "radar_v4.local_session_report",
        "radar_v4.observation",
        "radar_v4.pack_describe",
        "radar_v4.pack_identities",
        "radar_v4.pack_inventory",
        "radar_v4.pack_layout",
        "radar_v4.pack_manifest",
        "radar_v4.pack_readiness",
        "radar_v4.provenance_mix",
        "radar_v4.quarantine_journal",
        "radar_v4.reason_code",
        "radar_v4.reason_codes",
        "radar_v4.registry",
        "radar_v4.report_bind",
        "radar_v4.report_comparison",
        "radar_v4.ruler",
        "radar_v4.ruler_comparison",
        "radar_v4.session_report",
        "radar_v4.snapshot",
        "radar_v4.snapshot_inventory",
        "radar_v4.workshop_status",
    }
)


@dataclass(frozen=True)
class KindDetection:
    path: str
    document_kind: str | None
    inferred: bool
    known: bool
    error_code: str | None

    def serialize(self) -> str:
        document = {
            "document_kind": DOCUMENT_KIND,
            "error_code": self.error_code,
            "inferred": self.inferred,
            "known": self.known,
            "path": self.path,
            "detected_kind": self.document_kind,
        }
        return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def detect_document_kind(path: str | Path) -> KindDetection:
    """Read document_kind when present. Infer only for unlabeled local files."""
    target = Path(path)
    try:
        text = target.read_text(encoding="utf-8")
        raw = loads(text)
    except OSError:
        return KindDetection(str(target), None, False, False, "UNREADABLE_JSON")
    except JSONDecodeError:
        return KindDetection(str(target), None, False, False, "UNREADABLE_JSON")
    if not isinstance(raw, Mapping):
        return KindDetection(str(target), None, False, False, "UNKNOWN_DOCUMENT_KIND")
    labeled = raw.get("document_kind")
    if isinstance(labeled, str) and labeled:
        return KindDetection(
            str(target),
            labeled,
            False,
            labeled in KNOWN_DOCUMENT_KINDS,
            None if labeled in KNOWN_DOCUMENT_KINDS else "UNKNOWN_DOCUMENT_KIND",
        )
    inferred = _infer_kind(raw)
    if inferred is None:
        return KindDetection(str(target), None, False, False, "UNKNOWN_DOCUMENT_KIND")
    return KindDetection(str(target), inferred, True, inferred in KNOWN_DOCUMENT_KINDS, None)


def _infer_kind(raw: Mapping[str, object]) -> str | None:
    if "declaration" in raw and "observations" in raw:
        return "radar_v4.snapshot"
    if "envelope" in raw and "payload" in raw:
        return "radar_v4.observation"
    if all(field in raw for field in REQUIRED_DECLARATION_FIELDS):
        return "radar_v4.declaration"
    return None
