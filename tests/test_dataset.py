"""SOFTWARE and DATA CORRECTNESS — Phase 5 dataset admission."""

from __future__ import annotations

import importlib
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.dataset import DatasetDeclaration, admit_to_dataset
from radar_v4.evidence import ProvenanceClass
from tests.helpers import envelope


def _declaration(**overrides: str) -> DatasetDeclaration:
    values = dict(
        dataset_id="phase5-unit7",
        provenance_class=ProvenanceClass.HISTORICAL.value,
        provider="PHASE5_SOURCE",
        universe="HIST:AAA",
        interval="1d",
        timezone="UTC",
        transformation_version="phase5-v1",
        adjustment_policy="UNADJUSTED",
        locked_question="ordinary close-to-close changes for one symbol",
        primary_metric="close-to-close difference",
    )
    values.update(overrides)
    return DatasetDeclaration(**values)  # type: ignore[arg-type]


class DatasetAdmissionTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "admit_to_dataset"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "dataset.py"), doraise=True)

    def test_matching_historical_record_is_admitted(self) -> None:
        record = envelope(
            provenance=ProvenanceClass.HISTORICAL,
            symbol="HIST:AAA",
        )
        report = admit_to_dataset(_declaration(), (record,))
        self.assertEqual(report.accepted_count(), 1)
        self.assertEqual(report.quarantined_count(), 0)

    def test_interval_mismatch_is_quarantined(self) -> None:
        record = envelope(
            provenance=ProvenanceClass.HISTORICAL,
            symbol="HIST:AAA",
            interval="1h",
        )
        report = admit_to_dataset(_declaration(), (record,))
        self.assertEqual(report.accepted_count(), 0)
        self.assertIn(
            "DATASET_DECLARATION_MISMATCH",
            report.quarantined[0].validation.issue_codes(),
        )

    def test_fixture_does_not_admit_to_historical_dataset(self) -> None:
        record = envelope(symbol="HIST:AAA")
        report = admit_to_dataset(_declaration(), (record,))
        self.assertEqual(report.accepted_count(), 0)
        self.assertIn(
            "DATASET_DECLARATION_MISMATCH",
            report.quarantined[0].validation.issue_codes(),
        )


if __name__ == "__main__":
    unittest.main()
