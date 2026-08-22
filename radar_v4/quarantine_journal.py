"""Export refusals as a journal. Not a repair log and not a method."""

from __future__ import annotations

from json import dumps
from pathlib import Path

from radar_v4.atomic_write import write_text_atomic
from radar_v4.local_session import LocalSessionResult
from radar_v4.session import SessionResult
from radar_v4.snapshot_files import SnapshotFileError


def serialize_quarantine_journal(
    session: SessionResult | None = None,
    local: LocalSessionResult | None = None,
) -> str:
    entries: list[dict[str, str | None]] = []
    if local is not None and local.pack is not None:
        for issue in local.pack.pack_issues:
            entries.append(
                {
                    "code": issue.code,
                    "field": issue.field,
                    "reason": issue.reason,
                    "source": "pack",
                }
            )
        for item in local.pack.unreadable:
            entries.append(
                {
                    "code": item.code,
                    "field": None,
                    "reason": item.reason,
                    "source": "pack_unreadable",
                }
            )
        for record in local.pack.observation_intake.quarantined:
            for issue in record.validation.issues:
                entries.append(
                    {
                        "code": issue.code,
                        "field": issue.field,
                        "reason": issue.reason,
                        "source": "pack_observation",
                    }
                )
        session = local.session if session is None else session
    if session is not None:
        for record in session.admission.quarantined:
            for issue in record.validation.issues:
                entries.append(
                    {
                        "code": issue.code,
                        "field": issue.field,
                        "reason": issue.reason,
                        "source": "admission",
                    }
                )
        for _item, validation in session.rejected_observations:
            for issue in validation.issues:
                entries.append(
                    {
                        "code": issue.code,
                        "field": issue.field,
                        "reason": issue.reason,
                        "source": "observation",
                    }
                )
        for issue in session.series.issues:
            entries.append(
                {
                    "code": issue.code,
                    "field": issue.field,
                    "reason": issue.reason,
                    "source": "series",
                }
            )
    entries.sort(key=lambda item: (item["source"] or "", item["code"] or "", item["reason"] or ""))
    return dumps(
        {"entries": entries, "refusal_count": len(entries)},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def write_quarantine_journal_file(
    path: str | Path,
    session: SessionResult | None = None,
    local: LocalSessionResult | None = None,
) -> Path:
    target = Path(path)
    if target.exists() and target.is_dir():
        raise SnapshotFileError(
            "QUARANTINE_JOURNAL_PATH_IS_DIRECTORY",
            f"{target} is a directory, not a quarantine journal file",
        )
    return write_text_atomic(
        target, serialize_quarantine_journal(session=session, local=local) + "\n"
    )
