"""Pack-inventory identity checks. Not a measurement."""

from __future__ import annotations

from json import JSONDecodeError, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.integrity import IntegrityCheck
from radar_v4.pack_inventory import inventory_pack
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


def inventory_present_scan(path: Path) -> IntegrityCheck:
    inventory = inventory_pack(path)
    if not inventory.present:
        return IntegrityCheck(
            "radar_v4.inventory_present",
            False,
            "UNREADABLE_PACK",
            ("Inventory lock needs a pack directory. Not invented.",),
            {"path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.inventory_present",
        True,
        None,
        ("Pack directory is present. Not a measurement.",),
        {"path": str(path)},
    )


def inventory_declaration_scan(path: Path) -> IntegrityCheck:
    present = inventory_present_scan(path)
    if not present.valid:
        return present
    inventory = inventory_pack(path)
    found = any(item.role == "declaration" for item in inventory.files)
    if not found:
        return IntegrityCheck(
            "radar_v4.inventory_declaration",
            False,
            "INVENTORY_DECLARATION_REFUSED",
            ("A locked inventory needs a declaration file. Not repaired.",),
            {"path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.inventory_declaration",
        True,
        None,
        ("Inventory lists a declaration. Not market evidence.",),
        {"path": str(path)},
    )


def inventory_obs_scan(path: Path) -> IntegrityCheck:
    present = inventory_present_scan(path)
    if not present.valid:
        return present
    inventory = inventory_pack(path)
    names = inventory.observation_names()
    if not names:
        return IntegrityCheck(
            "radar_v4.inventory_empty",
            False,
            "INVENTORY_EMPTY_REFUSED",
            ("A locked inventory needs observation files. Not a pack.",),
            {"path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.inventory_empty",
        True,
        None,
        ("Inventory lists observations. Filenames are not a method.",),
        {"count": len(names), "path": str(path)},
    )


def inventory_hidden_scan(path: Path) -> IntegrityCheck:
    present = inventory_present_scan(path)
    if not present.valid:
        return present
    inventory = inventory_pack(path)
    hits = [item.name for item in inventory.files if item.name.startswith(".")]
    if hits:
        return IntegrityCheck(
            "radar_v4.inventory_hidden",
            False,
            "INVENTORY_HIDDEN_REFUSED",
            ("A locked inventory refuses hidden files. Not repaired.",),
            {"hits": hits, "path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.inventory_hidden",
        True,
        None,
        ("Inventory has no hidden files. Not a score.",),
        {"hits": [], "path": str(path)},
    )


def inventory_lock(path: Path) -> IntegrityCheck:
    parts = [
        inventory_present_scan(path),
        inventory_declaration_scan(path),
        inventory_obs_scan(path),
        inventory_hidden_scan(path),
    ]
    failed = [part for part in parts if not part.valid]
    if failed:
        first = failed[0]
        return IntegrityCheck(
            "radar_v4.inventory_lock",
            False,
            first.error_code,
            ("Inventory lock failed.",) + first.notes,
            {"failed": [part.document_kind for part in failed]},
        )
    return IntegrityCheck(
        "radar_v4.inventory_lock",
        True,
        None,
        ("Inventory lock passed. Not market evidence.",),
        {"failed": []},
    )


def inventory_lock_determinism(path: Path) -> IntegrityCheck:
    first = inventory_lock(path)
    second = inventory_lock(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.inventory_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Inventory lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_inventory_lock(left: Path, right: Path) -> IntegrityCheck:
    first = inventory_lock(left)
    second = inventory_lock(right)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.compare_inventory_lock",
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared inventory-lock records. Equality is not a score.",),
        {"equal": equal},
    )


def write_inventory_record(
    source: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = inventory_lock(source)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_inventory_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.inventory_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable inventory-lock record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.inventory_verify",
            False,
            "UNREADABLE_JSON",
            ("inventory-lock record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.inventory_verify",
            False,
            "UNREADABLE_JSON",
            ("inventory-lock record must be an object",),
            {"path": str(target)},
        )
    ok = raw.get("document_kind") == "radar_v4.inventory_lock" and raw.get("valid") is True
    return IntegrityCheck(
        "radar_v4.inventory_verify",
        ok,
        None if ok else "INVENTORY_RECORD_INVALID",
        ("Verified a local inventory-lock record. Not market evidence.",),
        {"path": str(target)},
    )


def inventory_status_bind(path: Path) -> IntegrityCheck:
    locked = inventory_lock(path)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.inventory_status_bind",
        matched,
        None if matched else "INVENTORY_STATUS_MISMATCH",
        ("Inventory lock and status share the locked unit. Not a measurement.",),
        {
            "inventory_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
