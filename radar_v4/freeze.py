"""Workshop freeze and record-compare. Not market evidence. Not a method."""

from __future__ import annotations

from json import JSONDecodeError, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.byte_check import byte_check
from radar_v4.certify import certify_pack, command_catalog, self_test
from radar_v4.integrity import IntegrityCheck
from radar_v4.lineage import admission_vs_kept
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_bounds import workshop_bounds
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


def _load_object(text: str) -> dict[str, object]:
    raw = loads(text)
    if not isinstance(raw, dict):
        raise SnapshotFileError("UNREADABLE_JSON", "record must be a JSON object")
    return raw


def compare_integrity(left: IntegrityCheck, right: IntegrityCheck, kind: str) -> IntegrityCheck:
    equal = left.serialize() == right.serialize()
    return IntegrityCheck(
        kind,
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared local records. Equality is not a method.",),
        {
            "equal": equal,
            "left_kind": left.document_kind,
            "right_kind": right.document_kind,
        },
    )


def compare_certify(left_dir: Path, right_dir: Path) -> IntegrityCheck:
    return compare_integrity(
        certify_pack(left_dir),
        certify_pack(right_dir),
        "radar_v4.compare_certify",
    )


def compare_lineage(left_dir: Path, right_dir: Path) -> IntegrityCheck:
    return compare_integrity(
        admission_vs_kept(left_dir),
        admission_vs_kept(right_dir),
        "radar_v4.compare_lineage",
    )


def certify_determinism(directory: Path) -> IntegrityCheck:
    first = certify_pack(directory)
    second = certify_pack(directory)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.certify_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("The same pack certified twice. Equality is not market evidence.",),
        {"equal": equal, "valid": first.valid},
    )


def self_test_determinism() -> IntegrityCheck:
    first = self_test()
    second = self_test()
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.self_test_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Self-test ran twice. Equality is not a research result.",),
        {"equal": equal, "valid": first.valid},
    )


def command_catalog_determinism() -> IntegrityCheck:
    first = command_catalog()
    second = command_catalog()
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.command_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Command catalog listed twice. A command is not a method.",),
        {"equal": equal, "count": first.details.get("count")},
    )


def readme_unit_lock(readme_path: Path | None = None) -> IntegrityCheck:
    target = (
        Path(readme_path)
        if readme_path is not None
        else Path(__file__).resolve().parents[1] / "README.md"
    )
    text = target.read_text(encoding="utf-8")
    needle = f"UNITS 7–{PHASE5_HIGHEST_UNIT}"
    if needle not in text:
        return IntegrityCheck(
            "radar_v4.readme_unit_lock",
            False,
            "README_UNIT_MISMATCH",
            ("README status must name the locked highest unit.",),
            {"expected": needle, "path": str(target)},
        )
    return IntegrityCheck(
        "radar_v4.readme_unit_lock",
        True,
        None,
        ("README names the locked highest unit. Not a research result.",),
        {"expected": needle, "path": str(target)},
    )


def workshop_freeze(directory: Path | None = None) -> IntegrityCheck:
    pack = Path(directory) if directory is not None else Path(__file__).resolve().parents[1] / "fixtures" / "synthetic_one_symbol_1d"
    status = _load_object(workshop_status())
    bounds = _load_object(workshop_bounds())
    stop = _load_object(workshop_stop_record())
    tested = self_test()
    certified = certify_pack(pack)
    bytes_ok = byte_check(pack)
    readme = readme_unit_lock()
    ok = (
        status.get("measured") is False
        and bounds.get("vendor_authorized") is False
        and stop.get("paper_trading_authorized") is False
        and tested.valid
        and certified.valid
        and bytes_ok.valid
        and readme.valid
        and int(status.get("highest_unit") or 0) == PHASE5_HIGHEST_UNIT
    )
    return IntegrityCheck(
        "radar_v4.freeze",
        ok,
        None if ok else "FREEZE_FAILED",
        (
            "Workshop freeze is a capability lock, not a research result.",
            "This does not authorize a vendor, paper trading, or Phase 6.",
        ),
        {
            "highest_unit": PHASE5_HIGHEST_UNIT,
            "measured": status.get("measured"),
            "vendor_authorized": bounds.get("vendor_authorized"),
            "paper_trading_authorized": stop.get("paper_trading_authorized"),
            "self_test": tested.valid,
            "certify": certified.valid,
            "byte_check": bytes_ok.valid,
            "readme_lock": readme.valid,
        },
    )


def write_freeze_record(
    destination: Path, directory: Path | None = None, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = workshop_freeze(directory)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_freeze_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = _load_object(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.freeze_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable freeze record",),
            {"path": str(target)},
        )
    except (JSONDecodeError, SnapshotFileError):
        return IntegrityCheck(
            "radar_v4.freeze_verify",
            False,
            "UNREADABLE_JSON",
            ("freeze record is not a JSON object",),
            {"path": str(target)},
        )
    details = raw.get("details")
    detail_map = details if isinstance(details, dict) else {}
    ok = (
        raw.get("document_kind") == "radar_v4.freeze"
        and raw.get("valid") is True
        and detail_map.get("measured") is False
        and detail_map.get("vendor_authorized") is False
        and detail_map.get("paper_trading_authorized") is False
        and int(detail_map.get("highest_unit") or 0) == PHASE5_HIGHEST_UNIT
    )
    return IntegrityCheck(
        "radar_v4.freeze_verify",
        ok,
        None if ok else "FREEZE_FAILED",
        ("Verified a local freeze record. Not market evidence.",),
        {"path": str(target), "highest_unit": detail_map.get("highest_unit")},
    )


def compare_freeze(left_text: str, right_text: str) -> IntegrityCheck:
    left = _load_object(left_text)
    right = _load_object(right_text)
    left_details = left.get("details") if isinstance(left.get("details"), dict) else {}
    right_details = right.get("details") if isinstance(right.get("details"), dict) else {}
    same = (
        left.get("document_kind") == "radar_v4.freeze"
        and right.get("document_kind") == "radar_v4.freeze"
        and left_details.get("highest_unit") == right_details.get("highest_unit")
        and left_details.get("measured") is False
        and right_details.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.compare_freeze",
        True,
        None,
        ("Freeze records compared. Same freeze is not a method.",),
        {
            "same_freeze": same,
            "left_highest_unit": left_details.get("highest_unit"),
            "right_highest_unit": right_details.get("highest_unit"),
        },
    )
