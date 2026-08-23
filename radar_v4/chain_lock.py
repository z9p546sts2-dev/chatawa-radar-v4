"""Pack three-way identity checks. Not a method."""

from __future__ import annotations

from json import loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.evidence_chain import three_way_pack
from radar_v4.integrity import (
    IntegrityCheck,
    lock_source_details,
    verify_recomputed_lock_record,
)
from radar_v4.pack_describe import inspect_pack_layout
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


def chain_readable_scan(path: Path) -> IntegrityCheck:
    target = Path(path)
    if not target.is_dir():
        return IntegrityCheck(
            "radar_v4.chain_readable",
            False,
            "UNREADABLE_PACK",
            ("Chain lock needs a pack directory. Not invented.",),
            {"path": str(target)},
        )
    return IntegrityCheck(
        "radar_v4.chain_readable",
        True,
        None,
        ("Pack directory is present. Not a measurement.",),
        {"path": str(target)},
    )


def chain_layout_scan(path: Path) -> IntegrityCheck:
    readable = chain_readable_scan(path)
    if not readable.valid:
        return readable
    layout = inspect_pack_layout(path)
    if not layout.ready_to_load:
        return IntegrityCheck(
            "radar_v4.chain_layout",
            False,
            "CHAIN_LAYOUT_REFUSED",
            ("A locked chain needs a declaration and observations.",),
            {"issues": list(layout.issues), "path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.chain_layout",
        True,
        None,
        ("Chain layout is present. Not market evidence.",),
        {"observation_files": layout.observation_files, "path": str(path)},
    )


def chain_three_scan(path: Path) -> IntegrityCheck:
    readable = chain_readable_scan(path)
    if not readable.valid:
        return readable
    check = three_way_pack(path)
    if not check.matched:
        return IntegrityCheck(
            "radar_v4.chain_three",
            False,
            check.error_code or "THREE_WAY_MISMATCH",
            ("Filesystem, inventory, and manifest must agree. Not repaired.",) + check.notes,
            check.details,
        )
    return IntegrityCheck(
        "radar_v4.chain_three",
        True,
        None,
        ("Three-way pack identity matched. Not a score.",),
        check.details,
    )


def chain_lock(path: Path) -> IntegrityCheck:
    parts = [
        chain_readable_scan(path),
        chain_layout_scan(path),
        chain_three_scan(path),
    ]
    failed = [part for part in parts if not part.valid]
    if failed:
        first = failed[0]
        return IntegrityCheck(
            "radar_v4.chain_lock",
            False,
            first.error_code,
            ("Chain lock failed.",) + first.notes,
            lock_source_details(
                path, {"failed": [part.document_kind for part in failed]}
            ),
        )
    return IntegrityCheck(
        "radar_v4.chain_lock",
        True,
        None,
        ("Chain lock passed. Not market evidence.",),
        lock_source_details(path, {"failed": []}),
    )


def chain_lock_determinism(path: Path) -> IntegrityCheck:
    first = chain_lock(path)
    second = chain_lock(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.chain_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Chain lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_chain_lock(left: Path, right: Path) -> IntegrityCheck:
    first = chain_lock(left)
    second = chain_lock(right)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.compare_chain_lock",
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared chain-lock records. Equality is not a score.",),
        {"equal": equal},
    )


def write_chain_record(
    source: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = chain_lock(source)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_chain_record(path: Path) -> IntegrityCheck:
    return verify_recomputed_lock_record(
        path,
        expected_kind="radar_v4.chain_lock",
        verify_kind="radar_v4.chain_verify",
        invalid_code="CHAIN_RECORD_INVALID",
        recompute=chain_lock,
    )


def chain_status_bind(path: Path) -> IntegrityCheck:
    locked = chain_lock(path)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.chain_status_bind",
        matched,
        None if matched else "CHAIN_STATUS_MISMATCH",
        ("Chain lock and status share the locked unit. Not a measurement.",),
        {
            "chain_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
