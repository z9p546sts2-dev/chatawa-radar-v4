"""SOFTWARE CORRECTNESS — Phase 5 units 751–800 inspectability."""

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
from radar_v4.cli import main
from radar_v4.inventory_lock import (
    compare_inventory_lock,
    inventory_lock,
    inventory_lock_determinism,
    inventory_status_bind,
    verify_inventory_record,
    write_inventory_record,
)
from radar_v4.layout_lock import (
    compare_layout_lock,
    layout_lock,
    layout_lock_determinism,
    layout_status_bind,
    verify_layout_record,
    write_layout_record,
)
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


class Units751To800Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("inventory_lock", "layout_lock"):
            self.assertTrue(hasattr(package, name), name)
        for relative in ("radar_v4/inventory_lock.py", "radar_v4/layout_lock.py"):
            py_compile(str(ROOT / relative), doraise=True)

    def test_highest_unit_is_800(self) -> None:
        self.assertGreaterEqual(PHASE5_HIGHEST_UNIT, 800)
        status = json.loads(workshop_status())
        self.assertGreaterEqual(status["highest_unit"], 800)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertGreaterEqual(stop["highest_unit"], 800)
        self.assertFalse(stop["vendor_authorized"])

    def test_synthetic_inventory_and_layout(self) -> None:
        self.assertTrue(inventory_lock(PACK).valid)
        self.assertTrue(inventory_lock_determinism(PACK).valid)
        self.assertTrue(compare_inventory_lock(PACK, PACK).valid)
        self.assertTrue(inventory_status_bind(PACK).valid)
        self.assertTrue(layout_lock(PACK).valid)
        self.assertTrue(layout_lock_determinism(PACK).valid)
        self.assertTrue(compare_layout_lock(PACK, PACK).valid)
        self.assertTrue(layout_status_bind(PACK).valid)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            inv_path = root / "inventory-lock.json"
            written = write_inventory_record(PACK, inv_path)
            self.assertTrue(written.valid)
            self.assertTrue(verify_inventory_record(inv_path).valid)
            layout_path = root / "layout-lock.json"
            written_layout = write_layout_record(PACK, layout_path)
            self.assertTrue(written_layout.valid)
            self.assertTrue(verify_layout_record(layout_path).valid)

    def test_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            empty = root / "empty"
            empty.mkdir()
            self.assertEqual(inventory_lock(empty).error_code, "INVENTORY_DECLARATION_REFUSED")
            self.assertEqual(layout_lock(empty).error_code, "LAYOUT_DECLARATION_MISSING")
            declaration_only = root / "decl-only"
            declaration_only.mkdir()
            (declaration_only / "declaration.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual(
                inventory_lock(declaration_only).error_code,
                "INVENTORY_EMPTY_REFUSED",
            )
            self.assertEqual(layout_lock(declaration_only).error_code, "LAYOUT_NO_OBSERVATIONS")
            hidden = root / "hidden"
            copytree(PACK, hidden)
            (hidden / ".secret.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual(inventory_lock(hidden).error_code, "INVENTORY_HIDDEN_REFUSED")
            no_manifest = root / "no-manifest"
            copytree(PACK, no_manifest)
            (no_manifest / "manifest.json").unlink()
            self.assertTrue(inventory_lock(no_manifest).valid)
            self.assertEqual(layout_lock(no_manifest).error_code, "LAYOUT_MANIFEST_REFUSED")

    def test_catalogs(self) -> None:
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)

    def test_cli_new_commands(self) -> None:
        commands = (
            ["inventory-lock", "--pack", str(PACK)],
            ["inventory-eq", "--pack", str(PACK)],
            ["compare-inventory-lock", "--left", str(PACK), "--right", str(PACK)],
            ["inventory-status", "--pack", str(PACK)],
            ["layout-lock", "--pack", str(PACK)],
            ["layout-eq", "--pack", str(PACK)],
            ["compare-layout-lock", "--left", str(PACK), "--right", str(PACK)],
            ["layout-status", "--pack", str(PACK)],
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
