"""JSON document intake. Parse text into envelopes, then quarantine. No network."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from json import JSONDecodeError, loads
from typing import Any

from radar_v4.evidence import EvidenceEnvelope
from radar_v4.intake import IntakeRecord, intake_envelopes


@dataclass(frozen=True)
class UnreadableDocument:
    index: int
    raw: str
    code: str
    reason: str


@dataclass(frozen=True)
class DocumentIntakeReport:
    accepted: tuple[IntakeRecord, ...]
    quarantined: tuple[IntakeRecord, ...]
    unreadable: tuple[UnreadableDocument, ...]

    def accepted_count(self) -> int:
        return len(self.accepted)

    def quarantined_count(self) -> int:
        return len(self.quarantined)

    def unreadable_count(self) -> int:
        return len(self.unreadable)


def intake_json_text(text: str) -> DocumentIntakeReport:
    """Parse one JSON object or array of objects into an intake report.

    Unreadable JSON or non-object items are not converted into fake
    envelopes. Validly parsed but identity-invalid envelopes are
    quarantined by Build Unit 2.
    """
    try:
        raw = loads(text)
    except JSONDecodeError as exc:
        return DocumentIntakeReport(
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
        return DocumentIntakeReport(
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

    envelopes: list[EvidenceEnvelope] = []
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
        try:
            envelopes.append(EvidenceEnvelope.from_mapping(item))
        except (TypeError, ValueError) as exc:
            unreadable.append(
                UnreadableDocument(
                    index=index,
                    raw=repr(item),
                    code="UNREADABLE_ITEM",
                    reason=str(exc),
                )
            )

    report = intake_envelopes(envelopes)
    return DocumentIntakeReport(
        accepted=report.accepted,
        quarantined=report.quarantined,
        unreadable=tuple(unreadable),
    )
