"""Observation payload attached to an admitted envelope. Not a signal."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from json import dumps

from radar_v4.evidence import EvidenceEnvelope


@dataclass(frozen=True)
class ObservationPayload:
    close: str
    open: str | None = None
    high: str | None = None
    low: str | None = None
    volume: str | None = None

    def canonical_payload(self) -> dict[str, str | None]:
        return {
            "close": self.close,
            "high": self.high,
            "low": self.low,
            "open": self.open,
            "volume": self.volume,
        }

    def compute_checksum(self) -> str:
        encoded = dumps(
            self.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        return sha256(encoded).hexdigest()


@dataclass(frozen=True)
class Observation:
    envelope: EvidenceEnvelope
    payload: ObservationPayload
    payload_checksum: str

    @classmethod
    def create(
        cls, envelope: EvidenceEnvelope, payload: ObservationPayload
    ) -> Observation:
        return cls(
            envelope=envelope,
            payload=payload,
            payload_checksum=payload.compute_checksum(),
        )


def parse_decimal(value: str | None, field: str) -> Decimal | None:
    if value is None:
        return None
    if value.strip() == "":
        raise InvalidOperation(f"{field} is blank")
    return Decimal(value)
