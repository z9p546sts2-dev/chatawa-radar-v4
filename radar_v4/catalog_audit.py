"""Audit reason-code and document-kind catalogs against the package."""

from __future__ import annotations

from ast import Constant, parse, walk
from json import dumps
from pathlib import Path
import re

from radar_v4.document_kind import KNOWN_DOCUMENT_KINDS
from radar_v4.reason_codes import REASON_CODES, RESULT_STATUSES
from radar_v4.workshop_record import ALLOWED_DISPOSITIONS, FORBIDDEN_DISPOSITIONS


CODE_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]{2,}$")


def _dump(document: dict[str, object]) -> str:
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _package_dir() -> Path:
    return Path(__file__).resolve().parent


def _string_literals(path: Path) -> list[str]:
    tree = parse(path.read_text(encoding="utf-8"), filename=str(path))
    return [node.value for node in walk(tree) if isinstance(node, Constant) and isinstance(node.value, str)]


def audit_reason_catalog(package_dir: str | Path | None = None) -> str:
    """Every CODE-looking literal should be catalogued or an allowed exception."""
    root = Path(package_dir) if package_dir is not None else _package_dir()
    allowed = REASON_CODES | RESULT_STATUSES | {
        "LEVEL 0 — MEASURED",
        "NONE",
        "UTC",
        "LIVE",
        "HISTORICAL",
        "BACKFILL",
        "SYNTHETIC",
        "FIXTURE",
        "REPLAY",
        "MANUALLY_EDITED",
        "UNADJUSTED",
        "UNKNOWN",
    }
    missing: list[dict[str, str]] = []
    for path in sorted(root.glob("*.py")):
        for value in _string_literals(path):
            if not CODE_PATTERN.fullmatch(value):
                continue
            if "_" not in value or value.endswith("_"):
                continue
            if value.endswith(
                (
                    "_CLASSES",
                    "_CODES",
                    "_STATUSES",
                    "_PROVENANCE",
                    "_KINDS",
                    "_FIELDS",
                    "_NAMES",
                    "_SUFFIXES",
                    "_METRICS",
                    "_DISPOSITIONS",
                    "_IMPORTS",
                    "_UNIT",
                )
            ):
                continue
            if value in allowed or value in ALLOWED_DISPOSITIONS or value in FORBIDDEN_DISPOSITIONS:
                continue
            if value.startswith("radar_v4"):
                continue
            missing.append({"code": value, "file": path.name})
    valid = not missing
    return _dump(
        {
            "document_kind": "radar_v4.catalog_audit",
            "error_code": None if valid else "CATALOG_GAP",
            "missing": missing,
            "notes": [
                "catalog audit is not a scoring system",
                "unknown codes must not be invented at runtime",
            ],
            "valid": valid,
        }
    )


def audit_document_kinds(package_dir: str | Path | None = None) -> str:
    """radar_v4.* document_kind literals should be in the known catalog."""
    root = Path(package_dir) if package_dir is not None else _package_dir()
    unknown: list[dict[str, str]] = []
    for path in sorted(root.glob("*.py")):
        for value in _string_literals(path):
            if not value.startswith("radar_v4.") or value == "radar_v4.":
                continue
            if value.count(".") != 1:
                continue
            if value in KNOWN_DOCUMENT_KINDS:
                continue
            unknown.append({"document_kind": value, "file": path.name})
    valid = not unknown
    return _dump(
        {
            "document_kind": "radar_v4.kind_audit",
            "error_code": None if valid else "UNKNOWN_DOCUMENT_KIND",
            "notes": ["unknown kinds are refused, not repaired"],
            "unknown": unknown,
            "valid": valid,
        }
    )
