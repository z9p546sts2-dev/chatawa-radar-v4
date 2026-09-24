"""Parse observation JSON documents. No network. No repair.

Unreadable text is not converted into a fake observation. Parsed but
invalid observations are quarantined with their validation issues.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from json import JSONDecodeError, loads
from typing import Any

from radar_v4.evidence import EvidenceEnvelope
from radar_v4.json_intake import UnreadableDocument
from radar_v4.observation import Observation, ObservationPayload
from radar_v4.observation_validation import validate_observation
from radar_v4.validation import ValidationResult


@dataclass(frozen=True)
class ObservationIntakeRecord:
    observation: Observation
    validation: ValidationResult


@dataclass(frozen=True)
class ObservationIntakeReport:
    accepted: tuple[Observation, ...]
    quarantined: tuple[ObservationIntakeRecord, ...]
    unreadable: tuple[UnreadableDocument, ...]

    def accepted_count(self) -> int:
        return len(self.accepted)

    def quarantined_count(self) -> int:
        return len(self.quarantined)

    def unreadable_count(self) -> int:
        return len(self.unreadable)


def intake_observation_json(text: str) -> ObservationIntakeReport:
    """Parse one object or array of observation documents."""
    try:
        raw = loads(text)
    except JSONDecodeError as exc:
        return ObservationIntakeReport(
            accepted=(),
            quarantined=(),
            unreadable=(
                UnreadableDocument(
                    index=0,
                    raw=text,
                    code="UNREADABLE_JSON",
                    reason=f"JSON could not be parsed: {exc.msg}",
                ),
            ),
        )

    if isinstance(raw, Mapping):
        items: Sequence[Any] = (raw,)
    elif isinstance(raw, list):
        items = raw
    else:
        return ObservationIntakeReport(
            accepted=(),
            quarantined=(),
            unreadable=(
                UnreadableDocument(
                    index=0,
                    raw=text,
                    code="UNREADABLE_JSON",
                    reason="JSON root must be an object or an array of objects",
                ),
            ),
        )

    accepted: list[Observation] = []
    quarantined: list[ObservationIntakeRecord] = []
    unreadable: list[UnreadableDocument] = []
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            unreadable.append(
                UnreadableDocument(
                    index=index,
                    raw=repr(item),
                    code="UNREADABLE_ITEM",
                    reason="array item is not a JSON object",
                )
            )
            continue
        parsed = _parse_document(item)
        if isinstance(parsed, UnreadableDocument):
            unreadable.append(
                UnreadableDocument(
                    index=index,
                    raw=parsed.raw,
                    code=parsed.code,
                    reason=parsed.reason,
                )
            )
            continue
        validation = validate_observation(parsed)
        if validation.valid:
            accepted.append(parsed)
        else:
            quarantined.append(
                ObservationIntakeRecord(observation=parsed, validation=validation)
            )
    return ObservationIntakeReport(
        accepted=tuple(accepted),
        quarantined=tuple(quarantined),
        unreadable=tuple(unreadable),
    )


def _parse_document(item: Mapping[str, Any]) -> Observation | UnreadableDocument:
    if "envelope" not in item:
        return UnreadableDocument(
            index=0,
            raw=repr(item),
            code="MISSING_ENVELOPE",
            reason="observation document has no envelope",
        )
    if "payload" not in item:
        return UnreadableDocument(
            index=0,
            raw=repr(item),
            code="MISSING_PAYLOAD",
            reason="observation document has no payload",
        )

    envelope = _parse_envelope(item["envelope"])
    if isinstance(envelope, UnreadableDocument):
        return envelope

    payload_raw = item["payload"]
    if not isinstance(payload_raw, Mapping):
        return UnreadableDocument(
            index=0,
            raw=repr(payload_raw),
            code="PAYLOAD_NOT_JSON_OBJECT",
            reason="payload must be a JSON object",
        )
    # Preserve fixture shorthand, but never infer or discard parts of a
    # non-fixture market record while parsing it for review.
    strict = envelope.provenance_class not in {"FIXTURE", "SYNTHETIC"}
    if strict:
        extra = sorted(set(payload_raw) - {"close", "open", "high", "low", "volume"})
        if extra:
            return UnreadableDocument(
                index=0,
                raw=repr(payload_raw),
                code="EXTRA_PAYLOAD_KEY",
                reason=f"unsupported payload keys: {', '.join(extra)}",
            )
        for field in ("close", "open", "high", "low", "volume"):
            value = payload_raw.get(field)
            if value is not None and not isinstance(value, str):
                number = isinstance(value, (int, float)) and not isinstance(value, bool)
                return UnreadableDocument(
                    index=0,
                    raw=repr(payload_raw),
                    code="JSON_NUMBER_NOT_STRING" if number else "UNREADABLE_ITEM",
                    reason=f"{field} must be a decimal string",
                )
        if item.get("payload_checksum") is None:
            return UnreadableDocument(
                index=0,
                raw=repr(item),
                code="MISSING_PAYLOAD_CHECKSUM",
                reason="non-fixture observation requires a supplied payload checksum",
            )
    try:
        payload = ObservationPayload(
            close="" if payload_raw.get("close") is None else str(payload_raw.get("close")),
            open=_optional(payload_raw.get("open")),
            high=_optional(payload_raw.get("high")),
            low=_optional(payload_raw.get("low")),
            volume=_optional(payload_raw.get("volume")),
        )
    except (TypeError, ValueError) as exc:
        return UnreadableDocument(
            index=0,
            raw=repr(payload_raw),
            code="UNREADABLE_ITEM",
            reason=str(exc),
        )

    checksum = item.get("payload_checksum")
    if checksum is None:
        return Observation.create(envelope, payload)
    return Observation(
        envelope=envelope,
        payload=payload,
        payload_checksum=str(checksum),
    )


def _parse_envelope(raw: object) -> EvidenceEnvelope | UnreadableDocument:
    if isinstance(raw, Mapping):
        try:
            return EvidenceEnvelope.from_mapping(raw)
        except (TypeError, ValueError) as exc:
            return UnreadableDocument(
                index=0,
                raw=repr(raw),
                code="UNREADABLE_ITEM",
                reason=str(exc),
            )
    if isinstance(raw, str):
        try:
            return EvidenceEnvelope.deserialize(raw)
        except (TypeError, ValueError) as exc:
            reason = str(exc)
            code = (
                "ENVELOPE_NOT_JSON_OBJECT"
                if "must be a JSON object" in reason
                else "UNREADABLE_ITEM"
            )
            return UnreadableDocument(
                index=0,
                raw=raw,
                code=code,
                reason=reason,
            )
    return UnreadableDocument(
        index=0,
        raw=repr(raw),
        code="ENVELOPE_NOT_JSON_OBJECT",
        reason="envelope must be a JSON object or a serialized envelope string",
    )


def _optional(value: object) -> str | None:
    if value is None:
        return None
    return str(value)
