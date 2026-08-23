"""SOFTWARE CORRECTNESS — Phase 5 units 701–750 inspectability."""

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

from radar_v4.audit_bundle import write_audit_bundle
from radar_v4.audit_lock import (
    audit_lock,
    audit_lock_determinism,
    audit_status_bind,
    compare_audit_lock,
    verify_audit_record,
    write_audit_record,
)
from radar_v4.catalog_audit import audit_document_kinds, audit_reason_catalog
from radar_v4.chain_lock import (
    chain_lock,
    chain_lock_determinism,
    chain_status_bind,
    compare_chain_lock,
    verify_chain_record,
    write_chain_record,
)
from radar_v4.cli import main
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


class Units701To750Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("audit_lock", "chain_lock"):
            self.assertTrue(hasattr(package, name), name)
        for relative in ("radar_v4/audit_lock.py", "radar_v4/chain_lock.py"):
            py_compile(str(ROOT / relative), doraise=True)

    def test_highest_unit_is_750(self) -> None:
        self.assertEqual(PHASE5_HIGHEST_UNIT, 750)
        status = json.loads(workshop_status())
        self.assertEqual(status["highest_unit"], 750)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertEqual(stop["highest_unit"], 750)
        self.assertFalse(stop["vendor_authorized"])

    def test_synthetic_audit_and_chain(self) -> None:
        self.assertTrue(chain_lock(PACK).valid)
        self.assertTrue(chain_lock_determinism(PACK).valid)
        self.assertTrue(compare_chain_lock(PACK, PACK).valid)
        self.assertTrue(chain_status_bind(PACK).valid)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            chain_path = root / "chain-lock.json"
            written = write_chain_record(PACK, chain_path)
            self.assertTrue(written.valid)
            self.assertTrue(verify_chain_record(chain_path).valid)
            audit_dir = root / "audit"
            write_audit_bundle(PACK, audit_dir)
            self.assertTrue(audit_lock(audit_dir).valid)
            self.assertTrue(audit_lock_determinism(audit_dir).valid)
            self.assertTrue(compare_audit_lock(audit_dir, audit_dir).valid)
            self.assertTrue(audit_status_bind(audit_dir).valid)
            record = root / "audit-lock.json"
            written_audit = write_audit_record(audit_dir, record)
            self.assertTrue(written_audit.valid)
            self.assertTrue(verify_audit_record(record).valid)

    def test_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            empty = root / "empty"
            empty.mkdir()
            self.assertEqual(chain_lock(empty).error_code, "CHAIN_LAYOUT_REFUSED")
            extra = root / "extra"
            copytree(PACK, extra)
            (extra / "extra.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual(chain_lock(extra).error_code, "THREE_WAY_MISMATCH")
            kind = root / "kind.json"
            kind.write_text(
                '{"document_kind":"radar_v4.workshop_status","files":{"a":"'
                + ("0" * 64)
                + '"}}\n',
                encoding="utf-8",
            )
            self.assertEqual(audit_lock(kind).error_code, "AUDIT_KIND_REFUSED")
            empty_audit = root / "empty-audit.json"
            empty_audit.write_text(
                '{"document_kind":"radar_v4.audit_bundle","files":{}}\n',
                encoding="utf-8",
            )
            self.assertEqual(audit_lock(empty_audit).error_code, "AUDIT_EMPTY_REFUSED")
            audit_dir = root / "tamper"
            write_audit_bundle(PACK, audit_dir)
            target = audit_dir / "declaration.json"
            target.write_text(target.read_text(encoding="utf-8") + " \n", encoding="utf-8")
            self.assertEqual(audit_lock(audit_dir).error_code, "AUDIT_BUNDLE_MISMATCH")

    def test_catalogs(self) -> None:
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)

    def test_cli_new_commands(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            audit_dir = Path(raw) / "audit"
            write_audit_bundle(PACK, audit_dir)
            commands = (
                ["chain-lock", "--pack", str(PACK)],
                ["chain-eq", "--pack", str(PACK)],
                ["compare-chain-lock", "--left", str(PACK), "--right", str(PACK)],
                ["chain-status", "--pack", str(PACK)],
                ["audit-lock", "--path", str(audit_dir)],
                ["audit-eq", "--path", str(audit_dir)],
                ["compare-audit-lock", "--left", str(audit_dir), "--right", str(audit_dir)],
                ["audit-status", "--path", str(audit_dir)],
            )
            for command in commands:
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    code = main(command)
                self.assertEqual(code, 0, f"{command} {stderr.getvalue()}")
                self.assertIn("document_kind", json.loads(stdout.getvalue()))


if __name__ == "__main__":
    unittest.main()
