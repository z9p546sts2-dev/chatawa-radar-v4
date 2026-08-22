"""Verify a snapshot together with optional sidecar files. No repair."""

from __future__ import annotations

from dataclasses import dataclass
from json import dumps
from pathlib import Path

from radar_v4.checksum_sidecar import sidecar_path, verify_checksum_sidecar
from radar_v4.ruler import ruler_checksum
from radar_v4.ruler_file import read_ruler_sidecar, ruler_sidecar_path
from radar_v4.snapshot_files import read_snapshot_file

DOCUMENT_KIND = "radar_v4.bundle_verification"


@dataclass(frozen=True)
class BundleVerification:
    snapshot_checksum: str
    ruler_checksum: str
    sidecar_present: bool
    ruler_present: bool
    sidecar_matched: bool | None
    ruler_matched: bool | None
    matched: bool
    issues: tuple[str, ...]

    def serialize(self) -> str:
        document = {
            "document_kind": DOCUMENT_KIND,
            "issues": list(self.issues),
            "matched": self.matched,
            "ruler_checksum": self.ruler_checksum,
            "ruler_matched": self.ruler_matched,
            "ruler_present": self.ruler_present,
            "sidecar_matched": self.sidecar_matched,
            "sidecar_present": self.sidecar_present,
            "snapshot_checksum": self.snapshot_checksum,
        }
        return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def verify_snapshot_bundle(
    snapshot_path: str | Path,
    require_sidecar: bool = False,
    require_ruler: bool = False,
) -> BundleVerification:
    """Check snapshot bytes against sidecar and ruler files when they exist.

    A missing sidecar or ruler is not a mismatch unless required.
    This does not invent, download, or repair files.
    """
    snapshot = read_snapshot_file(snapshot_path)
    issues: list[str] = []
    expected_ruler = ruler_checksum(snapshot.declaration)

    sidecar_file = sidecar_path(snapshot_path)
    sidecar_present = sidecar_file.is_file()
    sidecar_matched: bool | None
    if sidecar_present:
        sidecar_matched = bool(verify_checksum_sidecar(snapshot_path).matched)
        if sidecar_matched is False:
            issues.append("SNAPSHOT_CHECKSUM_MISMATCH")
    elif require_sidecar:
        sidecar_matched = False
        issues.append("BUNDLE_SIDECAR_MISSING")
    else:
        sidecar_matched = None

    ruler_file = ruler_sidecar_path(snapshot_path)
    ruler_present = ruler_file.is_file()
    ruler_matched: bool | None
    if ruler_present:
        recorded = read_ruler_sidecar(snapshot_path).get("ruler_checksum")
        ruler_matched = recorded == expected_ruler
        if ruler_matched is False:
            issues.append("BUNDLE_RULER_MISMATCH")
    elif require_ruler:
        ruler_matched = False
        issues.append("BUNDLE_RULER_MISSING")
    else:
        ruler_matched = None

    return BundleVerification(
        snapshot_checksum=snapshot.integrity_checksum(),
        ruler_checksum=expected_ruler,
        sidecar_present=sidecar_present,
        ruler_present=ruler_present,
        sidecar_matched=sidecar_matched,
        ruler_matched=ruler_matched,
        matched=len(issues) == 0,
        issues=tuple(issues),
    )
