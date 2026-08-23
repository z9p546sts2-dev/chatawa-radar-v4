"""Exported-pack identity checks. Portable. Not market evidence."""

from __future__ import annotations

from json import JSONDecodeError, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.dataset_pack import load_dataset_pack
from radar_v4.fixture_pack import PACK_ALLOWED_PROVENANCE
from radar_v4.integrity import IntegrityCheck
from radar_v4.manifest_lock import manifest_lock
from radar_v4.pack_describe import inspect_pack_layout
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


def export_layout_scan(path: Path) -> IntegrityCheck:
    layout = inspect_pack_layout(path)
    if "UNREADABLE_PACK" in layout.issues:
        return IntegrityCheck(
            "radar_v4.export_layout",
            False,
            "UNREADABLE_PACK",
            ("Export lock needs a pack directory. Not invented.",),
            {"path": str(path)},
        )
    if not layout.ready_to_load:
        return IntegrityCheck(
            "radar_v4.export_layout",
            False,
            "EXPORT_LAYOUT_REFUSED",
            ("An exportable pack needs a declaration and observations.",),
            {"issues": list(layout.issues), "path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.export_layout",
        True,
        None,
        ("Export layout is present. Filenames are not a method.",),
        {"observation_files": layout.observation_files, "path": str(path)},
    )


def export_manifest_scan(path: Path) -> IntegrityCheck:
    layout = inspect_pack_layout(path)
    if not layout.manifest_present:
        return IntegrityCheck(
            "radar_v4.export_manifest",
            False,
            "MANIFEST_MISSING",
            ("An exportable pack needs a stored manifest. Not repaired.",),
            {"path": str(path)},
        )
    locked = manifest_lock(path)
    if not locked.valid:
        return IntegrityCheck(
            "radar_v4.export_manifest",
            False,
            locked.error_code,
            ("Export lock needs a locked pack manifest.",) + locked.notes,
            {"path": str(path)},
        )
    return IntegrityCheck(
        "radar_v4.export_manifest",
        True,
        None,
        ("Export manifest is locked. Not market evidence.",),
        {"path": str(path)},
    )


def export_provenance_scan(path: Path) -> IntegrityCheck:
    report = load_dataset_pack(path)
    if report.declaration is None:
        return IntegrityCheck(
            "radar_v4.export_provenance",
            False,
            "EXPORT_PROVENANCE_REFUSED",
            ("Export lock needs a usable FIXTURE or SYNTHETIC declaration.",),
            {"path": str(path)},
        )
    allowed = report.declaration.provenance_class in PACK_ALLOWED_PROVENANCE
    if not allowed:
        return IntegrityCheck(
            "radar_v4.export_provenance",
            False,
            "EXPORT_PROVENANCE_REFUSED",
            ("Pack export may lock only FIXTURE or SYNTHETIC. HISTORICAL is refused.",),
            {"path": str(path), "provenance": report.declaration.provenance_class},
        )
    return IntegrityCheck(
        "radar_v4.export_provenance",
        True,
        None,
        ("Export provenance is FIXTURE or SYNTHETIC. Not HISTORICAL evidence.",),
        {"path": str(path), "provenance": report.declaration.provenance_class},
    )


def export_lock(path: Path) -> IntegrityCheck:
    parts = [
        export_layout_scan(path),
        export_manifest_scan(path),
        export_provenance_scan(path),
    ]
    failed = [part for part in parts if not part.valid]
    if failed:
        first = failed[0]
        return IntegrityCheck(
            "radar_v4.export_lock",
            False,
            first.error_code,
            ("Export lock failed.",) + first.notes,
            {"failed": [part.document_kind for part in failed]},
        )
    return IntegrityCheck(
        "radar_v4.export_lock",
        True,
        None,
        ("Export lock passed. Not market evidence.",),
        {"failed": []},
    )


def export_lock_determinism(path: Path) -> IntegrityCheck:
    first = export_lock(path)
    second = export_lock(path)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.export_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Export lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_export_lock(left: Path, right: Path) -> IntegrityCheck:
    first = export_lock(left)
    second = export_lock(right)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.compare_export_lock",
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared export-lock records. Equality is not a score.",),
        {"equal": equal},
    )


def write_export_record(
    source: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = export_lock(source)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_export_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.export_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable export-lock record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.export_verify",
            False,
            "UNREADABLE_JSON",
            ("export-lock record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.export_verify",
            False,
            "UNREADABLE_JSON",
            ("export-lock record must be an object",),
            {"path": str(target)},
        )
    ok = raw.get("document_kind") == "radar_v4.export_lock" and raw.get("valid") is True
    return IntegrityCheck(
        "radar_v4.export_verify",
        ok,
        None if ok else "EXPORT_RECORD_INVALID",
        ("Verified a local export-lock record. Not market evidence.",),
        {"path": str(target)},
    )


def export_status_bind(path: Path) -> IntegrityCheck:
    locked = export_lock(path)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.export_status_bind",
        matched,
        None if matched else "EXPORT_STATUS_MISMATCH",
        ("Export lock and status share the locked unit. Not a measurement.",),
        {
            "export_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
