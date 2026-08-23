"""SOFTWARE CORRECTNESS — Phase 5 units 201–250 inspectability."""

from __future__ import annotations

import importlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from py_compile import compile as py_compile
from shutil import copytree

from radar_v4.catalog_audit import audit_document_kinds, audit_reason_catalog
from radar_v4.certify import (
    certify_pack,
    command_catalog,
    compare_stops,
    fixture_label_check,
    name_vs_ruler,
    reserved_name_scan,
    self_test,
    utf16_scan,
    write_certify_record,
)
from radar_v4.cli import main
from radar_v4.decimal_check import decimal_check_directory, decimal_check_text
from radar_v4.hygiene import (
    duplicate_digest_scan,
    hidden_file_scan,
    pack_hygiene,
    scan_python_source,
    scan_workshop_tree,
)
from radar_v4.lineage import (
    admission_vs_kept,
    clock_skew_describe,
    snapshot_order_check,
    volume_describe,
    write_lineage_record,
)
from radar_v4.local_session import run_session_from_pack
from radar_v4.snapshot_files import write_snapshot_file
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


class Units201To250Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in (
            "pack_hygiene",
            "certify_pack",
            "self_test",
            "command_catalog",
        ):
            self.assertTrue(hasattr(package, name), name)
        for relative in (
            "radar_v4/hygiene.py",
            "radar_v4/decimal_check.py",
            "radar_v4/lineage.py",
            "radar_v4/certify.py",
        ):
            py_compile(str(ROOT / relative), doraise=True)

    def test_highest_unit_is_250(self) -> None:
        self.assertEqual(PHASE5_HIGHEST_UNIT, 250)
        status = json.loads(workshop_status())
        self.assertEqual(status["highest_unit"], 250)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertEqual(stop["highest_unit"], 250)
        self.assertFalse(stop["measured"])
        self.assertFalse(stop["vendor_authorized"])

    def test_synthetic_pack_hygiene_and_certify(self) -> None:
        self.assertTrue(scan_workshop_tree().valid)
        self.assertTrue(pack_hygiene(PACK).valid)
        self.assertTrue(decimal_check_directory(PACK).valid)
        self.assertTrue(name_vs_ruler(PACK).valid)
        self.assertTrue(reserved_name_scan(PACK).valid)
        self.assertTrue(utf16_scan(PACK).valid)
        self.assertTrue(fixture_label_check(PACK).valid)
        admission = admission_vs_kept(PACK)
        self.assertEqual(admission.details["admitted"], 3)
        self.assertEqual(admission.details["kept"], 3)
        span = clock_skew_describe(PACK)
        self.assertIsNone(span.error_code)
        self.assertEqual(volume_describe(PACK).details["observations_with_volume"], 0)
        certified = certify_pack(PACK)
        self.assertTrue(certified.valid, certified.serialize())
        self.assertTrue(self_test().valid, self_test().serialize())

    def test_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / ".hidden").write_text("x", encoding="utf-8")
            self.assertEqual(hidden_file_scan(root).error_code, "HIDDEN_FILE_REFUSED")
            (root / "a.json").write_text("same\n", encoding="utf-8")
            (root / "b.json").write_text("same\n", encoding="utf-8")
            self.assertEqual(duplicate_digest_scan(root).error_code, "DUPLICATE_DIGEST_REFUSED")
            (root / "live.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual(reserved_name_scan(root).error_code, "RESERVED_NAME_REFUSED")
            utf16 = root / "wide.txt"
            utf16.write_bytes(b"\xff\xfeA\x00")
            self.assertEqual(utf16_scan(root).error_code, "UTF16_REFUSED")
            numbered = decimal_check_text(
                '{"payload":{"close":10.5}}',
                path="n.json",
            )
            self.assertEqual(numbered.error_code, "JSON_NUMBER_NOT_STRING")
            infinite = decimal_check_text(
                '{"payload":{"close":"NaN"}}',
                path="nan.json",
            )
            self.assertEqual(infinite.error_code, "NON_FINITE_CLOSE")
            scientific = decimal_check_text(
                '{"payload":{"close":"1e2"}}',
                path="sci.json",
            )
            self.assertTrue(scientific.valid)
            self.assertEqual(scientific.error_code, "SCIENTIFIC_NOTATION_DESCRIBE")
            bad = root / "bad.py"
            bad.write_text("value = eval('1')\n", encoding="utf-8")
            scan = scan_python_source(bad)
            self.assertFalse(scan.valid)
            self.assertEqual(scan.error_code, "DANGEROUS_CALL_REFUSED")

    def test_lineage_write_and_snapshot_order(self) -> None:
        result = run_session_from_pack(PACK)
        assert result.session is not None
        with tempfile.TemporaryDirectory() as raw:
            snapshot = Path(raw) / "snapshot.json"
            write_snapshot_file(snapshot, result.session.snapshot)
            self.assertTrue(snapshot_order_check(snapshot).valid)
            lineage_path = Path(raw) / "lineage.json"
            record = write_lineage_record(PACK, lineage_path)
            self.assertTrue(lineage_path.is_file())
            self.assertEqual(record.document_kind, "radar_v4.lineage_record")
            certify_path = Path(raw) / "certify.json"
            written = write_certify_record(PACK, certify_path)
            self.assertTrue(written.valid)
            self.assertTrue(certify_path.is_file())
            copied = Path(raw) / "copy"
            copytree(PACK, copied)
            (copied / "signal.json").write_text("{}\n", encoding="utf-8")
            self.assertFalse(certify_pack(copied).valid)

    def test_compare_stops_and_catalogs(self) -> None:
        stop = workshop_stop_record()
        compared = compare_stops(stop, stop)
        self.assertTrue(compared.valid)
        self.assertTrue(compared.details["same_freeze"])
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)
        commands = command_catalog()
        self.assertGreaterEqual(int(commands.details["count"]), 20)
        self.assertIn("certify", commands.details["commands"])

    def test_cli_new_commands(self) -> None:
        for command in (
            ["hygiene-scan"],
            ["pack-hygiene", "--pack", str(PACK)],
            ["decimal-check", "--pack", str(PACK)],
            ["lineage", "--pack", str(PACK)],
            ["certify", "--pack", str(PACK)],
            ["self-test"],
            ["commands"],
            ["fixture-label", "--pack", str(PACK)],
            ["name-vs-ruler", "--pack", str(PACK)],
        ):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(command)
            self.assertEqual(code, 0, f"{command} {stderr.getvalue()}")
            self.assertIn("document_kind", json.loads(stdout.getvalue()))


if __name__ == "__main__":
    unittest.main()
