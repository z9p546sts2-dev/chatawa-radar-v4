"""SOFTWARE and DATA CORRECTNESS — Phase 5 local dataset pack."""

from __future__ import annotations

import importlib
import json
import tempfile
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.dataset_pack import load_dataset_pack
from radar_v4.evidence import ProvenanceClass
from radar_v4.observation import Observation, ObservationPayload
from tests.helpers import envelope


def _declaration(**overrides: object) -> dict[str, object]:
    document: dict[str, object] = {
        "dataset_id": "phase5-pack",
        "provenance_class": ProvenanceClass.SYNTHETIC.value,
        "provider": "PHASE5_SOURCE",
        "universe": "SYN:AAA",
        "interval": "1d",
        "timezone": "UTC",
        "transformation_version": "phase5-v1",
        "adjustment_policy": "UNADJUSTED",
        "locked_question": "ordinary close-to-close changes for one symbol",
        "primary_metric": "close-to-close difference",
    }
    document.update(overrides)
    return document


def _obs(day: int, close: str, provenance=ProvenanceClass.SYNTHETIC) -> Observation:
    return Observation.create(
        envelope(provenance=provenance, symbol="SYN:AAA", day=day),
        ObservationPayload(close=close),
    )


def _write_obs(path: Path, item: Observation) -> None:
    path.write_text(
        json.dumps(
            {
                "envelope": item.envelope.serialize(),
                "payload": item.payload.canonical_payload(),
                "payload_checksum": item.payload_checksum,
            }
        ),
        encoding="utf-8",
    )


class DatasetPackTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "load_dataset_pack"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "dataset_pack.py"), doraise=True)

    def test_missing_directory_is_unreadable(self) -> None:
        report = load_dataset_pack("/tmp/radar-v4-no-such-dataset-pack")
        self.assertFalse(report.usable())
        self.assertEqual(report.unreadable[0].code, "UNREADABLE_PACK")

    def test_synthetic_pack_is_usable(self) -> None:
        item = _obs(7, "10.00")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "declaration.json").write_text(
                json.dumps(_declaration()), encoding="utf-8"
            )
            _write_obs(root / "obs.json", item)
            report = load_dataset_pack(root)
        self.assertTrue(report.usable())
        self.assertEqual(report.observation_intake.accepted_count(), 1)

    def test_historical_declaration_is_not_usable(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "declaration.json").write_text(
                json.dumps(_declaration(provenance_class="HISTORICAL")),
                encoding="utf-8",
            )
            report = load_dataset_pack(root)
        self.assertFalse(report.usable())
        self.assertEqual(
            [issue.code for issue in report.pack_issues],
            ["PACK_PROVENANCE_NOT_ALLOWED"],
        )

    def test_historical_observation_is_quarantined(self) -> None:
        historical = _obs(7, "10.00", provenance=ProvenanceClass.HISTORICAL)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "declaration.json").write_text(
                json.dumps(_declaration()), encoding="utf-8"
            )
            _write_obs(root / "hist.json", historical)
            report = load_dataset_pack(root)
        self.assertTrue(report.usable())
        self.assertEqual(report.observation_intake.accepted_count(), 0)
        self.assertIn(
            "PACK_PROVENANCE_NOT_ALLOWED",
            report.observation_intake.quarantined[0].validation.issue_codes(),
        )


if __name__ == "__main__":
    unittest.main()
