"""Local replay and export round-trips. No vendor. No new question."""

from __future__ import annotations

from pathlib import Path

from radar_v4.integrity import IntegrityCheck
from radar_v4.local_session import run_session_from_pack, run_session_from_snapshot
from radar_v4.pack_export import PackExportError, export_snapshot_to_pack
from radar_v4.ruler import ruler_checksum


def check_replay_equality(directory: str | Path) -> IntegrityCheck:
    """Run a pack, replay its snapshot, and compare stored changes."""
    first = run_session_from_pack(directory)
    if first.session is None or first.session.baseline is None:
        return IntegrityCheck(
            "radar_v4.replay_equality",
            False,
            first.error_code or "PACK_NOT_USABLE",
            ("replay equality needs a measured local session",),
            {},
        )
    replayed = run_session_from_snapshot(first.session.snapshot)
    if replayed.baseline is None:
        return IntegrityCheck(
            "radar_v4.replay_equality",
            False,
            "ARITHMETIC_MISMATCH",
            ("replay produced no baseline",),
            {},
        )
    left = first.session.baseline.changes
    right = replayed.baseline.changes
    valid = left == right
    return IntegrityCheck(
        "radar_v4.replay_equality",
        valid,
        None if valid else "REPLAY_MISMATCH",
        (
            "replay equality is software identity, not market evidence",
            "SYNTHETIC numbers remain SYNTHETIC",
        ),
        {"replayed": list(right), "stored": list(left)},
    )


def check_export_roundtrip(directory: str | Path, destination: str | Path) -> IntegrityCheck:
    """Export a snapshot to a new pack and compare ruler plus membership."""
    first = run_session_from_pack(directory)
    if first.session is None:
        return IntegrityCheck(
            "radar_v4.export_roundtrip",
            False,
            first.error_code or "PACK_NOT_USABLE",
            ("export round-trip needs a usable pack",),
            {},
        )
    try:
        written = export_snapshot_to_pack(first.session.snapshot, destination)
    except PackExportError as exc:
        return IntegrityCheck(
            "radar_v4.export_roundtrip",
            False,
            exc.code,
            (exc.reason,),
            {},
        )
    second = run_session_from_pack(written)
    if second.session is None:
        return IntegrityCheck(
            "radar_v4.export_roundtrip",
            False,
            second.error_code or "PACK_NOT_USABLE",
            ("exported pack was not usable",),
            {"directory": str(written)},
        )
    left = ruler_checksum(first.session.snapshot.declaration)
    right = ruler_checksum(second.session.snapshot.declaration)
    count_left = first.session.kept_observation_count()
    count_right = second.session.kept_observation_count()
    valid = left == right and count_left == count_right
    return IntegrityCheck(
        "radar_v4.export_roundtrip",
        valid,
        None if valid else "EXPORT_ROUNDTRIP_MISMATCH",
        (
            "round-trip identity is not HISTORICAL evidence",
            "export remains FIXTURE/SYNTHETIC only",
        ),
        {
            "directory": str(written),
            "exported_count": count_right,
            "exported_ruler": right,
            "source_count": count_left,
            "source_ruler": left,
        },
    )
