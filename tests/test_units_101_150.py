"""SOFTWARE CORRECTNESS — Phase 5 units 101–150 inspectability."""

from __future__ import annotations

import importlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.audit_bundle import verify_audit_bundle, write_audit_bundle
from radar_v4.cli import main
from radar_v4.evidence_chain import (
    inspect_evidence_chain,
    reconcile_journal_to_pack,
    three_way_pack,
)
from radar_v4.integrity import (
    check_claim_level,
    check_readiness_semantics,
    check_workshop_status_semantics,
    inspect_close_scale,
    inspect_gaps,
    inspect_locked_scope,
    inspect_payload_keys,
    inspect_timestamps,
    recompute_change_records,
    recompute_from_snapshot,
    require_document_kind,
    scan_forbidden_fields,
)
from radar_v4.local_session import run_session_from_pack
from radar_v4.pack_safety import inspect_pack_safety
from radar_v4.session_report import write_local_session_report_file
from radar_v4.snapshot_files import write_snapshot_file
from radar_v4.workshop_bounds import scan_package_network_imports, workshop_bounds
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


class Units101To150Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in (
            "check_claim_level",
            "inspect_locked_scope",
            "inspect_pack_safety",
            "inspect_evidence_chain",
            "write_audit_bundle",
            "workshop_bounds",
        ):
            self.assertTrue(hasattr(package, name), name)
        for relative in (
            "radar_v4/integrity.py",
            "radar_v4/pack_safety.py",
            "radar_v4/evidence_chain.py",
            "radar_v4/audit_bundle.py",
            "radar_v4/workshop_bounds.py",
        ):
            py_compile(str(ROOT / relative), doraise=True)

    def test_highest_unit_is_150_and_status_is_not_a_measurement(self) -> None:
        self.assertEqual(PHASE5_HIGHEST_UNIT, 150)
        status = json.loads(workshop_status())
        self.assertEqual(status["highest_unit"], 150)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        self.assertTrue(check_workshop_status_semantics().valid)
        bounds = json.loads(workshop_bounds())
        self.assertEqual(bounds["highest_unit"], 150)
        self.assertFalse(bounds["measured"])
        self.assertFalse(bounds["vendor_authorized"])
        self.assertIn("Phase 6 method research", bounds["not_authorized"])

    def test_synthetic_pack_integrity_path(self) -> None:
        result = run_session_from_pack(PACK)
        assert result.session is not None
        with tempfile.TemporaryDirectory() as raw:
            snapshot = Path(raw) / "snap.json"
            report = Path(raw) / "report.json"
            write_snapshot_file(snapshot, result.session.snapshot)
            write_local_session_report_file(report, result)
            self.assertTrue(check_claim_level(report).valid)
            self.assertTrue(recompute_change_records(report).valid)
            self.assertTrue(recompute_from_snapshot(report, snapshot).valid)
            chain = inspect_evidence_chain(PACK, snapshot, report)
            self.assertTrue(chain.matched, chain.serialize())

    def test_locked_scope_and_descriptive_inspectors(self) -> None:
        scope = inspect_locked_scope(PACK)
        self.assertTrue(scope.valid, scope.serialize())
        self.assertEqual(scope.details["symbol_count"], 1)
        self.assertTrue(inspect_payload_keys(PACK).valid)
        self.assertTrue(inspect_timestamps(PACK).valid)
        self.assertFalse(inspect_timestamps(PACK).details["uses_file_mtime"])
        gaps = inspect_gaps(PACK)
        self.assertTrue(gaps.valid)
        self.assertEqual(gaps.details["gap_count"], 2)
        self.assertIn("does not invent a market calendar", " ".join(gaps.notes))
        scale = inspect_close_scale(PACK)
        self.assertEqual(scale.details["unique_places"], [2])
        self.assertTrue(check_readiness_semantics(PACK).valid)
        self.assertTrue(inspect_pack_safety(PACK).safe)
        self.assertTrue(three_way_pack(PACK).matched)
        self.assertTrue(require_document_kind(PACK / "manifest.json").valid)
        self.assertTrue(scan_forbidden_fields(PACK / "declaration.json").valid)

    def test_claim_level_mismatch_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            report = Path(raw) / "bad.json"
            report.write_text(
                json.dumps(
                    {
                        "document_kind": "radar_v4.session_report",
                        "baseline": {
                            "status": "INSUFFICIENT_EVIDENCE",
                            "claim_level": "LEVEL 0 — MEASURED",
                            "changes": [],
                            "change_records": [],
                        },
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n",
                encoding="utf-8",
            )
            check = check_claim_level(report)
        self.assertFalse(check.valid)
        self.assertEqual(check.error_code, "CLAIM_LEVEL_MISMATCH")

    def test_arithmetic_mismatch_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            report = Path(raw) / "bad.json"
            report.write_text(
                json.dumps(
                    {
                        "document_kind": "radar_v4.session_report",
                        "baseline": {
                            "status": "MEASURED",
                            "claim_level": "LEVEL 0 — MEASURED",
                            "changes": ["9.99"],
                            "change_records": [
                                {
                                    "from_close": "10.00",
                                    "to_close": "10.50",
                                    "difference": "9.99",
                                }
                            ],
                        },
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n",
                encoding="utf-8",
            )
            check = recompute_change_records(report)
        self.assertFalse(check.valid)
        self.assertEqual(check.error_code, "ARITHMETIC_MISMATCH")

    def test_forbidden_fields_and_extra_payload_keys(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "signal.json").write_text(
                '{"edge": true}\n',
                encoding="utf-8",
            )
            forbidden = scan_forbidden_fields(root / "signal.json")
            (root / "declaration.json").write_text(
                (PACK / "declaration.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (root / "obs.json").write_text(
                json.dumps(
                    {
                        "envelope": json.loads(
                            (PACK / "obs_2026-08-07.json").read_text(encoding="utf-8")
                        )["envelope"],
                        "payload": {"close": "10.00", "rsi": "70"},
                    }
                ),
                encoding="utf-8",
            )
            extras = inspect_payload_keys(root)
        self.assertFalse(forbidden.valid)
        self.assertEqual(forbidden.error_code, "FORBIDDEN_FIELD")
        self.assertFalse(extras.valid)
        self.assertEqual(extras.error_code, "EXTRA_PAYLOAD_KEY")

    def test_pack_safety_refuses_bom_and_nested(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "declaration.json").write_bytes(
                b"\xef\xbb\xbf{\"dataset_id\":\"x\"}\n"
            )
            nested = root / "inner"
            nested.mkdir()
            (nested / "hidden.json").write_text("{}\n", encoding="utf-8")
            report = inspect_pack_safety(root)
        self.assertFalse(report.safe)
        self.assertIn("PACK_BOM", report.issues)
        self.assertIn("PACK_NESTED_JSON", report.issues)

    def test_audit_bundle_round_trip_and_no_network(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw) / "audit"
            write_audit_bundle(PACK, out)
            verification = verify_audit_bundle(out)
            self.assertTrue(verification.matched, verification.serialize())
            (out / "obs_2026-08-07.json").write_bytes(b"tampered\n")
            self.assertFalse(verify_audit_bundle(out).matched)
        scan = json.loads(scan_package_network_imports())
        self.assertTrue(scan["valid"], scan)

    def test_journal_reconcile_on_clean_pack(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            journal = Path(raw) / "journal.json"
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                code = main(
                    ["quarantine", "--pack", str(PACK), "--out", str(journal)]
                )
            self.assertEqual(code, 0)
            check = reconcile_journal_to_pack(PACK, journal)
            self.assertTrue(check.matched, check.serialize())

    def test_cli_new_inspect_commands(self) -> None:
        for command, extra in (
            (["locked-scope", "--pack", str(PACK)], True),
            (["pack-safety", "--pack", str(PACK)], True),
            (["gaps", "--pack", str(PACK)], True),
            (["bounds"], True),
            (["no-network"], True),
            (["three-way", "--pack", str(PACK)], True),
        ):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(command)
            self.assertEqual(code, 0, f"{command} {stderr.getvalue()}")
            if extra:
                document = json.loads(stdout.getvalue())
                self.assertIn("document_kind", document)


if __name__ == "__main__":
    unittest.main()
