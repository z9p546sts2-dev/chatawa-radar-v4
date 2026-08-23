"""Workshop identity, locked-question bind, disposition, and stop record.

None of these measure a market or authorize the next class of work.
"""

from __future__ import annotations

from hashlib import sha256
from json import JSONDecodeError, dumps, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.dataset_pack import load_dataset_pack
from radar_v4.integrity import IntegrityCheck
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_bounds import scan_package_network_imports, workshop_bounds
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


ALLOWED_DISPOSITIONS = frozenset({"UNREVIEWED", "ACKNOWLEDGED", "NEEDS_REVIEW"})
FORBIDDEN_DISPOSITIONS = frozenset(
    {"EDGE", "BUY", "SELL", "APPROVE_TRADE", "BEST_TRADES", "PAPER"}
)


def _dump(document: dict[str, object]) -> str:
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def package_source_identity(package_dir: str | Path | None = None) -> str:
    """SHA-256 each local package file. This is software identity, not a market."""
    root = Path(package_dir) if package_dir is not None else Path(__file__).resolve().parent
    files = {
        path.name: sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.glob("*.py"))
    }
    return _dump(
        {
            "document_kind": "radar_v4.package_identity",
            "files": files,
            "notes": [
                "package identity is not data correctness",
                "this does not hash vendor datasets",
            ],
        }
    )


def inspect_question_lock(
    directory: str | Path, question_path: str | Path | None = None
) -> IntegrityCheck:
    """Bind a pack declaration to the locked Phase 5 question file."""
    pack = load_dataset_pack(directory)
    if pack.declaration is None:
        return IntegrityCheck(
            "radar_v4.question_lock",
            False,
            "UNREADABLE_DECLARATION",
            ("pack has no usable declaration",),
            {},
        )
    target = (
        Path(question_path)
        if question_path is not None
        else Path(__file__).resolve().parents[1] / "RADAR_V4_PHASE5_LOCKED_QUESTION_TC.md"
    )
    try:
        text = target.read_text(encoding="utf-8")
    except OSError:
        return IntegrityCheck(
            "radar_v4.question_lock",
            False,
            "UNREADABLE_JSON",
            ("locked question file is unreadable",),
            {"path": str(target)},
        )
    declared = pack.declaration.locked_question.casefold()
    valid = "close-to-close" in declared and "close-to-close" in text.casefold()
    valid = valid and "ordinary" in text.casefold()
    return IntegrityCheck(
        "radar_v4.question_lock",
        valid,
        None if valid else "LOCKED_SCOPE_VIOLATION",
        (
            "the locked question is unchanged",
            "this does not authorize a second question",
        ),
        {
            "declared": pack.declaration.locked_question,
            "question_file": str(target),
        },
    )


def serialize_disposition(disposition: str, note: str | None = None) -> str:
    label = disposition.strip().upper()
    if label in FORBIDDEN_DISPOSITIONS:
        raise SnapshotFileError(
            "FORBIDDEN_DISPOSITION",
            f"{label} is not a human-review disposition",
        )
    if label not in ALLOWED_DISPOSITIONS:
        raise SnapshotFileError(
            "UNKNOWN_DISPOSITION",
            f"{label} is not UNREVIEWED, ACKNOWLEDGED, or NEEDS_REVIEW",
        )
    return _dump(
        {
            "claim_level": "NONE",
            "disposition": label,
            "document_kind": "radar_v4.human_disposition",
            "measured": False,
            "note": note,
            "notes": [
                "disposition is not a ranking",
                "disposition is not a trade approval",
            ],
        }
    )


def write_disposition(
    path: str | Path, disposition: str, note: str | None = None, replace: bool = False
) -> Path:
    target = Path(path)
    if file_exists_without_replace(target, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{target} already exists")
    return write_text_atomic(target, serialize_disposition(disposition, note) + "\n")


def read_disposition(path: str | Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.human_disposition",
            False,
            "UNREADABLE_JSON",
            ("unreadable disposition",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.human_disposition",
            False,
            "UNREADABLE_JSON",
            ("disposition is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.human_disposition",
            False,
            "UNREADABLE_JSON",
            ("disposition must be an object",),
            {"path": str(target)},
        )
    label = str(raw.get("disposition") or "")
    forbidden = label in FORBIDDEN_DISPOSITIONS
    valid = (
        raw.get("document_kind") == "radar_v4.human_disposition"
        and label in ALLOWED_DISPOSITIONS
        and raw.get("measured") is False
        and raw.get("claim_level") == "NONE"
        and not forbidden
    )
    return IntegrityCheck(
        "radar_v4.human_disposition",
        valid,
        None if valid else ("FORBIDDEN_DISPOSITION" if forbidden else "UNKNOWN_DISPOSITION"),
        ("human disposition is not usefulness",),
        {"disposition": label, "path": str(target)},
    )


def workshop_stop_record() -> str:
    """Capability freeze. Does not measure and does not authorize Phase 6."""
    return _dump(
        {
            "bounds": loads(workshop_bounds()),
            "document_kind": "radar_v4.stop_record",
            "highest_unit": PHASE5_HIGHEST_UNIT,
            "measured": False,
            "network_scan": loads(scan_package_network_imports()),
            "notes": [
                "stop record is a capability freeze, not a research result",
                "units 851-900 are inspectability, not data correctness",
                "authorization does not earn a claim class",
            ],
            "paper_trading_authorized": False,
            "status": loads(workshop_status()),
            "vendor_authorized": False,
        }
    )
