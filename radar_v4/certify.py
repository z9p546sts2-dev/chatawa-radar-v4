"""Compose local pack checks. Passing is not market evidence and not a method."""

from __future__ import annotations

import ast
from json import loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.catalog_audit import audit_document_kinds, audit_reason_catalog
from radar_v4.dataset_pack import load_dataset_pack
from radar_v4.decimal_check import decimal_check_directory
from radar_v4.hygiene import pack_hygiene
from radar_v4.integrity import IntegrityCheck
from radar_v4.lineage import admission_vs_kept
from radar_v4.pack_safety import inspect_pack_safety
from radar_v4.record_check import (
    inspect_leftovers,
    inspect_ohlc,
    inspect_pack_urls,
    inspect_primary_metric,
    inspect_retrieval_order,
    inspect_ruler_fields,
    inspect_unexpected_files,
    scan_percent_fields,
)
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


RESERVED_NAMES = frozenset(
    {
        "live.json",
        "historical.json",
        "edge.json",
        "signal.json",
        "trade.json",
        "paper.json",
        "best_trades.json",
    }
)


def list_commands(main_path: Path | None = None) -> list[str]:
    roots = []
    if main_path is not None:
        roots.append(Path(main_path))
    else:
        package = Path(__file__).resolve().parent
        roots.extend([package / "cli.py", package / "workshop_cli.py"])
    names: list[str] = []
    for path in roots:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Attribute) or node.func.attr != "add_parser":
                continue
            if (
                node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                names.append(node.args[0].value)
    return names


def command_catalog() -> IntegrityCheck:
    commands = list_commands()
    return IntegrityCheck(
        "radar_v4.command_catalog",
        True,
        None,
        ("Local command list. A command is not a method.",),
        {"commands": commands, "count": len(commands)},
    )


def reserved_name_scan(directory: Path) -> IntegrityCheck:
    hits = sorted(path.name for path in Path(directory).iterdir() if path.name.lower() in RESERVED_NAMES)
    if hits:
        return IntegrityCheck(
            "radar_v4.reserved_names",
            False,
            "RESERVED_NAME_REFUSED",
            ("A reserved live/trade/edge filename is not a workshop pack file.",),
            {"hits": hits},
        )
    return IntegrityCheck(
        "radar_v4.reserved_names",
        True,
        None,
        ("No reserved live/trade/edge filenames.",),
        {"hits": []},
    )


def name_vs_ruler(directory: Path) -> IntegrityCheck:
    pack = load_dataset_pack(directory)
    if pack.declaration is None:
        return IntegrityCheck(
            "radar_v4.name_vs_ruler",
            True,
            None,
            ("No usable declaration in this directory.",),
            {},
        )
    mismatches = [
        item.envelope.symbol_or_universe or ""
        for item in pack.observation_intake.accepted
        if item.envelope.symbol_or_universe != pack.declaration.universe
    ]
    if mismatches:
        return IntegrityCheck(
            "radar_v4.name_vs_ruler",
            False,
            "NAME_VS_RULER_REFUSED",
            ("An observation symbol does not match the declaration universe.",),
            {"ruler_symbol": pack.declaration.universe, "mismatches": mismatches},
        )
    return IntegrityCheck(
        "radar_v4.name_vs_ruler",
        True,
        None,
        ("Observation symbols match the declaration universe.",),
        {"symbol": pack.declaration.universe},
    )


def utf16_scan(directory: Path) -> IntegrityCheck:
    hits: list[str] = []
    for path in sorted(Path(directory).iterdir()):
        if not path.is_file():
            continue
        raw = path.read_bytes()[:4]
        if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
            hits.append(path.name)
    if hits:
        return IntegrityCheck(
            "radar_v4.text_encoding",
            False,
            "UTF16_REFUSED",
            ("UTF-16 is not a workshop encoding.",),
            {"hits": hits},
        )
    return IntegrityCheck(
        "radar_v4.text_encoding",
        True,
        None,
        ("No UTF-16 BOM found.",),
        {"hits": []},
    )


def fixture_label_check(directory: Path) -> IntegrityCheck:
    pack = load_dataset_pack(directory)
    if pack.declaration is None:
        return IntegrityCheck(
            "radar_v4.fixture_label",
            True,
            None,
            ("No pack declaration in this directory.",),
            {},
        )
    if pack.declaration.provenance_class != "SYNTHETIC":
        return IntegrityCheck(
            "radar_v4.fixture_label",
            False,
            "FIXTURE_LABEL_REFUSED",
            ("Only SYNTHETIC fixture labels are local workshop labels.",),
            {"kind": pack.declaration.provenance_class},
        )
    return IntegrityCheck(
        "radar_v4.fixture_label",
        True,
        None,
        ("Fixture label is SYNTHETIC.",),
        {"kind": pack.declaration.provenance_class},
    )


def compare_stops(left_text: str, right_text: str) -> IntegrityCheck:
    left = loads(left_text)
    right = loads(right_text)
    if not isinstance(left, dict) or not isinstance(right, dict):
        return IntegrityCheck(
            "radar_v4.compare_stops",
            False,
            "UNREADABLE_JSON",
            ("A stop record must be a JSON object.",),
            {},
        )
    same = (
        left.get("highest_unit") == right.get("highest_unit")
        and left.get("measured") is False
        and right.get("measured") is False
        and left.get("vendor_authorized") is False
        and right.get("vendor_authorized") is False
    )
    return IntegrityCheck(
        "radar_v4.compare_stops",
        True,
        None,
        ("Stop records compared. Same freeze is not a method.",),
        {
            "same_freeze": same,
            "left_highest_unit": left.get("highest_unit"),
            "right_highest_unit": right.get("highest_unit"),
        },
    )


def self_test() -> IntegrityCheck:
    status = loads(workshop_status())
    catalog = loads(audit_reason_catalog())
    kinds = loads(audit_document_kinds())
    ok = (
        status.get("measured") is False
        and catalog.get("valid") is True
        and kinds.get("valid") is True
        and int(status.get("highest_unit") or 0) == PHASE5_HIGHEST_UNIT
    )
    return IntegrityCheck(
        "radar_v4.self_test",
        ok,
        None if ok else "SELF_TEST_FAILED",
        ("Local self-test of workshop invariants. Not market evidence.",),
        {
            "highest_unit": PHASE5_HIGHEST_UNIT,
            "measured": status.get("measured"),
            "catalog_valid": catalog.get("valid"),
            "kinds_valid": kinds.get("valid"),
        },
    )


def _percent_pack(directory: Path) -> IntegrityCheck:
    failures: list[str] = []
    for path in sorted(Path(directory).glob("*.json")):
        check = scan_percent_fields(path)
        if not check.valid:
            failures.append(path.name)
    if failures:
        return IntegrityCheck(
            "radar_v4.percent_fields",
            False,
            "PERCENT_FIELD",
            ("A pack JSON file names a percent or return field.",),
            {"failures": failures},
        )
    return IntegrityCheck(
        "radar_v4.percent_fields",
        True,
        None,
        ("No percent or return field names.",),
        {"failures": []},
    )


def _safety_as_check(directory: Path) -> IntegrityCheck:
    report = inspect_pack_safety(directory)
    return IntegrityCheck(
        "radar_v4.pack_safety",
        report.safe,
        None if report.safe else (report.issues[0] if report.issues else "PACK_NOT_USABLE"),
        ("Pack safety is not market evidence.",),
        {"issues": list(report.issues)},
    )


def certify_pack(directory: Path) -> IntegrityCheck:
    checks = [
        _safety_as_check(directory),
        inspect_unexpected_files(directory),
        inspect_leftovers(directory),
        inspect_pack_urls(directory),
        _percent_pack(directory),
        inspect_ohlc(directory),
        inspect_retrieval_order(directory),
        inspect_ruler_fields(directory),
        inspect_primary_metric(directory),
        pack_hygiene(directory),
        decimal_check_directory(directory),
        admission_vs_kept(directory),
        reserved_name_scan(directory),
        name_vs_ruler(directory),
        utf16_scan(directory),
        fixture_label_check(directory),
    ]
    failed = [check for check in checks if not check.valid]
    if failed:
        first = failed[0]
        return IntegrityCheck(
            "radar_v4.certify",
            False,
            first.error_code or "CERTIFY_FAILED",
            ("Pack certify failed. Not a market judgment.",) + first.notes,
            {"failed": [check.document_kind for check in failed]},
        )
    return IntegrityCheck(
        "radar_v4.certify",
        True,
        None,
        (
            "Local pack checks passed. Not market evidence. Not a method. "
            "Not authorization to buy data or open Phase 6."
        ),
        {"failed": [], "check_count": len(checks)},
    )


def write_certify_record(
    directory: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = certify_pack(directory)
    write_text_atomic(destination, record.serialize() + "\n")
    return record
