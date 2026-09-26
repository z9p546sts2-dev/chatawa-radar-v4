"""Offline custody for one supplied completed-session observation.

This route preserves files for human review. It does not qualify a source,
admit a dataset, fetch market data, or execute a market method.
"""

from __future__ import annotations

import os
import shutil
import stat
import tempfile
from hashlib import sha256
from json import dumps
from pathlib import Path
from uuid import uuid4

from radar_v4.evidence import format_canonical_timestamp
from radar_v4.observation_json import intake_observation_json


class ManualObservationError(ValueError):
    def __init__(self, code: str, reason: str) -> None:
        self.code = code
        self.reason = reason
        super().__init__(reason)


def prepare_manual_observation(
    observation_path: str | Path,
    raw_path: str | Path,
    custody_root: str | Path,
) -> Path:
    """Copy one declared observation and its raw file into private, new custody."""
    repository = Path(__file__).resolve().parents[1]
    root = Path(custody_root)
    if root.is_symlink() or not root.is_dir():
        raise ManualObservationError("PRIVATE_ROOT_REQUIRED", "use an existing private directory")
    resolved_root = root.resolve()
    if _inside_repository(resolved_root, repository):
        raise ManualObservationError("PUBLIC_PATH_REFUSED", "custody directory is inside the repository")
    if os.name != "nt" and stat.S_IMODE(root.stat().st_mode) & 0o077:
        raise ManualObservationError("PRIVATE_ROOT_REQUIRED", "custody directory must be owner-only")
    if Path(observation_path).resolve() == Path(raw_path).resolve():
        raise ManualObservationError("INVALID_OBSERVATION", "raw and observation inputs must be separate files")
    try:
        if Path(observation_path).samefile(raw_path):
            raise ManualObservationError(
                "INVALID_OBSERVATION", "raw and observation inputs must be separate files"
            )
    except OSError:
        # The input reader below reports a missing or unreadable file.
        pass

    observation_bytes = _read_private_input(observation_path, repository)
    raw_bytes = _read_private_input(raw_path, repository)
    try:
        report = intake_observation_json(observation_bytes.decode("utf-8"))
    except UnicodeError as exc:
        raise ManualObservationError("INVALID_OBSERVATION", "observation is not UTF-8") from exc
    if report.accepted_count() != 1 or report.quarantined or report.unreadable:
        raise ManualObservationError("INVALID_OBSERVATION", "supply exactly one valid observation")
    observation = report.accepted[0]
    envelope = observation.envelope
    if envelope.provenance_class != "HISTORICAL" or envelope.interval != "1d":
        raise ManualObservationError(
            "OBSERVATION_NOT_ADMITTED",
            "manual preparation requires one HISTORICAL 1d completed-session record",
        )
    assert envelope.market_timestamp is not None
    assert envelope.retrieval_timestamp is not None
    if envelope.retrieval_timestamp < envelope.market_timestamp:
        raise ManualObservationError(
            "RETRIEVAL_BEFORE_MARKET", "retrieval precedes the declared market timestamp"
        )

    receipt = {
        "document_kind": "radar_v4.manual_observation_receipt",
        "review_status": "pending_source_review",
        "provenance_class": envelope.provenance_class,
        "provider": envelope.provider,
        "symbol_or_universe": envelope.symbol_or_universe,
        "interval": envelope.interval,
        "timezone": envelope.timezone,
        "transformation_version": envelope.transformation_version,
        "market_timestamp": format_canonical_timestamp(envelope.market_timestamp),
        "retrieval_timestamp": format_canonical_timestamp(envelope.retrieval_timestamp),
        "envelope_checksum": envelope.checksum,
        "payload_checksum": observation.payload_checksum,
        "raw_sha256": sha256(raw_bytes).hexdigest(),
        "observation_sha256": sha256(observation_bytes).hexdigest(),
    }
    temporary: Path | None = None
    try:
        temporary = Path(tempfile.mkdtemp(prefix=".observation-", dir=resolved_root))
        _write_private(temporary / "raw.bin", raw_bytes)
        _write_private(temporary / "observation.json", observation_bytes)
        _write_private(
            temporary / "receipt.json",
            (dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8"),
        )
        target = resolved_root / (
            envelope.market_timestamp.date().isoformat() + "-" + uuid4().hex
        )
        if target.exists():
            raise ManualObservationError("FILE_EXISTS", "custody receipt already exists")
        temporary.rename(target)
        return target / "receipt.json"
    except OSError as exc:
        if temporary is not None:
            shutil.rmtree(temporary, ignore_errors=True)
        raise ManualObservationError(
            "CUSTODY_WRITE_FAILED", "private custody could not be written"
        ) from exc
    except BaseException:
        if temporary is not None:
            shutil.rmtree(temporary, ignore_errors=True)
        raise


def _read_private_input(path: str | Path, repository: Path) -> bytes:
    candidate = Path(path)
    if (
        candidate.is_symlink()
        or not candidate.is_file()
        or _inside_repository(candidate.resolve(), repository)
    ):
        raise ManualObservationError("PUBLIC_PATH_REFUSED", "input must be a regular file outside the repository")
    try:
        data = candidate.read_bytes()
    except OSError as exc:
        raise ManualObservationError("UNREADABLE_ITEM", "input file could not be read") from exc
    if not data:
        raise ManualObservationError("UNREADABLE_ITEM", "input file is empty")
    return data


def _write_private(path: Path, data: bytes) -> None:
    with path.open("xb") as stream:
        os.chmod(path, 0o600)
        stream.write(data)


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _inside_repository(path: Path, project_root: Path) -> bool:
    return _inside(path, project_root) or any(
        (parent / ".git").exists() for parent in (path, *path.parents)
    )
