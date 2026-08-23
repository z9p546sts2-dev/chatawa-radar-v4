"""Pack-layout identity checks. Not a method."""

from __future__ import annotations

from json import JSONDecodeError, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.integrity import IntegrityCheck
from radar_v4.pack_describe import inspect_pack_layout
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


def layout_declaration_scan(path: Path) -> IntegrityCheck:
    layout = inspect_pack_layout(path)
    if "UNREADABLE_PACK" in layout.issues:
        return IntegrityCheck(
            "radar_v4.layout_declaration",
            False,
            "UNREADABLE_PACK",
            ("Layout lock needs a pack directory. Not invented.",),
            {"path": str(path)},
        )
    if not layout.declaration_present:
        return IntegrityCheck(
            "radar_v4.layout_declaration",
            False,
            "LAYOUT_DECLARATION_MISSING",
            ("A locked layout needs declaration.json. Not repaired.",),
            {"path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.layout_declaration",
        True,
        None,
        ("Layout has a declaration. Not a measurement.",),
        {"path": str(path)},
    )


def layout_observation_scan(path: Path) -> IntegrityCheck:
    layout = inspect_pack_layout(path)
    if "UNREADABLE_PACK" in layout.issues:
        return IntegrityCheck(
            "radar_v4.layout_observations",
            False,
            "UNREADABLE_PACK",
            ("Layout lock needs a pack directory. Not invented.",),
            {"path": str(path)},
        )
    if layout.observation_files == 0:
        return IntegrityCheck(
            "radar_v4.layout_observations",
            False,
            "LAYOUT_NO_OBSERVATIONS",
            ("A locked layout needs observation files. Not a pack.",),
            {"path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.layout_observations",
        True,
        None,
        ("Layout has observations. Filenames are not a method.",),
        {"count": layout.observation_files, "path": str(path)},
    )


def layout_manifest_scan(path: Path) -> IntegrityCheck:
    layout = inspect_pack_layout(path)
    if "UNREADABLE_PACK" in layout.issues:
        return IntegrityCheck(
            "radar_v4.layout_manifest",
            False,
            "UNREADABLE_PACK",
            ("Layout lock needs a pack directory. Not invented.",),
            {"path": str(path)},
        )
    if not layout.manifest_present:
        return IntegrityCheck(
            "radar_v4.layout_manifest",
            False,
            "LAYOUT_MANIFEST_REFUSED",
            ("A locked layout needs manifest.json. Not repaired.",),
            {"path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.layout_manifest",
        True,
        None,
        ("Layout has a stored manifest. Not market evidence.",),
        {"path": str(path)},
    )


def layout_lock(path: Path) -> IntegrityCheck:
    parts = [
        layout_declaration_scan(path),
        layout_observation_scan(path),
        layout_manifest_scan(path),
    ]
    failed = [part for part in parts if not part.valid]
    if failed:
        first = failed[0]
        return IntegrityCheck(
            "radar_v4.layout_lock",
            False,
            first.error_code,
            ("Layout lock failed.",) + first.notes,
            {"failed": [part.document_kind for part in failed]},
        )
    return IntegrityCheck(
        "radar_v4.layout_lock",
        True,
        None,
        ("Layout lock passed. Not market evidence.",),
        {"failed": []},
    )


def layout_lock_determinism(path: Path) -> IntegrityCheck:
    first = layout_lock(path)
    second = layout_lock(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.layout_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Layout lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_layout_lock(left: Path, right: Path) -> IntegrityCheck:
    first = layout_lock(left)
    second = layout_lock(right)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.compare_layout_lock",
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared layout-lock records. Equality is not a score.",),
        {"equal": equal},
    )


def write_layout_record(
    source: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = layout_lock(source)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_layout_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.layout_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable layout-lock record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.layout_verify",
            False,
            "UNREADABLE_JSON",
            ("layout-lock record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.layout_verify",
            False,
            "UNREADABLE_JSON",
            ("layout-lock record must be an object",),
            {"path": str(target)},
        )
    ok = raw.get("document_kind") == "radar_v4.layout_lock" and raw.get("valid") is True
    return IntegrityCheck(
        "radar_v4.layout_verify",
        ok,
        None if ok else "LAYOUT_RECORD_INVALID",
        ("Verified a local layout-lock record. Not market evidence.",),
        {"path": str(target)},
    )


def layout_status_bind(path: Path) -> IntegrityCheck:
    locked = layout_lock(path)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.layout_status_bind",
        matched,
        None if matched else "LAYOUT_STATUS_MISMATCH",
        ("Layout lock and status share the locked unit. Not a measurement.",),
        {
            "layout_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
