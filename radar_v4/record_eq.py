"""Record equality and count binds. Not market evidence."""

from __future__ import annotations

from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.freeze import workshop_freeze
from radar_v4.integrity import IntegrityCheck, verify_recomputed_lock_record
from radar_v4.local_session import run_session_from_pack
from radar_v4.name_lock import name_lock
from radar_v4.pack_describe import pack_readiness
from radar_v4.path_lock import path_lock
from radar_v4.snapshot_files import SnapshotFileError
from radar_v4.workshop_record import package_source_identity


def path_lock_determinism(directory: Path) -> IntegrityCheck:
    first = path_lock(directory)
    second = path_lock(directory)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.path_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Path lock ran twice. Equality is not a method.",),
        {"equal": equal, "valid": first.valid},
    )


def freeze_determinism(directory: Path | None = None) -> IntegrityCheck:
    first = workshop_freeze(directory)
    second = workshop_freeze(directory)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.freeze_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Freeze ran twice. Equality is not a research result.",),
        {"equal": equal, "valid": first.valid},
    )


def name_lock_determinism(directory: Path) -> IntegrityCheck:
    first = name_lock(directory)
    second = name_lock(directory)
    equal = first.serialize() == second.serialize()
    return IntegrityCheck(
        "radar_v4.name_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Name lock ran twice. Equality is not market evidence.",),
        {"equal": equal, "valid": first.valid},
    )


def package_identity_determinism() -> IntegrityCheck:
    first = package_source_identity()
    second = package_source_identity()
    equal = first == second
    return IntegrityCheck(
        "radar_v4.package_determinism",
        equal,
        None if equal else "DETERMINISM_MISMATCH",
        ("Package identity hashed twice. This is software identity, not a market.",),
        {"equal": equal},
    )


def compare_path_lock(left_dir: Path, right_dir: Path) -> IntegrityCheck:
    left = path_lock(left_dir)
    right = path_lock(right_dir)
    equal = left.serialize() == right.serialize()
    return IntegrityCheck(
        "radar_v4.compare_path_lock",
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared path-lock records. Equality is not a method.",),
        {"equal": equal},
    )


def snapshot_count_bind(directory: Path) -> IntegrityCheck:
    readiness = pack_readiness(directory)
    result = run_session_from_pack(directory)
    if result.session is None:
        return IntegrityCheck(
            "radar_v4.snapshot_count",
            False,
            result.error_code or "PACK_NOT_USABLE",
            ("Snapshot count bind needs a usable pack.",),
            {},
        )
    kept = result.session.kept_observation_count()
    matched = kept == readiness.admitted_observations
    return IntegrityCheck(
        "radar_v4.snapshot_count",
        matched,
        None if matched else "COUNT_MISMATCH",
        ("Snapshot kept count must match declaration-admitted count.",),
        {
            "admitted": readiness.admitted_observations,
            "kept": kept,
        },
    )


def write_path_record(
    directory: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = path_lock(directory)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_path_record(path: Path) -> IntegrityCheck:
    return verify_recomputed_lock_record(
        path,
        expected_kind="radar_v4.path_lock",
        verify_kind="radar_v4.path_verify",
        invalid_code="PATH_RECORD_INVALID",
        recompute=path_lock,
    )


def write_name_record(
    directory: Path, destination: Path, replace: bool = False
) -> IntegrityCheck:
    if file_exists_without_replace(destination, replace):
        raise SnapshotFileError("FILE_EXISTS", f"{destination} already exists")
    record = name_lock(directory)
    write_text_atomic(destination, record.serialize() + "\n")
    return record


def verify_name_record(path: Path) -> IntegrityCheck:
    return verify_recomputed_lock_record(
        path,
        expected_kind="radar_v4.name_lock",
        verify_kind="radar_v4.name_verify",
        invalid_code="NAME_RECORD_INVALID",
        recompute=name_lock,
    )


def compare_name_lock(left_dir: Path, right_dir: Path) -> IntegrityCheck:
    left = name_lock(left_dir)
    right = name_lock(right_dir)
    equal = left.serialize() == right.serialize()
    return IntegrityCheck(
        "radar_v4.compare_name_lock",
        equal,
        None if equal else "RECORD_MISMATCH",
        ("Compared name-lock records. Equality is not a method.",),
        {"equal": equal},
    )
