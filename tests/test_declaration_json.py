"""SOFTWARE and DATA CORRECTNESS — Phase 5 declaration JSON intake."""

from __future__ import annotations

import importlib
import json
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.declaration_json import intake_declaration_json
from radar_v4.evidence import ProvenanceClass


def _valid_document(**overrides: object) -> dict[str, object]:
    document: dict[str, object] = {
        "dataset_id": "phase5-decl",
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


class DeclarationJsonTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "intake_declaration_json"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "declaration_json.py"), doraise=True)

    def test_valid_object_is_accepted(self) -> None:
        report = intake_declaration_json(json.dumps(_valid_document()))
        self.assertIsNone(report.unreadable)
        assert report.declaration is not None
        self.assertEqual(report.declaration.dataset_id, "phase5-decl")
        self.assertEqual(report.declaration.universe, "SYN:AAA")

    def test_unreadable_json_is_not_a_declaration(self) -> None:
        report = intake_declaration_json("{not json")
        self.assertIsNone(report.declaration)
        assert report.unreadable is not None
        self.assertEqual(report.unreadable.code, "UNREADABLE_JSON")

    def test_missing_field_is_not_defaulted(self) -> None:
        document = _valid_document()
        del document["interval"]
        report = intake_declaration_json(json.dumps(document))
        self.assertIsNone(report.declaration)
        assert report.validation is not None
        self.assertIn("MISSING_DECLARATION_FIELD", report.validation.issue_codes())

    def test_unknown_provenance_is_rejected(self) -> None:
        report = intake_declaration_json(
            json.dumps(_valid_document(provenance_class="MADE_UP"))
        )
        self.assertIsNone(report.declaration)
        assert report.validation is not None
        self.assertIn("UNKNOWN_PROVENANCE_CLASS", report.validation.issue_codes())


if __name__ == "__main__":
    unittest.main()
