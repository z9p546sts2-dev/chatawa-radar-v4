"""Export refusals as a journal. Not a repair log and not a method."""

from __future__ import annotations

from collections.abc import Mapping
from json import JSONDecodeError, dumps, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.local_session import LocalSessionResult
from radar_v4.session import SessionResult
from radar_v4.snapshot_files import SnapshotFileError

DOCUMENT_KIND = "radar_v4.quarantine_journal"


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
        {
            "document_kind": DOCUMENT_KIND,
            "entries": entries,
            "journal_version": 1,
            "refusal_count": len(entries),
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def write_quarantine_journal_file(
    path: str | Path,
    session: SessionResult | None = None,
    local: LocalSessionResult | None = None,
    replace: bool = False,
) -> Path:
    target = Path(path)
    if target.exists() and target.is_dir():
        raise SnapshotFileError(
            "QUARANTINE_JOURNAL_PATH_IS_DIRECTORY",
            f"{target} is a directory, not a quarantine journal file",
        )
    if file_exists_without_replace(target, replace):
        raise SnapshotFileError(
            "FILE_EXISTS",
            f"{target} already exists; pass replace=True to overwrite",
        )
    return write_text_atomic(
        target, serialize_quarantine_journal(session=session, local=local) + "\n"
    )


def read_quarantine_journal_file(path: str | Path) -> dict[str, object]:
    target = Path(path)
    if target.exists() and target.is_dir():
        raise SnapshotFileError(
            "QUARANTINE_JOURNAL_PATH_IS_DIRECTORY",
            f"{target} is a directory, not a quarantine journal file",
        )
    try:
        text = target.read_text(encoding="utf-8")
    except OSError as exc:
        raise SnapshotFileError(
            "UNREADABLE_JOURNAL",
            f"quarantine journal could not be read: {exc}",
        ) from exc
    try:
        raw = loads(text)
    except JSONDecodeError as exc:
        raise SnapshotFileError(
            "UNREADABLE_JOURNAL",
            f"quarantine journal is not readable JSON: {exc.msg}",
        ) from exc
    if not isinstance(raw, Mapping):
        raise SnapshotFileError(
            "UNREADABLE_JOURNAL",
            "quarantine journal must be a JSON object",
        )
    kind = raw.get("document_kind")
    if kind is not None and kind != DOCUMENT_KIND:
        raise SnapshotFileError(
            "UNREADABLE_JOURNAL",
            f"document_kind {kind!r} is not {DOCUMENT_KIND}",
        )
    return dict(raw)
