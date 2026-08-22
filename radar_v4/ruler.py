"""Measurement-ruler identity. Not a score and not a dataset nickname."""

from __future__ import annotations

from hashlib import sha256
from json import dumps

from radar_v4.dataset import DatasetDeclaration

RULER_FIELDS = (
    "provenance_class",
    "provider",
    "universe",
    "interval",
    "timezone",
    "transformation_version",
    "adjustment_policy",
    "locked_question",
    "primary_metric",
)


class RulerMismatchError(ValueError):
    def __init__(self, code: str, reason: str) -> None:
        self.code = code
        self.reason = reason
        super().__init__(reason)


def declaration_ruler(declaration: DatasetDeclaration) -> dict[str, str]:
    """Fields that make two datasets the same measurement ruler.

    dataset_id is a name, not the ruler. max_staleness is operational.
    """
    return {field: str(getattr(declaration, field)) for field in RULER_FIELDS}


def ruler_checksum(declaration: DatasetDeclaration) -> str:
    encoded = dumps(
        declaration_ruler(declaration),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def rulers_match(left: DatasetDeclaration, right: DatasetDeclaration) -> bool:
    return ruler_checksum(left) == ruler_checksum(right)


def require_ruler(declaration: DatasetDeclaration, expected: str) -> None:
    actual = ruler_checksum(declaration)
    if actual != expected:
        raise RulerMismatchError(
            "RULER_MISMATCH",
            f"declaration ruler {actual} does not match expected {expected}",
        )
