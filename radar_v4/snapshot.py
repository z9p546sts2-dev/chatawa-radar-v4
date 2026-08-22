"""Deterministic dataset snapshot. No vendor fetch."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from json import dumps, loads
from typing import Any

from radar_v4.dataset import DatasetDeclaration
from radar_v4.evidence import EvidenceEnvelope
from radar_v4.observation import Observation, ObservationPayload


@dataclass(frozen=True)
class DatasetSnapshot:
    declaration: DatasetDeclaration
    observations: tuple[Observation, ...]

    def serialize(self) -> str:
        document = {
            "declaration": asdict(self.declaration),
            "observations": [
                {
                    "envelope": item.envelope.serialize(),
                    "payload": item.payload.canonical_payload(),
                    "payload_checksum": item.payload_checksum,
                }
                for item in self.observations
            ],
        }
        return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

    @classmethod
    def deserialize(cls, serialized: str) -> DatasetSnapshot:
        raw = loads(serialized)
        if not isinstance(raw, Mapping):
            raise ValueError("snapshot must be a JSON object")
        declaration_raw = raw.get("declaration")
        if not isinstance(declaration_raw, Mapping):
            raise ValueError("snapshot declaration is missing")
        declaration = DatasetDeclaration(
            dataset_id=str(declaration_raw["dataset_id"]),
            provenance_class=str(declaration_raw["provenance_class"]),
            provider=str(declaration_raw["provider"]),
            universe=str(declaration_raw["universe"]),
            interval=str(declaration_raw["interval"]),
            timezone=str(declaration_raw["timezone"]),
            transformation_version=str(declaration_raw["transformation_version"]),
            adjustment_policy=str(declaration_raw["adjustment_policy"]),
            locked_question=str(declaration_raw["locked_question"]),
            primary_metric=str(declaration_raw["primary_metric"]),
            max_staleness=declaration_raw.get("max_staleness"),
        )
        rows = raw.get("observations")
        if not isinstance(rows, list):
            raise ValueError("snapshot observations must be an array")
        observations: list[Observation] = []
        for row in rows:
            if not isinstance(row, Mapping):
                raise ValueError("snapshot observation must be an object")
            envelope = EvidenceEnvelope.deserialize(str(row["envelope"]))
            payload_raw = row.get("payload")
            if not isinstance(payload_raw, Mapping):
                raise ValueError("snapshot payload must be an object")
            payload = ObservationPayload(
                close=str(payload_raw["close"]),
                open=_optional(payload_raw.get("open")),
                high=_optional(payload_raw.get("high")),
                low=_optional(payload_raw.get("low")),
                volume=_optional(payload_raw.get("volume")),
            )
            observations.append(
                Observation(
                    envelope=envelope,
                    payload=payload,
                    payload_checksum=str(row["payload_checksum"]),
                )
            )
        return cls(declaration=declaration, observations=tuple(observations))


def _optional(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def make_snapshot(
    declaration: DatasetDeclaration, observations: Sequence[Observation]
) -> DatasetSnapshot:
    return DatasetSnapshot(declaration=declaration, observations=tuple(observations))
