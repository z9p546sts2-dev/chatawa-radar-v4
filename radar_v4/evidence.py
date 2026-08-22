"""Evidence envelope: identity and provenance, not market interpretation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone as dt_timezone
from enum import Enum
from hashlib import sha256
from json import dumps, loads
from typing import Any, Mapping
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

ALLOWED_PROVENANCE_CLASSES = frozenset(
    {
        "LIVE",
        "HISTORICAL",
        "BACKFILL",
        "SYNTHETIC",
        "FIXTURE",
        "REPLAY",
        "MANUALLY_EDITED",
    }
)

CANONICAL_HASH_FIELDS = (
    "provenance_class",
    "provider",
    "symbol_or_universe",
    "market_timestamp",
    "retrieval_timestamp",
    "interval",
    "timezone",
    "transformation_version",
    "context_decision_use_tag",
)

SERIALIZATION_RULES = (
    "JSON object with sorted keys and compact separators (',', ':').",
    "Timestamps are timezone-aware ISO-8601 with microseconds and numeric offset.",
    "Omitted optional context_decision_use_tag is JSON null.",
    "Checksum is excluded from the hashed canonical payload.",
    "No timezone is assumed. Missing timezone is not replaced with UTC.",
)


class ProvenanceClass(str, Enum):
    LIVE = "LIVE"
    HISTORICAL = "HISTORICAL"
    BACKFILL = "BACKFILL"
    SYNTHETIC = "SYNTHETIC"
    FIXTURE = "FIXTURE"
    REPLAY = "REPLAY"
    MANUALLY_EDITED = "MANUALLY_EDITED"


def format_canonical_timestamp(value: datetime) -> str:
    """Serialize a timezone-aware datetime to a stable ISO-8601 string."""
    return value.isoformat(timespec="microseconds")


def parse_canonical_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("canonical timestamp must include timezone offset")
    return parsed


def _canonical_timestamp_or_none(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime) and value.tzinfo is not None:
        return format_canonical_timestamp(value)
    return None


def _json_ready(value: object) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return None
        return format_canonical_timestamp(value)
    return str(value)


@dataclass(frozen=True)
class EvidenceEnvelope:
    """Identity record for later research evidence.

    The optional context_decision_use_tag is metadata only. Build Unit 1
    attaches no market, ranking, or decision behavior to it.
    """

    provenance_class: str | None
    provider: str | None
    symbol_or_universe: str | None
    market_timestamp: datetime | None
    retrieval_timestamp: datetime | None
    interval: str | None
    timezone: str | None
    transformation_version: str | None
    checksum: str | None = None
    context_decision_use_tag: str | None = None

    @classmethod
    def create(
        cls,
        *,
        provenance_class: ProvenanceClass | str,
        provider: str,
        symbol_or_universe: str,
        market_timestamp: datetime,
        retrieval_timestamp: datetime,
        interval: str,
        timezone: str,
        transformation_version: str,
        context_decision_use_tag: str | None = None,
    ) -> EvidenceEnvelope:
        """Build an envelope and generate its integrity checksum."""
        unsigned = cls(
            provenance_class=str(provenance_class),
            provider=provider,
            symbol_or_universe=symbol_or_universe,
            market_timestamp=market_timestamp,
            retrieval_timestamp=retrieval_timestamp,
            interval=interval,
            timezone=timezone,
            transformation_version=transformation_version,
            checksum=None,
            context_decision_use_tag=context_decision_use_tag,
        )
        return unsigned.with_checksum(unsigned.compute_checksum())

    def with_checksum(self, checksum: str) -> EvidenceEnvelope:
        return EvidenceEnvelope(
            provenance_class=self.provenance_class,
            provider=self.provider,
            symbol_or_universe=self.symbol_or_universe,
            market_timestamp=self.market_timestamp,
            retrieval_timestamp=self.retrieval_timestamp,
            interval=self.interval,
            timezone=self.timezone,
            transformation_version=self.transformation_version,
            checksum=checksum,
            context_decision_use_tag=self.context_decision_use_tag,
        )

    def canonical_payload(self) -> dict[str, Any]:
        """Fields that constitute the checksum input, in hash-field order."""
        return {
            "provenance_class": self.provenance_class,
            "provider": self.provider,
            "symbol_or_universe": self.symbol_or_universe,
            "market_timestamp": _canonical_timestamp_or_none(self.market_timestamp),
            "retrieval_timestamp": _canonical_timestamp_or_none(
                self.retrieval_timestamp
            ),
            "interval": self.interval,
            "timezone": self.timezone,
            "transformation_version": self.transformation_version,
            "context_decision_use_tag": self.context_decision_use_tag,
        }

    def canonical_bytes(self) -> bytes:
        return dumps(
            self.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")

    def compute_checksum(self) -> str:
        return sha256(self.canonical_bytes()).hexdigest()

    def serialize(self) -> str:
        """Deterministic JSON including the checksum field."""
        document = dict(self.canonical_payload())
        document["checksum"] = self.checksum
        return dumps(
            document,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

    @classmethod
    def deserialize(cls, serialized: str) -> EvidenceEnvelope:
        raw = loads(serialized)
        if not isinstance(raw, Mapping):
            raise ValueError("serialized envelope must be a JSON object")
        return cls.from_mapping(raw)

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> EvidenceEnvelope:
        market_raw = raw.get("market_timestamp")
        retrieval_raw = raw.get("retrieval_timestamp")
        return cls(
            provenance_class=_optional_str(raw.get("provenance_class")),
            provider=_optional_str(raw.get("provider")),
            symbol_or_universe=_optional_str(raw.get("symbol_or_universe")),
            market_timestamp=_timestamp_from_raw(market_raw),
            retrieval_timestamp=_timestamp_from_raw(retrieval_raw),
            interval=_optional_str(raw.get("interval")),
            timezone=_optional_str(raw.get("timezone")),
            transformation_version=_optional_str(raw.get("transformation_version")),
            checksum=_optional_str(raw.get("checksum")),
            context_decision_use_tag=_optional_str(raw.get("context_decision_use_tag")),
        )


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _timestamp_from_raw(value: object) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return parse_canonical_timestamp(value)
    raise ValueError("timestamp must be datetime, ISO-8601 string, or null")


def resolve_declared_timezone(name: str) -> dt_timezone | ZoneInfo:
    if name == "UTC":
        return dt_timezone.utc
    return ZoneInfo(name)


def timezone_offset_matches(value: datetime, declared: str) -> bool:
    try:
        zone = resolve_declared_timezone(declared)
    except ZoneInfoNotFoundError:
        return False
    return value.utcoffset() == datetime(
        value.year,
        value.month,
        value.day,
        value.hour,
        value.minute,
        value.second,
        value.microsecond,
        tzinfo=zone,
    ).utcoffset()


def is_known_timezone(name: str) -> bool:
    if name == "UTC":
        return True
    try:
        ZoneInfo(name)
    except ZoneInfoNotFoundError:
        return False
    return True
