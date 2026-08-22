"""SOFTWARE and DATA CORRECTNESS — Phase 5 observation JSON intake."""

from __future__ import annotations

import importlib
import json
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.evidence import ProvenanceClass
from radar_v4.observation import Observation, ObservationPayload
from radar_v4.observation_json import intake_observation_json
from tests.helpers import envelope


class ObservationJsonIntakeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.obs = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA"),
            ObservationPayload(
                open="10.00",
                high="11.00",
                low="9.00",
                close="10.50",
                volume="100",
            ),
        )

    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "intake_observation_json"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "observation_json.py"), doraise=True)

    def test_valid_object_round_trips(self) -> None:
        doc = json.dumps(
            {
                "envelope": self.obs.envelope.serialize(),
                "payload": self.obs.payload.canonical_payload(),
                "payload_checksum": self.obs.payload_checksum,
            }
        )
        result = intake_observation_json(doc)
        self.assertEqual(result.unreadable_count(), 0)
        self.assertEqual(result.quarantined_count(), 0)
        self.assertEqual(result.accepted_count(), 1)
        self.assertEqual(result.accepted[0].payload_checksum, self.obs.payload_checksum)
        self.assertEqual(result.accepted[0].payload.close, "10.50")

    def test_array_of_documents(self) -> None:
        doc = json.dumps(
            [
                {
                    "envelope": self.obs.envelope.serialize(),
                    "payload": self.obs.payload.canonical_payload(),
                }
            ]
        )
        result = intake_observation_json(doc)
        self.assertEqual(result.accepted_count(), 1)

    def test_envelope_object_is_accepted(self) -> None:
        doc = json.dumps(
            {
                "envelope": json.loads(self.obs.envelope.serialize()),
                "payload": self.obs.payload.canonical_payload(),
            }
        )
        result = intake_observation_json(doc)
        self.assertEqual(result.accepted_count(), 1)

    def test_unreadable_json_is_not_an_observation(self) -> None:
        result = intake_observation_json("{not json")
        self.assertEqual(result.accepted_count(), 0)
        self.assertEqual(result.quarantined_count(), 0)
        self.assertEqual(result.unreadable_count(), 1)
        self.assertEqual(result.unreadable[0].code, "UNREADABLE_JSON")

    def test_payload_checksum_mismatch_is_quarantined(self) -> None:
        doc = json.dumps(
            {
                "envelope": self.obs.envelope.serialize(),
                "payload": self.obs.payload.canonical_payload(),
                "payload_checksum": "0" * 64,
            }
        )
        result = intake_observation_json(doc)
        self.assertEqual(result.accepted_count(), 0)
        self.assertEqual(result.unreadable_count(), 0)
        self.assertEqual(result.quarantined_count(), 1)
        self.assertIn(
            "PAYLOAD_CHECKSUM_MISMATCH",
            result.quarantined[0].validation.issue_codes(),
        )

    def test_envelope_array_is_unreadable(self) -> None:
        doc = json.dumps(
            {
                "envelope": "[]",
                "payload": self.obs.payload.canonical_payload(),
            }
        )
        result = intake_observation_json(doc)
        self.assertEqual(result.accepted_count(), 0)
        self.assertEqual(result.unreadable[0].code, "ENVELOPE_NOT_JSON_OBJECT")


if __name__ == "__main__":
    unittest.main()
