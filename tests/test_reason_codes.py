"""SOFTWARE CORRECTNESS — Phase 5 reason-code catalog."""

from __future__ import annotations

import importlib
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.reason_codes import REASON_CODES, RESULT_STATUSES


class ReasonCodeTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "REASON_CODES"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "reason_codes.py"), doraise=True)

    def test_catalog_includes_current_refusal_codes(self) -> None:
        for code in (
            "DATASET_DECLARATION_MISMATCH",
            "PACK_PROVENANCE_NOT_ALLOWED",
            "OBSERVATION_NOT_ADMITTED",
            "DUPLICATE_MARKET_TIMESTAMP",
            "CONTRADICTORY_IDENTITY",
            "UNREADABLE_JSON",
            "UNREADABLE_SNAPSHOT_FILE",
            "CHANGE_DISCONTINUITY",
            "SNAPSHOT_CHECKSUM_MISMATCH",
            "UNREADABLE_REGISTRY_FILE",
            "RULER_MISMATCH",
            "UNREADABLE_SIDECAR",
            "MANIFEST_CHECKSUM_MISMATCH",
            "MANIFEST_REQUIRED",
            "FILE_EXISTS",
            "BUNDLE_SIDECAR_MISSING",
            "BUNDLE_RULER_MISSING",
            "BUNDLE_RULER_MISMATCH",
            "UNREADABLE_JOURNAL",
            "UNREADABLE_SESSION_REPORT",
            "UNREADABLE_MANIFEST",
            "UNKNOWN_DOCUMENT_KIND",
            "REPORT_SNAPSHOT_MISMATCH",
            "DETERMINISM_MISMATCH",
            "NOT_CANONICAL_JSON",
            "LAYOUT_DECLARATION_MISSING",
            "CLAIM_LEVEL_MISMATCH",
            "ARITHMETIC_MISMATCH",
            "LOCKED_SCOPE_VIOLATION",
            "FORBIDDEN_FIELD",
            "PACK_BOM",
            "CHAIN_MISMATCH",
            "AUDIT_BUNDLE_MISMATCH",
            "NETWORK_IMPORT",
        ):
            self.assertIn(code, REASON_CODES)

    def test_result_statuses_remain_descriptive(self) -> None:
        self.assertIn("MEASURED", RESULT_STATUSES)
        self.assertIn("INSUFFICIENT_EVIDENCE", RESULT_STATUSES)
        self.assertIn("INVALID_COMPARISON", RESULT_STATUSES)
        self.assertNotIn("EDGE", RESULT_STATUSES)


if __name__ == "__main__":
    unittest.main()
