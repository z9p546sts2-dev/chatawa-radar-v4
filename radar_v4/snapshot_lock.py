"""Snapshot identity checks. Not market evidence."""

from __future__ import annotations

from json import JSONDecodeError, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.fixture_pack import PACK_ALLOWED_PROVENANCE
from radar_v4.integrity import IntegrityCheck
from radar_v4.local_session import run_session_from_pack
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


def _load_object(path: Path, kind: str, code: str) -> tuple[dict[str, object] | None, IntegrityCheck | None]:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return None, IntegrityCheck(
            kind,
            False,
            code,
            ("unreadable snapshot",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return None, IntegrityCheck(
            kind,
            False,
            code,
            ("snapshot is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return None, IntegrityCheck(
            kind,
            False,
            code,
            ("snapshot must be an object",),
            {"path": str(target)},
        )
    return raw, None


def _snapshot_parts(raw: dict[str, object], source: str) -> list[IntegrityCheck]:
    declaration = raw.get("declaration")
    observations = raw.get("observations")
    shape_ok = isinstance(declaration, dict) and isinstance(observations, list)
    parts = [
        IntegrityCheck(
            "radar_v4.snapshot_shape",
            shape_ok,
            None if shape_ok else "SNAPSHOT_SHAPE_REFUSED",
            (
                ("Snapshot has declaration and observations.",)
                if shape_ok
                else ("A snapshot must have a declaration object and observations array.",)
            ),
            {"path": source},
        )
    ]
    if not shape_ok:
        return parts
    assert isinstance(observations, list)
    if not observations:
        parts.append(
            IntegrityCheck(
                "radar_v4.snapshot_empty",
                False,
                "SNAPSHOT_EMPTY_REFUSED",
                ("An empty observation list is not a locked snapshot.",),
                {"path": source},
            )
        )
    else:
        hits = []
        for index, item in enumerate(observations):
            if not isinstance(item, dict) or "envelope" not in item or "payload" not in item:
                hits.append(index)
        parts.append(
            IntegrityCheck(
                "radar_v4.snapshot_rows",
                not hits,
                None if not hits else "SNAPSHOT_SHAPE_REFUSED",
                (
                    ("Observation rows carry envelope and payload.",)
                    if not hits
                    else ("An observation row is missing envelope or payload.",)
                ),
                {"hits": hits, "path": source},
            )
        )
    provenance = declaration.get("provenance_class") if isinstance(declaration, dict) else None
    allowed = provenance in PACK_ALLOWED_PROVENANCE
    parts.append(
        IntegrityCheck(
            "radar_v4.snapshot_provenance",
            allowed,
            None if allowed else "SNAPSHOT_PROVENANCE_REFUSED",
            (
                ("Snapshot provenance is FIXTURE or SYNTHETIC.",)
                if allowed
                else ("HISTORICAL or LIVE snapshots are not locked as workshop evidence.",)
            ),
            {"path": source, "provenance": provenance},
        )
    )
    return parts


def _compose(raw: dict[str, object], source: str) -> IntegrityCheck:
    parts = _snapshot_parts(raw, source)
    failed = [part for part in parts if not part.valid]
    if failed:
        first = failed[0]
        return IntegrityCheck(
            "radar_v4.snapshot_lock",
            False,
            first.error_code,
            ("Snapshot lock failed.",) + first.notes,
            {"failed": [part.document_kind for part in failed]},
        )
    return IntegrityCheck(
        "radar_v4.snapshot_lock",
        True,
        None,
        ("Snapshot lock passed. Not market evidence.",),
        {"failed": []},
    )


def snapshot_lock(path: Path) -> IntegrityCheck:
    raw, error = _load_object(path, "radar_v4.snapshot_readable", "UNREADABLE_SNAPSHOT_FILE")
    if error is not None:
        return IntegrityCheck(
            "radar_v4.snapshot_lock",
            False,
            error.error_code,
            ("Snapshot lock failed.",) + error.notes,
            {"failed": [error.document_kind]},
        )
    assert raw is not None
    return _compose(raw, str(path))


def pack_snapshot_lock(directory: Path) -> IntegrityCheck:
    result = run_session_from_pack(directory)
    if result.session is None:
        return IntegrityCheck(
            "radar_v4.snapshot_lock",
            False,
            result.error_code or "PACK_NOT_USABLE",
            ("Snapshot lock needs a usable pack.",),
            {"failed": []},
        )
    raw = loads(result.session.snapshot.serialize())
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.snapshot_lock",
            False,
            "UNREADABLE_SNAPSHOT_FILE",
            ("Serialized snapshot is not an object.",),
            {"failed": []},
        )
    return _compose(raw, str(directory))


def snapshot_lock_any(target: Path) -> IntegrityCheck:
    path = Path(target)
    if path.is_dir():
        return pack_snapshot_lock(path)
    return snapshot_lock(path)


def snapshot_lock_determinism(target: Path) -> IntegrityCheck:
    first = snapshot_lock_any(target)
    second = snapshot_lock_any(target)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.snapshot_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Snapshot lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def compare_snapshot_lock(left: Path, right: Path) -> IntegrityCheck:
    first = snapshot_lock_any(left)
    second = snapshot_lock_any(right)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.compare_snapshot_lock",
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared snapshot-lock records. Equality is not market evidence.",),
        {"equal": equal},
    )


def write_snapshot_record(
    target: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = snapshot_lock_any(target)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_snapshot_record(path: Path) -> IntegrityCheck:
    target = Path(path)
    try:
        raw = loads(target.read_text(encoding="utf-8"))
    except OSError:
        return IntegrityCheck(
            "radar_v4.snapshot_verify",
            False,
            "UNREADABLE_JSON",
            ("unreadable snapshot-lock record",),
            {"path": str(target)},
        )
    except JSONDecodeError:
        return IntegrityCheck(
            "radar_v4.snapshot_verify",
            False,
            "UNREADABLE_JSON",
            ("snapshot-lock record is not JSON",),
            {"path": str(target)},
        )
    if not isinstance(raw, dict):
        return IntegrityCheck(
            "radar_v4.snapshot_verify",
            False,
            "UNREADABLE_JSON",
            ("snapshot-lock record must be an object",),
            {"path": str(target)},
        )
    ok = raw.get("document_kind") == "radar_v4.snapshot_lock" and raw.get("valid") is True
    return IntegrityCheck(
        "radar_v4.snapshot_verify",
        ok,
        None if ok else "SNAPSHOT_RECORD_INVALID",
        ("Verified a local snapshot-lock record. Not market evidence.",),
        {"path": str(target)},
    )


def snapshot_status_bind(target: Path) -> IntegrityCheck:
    locked = snapshot_lock_any(target)
    status = loads(workshop_status())
    status_unit = int(status.get("highest_unit") or 0)
    matched = (
        locked.valid
        and status_unit == PHASE5_HIGHEST_UNIT
        and status.get("measured") is False
    )
    return IntegrityCheck(
        "radar_v4.snapshot_status_bind",
        matched,
        None if matched else "SNAPSHOT_STATUS_MISMATCH",
        ("Snapshot lock and status share the locked unit. Not a measurement.",),
        {
            "locked_unit": PHASE5_HIGHEST_UNIT,
            "snapshot_valid": locked.valid,
            "status_unit": status_unit,
        },
    )
