"""Ruler-sidecar identity checks. Not a market calendar."""

from __future__ import annotations

from json import JSONDecodeError, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.dataset_pack import load_dataset_pack
from radar_v4.integrity import (
    IntegrityCheck,
    lock_source_details,
    verify_recomputed_lock_record,
)
from radar_v4.report_lock import _load_report, report_lock
from radar_v4.ruler import ruler_checksum
from radar_v4.ruler_file import serialize_ruler
from radar_v4.snapshot_files import SnapshotFileError

RULER_KIND = "radar_v4.ruler"


def _load_ruler(path: Path) -> tuple[dict[str, object] | None, IntegrityCheck | None]:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return None, IntegrityCheck(
            "radar_v4.ruler_readable",
            False,
            "UNREADABLE_RULER_SIDECAR",
            ("unreadable ruler sidecar",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return None, IntegrityCheck(
            "radar_v4.ruler_readable",
            False,
            "UNREADABLE_RULER_SIDECAR",
            ("ruler sidecar is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return None, IntegrityCheck(
            "radar_v4.ruler_readable",
            False,
            "UNREADABLE_RULER_SIDECAR",
            ("ruler sidecar must be an object",),
            {"path": str(target)},
        )
    return raw, None


def _ruler_parts(raw: dict[str, object], source: str) -> list[IntegrityCheck]:
    parts: list[IntegrityCheck] = []
    if raw.get("document_kind") != RULER_KIND:
        parts.append(
            IntegrityCheck(
                "radar_v4.ruler_kind",
                False,
                "RULER_KIND_REFUSED",
                ("A ruler must name radar_v4.ruler. Not repaired.",),
                {"path": source},
            )
        )
    else:
        parts.append(
            IntegrityCheck(
                "radar_v4.ruler_kind",
                True,
                None,
                ("Ruler kind is locked. Not a calendar.",),
                {"path": source},
            )
        )
    ruler = raw.get("ruler")
    if not isinstance(ruler, dict):
        parts.append(
            IntegrityCheck(
                "radar_v4.ruler_object",
                False,
                "RULER_OBJECT_INVALID",
                ("A ruler document must carry a ruler object.",),
                {"path": source},
            )
        )
    else:
        parts.append(
            IntegrityCheck(
                "radar_v4.ruler_object",
                True,
                None,
                ("Ruler object present. Not a method.",),
                {"path": source},
            )
        )
    checksum = raw.get("ruler_checksum")
    if not isinstance(checksum, str) or not checksum:
        parts.append(
            IntegrityCheck(
                "radar_v4.ruler_checksum_required",
                False,
                "RULER_CHECKSUM_MISSING",
                ("A ruler document must carry a ruler checksum.",),
                {"path": source},
            )
        )
    else:
        parts.append(
            IntegrityCheck(
                "radar_v4.ruler_checksum_required",
                True,
                None,
                ("Ruler checksum present. Not market evidence.",),
                {"path": source},
            )
        )
    return parts


def ruler_lock(path: Path) -> IntegrityCheck:
    raw, error = _load_ruler(path)
    if error is not None:
        return IntegrityCheck(
            "radar_v4.ruler_lock",
            False,
            error.error_code,
            ("Ruler lock failed.",) + error.notes,
            lock_source_details(path, {"failed": [error.document_kind]}),
        )
    assert raw is not None
    return _compose_ruler(raw, str(path))


def pack_ruler_lock(directory: Path) -> IntegrityCheck:
    pack = load_dataset_pack(directory)
    if pack.declaration is None:
        return IntegrityCheck(
            "radar_v4.ruler_lock",
            False,
            "UNREADABLE_DECLARATION",
            ("Ruler lock needs a usable declaration.",),
            lock_source_details(directory, {"failed": ["radar_v4.ruler_kind"]}),
        )
    raw = loads(serialize_ruler(pack.declaration))
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.ruler_lock",
            False,
            "UNREADABLE_RULER_SIDECAR",
            ("Serialized ruler is not an object.",),
            lock_source_details(directory, {"failed": []}),
        )
    return _compose_ruler(raw, str(directory))


def _compose_ruler(raw: dict[str, object], source: str) -> IntegrityCheck:
    parts = _ruler_parts(raw, source)
    failed = [part for part in parts if not part.valid]
    if failed:
        first = failed[0]
        return IntegrityCheck(
            "radar_v4.ruler_lock",
            False,
            first.error_code,
            ("Ruler lock failed.",) + first.notes,
            lock_source_details(
                Path(source), {"failed": [part.document_kind for part in failed]}
            ),
        )
    return IntegrityCheck(
        "radar_v4.ruler_lock",
        True,
        None,
        ("Ruler lock passed. Not a market calendar.",),
        lock_source_details(Path(source), {"failed": []}),
    )


def ruler_lock_any(target: Path) -> IntegrityCheck:
    path = Path(target)
    if path.is_dir():
        return pack_ruler_lock(path)
    return ruler_lock(path)


def ruler_lock_determinism(target: Path) -> IntegrityCheck:
    first = ruler_lock_any(target)
    second = ruler_lock_any(target)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.ruler_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Ruler lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_ruler_lock(left: Path, right: Path) -> IntegrityCheck:
    first = ruler_lock_any(left)
    second = ruler_lock_any(right)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.compare_ruler_lock",
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared ruler-lock records. Equality is not a calendar.",),
        {"equal": equal},
    )


def write_ruler_record(
    target: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = ruler_lock_any(target)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_ruler_record(path: Path) -> IntegrityCheck:
    return verify_recomputed_lock_record(
        path,
        expected_kind="radar_v4.ruler_lock",
        verify_kind="radar_v4.ruler_verify",
        invalid_code="RULER_RECORD_INVALID",
        recompute=ruler_lock_any,
    )


def _report_ruler_checksum(raw: dict[str, object]) -> str | None:
    if raw.get("document_kind") == "radar_v4.session_report":
        value = raw.get("ruler_checksum")
        return value if isinstance(value, str) and value else None
    session = raw.get("session")
    if isinstance(session, dict):
        value = session.get("ruler_checksum")
        return value if isinstance(value, str) and value else None
    return None


def report_ruler_bind(report: Path, directory: Path) -> IntegrityCheck:
    locked = report_lock(report)
    if not locked.valid:
        return IntegrityCheck(
            "radar_v4.report_ruler_bind",
            False,
            locked.error_code,
            ("Report-ruler bind needs a locked report.",) + locked.notes,
            {},
        )
    raw, error = _load_report(report)
    if error is not None:
        return IntegrityCheck(
            "radar_v4.report_ruler_bind",
            False,
            error.error_code,
            ("Report-ruler bind could not read the report.",) + error.notes,
            {},
        )
    assert raw is not None
    claimed = _report_ruler_checksum(raw)
    pack = load_dataset_pack(directory)
    if pack.declaration is None:
        return IntegrityCheck(
            "radar_v4.report_ruler_bind",
            False,
            "UNREADABLE_DECLARATION",
            ("Report-ruler bind needs a usable declaration.",),
            {},
        )
    actual = ruler_checksum(pack.declaration)
    matched = claimed == actual
    return IntegrityCheck(
        "radar_v4.report_ruler_bind",
        matched,
        None if matched else "REPORT_RULER_MISMATCH",
        ("Report ruler checksum bound to pack declaration. Not a method.",),
        {"actual": actual, "claimed": claimed},
    )
