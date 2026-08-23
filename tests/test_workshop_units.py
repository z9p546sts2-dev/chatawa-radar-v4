"""SOFTWARE CORRECTNESS — Phase 5 units 58–100 workshop operations."""

from __future__ import annotations

import importlib
import json
import tempfile
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.document_kind import detect_document_kind
from radar_v4.local_session import run_session_from_pack
from radar_v4.pack_describe import (
    describe_pack,
    inspect_pack_layout,
    pack_identities,
    pack_readiness,
    provenance_mix,
)
from radar_v4.session_report import write_local_session_report_file
from radar_v4.snapshot_files import write_snapshot_file
from radar_v4.snapshot_inventory import snapshot_inventory
from radar_v4.workshop_check import (
    bind_report_to_snapshot,
    check_canonical_json,
    check_pack_determinism,
    lookup_reason_code,
    workshop_status,
)
from radar_v4.workshop_compare import (
    compare_inventories,
    compare_rulers,
    compare_session_reports,
    inventory_vs_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


class WorkshopUnitTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in (
            "detect_document_kind",
            "describe_pack",
            "compare_rulers",
            "check_pack_determinism",
            "workshop_status",
            "snapshot_inventory",
        ):
            self.assertTrue(hasattr(package, name), name)
        for relative in (
            "radar_v4/document_kind.py",
            "radar_v4/pack_describe.py",
            "radar_v4/workshop_compare.py",
            "radar_v4/workshop_check.py",
            "radar_v4/snapshot_inventory.py",
            "radar_v4/workshop_cli.py",
        ):
            py_compile(str(ROOT / relative), doraise=True)

    def test_detect_kind_on_labeled_and_inferred_files(self) -> None:
        labeled = detect_document_kind(PACK / "manifest.json")
        self.assertEqual(labeled.document_kind, "radar_v4.pack_manifest")
        self.assertFalse(labeled.inferred)
        inferred = detect_document_kind(PACK / "declaration.json")
        self.assertEqual(inferred.document_kind, "radar_v4.declaration")
        self.assertTrue(inferred.inferred)

    def test_pack_describe_does_not_measure(self) -> None:
        layout = inspect_pack_layout(PACK)
        self.assertTrue(layout.ready_to_load)
        mix = provenance_mix(PACK)
        self.assertGreaterEqual(mix.counts.get("SYNTHETIC", 0), 3)
        identities = pack_identities(PACK)
        self.assertEqual(len(identities.accepted), 3)
        readiness = pack_readiness(PACK)
        self.assertTrue(readiness.enough_for_close_to_close)
        self.assertEqual(readiness.admitted_observations, 3)
        self.assertIn("not a measurement", " ".join(readiness.notes))
        description = json.loads(describe_pack(PACK).serialize())
        self.assertEqual(description["document_kind"], "radar_v4.pack_describe")
        self.assertIn("ruler_checksum", description["ruler"])

    def test_rulers_and_inventories_match_the_same_pack(self) -> None:
        self.assertTrue(compare_rulers(PACK, PACK).equal)
        self.assertTrue(compare_inventories(PACK, PACK).equal)
        self.assertTrue(inventory_vs_manifest(PACK).matched)

    def test_determinism_and_report_bind(self) -> None:
        determinism = check_pack_determinism(PACK)
        self.assertTrue(determinism.equal)
        result = run_session_from_pack(PACK)
        assert result.session is not None
        with tempfile.TemporaryDirectory() as raw:
            snapshot = Path(raw) / "snap.json"
            report = Path(raw) / "report.json"
            write_snapshot_file(snapshot, result.session.snapshot)
            write_local_session_report_file(report, result)
            inventory = snapshot_inventory(snapshot)
            bind = bind_report_to_snapshot(report, snapshot)
            reports = compare_session_reports(report, report)
        self.assertEqual(inventory.observation_count, 3)
        self.assertTrue(bind.matched)
        self.assertTrue(reports.equal)

    def test_admission_does_not_measure(self) -> None:
        result = run_session_from_pack(PACK, measure=False)
        assert result.session is not None
        self.assertIsNone(result.session.baseline)

    def test_canonical_and_status_and_code_lookup(self) -> None:
        check = check_canonical_json(PACK / "manifest.json")
        self.assertTrue(check.canonical)
        status = json.loads(workshop_status())
        self.assertEqual(status["highest_unit"], 750)
        self.assertFalse(status["measured"])
        self.assertFalse(status["method_defined"])
        self.assertFalse(status["vendor_authorized"])
        self.assertEqual(status["available_claim_level"], "LEVEL 0 — MEASURED")
        self.assertNotIn("claim_level", status)
        self.assertTrue(lookup_reason_code("FILE_EXISTS").known)
        self.assertFalse(lookup_reason_code("NOT_A_REAL_CODE").known)
        with tempfile.TemporaryDirectory() as raw:
            padded = Path(raw) / "padded.json"
            padded.write_text(
                "\n" + (PACK / "manifest.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            self.assertFalse(check_canonical_json(padded).canonical)
            self.assertEqual(check_canonical_json(padded).error_code, "NOT_CANONICAL_JSON")
            extra_newlines = Path(raw) / "extra_newlines.json"
            extra_newlines.write_text(
                (PACK / "manifest.json").read_text(encoding="utf-8") + "\n",
                encoding="utf-8",
            )
            self.assertFalse(check_canonical_json(extra_newlines).canonical)
            self.assertEqual(
                check_canonical_json(extra_newlines).error_code,
                "NOT_CANONICAL_JSON",
            )

    def test_readiness_requires_declaration_match(self) -> None:
        from radar_v4.evidence import ProvenanceClass
        from radar_v4.observation import Observation, ObservationPayload
        from tests.helpers import envelope
        from tests.test_dataset_pack import _declaration, _write_obs

        first = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:BBB", day=7),
            ObservationPayload(close="10.00"),
        )
        second = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:BBB", day=8),
            ObservationPayload(close="11.00"),
        )
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "declaration.json").write_text(
                json.dumps(_declaration()), encoding="utf-8"
            )
            _write_obs(root / "obs_a.json", first)
            _write_obs(root / "obs_b.json", second)
            readiness = pack_readiness(root)
        self.assertGreaterEqual(readiness.accepted_observations, 2)
        self.assertEqual(readiness.admitted_observations, 0)
        self.assertFalse(readiness.enough_for_close_to_close)


if __name__ == "__main__":
    unittest.main()
