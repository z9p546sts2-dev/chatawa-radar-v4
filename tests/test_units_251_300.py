"""SOFTWARE CORRECTNESS — Phase 5 units 251–300 inspectability."""

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

from radar_v4.byte_check import (
    byte_check,
    claim_word_scan,
    count_check,
    filename_date_check,
    shebang_scan,
    trailing_whitespace_scan,
)
from radar_v4.catalog_audit import audit_document_kinds, audit_reason_catalog
from radar_v4.cli import main
from radar_v4.freeze import (
    certify_determinism,
    command_catalog_determinism,
    compare_certify,
    compare_freeze,
    compare_lineage,
    readme_unit_lock,
    self_test_determinism,
    verify_freeze_record,
    workshop_freeze,
    write_freeze_record,
)
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


class Units251To300Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("byte_check", "workshop_freeze"):
            self.assertTrue(hasattr(package, name), name)
        for relative in ("radar_v4/byte_check.py", "radar_v4/freeze.py"):
            py_compile(str(ROOT / relative), doraise=True)

    def test_highest_unit_is_at_least_300(self) -> None:
        self.assertGreaterEqual(PHASE5_HIGHEST_UNIT, 300)
        status = json.loads(workshop_status())
        self.assertGreaterEqual(status["highest_unit"], 300)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertGreaterEqual(stop["highest_unit"], 300)
        self.assertFalse(stop["vendor_authorized"])
        self.assertFalse(stop["paper_trading_authorized"])

    def test_synthetic_pack_byte_and_freeze(self) -> None:
        self.assertTrue(byte_check(PACK).valid, byte_check(PACK).serialize())
        self.assertTrue(filename_date_check(PACK).valid)
        self.assertTrue(count_check(PACK).valid)
        self.assertTrue(certify_determinism(PACK).valid)
        self.assertTrue(self_test_determinism().valid)
        self.assertTrue(command_catalog_determinism().valid)
        self.assertTrue(compare_certify(PACK, PACK).valid)
        self.assertTrue(compare_lineage(PACK, PACK).valid)
        self.assertTrue(readme_unit_lock().valid, readme_unit_lock().serialize())
        freeze = workshop_freeze(PACK)
        self.assertTrue(freeze.valid, freeze.serialize())

    def test_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            padded = root / "pad.json"
            padded.write_text('{"a":1}  \n', encoding="utf-8")
            self.assertEqual(trailing_whitespace_scan(root).error_code, "TRAILING_WHITESPACE")
            bang = root / "run.json"
            bang.write_bytes(b"#!/bin/sh\n")
            self.assertEqual(shebang_scan(root).error_code, "SHEBANG_REFUSED")
            claim = root / "claim.json"
            claim.write_text('{"note":"edge"}\n', encoding="utf-8")
            self.assertEqual(claim_word_scan(claim).error_code, "CLAIM_WORD_REFUSED")
            copied = Path(raw) / "copy"
            copytree(PACK, copied)
            (copied / "obs_1999-01-01.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual(filename_date_check(copied).error_code, "FILENAME_DATE_REFUSED")
            self.assertEqual(count_check(copied).error_code, "COUNT_MISMATCH")

    def test_freeze_write_and_catalogs(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "freeze.json"
            written = write_freeze_record(path, PACK)
            self.assertTrue(written.valid, written.serialize())
            self.assertTrue(verify_freeze_record(path).valid)
            text = path.read_text(encoding="utf-8")
            compared = compare_freeze(text, text)
            self.assertTrue(compared.valid)
            self.assertTrue(compared.details["same_freeze"])
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)

    def test_cli_new_commands(self) -> None:
        for command in (
            ["byte-check", "--pack", str(PACK)],
            ["filename-date", "--pack", str(PACK)],
            ["count-check", "--pack", str(PACK)],
            ["certify-eq", "--pack", str(PACK)],
            ["self-test-eq"],
            ["readme-lock"],
            ["freeze", "--pack", str(PACK)],
            ["compare-certify", "--left", str(PACK), "--right", str(PACK)],
        ):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(command)
            self.assertEqual(code, 0, f"{command} {stderr.getvalue()}")
            self.assertIn("document_kind", json.loads(stdout.getvalue()))


if __name__ == "__main__":
    unittest.main()
