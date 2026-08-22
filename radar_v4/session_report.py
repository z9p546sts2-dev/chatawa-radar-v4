"""Serialize a session result for local audit. Not a method claim."""

from __future__ import annotations

from json import dumps
from pathlib import Path

from radar_v4.session import SessionResult
from radar_v4.snapshot_files import SnapshotFileError


def serialize_session_report(result: SessionResult) -> str:
    quarantine_codes = sorted(
        {
            code
            for record in result.admission.quarantined
            for code in record.validation.issue_codes()
        }
    )
    rejected_codes = sorted(
        {
            code
            for _item, validation in result.rejected_observations
            for code in validation.issue_codes()
        }
    )
    baseline = result.baseline
    document = {
        "admission_accepted": result.admission.accepted_count(),
        "admission_quarantine_codes": quarantine_codes,
        "admission_quarantined": result.admission.quarantined_count(),
        "baseline": None
        if baseline is None
        else {
            "change_count": baseline.change_count,
            "changes": list(baseline.changes),
            "claim_level": baseline.claim_level,
            "notes": list(baseline.notes),
            "status": baseline.status,
        },
        "dataset_id": result.snapshot.declaration.dataset_id,
        "kept_observation_count": result.kept_observation_count(),
        "rejected_codes": rejected_codes,
        "rejected_observation_count": result.rejected_observation_count(),
        "series_issue_codes": list(result.series.issue_codes()),
        "series_valid": result.series.valid,
    }
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def write_session_report_file(path: str | Path, result: SessionResult) -> Path:
    target = Path(path)
    if target.exists() and target.is_dir():
        raise SnapshotFileError(
            "SESSION_REPORT_PATH_IS_DIRECTORY",
            f"{target} is a directory, not a session report file",
        )
    target.write_text(serialize_session_report(result) + "\n", encoding="utf-8")
    return target
