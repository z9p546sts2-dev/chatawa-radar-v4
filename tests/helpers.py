"""Shared test constructors. Not a market fixture catalog."""

from __future__ import annotations

from datetime import datetime, timezone

from radar_v4.evidence import EvidenceEnvelope, ProvenanceClass


def aware(day: int, hour: int = 14) -> datetime:
    return datetime(2026, 8, day, hour, 0, 0, tzinfo=timezone.utc)


def envelope(
    *,
    provenance: ProvenanceClass | str = ProvenanceClass.FIXTURE,
    provider: str = "PHASE5_SOURCE",
    symbol: str = "FIXTURE:AAA",
    day: int = 7,
    interval: str = "1d",
    timezone_name: str = "UTC",
    transformation: str = "phase5-v1",
) -> EvidenceEnvelope:
    return EvidenceEnvelope.create(
        provenance_class=provenance,
        provider=provider,
        symbol_or_universe=symbol,
        market_timestamp=aware(day, 14),
        retrieval_timestamp=aware(day, 15),
        interval=interval,
        timezone=timezone_name,
        transformation_version=transformation,
    )
