"""Parse observation JSON documents. No network. No repair.

Unreadable text is not converted into a fake observation. Parsed but
invalid observations are quarantined with their validation issues.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from json import JSONDecodeError, loads
from typing import Any

from radar_v4.evidence import EvidenceEnvelope, format_canonical_timestamp
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


def summarize_observation_intake(report: ObservationIntakeReport) -> dict[str, Any]:
    """Read-only coverage and refusal summary. No calendar or freshness claim."""
    groups: dict[tuple[str, ...], dict[str, Any]] = {}
    for item in report.accepted:
        envelope = item.envelope
        key = (
            envelope.provenance_class or "",
            envelope.provider or "",
            envelope.symbol_or_universe or "",
            envelope.interval or "",
            envelope.timezone or "",
            envelope.transformation_version or "",
        )
        if key not in groups:
            groups[key] = {
                "provenance_class": key[0],
                "provider": key[1],
                "symbol_or_universe": key[2],
                "interval": key[3],
                "timezone": key[4],
                "transformation_version": key[5],
                "observations": 0,
                "missing_fields": {"open": 0, "high": 0, "low": 0, "volume": 0},
                "market_timestamps": [],
            }
        group = groups[key]
        group["observations"] += 1
        for field in ("open", "high", "low", "volume"):
            if getattr(item.payload, field) is None:
                group["missing_fields"][field] += 1
        assert envelope.market_timestamp is not None  # accepted observations are valid
        group["market_timestamps"].append(envelope.market_timestamp)

    summaries = []
    for key in sorted(groups):
        group = groups[key]
        timestamps = sorted(group["market_timestamps"])
        group["market_timestamps"] = [
            format_canonical_timestamp(timestamp) for timestamp in timestamps
        ]
        group["repeated_market_timestamps"] = len(timestamps) - len(set(timestamps))
        summaries.append(group)

    refusal_codes: Counter[str] = Counter()
    for item in report.quarantined:
        refusal_codes.update(item.validation.issue_codes())
    refusal_codes.update(item.code for item in report.unreadable)
    return {
        "document_kind": "radar_v4.observation",
        "accepted": report.accepted_count(),
        "quarantined": report.quarantined_count(),
        "unreadable": report.unreadable_count(),
        "intake_clean": (
            bool(report.accepted)
            and not report.quarantined
            and not report.unreadable
            and all(group["repeated_market_timestamps"] == 0 for group in summaries)
        ),
        "groups": summaries,
        "refusal_codes": dict(sorted(refusal_codes.items())),
    }
