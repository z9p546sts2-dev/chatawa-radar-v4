"""Bind pack, snapshot, report, journal, and filesystem identities."""

from __future__ import annotations

from dataclasses import dataclass
from json import dumps
from pathlib import Path

from radar_v4.dataset_pack import load_dataset_pack
from radar_v4.pack_inventory import inventory_pack
from radar_v4.pack_manifest import PackManifestError, read_pack_manifest
from radar_v4.quarantine_journal import read_quarantine_journal_file
from radar_v4.ruler import ruler_checksum
from radar_v4.session_report import read_session_report_file
from radar_v4.snapshot_files import SnapshotFileError, read_snapshot_file


def _dump(document: dict[str, object]) -> str:
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


@dataclass(frozen=True)
class ChainCheck:
    matched: bool
    error_code: str | None
    notes: tuple[str, ...]
    details: dict[str, object]

    def serialize(self) -> str:
        return _dump(
            {
                "details": self.details,
                "document_kind": "radar_v4.evidence_chain",
                "error_code": self.error_code,
                "matched": self.matched,
                "notes": list(self.notes),
            }
        )


def _session_from_report(document: dict[str, object]) -> dict[str, object] | None:
    session = document.get("session")
    if isinstance(session, dict):
        return session
    if document.get("document_kind") == "radar_v4.session_report":
        return document
    return None


def bind_declaration_to_snapshot(directory: str | Path, snapshot_path: str | Path) -> ChainCheck:
    pack = load_dataset_pack(directory)
    snapshot = read_snapshot_file(snapshot_path)
    if pack.declaration is None:
        return ChainCheck(
            False,
            "CHAIN_MISMATCH",
            ("pack has no usable declaration",),
            {},
        )
    left = ruler_checksum(pack.declaration)
    right = ruler_checksum(snapshot.declaration)
    matched = left == right
    return ChainCheck(
        matched,
        None if matched else "CHAIN_MISMATCH",
        ("ruler identity is not dataset_id",),
        {"pack_ruler": left, "snapshot_ruler": right},
    )


def bind_pack_to_snapshot(directory: str | Path, snapshot_path: str | Path) -> ChainCheck:
    pack = load_dataset_pack(directory)
    snapshot = read_snapshot_file(snapshot_path)
    pack_ids = sorted(
        item.envelope.identity_key() for item in pack.observation_intake.accepted
    )
    snap_ids = sorted(item.envelope.identity_key() for item in snapshot.observations)
    matched = pack_ids == snap_ids
    return ChainCheck(
        matched,
        None if matched else "CHAIN_MISMATCH",
        ("membership compare does not measure close-to-close",),
        {
            "pack_identities": pack_ids,
            "snapshot_identities": snap_ids,
        },
    )


def bind_report_chain(
    directory: str | Path, snapshot_path: str | Path, report_path: str | Path
) -> ChainCheck:
    snapshot = read_snapshot_file(snapshot_path)
    document = read_session_report_file(report_path)
    session = _session_from_report(document)
    pack = load_dataset_pack(directory)
    claimed = None if session is None else session.get("snapshot_checksum")
    actual = snapshot.integrity_checksum()
    ruler = None if pack.declaration is None else ruler_checksum(pack.declaration)
    reported_ruler = None if session is None else session.get("ruler_checksum")
    matched = claimed == actual and ruler == reported_ruler and ruler is not None
    return ChainCheck(
        matched,
        None if matched else "CHAIN_MISMATCH",
        (
            "report, snapshot, and pack ruler must agree",
            "agreement is not market evidence",
        ),
        {
            "claimed_snapshot": claimed,
            "pack_ruler": ruler,
            "reported_ruler": reported_ruler,
            "snapshot_checksum": actual,
        },
    )


def three_way_pack(directory: str | Path) -> ChainCheck:
    """Filesystem JSON names vs inventory vs manifest keys."""
    root = Path(directory)
    inventory = inventory_pack(root)
    if not inventory.present:
        return ChainCheck(False, "UNREADABLE_PACK", ("pack is not a directory",), {})
    filesystem = sorted(
        path.name
        for path in root.iterdir()
        if path.is_file()
        and path.suffix == ".json"
        and path.name != "manifest.json"
        and (
            path.name == "declaration.json"
            or path.name not in {"snapshot.json", "session_report.json", "journal.json", "registry.json", "quarantine.json", "ruler.json"}
        )
    )
    inventoried = sorted(
        item.name
        for item in inventory.files
        if item.role in {"declaration", "observation"}
    )
    try:
        manifest = read_pack_manifest(root)
        manifested = sorted(manifest.files)
    except PackManifestError as exc:
        return ChainCheck(
            False,
            exc.code,
            ("manifest could not be read",),
            {"filesystem": filesystem, "inventory": inventoried},
        )
    matched = filesystem == inventoried == manifested
    return ChainCheck(
        matched,
        None if matched else "THREE_WAY_MISMATCH",
        ("three-way compare does not repair files",),
        {
            "filesystem": filesystem,
            "inventory": inventoried,
            "manifest": manifested,
        },
    )


def reconcile_journal_to_pack(directory: str | Path, journal_path: str | Path) -> ChainCheck:
    pack = load_dataset_pack(directory)
    document = read_quarantine_journal_file(journal_path)
    entries = document.get("entries")
    journal_codes = sorted(
        {
            str(item.get("code"))
            for item in entries
            if isinstance(item, dict) and item.get("code")
        }
    ) if isinstance(entries, list) else []
    pack_codes = sorted(
        {
            code
            for record in pack.observation_intake.quarantined
            for code in record.validation.issue_codes()
        }
        | {issue.code for issue in pack.pack_issues}
    )
    # A journal may record a subset written at a different time. Require
    # every journal code to exist in the current pack refusals, or both empty.
    extra = sorted(set(journal_codes) - set(pack_codes))
    matched = not extra
    return ChainCheck(
        matched,
        None if matched else "JOURNAL_PACK_MISMATCH",
        (
            "journal codes must still be present in the pack refusals",
            "this does not rewrite the journal",
        ),
        {"journal_codes": journal_codes, "pack_codes": pack_codes, "extra": extra},
    )


def inspect_evidence_chain(
    directory: str | Path,
    snapshot_path: str | Path | None = None,
    report_path: str | Path | None = None,
) -> ChainCheck:
    notes = ("chain inspect does not measure a new question",)
    if snapshot_path is None and report_path is None:
        three = three_way_pack(directory)
        return ChainCheck(three.matched, three.error_code, notes + three.notes, three.details)
    if snapshot_path is not None and report_path is not None:
        return bind_report_chain(directory, snapshot_path, report_path)
    if snapshot_path is not None:
        declaration = bind_declaration_to_snapshot(directory, snapshot_path)
        membership = bind_pack_to_snapshot(directory, snapshot_path)
        matched = declaration.matched and membership.matched
        return ChainCheck(
            matched,
            None if matched else "CHAIN_MISMATCH",
            notes,
            {
                "declaration": _loads(declaration.serialize()),
                "membership": _loads(membership.serialize()),
            },
        )
    try:
        read_session_report_file(report_path)  # type: ignore[arg-type]
    except SnapshotFileError as exc:
        return ChainCheck(False, exc.code, notes, {})
    return ChainCheck(
        False,
        "CHAIN_MISMATCH",
        notes + ("a report chain also needs a snapshot",),
        {},
    )


def _loads(text: str) -> dict[str, object]:
    from json import loads

    parsed = loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("expected a JSON object")
    return parsed
