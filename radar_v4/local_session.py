"""Run a Phase 5 session from a local pack or snapshot. No network."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from radar_v4.dataset_pack import DatasetPackReport, load_dataset_pack
from radar_v4.ruler import RulerMismatchError, require_ruler
from radar_v4.session import SessionResult, run_dataset_session
from radar_v4.snapshot import DatasetSnapshot
from radar_v4.snapshot_files import read_snapshot_file


@dataclass(frozen=True)
class LocalSessionResult:
    pack: DatasetPackReport | None
    session: SessionResult | None
    error_code: str | None


def run_session_from_snapshot(
    snapshot: DatasetSnapshot,
    expected_ruler: str | None = None,
    measure: bool = True,
) -> SessionResult:
    """Re-run admission, series, and baseline on a preserved snapshot."""
    if expected_ruler is not None:
        require_ruler(snapshot.declaration, expected_ruler)
    envelopes = tuple(item.envelope for item in snapshot.observations)
    return run_dataset_session(
        snapshot.declaration, envelopes, snapshot.observations, measure=measure
    )


def run_session_from_snapshot_file(
    path: str | Path, expected_ruler: str | None = None, measure: bool = True
) -> SessionResult:
    return run_session_from_snapshot(
        read_snapshot_file(path), expected_ruler, measure=measure
    )


def run_session_from_pack(
    directory: str | Path,
    require_manifest: bool = False,
    expected_ruler: str | None = None,
    measure: bool = True,
) -> LocalSessionResult:
    """Load a FIXTURE/SYNTHETIC pack and run a dataset session if usable."""
    pack = load_dataset_pack(directory, require_manifest=require_manifest)
    if not pack.usable():
        return LocalSessionResult(
            pack=pack,
            session=None,
            error_code="PACK_NOT_USABLE",
        )
    assert pack.declaration is not None
    if expected_ruler is not None:
        try:
            require_ruler(pack.declaration, expected_ruler)
        except RulerMismatchError:
            return LocalSessionResult(
                pack=pack,
                session=None,
                error_code="RULER_MISMATCH",
            )
    observations = pack.observation_intake.accepted
    envelopes = tuple(item.envelope for item in observations)
    session = run_dataset_session(
        pack.declaration, envelopes, observations, measure=measure
    )
    return LocalSessionResult(pack=pack, session=session, error_code=None)
