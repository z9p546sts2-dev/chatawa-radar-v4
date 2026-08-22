"""Serialize a session result for local audit. Not a method claim."""

from __future__ import annotations

from json import dumps
from pathlib import Path

from radar_v4.change_continuity import inspect_change_records
from radar_v4.local_session import LocalSessionResult
from radar_v4.ruler import ruler_checksum
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
            "change_records": [item.to_json_dict() for item in baseline.change_records],
            "changes": list(baseline.changes),
            "claim_level": baseline.claim_level,
            "notes": list(baseline.notes),
            "status": baseline.status,
        },
        "dataset_id": result.snapshot.declaration.dataset_id,
        "ruler_checksum": ruler_checksum(result.snapshot.declaration),
        "kept_observation_count": result.kept_observation_count(),
        "rejected_codes": rejected_codes,
        "rejected_observation_count": result.rejected_observation_count(),
        "change_continuity_valid": None
        if baseline is None
        else inspect_change_records(baseline.change_records).valid,
        "series_issue_codes": list(result.series.issue_codes()),
        "series_valid": result.series.valid,
        "snapshot_checksum": result.snapshot.integrity_checksum(),
        "document_kind": "radar_v4.session_report",
        "report_version": 1,
    }
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def serialize_local_session_report(result: LocalSessionResult) -> str:
    """Include pack refusals. Does not invent a session when the pack is unusable."""
    pack = result.pack
    pack_issue_codes = []
    pack_quarantine_codes = []
    pack_unreadable_codes = []
    if pack is not None:
        pack_issue_codes = sorted({issue.code for issue in pack.pack_issues})
        pack_quarantine_codes = sorted(
            {
                code
                for record in pack.observation_intake.quarantined
                for code in record.validation.issue_codes()
            }
        )
        pack_unreadable_codes = sorted({item.code for item in pack.unreadable})
    document = {
        "error_code": result.error_code,
        "pack_issue_codes": pack_issue_codes,
        "pack_quarantine_codes": pack_quarantine_codes,
        "pack_unreadable_codes": pack_unreadable_codes,
        "document_kind": "radar_v4.local_session_report",
        "pack_usable": bool(pack is not None and pack.usable()),
        "report_version": 1,
        "session": None
        if result.session is None
        else _loads_object(serialize_session_report(result.session)),
    }
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def write_session_report_file(path: str | Path, result: SessionResult) -> Path:
    return _write_report_file(path, serialize_session_report(result))


def write_local_session_report_file(
    path: str | Path, result: LocalSessionResult
) -> Path:
    return _write_report_file(path, serialize_local_session_report(result))


def _write_report_file(path: str | Path, text: str) -> Path:
    target = Path(path)
    if target.exists() and target.is_dir():
        raise SnapshotFileError(
            "SESSION_REPORT_PATH_IS_DIRECTORY",
            f"{target} is a directory, not a session report file",
        )
    target.write_text(text + "\n", encoding="utf-8")
    return target


def _loads_object(text: str) -> dict[str, object]:
    from json import loads

    parsed = loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("session report must be a JSON object")
    return parsed
