"""Read and write the in-memory registry on the local filesystem only."""

from __future__ import annotations

from collections.abc import Mapping
from json import JSONDecodeError, dumps, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic
from radar_v4.evidence import EvidenceEnvelope
from radar_v4.intake import IntakeRecord
from radar_v4.registry import EvidenceRegistry
from radar_v4.validation import ValidationIssue, ValidationResult

DOCUMENT_KIND = "radar_v4.registry"


class RegistryFileError(ValueError):
    def __init__(self, code: str, reason: str) -> None:
        self.code = code
        self.reason = reason
        super().__init__(reason)


def write_registry_file(
    path: str | Path, registry: EvidenceRegistry, replace: bool = False
) -> Path:
    target = Path(path)
    if target.exists() and target.is_dir():
        raise RegistryFileError(
            "REGISTRY_PATH_IS_DIRECTORY",
            f"{target} is a directory, not a registry file",
        )
    if file_exists_without_replace(target, replace):
        raise RegistryFileError(
            "FILE_EXISTS",
            f"{target} already exists; pass replace=True to overwrite",
        )
    document = {
        "document_kind": DOCUMENT_KIND,
        "registry_version": 1,
        "accepted": [item.serialize() for item in registry.accepted_envelopes()],
        "quarantined": [
            {
                "envelope": record.envelope.serialize(),
                "issues": [
                    {
                        "code": issue.code,
                        "field": issue.field,
                        "reason": issue.reason,
                    }
                    for issue in record.validation.issues
                ],
            }
            for record in registry.quarantined_records()
        ],
    }
    return write_text_atomic(
        target,
        dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n",
    )


def read_registry_file(path: str | Path) -> EvidenceRegistry:
    target = Path(path)
    if target.exists() and target.is_dir():
        raise RegistryFileError(
            "REGISTRY_PATH_IS_DIRECTORY",
            f"{target} is a directory, not a registry file",
        )
    try:
        text = target.read_text(encoding="utf-8")
    except OSError as exc:
        raise RegistryFileError(
            "UNREADABLE_REGISTRY_FILE",
            f"registry file could not be read: {exc}",
        ) from exc
    try:
        raw = loads(text)
    except JSONDecodeError as exc:
        raise RegistryFileError(
            "UNREADABLE_REGISTRY_FILE",
            f"registry file is not readable JSON: {exc.msg}",
        ) from exc
    if not isinstance(raw, Mapping):
        raise RegistryFileError(
            "UNREADABLE_REGISTRY_FILE",
            "registry file must be a JSON object",
        )
    kind = raw.get("document_kind")
    if kind is not None and kind != DOCUMENT_KIND:
        raise RegistryFileError(
            "UNREADABLE_REGISTRY_FILE",
            f"document_kind {kind!r} is not {DOCUMENT_KIND}",
        )
    registry = EvidenceRegistry()
    accepted_raw = raw.get("accepted")
    if accepted_raw is None:
        accepted_raw = []
    if not isinstance(accepted_raw, list):
        raise RegistryFileError(
            "UNREADABLE_REGISTRY_FILE",
            "registry accepted must be an array",
        )
    envelopes: list[EvidenceEnvelope] = []
    for item in accepted_raw:
        try:
            envelopes.append(EvidenceEnvelope.deserialize(str(item)))
        except (TypeError, ValueError) as exc:
            raise RegistryFileError(
                "UNREADABLE_REGISTRY_FILE",
                f"accepted envelope is unreadable: {exc}",
            ) from exc
    registry.put(envelopes)

    quarantined_raw = raw.get("quarantined")
    if quarantined_raw is None:
        quarantined_raw = []
    if not isinstance(quarantined_raw, list):
        raise RegistryFileError(
            "UNREADABLE_REGISTRY_FILE",
            "registry quarantined must be an array",
        )
    restored: list[IntakeRecord] = []
    for item in quarantined_raw:
        if not isinstance(item, Mapping):
            raise RegistryFileError(
                "UNREADABLE_REGISTRY_FILE",
                "quarantined item must be an object",
            )
        try:
            envelope = EvidenceEnvelope.deserialize(str(item["envelope"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise RegistryFileError(
                "UNREADABLE_REGISTRY_FILE",
                f"quarantined envelope is unreadable: {exc}",
            ) from exc
        issues_raw = item.get("issues")
        if issues_raw is None:
            issues_raw = []
        if not isinstance(issues_raw, list):
            raise RegistryFileError(
                "UNREADABLE_REGISTRY_FILE",
                "quarantined issues must be an array",
            )
        issues: list[ValidationIssue] = []
        for issue in issues_raw:
            if not isinstance(issue, Mapping):
                raise RegistryFileError(
                    "UNREADABLE_REGISTRY_FILE",
                    "quarantined issue must be an object",
                )
            issues.append(
                ValidationIssue(
                    code=str(issue.get("code") or "UNREADABLE_ITEM"),
                    reason=str(issue.get("reason") or ""),
                    field=None if issue.get("field") is None else str(issue.get("field")),
                )
            )
        restored.append(
            IntakeRecord(
                envelope=envelope,
                validation=ValidationResult(valid=False, issues=tuple(issues)),
            )
        )
    registry.record_quarantine(restored)
    return registry
