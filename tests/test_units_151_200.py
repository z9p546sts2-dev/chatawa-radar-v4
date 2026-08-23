"""SOFTWARE CORRECTNESS — Phase 5 units 151–200 inspectability."""

from __future__ import annotations

import importlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.catalog_audit import audit_document_kinds, audit_reason_catalog
from radar_v4.cli import main
from radar_v4.local_session import run_session_from_pack
from radar_v4.record_check import (
    describe_close_zeros,
    inspect_file_modes,
    inspect_leftovers,
    inspect_ohlc,
    inspect_pack_urls,
    inspect_primary_metric,
    inspect_retrieval_order,
    inspect_ruler_fields,
    inspect_status_taxonomy,
    inspect_text_safety,
    inspect_unexpected_files,
    scan_percent_fields,
)
from radar_v4.roundtrip_check import check_export_roundtrip, check_replay_equality
from radar_v4.session_report import write_local_session_report_file
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import (
    inspect_question_lock,
    package_source_identity,
    read_disposition,
    workshop_stop_record,
    write_disposition,
)


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


class Units151To200Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in (
            "inspect_ohlc",
            "check_replay_equality",
            "audit_reason_catalog",
            "workshop_stop_record",
        ):
            self.assertTrue(hasattr(package, name), name)
        for relative in (
            "radar_v4/record_check.py",
            "radar_v4/roundtrip_check.py",
            "radar_v4/catalog_audit.py",
            "radar_v4/workshop_record.py",
        ):
            py_compile(str(ROOT / relative), doraise=True)

    def test_highest_unit_is_200(self) -> None:
        self.assertEqual(PHASE5_HIGHEST_UNIT, 200)
        status = json.loads(workshop_status())
        self.assertEqual(status["highest_unit"], 200)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertEqual(stop["highest_unit"], 200)
        self.assertFalse(stop["measured"])
        self.assertFalse(stop["vendor_authorized"])

    def test_synthetic_pack_record_checks(self) -> None:
        self.assertTrue(inspect_ohlc(PACK).valid)
        self.assertTrue(inspect_retrieval_order(PACK).valid)
        self.assertTrue(inspect_ruler_fields(PACK).valid)
        self.assertTrue(inspect_unexpected_files(PACK).valid)
        self.assertTrue(inspect_leftovers(PACK).valid)
        self.assertTrue(inspect_file_modes(PACK).valid)
        self.assertTrue(inspect_pack_urls(PACK).valid)
        self.assertTrue(inspect_primary_metric(PACK).valid)
        self.assertTrue(inspect_question_lock(PACK).valid)
        self.assertTrue(inspect_text_safety(PACK / "manifest.json").valid)
        zeros = describe_close_zeros(PACK)
        self.assertEqual(zeros.details["zeros"], 0)
        self.assertTrue(check_replay_equality(PACK).valid)

    def test_roundtrip_and_taxonomy(self) -> None:
        result = run_session_from_pack(PACK)
        assert result.session is not None
        with tempfile.TemporaryDirectory() as raw:
            report = Path(raw) / "report.json"
            write_local_session_report_file(report, result)
            self.assertTrue(inspect_status_taxonomy(report).valid)
            exported = Path(raw) / "exported"
            roundtrip = check_export_roundtrip(PACK, exported)
            self.assertTrue(roundtrip.valid, roundtrip.serialize())

    def test_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "prices.csv").write_text("close\n10\n", encoding="utf-8")
            self.assertFalse(inspect_unexpected_files(root).valid)
            (root / "note.tmp").write_text("x", encoding="utf-8")
            self.assertFalse(inspect_leftovers(root).valid)
            crlf = root / "crlf.json"
            crlf.write_bytes(b'{"a":1}\r\n')
            self.assertFalse(inspect_text_safety(crlf).valid)
            percent = root / "pct.json"
            percent.write_text('{"percent_change":"1"}\n', encoding="utf-8")
            self.assertEqual(scan_percent_fields(percent).error_code, "PERCENT_FIELD")
            live = root / "url.json"
            live.write_text('{"source":"https://example.com/bars"}\n', encoding="utf-8")
            # url-scan reads a pack directory of json files
            self.assertFalse(inspect_pack_urls(root).valid)

    def test_disposition_and_catalogs(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "disp.json"
            write_disposition(path, "UNREVIEWED")
            self.assertTrue(read_disposition(path).valid)
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)
        identity = json.loads(package_source_identity())
        self.assertIn("workshop_record.py", identity["files"])

    def test_cli_new_commands(self) -> None:
        for command in (
            ["ohlc-check", "--pack", str(PACK)],
            ["replay-eq", "--pack", str(PACK)],
            ["question-lock", "--pack", str(PACK)],
            ["stop-record"],
            ["catalog-audit"],
            ["package-identity"],
        ):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(command)
            self.assertEqual(code, 0, f"{command} {stderr.getvalue()}")
            self.assertIn("document_kind", json.loads(stdout.getvalue()))


if __name__ == "__main__":
    unittest.main()
