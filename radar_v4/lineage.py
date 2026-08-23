"""Admission, order, and span descriptions. Not market evidence."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.dataset_pack import load_dataset_pack
from radar_v4.integrity import IntegrityCheck
from radar_v4.pack_describe import pack_readiness
from radar_v4.snapshot_files import SnapshotFileError, read_snapshot_file


def admission_vs_kept(directory: Path) -> IntegrityCheck:
    readiness = pack_readiness(directory)
    return IntegrityCheck(
        "radar_v4.lineage",
        True,
        None,
        ("Admission versus kept count. Not a quality score.",),
        {
            "accepted": readiness.accepted_observations,
            "admitted": readiness.admitted_observations,
            "kept": readiness.admitted_observations,
            "refused": readiness.accepted_observations - readiness.admitted_observations,
        },
    )


def snapshot_order_check(path: Path | str) -> IntegrityCheck:
    snapshot = read_snapshot_file(path)
    stamps = [
        item.envelope.market_timestamp
        for item in snapshot.observations
        if item.envelope.market_timestamp is not None
    ]
    if stamps != sorted(stamps):
        return IntegrityCheck(
            "radar_v4.snapshot_order",
            False,
            "SNAPSHOT_ORDER_REFUSED",
            ("Snapshot observation timestamps are not sorted.",),
            {"timestamps": [stamp.isoformat() for stamp in stamps]},
        )
    return IntegrityCheck(
        "radar_v4.snapshot_order",
        True,
        None,
        ("Snapshot observation timestamps are sorted.",),
        {"count": len(stamps)},
    )


def clock_skew_describe(directory: Path) -> IntegrityCheck:
    pack = load_dataset_pack(directory)
    stamps = sorted(
        item.envelope.market_timestamp
        for item in pack.observation_intake.accepted
        if item.envelope.market_timestamp is not None
    )
    if len(stamps) < 2:
        return IntegrityCheck(
            "radar_v4.clock_skew",
            True,
            "INSUFFICIENT_EVIDENCE",
            ("Fewer than two observations. Skew is not described.",),
            {"count": len(stamps)},
        )
    delta = stamps[-1] - stamps[0]
    return IntegrityCheck(
        "radar_v4.clock_skew",
        True,
        None,
        ("First-to-last timestamp span. Not a trading clock.",),
        {
            "first": stamps[0].isoformat(),
            "last": stamps[-1].isoformat(),
            "seconds": str(Decimal(str(delta.total_seconds()))),
        },
    )


def span_describe(directory: Path) -> IntegrityCheck:
    return clock_skew_describe(directory)


def duplicate_close_describe(directory: Path) -> IntegrityCheck:
    loaded = sorted(
        (
            item
            for item in load_dataset_pack(directory).observation_intake.accepted
            if item.envelope.market_timestamp is not None
        ),
        key=lambda item: item.envelope.market_timestamp or item.envelope.retrieval_timestamp,
    )
    pairs: list[dict[str, str]] = []
    for left, right in zip(loaded, loaded[1:]):
        if left.payload.close == right.payload.close:
            pairs.append(
                {
                    "left": left.envelope.market_timestamp.isoformat()
                    if left.envelope.market_timestamp
                    else "",
                    "right": right.envelope.market_timestamp.isoformat()
                    if right.envelope.market_timestamp
                    else "",
                    "close": left.payload.close,
                }
            )
    return IntegrityCheck(
        "radar_v4.duplicate_close",
        True,
        None,
        ("Consecutive equal closes described. Not a signal.",),
        {"pairs": pairs, "count": len(pairs)},
    )


def volume_describe(directory: Path) -> IntegrityCheck:
    present = 0
    for item in load_dataset_pack(directory).observation_intake.accepted:
        if item.payload.volume is not None:
            present += 1
    return IntegrityCheck(
        "radar_v4.volume_describe",
        True,
        None,
        ("Volume is not used by the locked question. Described only.",),
        {"observations_with_volume": present},
    )


def write_lineage_record(
    directory: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    admission = admission_vs_kept(directory)
    skew = clock_skew_describe(directory)
    dups = duplicate_close_describe(directory)
    volume = volume_describe(directory)
    record = IntegrityCheck(
        "radar_v4.lineage_record",
        True,
        None,
        ("Local lineage description. Not market evidence.",),
        {
            "admission": admission.details,
            "span": skew.details,
            "duplicate_closes": dups.details,
            "volume": volume.details,
        },
    )
    write_text_atomic(destination, record.serialize() + "\n")
    return record
