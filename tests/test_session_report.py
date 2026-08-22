"""SOFTWARE CORRECTNESS — Phase 5 session report serialize."""

from __future__ import annotations

import importlib
import json
import tempfile
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.dataset import DatasetDeclaration
from radar_v4.evidence import ProvenanceClass
from radar_v4.observation import Observation, ObservationPayload
from radar_v4.session import run_dataset_session
from radar_v4.session_report import serialize_session_report, write_session_report_file
from radar_v4.snapshot_files import SnapshotFileError
from tests.helpers import envelope


class SessionReportTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "serialize_session_report"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "session_report.py"), doraise=True)

    def test_report_is_deterministic_and_descriptive(self) -> None:
        declaration = DatasetDeclaration(
            dataset_id="phase5-report",
            provenance_class=ProvenanceClass.SYNTHETIC.value,
            provider="PHASE5_SOURCE",
            universe="SYN:AAA",
            interval="1d",
            timezone="UTC",
            transformation_version="phase5-v1",
            adjustment_policy="UNADJUSTED",
            locked_question="ordinary close-to-close changes for one symbol",
            primary_metric="close-to-close difference",
        )
        first = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA", day=7),
            ObservationPayload(close="10.00"),
        )
        second = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA", day=8),
            ObservationPayload(close="10.25"),
        )
        result = run_dataset_session(
            declaration, (first.envelope, second.envelope), (first, second)
        )
        first_text = serialize_session_report(result)
        second_text = serialize_session_report(result)
        self.assertEqual(first_text, second_text)
        document = json.loads(first_text)
        self.assertEqual(document["dataset_id"], "phase5-report")
        self.assertEqual(document["baseline"]["status"], "MEASURED")
        self.assertEqual(document["baseline"]["claim_level"], "LEVEL 0 — MEASURED")
        self.assertEqual(document["kept_observation_count"], 2)
        self.assertEqual(len(document["snapshot_checksum"]), 64)
        self.assertEqual(document["baseline"]["change_records"][0]["difference"], "0.25")

    def test_directory_path_is_refused(self) -> None:
        declaration = DatasetDeclaration(
            dataset_id="phase5-report-dir",
            provenance_class=ProvenanceClass.SYNTHETIC.value,
            provider="PHASE5_SOURCE",
            universe="SYN:AAA",
            interval="1d",
            timezone="UTC",
            transformation_version="phase5-v1",
            adjustment_policy="UNADJUSTED",
            locked_question="ordinary close-to-close changes for one symbol",
            primary_metric="close-to-close difference",
        )
        item = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA"),
            ObservationPayload(close="1.00"),
        )
        result = run_dataset_session(declaration, (item.envelope,), (item,))
        with tempfile.TemporaryDirectory() as raw:
            with self.assertRaises(SnapshotFileError) as ctx:
                write_session_report_file(Path(raw), result)
            self.assertEqual(ctx.exception.code, "SESSION_REPORT_PATH_IS_DIRECTORY")


if __name__ == "__main__":
    unittest.main()
