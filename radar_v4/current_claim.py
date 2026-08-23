"""A later stamp may not claim the bars are current. Not a method."""

from __future__ import annotations

from json import JSONDecodeError, dumps, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.dataset_pack import load_dataset_pack
from radar_v4.evidence import format_canonical_timestamp, parse_canonical_timestamp
from radar_v4.freshness_lock import freshness_lock
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


def current_claim(freshness: Path, pack: Path) -> IntegrityCheck:
    locked = freshness_lock(freshness)
    extra = {
        "freshness_path": str(Path(freshness).resolve()),
        "pack_path": str(Path(pack).resolve()),
        "as_of": locked.details.get("as_of"),
        "claim_current": locked.details.get("claim_current"),
    }
    if not locked.valid:
        extra["failed"] = ["radar_v4.freshness_lock"]
        return IntegrityCheck(
            "radar_v4.current_claim",
            False,
            locked.error_code,
            ("Current-claim failed on the freshness document.",) + locked.notes,
            lock_source_details(freshness, extra),
        )
    last_bar = _last_bar(pack)
    extra["last_bar"] = last_bar
    if last_bar is None:
        extra["failed"] = ["radar_v4.current_claim"]
        return IntegrityCheck(
            "radar_v4.current_claim",
            False,
            "UNREADABLE_PACK",
            ("Current-claim needs a pack with market timestamps.",),
            lock_source_details(freshness, extra),
        )
    as_of = locked.details.get("as_of")
    claim = locked.details.get("claim_current")
    assert isinstance(as_of, str)
    stamp = parse_canonical_timestamp(as_of)
    bar = parse_canonical_timestamp(last_bar)
    conceals = claim is True and stamp > bar
    extra["failed"] = []
    extra["stamp_after_last_bar"] = stamp > bar
    return IntegrityCheck(
        "radar_v4.current_claim",
        not conceals,
        None if not conceals else "FRESH_STAMP_STALE_BARS",
        (
            "A later stamp may not claim the series is current.",
            "Fresh prices may not conceal stale bars.",
        ),
        lock_source_details(freshness, extra),
    )


def current_claim_determinism(freshness: Path, pack: Path) -> IntegrityCheck:
    first = current_claim(freshness, pack)
    second = current_claim(freshness, pack)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.current_claim_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Current-claim ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def write_current_claim_record(
    freshness: Path, pack: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = current_claim(freshness, pack)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_current_claim_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.current_claim_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable current-claim record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.current_claim_verify",
            False,
            "UNREADABLE_JSON",
            ("current-claim record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.current_claim_verify",
            False,
            "UNREADABLE_JSON",
            ("current-claim record must be an object",),
            {"path": str(target)},
        )
    details = raw.get("details")
    freshness = details.get("freshness_path") if isinstance(details, dict) else None
    pack = details.get("pack_path") if isinstance(details, dict) else None
    if (
        not isinstance(freshness, str)
        or not freshness
        or not isinstance(pack, str)
        or not pack
    ):
        return IntegrityCheck(
            "radar_v4.current_claim_verify",
            False,
            "CURRENT_CLAIM_INVALID",
            ("current-claim record is missing freshness_path or pack_path; kind+valid is not a verify",),
            {"path": str(target)},
        )
    freshness_path = Path(freshness)
    pack_path = Path(pack)
    if not freshness_path.exists() or not pack_path.exists():
        return IntegrityCheck(
            "radar_v4.current_claim_verify",
            False,
            "UNREADABLE_PACK",
            ("current-claim sources are not present",),
            {"path": str(target), "freshness_path": freshness, "pack_path": pack},
        )
    recomputed = current_claim(freshness_path, pack_path)
    matched = (
        raw.get("document_kind") == "radar_v4.current_claim"
        and raw.get("valid") is True
        and recomputed.valid
        and recomputed.serialize() == _dump(raw)
    )
    if not matched and (
        raw.get("document_kind") != "radar_v4.current_claim" or raw.get("valid") is not True
    ):
        error = "CURRENT_CLAIM_INVALID"
    elif not matched and not recomputed.valid:
        error = "CURRENT_CLAIM_INVALID"
    elif not matched:
        error = "RECORD_MISMATCH"
    else:
        error = None
    return IntegrityCheck(
        "radar_v4.current_claim_verify",
        matched,
        error,
        (
            "Verified a current-claim record by recomputing from freshness and pack.",
            "Not market evidence.",
        ),
        {"path": str(target), "freshness_path": freshness, "pack_path": pack},
    )


def current_claim_status(freshness: Path, pack: Path) -> IntegrityCheck:
    locked = current_claim(freshness, pack)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.current_claim_status",
        matched,
        None if matched else "CURRENT_CLAIM_STATUS_MISMATCH",
        ("Current-claim and status share the locked unit. Not a measurement.",),
        {
            "claim_valid": locked.valid,
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "status_unit": status_unit,
        },
    )
