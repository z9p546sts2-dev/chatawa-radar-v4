"""A pack bar after as-of is lookahead. Not a method."""

from __future__ import annotations

from json import JSONDecodeError, dumps, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.dataset_pack import load_dataset_pack
from radar_v4.evidence import format_canonical_timestamp, parse_canonical_timestamp
from radar_v4.horizon_lock import horizon_lock
from radar_v4.integrity import IntegrityCheck, lock_source_details
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


def _dump(document: dict[str, object]) -> str:
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _last_bar(pack: Path) -> str | None:
    report = load_dataset_pack(pack)
    stamps = [
        item.envelope.market_timestamp
        for item in report.observation_intake.accepted
        if item.envelope.market_timestamp is not None
    ]
    if not stamps:
        return None
    return format_canonical_timestamp(max(stamps))


def horizon_bind(horizon: Path, pack: Path) -> IntegrityCheck:
    locked = horizon_lock(horizon)
    extra = {
        "horizon_path": str(Path(horizon).resolve()),
        "pack_path": str(Path(pack).resolve()),
        "as_of": locked.details.get("as_of"),
        "include_through": locked.details.get("include_through"),
    }
    if not locked.valid:
        extra["failed"] = ["radar_v4.horizon_lock"]
        return IntegrityCheck(
            "radar_v4.horizon_bind",
            False,
            locked.error_code,
            ("Horizon bind failed on the horizon document.",) + locked.notes,
            lock_source_details(horizon, extra),
        )
    last_bar = _last_bar(pack)
    extra["last_bar"] = last_bar
    if last_bar is None:
        extra["failed"] = ["radar_v4.horizon_bind"]
        return IntegrityCheck(
            "radar_v4.horizon_bind",
            False,
            "UNREADABLE_PACK",
            ("Horizon bind needs a pack with market timestamps.",),
            lock_source_details(horizon, extra),
        )
    as_of = locked.details.get("as_of")
    assert isinstance(as_of, str)
    stamp = parse_canonical_timestamp(as_of)
    bar = parse_canonical_timestamp(last_bar)
    lookahead = bar > stamp
    extra["failed"] = []
    extra["bar_after_as_of"] = lookahead
    return IntegrityCheck(
        "radar_v4.horizon_bind",
        not lookahead,
        None if not lookahead else "LOOKAHEAD_BAR",
        (
            "A bar after as_of is lookahead, not a measurement.",
            "This does not invent a calendar or a fill.",
        ),
        lock_source_details(horizon, extra),
    )


def horizon_bind_determinism(horizon: Path, pack: Path) -> IntegrityCheck:
    first = horizon_bind(horizon, pack)
    second = horizon_bind(horizon, pack)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.horizon_bind_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Horizon bind ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def write_horizon_bind_record(
    horizon: Path, pack: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = horizon_bind(horizon, pack)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_horizon_bind_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.horizon_bind_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable horizon-bind record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.horizon_bind_verify",
            False,
            "UNREADABLE_JSON",
            ("horizon-bind record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.horizon_bind_verify",
            False,
            "UNREADABLE_JSON",
            ("horizon-bind record must be an object",),
            {"path": str(target)},
        )
    details = raw.get("details")
    horizon = details.get("horizon_path") if isinstance(details, dict) else None
    pack = details.get("pack_path") if isinstance(details, dict) else None
    if (
        not isinstance(horizon, str)
        or not horizon
        or not isinstance(pack, str)
        or not pack
    ):
        return IntegrityCheck(
            "radar_v4.horizon_bind_verify",
            False,
            "HORIZON_BIND_INVALID",
            ("horizon-bind record is missing horizon_path or pack_path; kind+valid is not a verify",),
            {"path": str(target)},
        )
    horizon_path = Path(horizon)
    pack_path = Path(pack)
    if not horizon_path.exists() or not pack_path.exists():
        return IntegrityCheck(
            "radar_v4.horizon_bind_verify",
            False,
            "UNREADABLE_PACK",
            ("horizon-bind sources are not present",),
            {"path": str(target), "horizon_path": horizon, "pack_path": pack},
        )
    recomputed = horizon_bind(horizon_path, pack_path)
    matched = (
        raw.get("document_kind") == "radar_v4.horizon_bind"
        and raw.get("valid") is True
        and recomputed.valid
        and recomputed.serialize() == _dump(raw)
    )
    if not matched and (
        raw.get("document_kind") != "radar_v4.horizon_bind" or raw.get("valid") is not True
    ):
        error = "HORIZON_BIND_INVALID"
    elif not matched and not recomputed.valid:
        error = "HORIZON_BIND_INVALID"
    elif not matched:
        error = "RECORD_MISMATCH"
    else:
        error = None
    return IntegrityCheck(
        "radar_v4.horizon_bind_verify",
        matched,
        error,
        (
            "Verified a horizon-bind record by recomputing from horizon and pack.",
            "Not market evidence.",
        ),
        {"path": str(target), "horizon_path": horizon, "pack_path": pack},
    )


def horizon_bind_status(horizon: Path, pack: Path) -> IntegrityCheck:
    locked = horizon_bind(horizon, pack)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.horizon_bind_status",
        matched,
        None if matched else "HORIZON_BIND_STATUS_MISMATCH",
        ("Horizon bind and status share the locked unit. Not a measurement.",),
        {
            "bind_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
