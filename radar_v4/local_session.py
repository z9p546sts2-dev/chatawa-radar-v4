"""Run a Phase 5 session from a local pack or snapshot. No network."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from radar_v4.dataset_pack import DatasetPackReport, load_dataset_pack
from radar_v4.session import SessionResult, run_dataset_session
from radar_v4.snapshot import DatasetSnapshot
from radar_v4.snapshot_files import read_snapshot_file


@dataclass(frozen=True)
class LocalSessionResult:
    pack: DatasetPackReport | None
    session: SessionResult | None
    error_code: str | None


def run_session_from_snapshot(snapshot: DatasetSnapshot) -> SessionResult:
    """Re-run admission, series, and baseline on a preserved snapshot."""
    envelopes = tuple(item.envelope for item in snapshot.observations)
    return run_dataset_session(snapshot.declaration, envelopes, snapshot.observations)


def run_session_from_snapshot_file(path: str | Path) -> SessionResult:
    return run_session_from_snapshot(read_snapshot_file(path))


def run_session_from_pack(directory: str | Path) -> LocalSessionResult:
    """Load a FIXTURE/SYNTHETIC pack and run a dataset session if usable."""
    pack = load_dataset_pack(directory)
    if not pack.usable():
        return LocalSessionResult(
            pack=pack,
            session=None,
            error_code="PACK_NOT_USABLE",
        )
    assert pack.declaration is not None
    observations = pack.observation_intake.accepted
    envelopes = tuple(item.envelope for item in observations)
    session = run_dataset_session(pack.declaration, envelopes, observations)
    return LocalSessionResult(pack=pack, session=session, error_code=None)
