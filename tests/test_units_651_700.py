"""SOFTWARE CORRECTNESS — Phase 5 units 651–700 inspectability."""

from __future__ import annotations

import importlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from py_compile import compile as py_compile
from shutil import copy2

from radar_v4.bundle_lock import (
    bundle_lock,
    bundle_lock_determinism,
    bundle_status_bind,
    compare_bundle_lock,
    verify_bundle_record,
    write_bundle_record,
)
from radar_v4.bundle_verify import write_snapshot_bundle
from radar_v4.catalog_audit import audit_document_kinds, audit_reason_catalog
from radar_v4.cli import main
from radar_v4.export_lock import (
    compare_export_lock,
    export_lock,
    export_lock_determinism,
    export_status_bind,
    verify_export_record,
    write_export_record,
)
from radar_v4.local_session import run_session_from_pack
from radar_v4.pack_manifest import write_pack_manifest
from radar_v4.snapshot_files import write_snapshot_file
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


def _write_bundle(root: Path) -> Path:
    result = run_session_from_pack(PACK)
    assert result.session is not None
    snapshot = root / "snap.json"
    write_snapshot_bundle(snapshot, result.session.snapshot)
    return snapshot


class Units651To700Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("bundle_lock", "export_lock"):
            self.assertTrue(hasattr(package, name), name)
        for relative in ("radar_v4/bundle_lock.py", "radar_v4/export_lock.py"):
            py_compile(str(ROOT / relative), doraise=True)

    def test_highest_unit_is_700(self) -> None:
        self.assertEqual(PHASE5_HIGHEST_UNIT, 700)
        status = json.loads(workshop_status())
        self.assertEqual(status["highest_unit"], 700)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertEqual(stop["highest_unit"], 700)
        self.assertFalse(stop["vendor_authorized"])

    def test_synthetic_bundle_and_export(self) -> None:
        self.assertTrue(export_lock(PACK).valid)
        self.assertTrue(export_lock_determinism(PACK).valid)
        self.assertTrue(compare_export_lock(PACK, PACK).valid)
        self.assertTrue(export_status_bind(PACK).valid)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            export_path = root / "export-lock.json"
            written = write_export_record(PACK, export_path)
            self.assertTrue(written.valid)
            self.assertTrue(verify_export_record(export_path).valid)
            snapshot = _write_bundle(root)
            self.assertTrue(bundle_lock(snapshot).valid)
            self.assertTrue(bundle_lock_determinism(snapshot).valid)
            self.assertTrue(compare_bundle_lock(snapshot, snapshot).valid)
            self.assertTrue(bundle_status_bind(snapshot).valid)
            record = root / "bundle-lock.json"
            written_bundle = write_bundle_record(snapshot, record)
            self.assertTrue(written_bundle.valid)
            self.assertTrue(verify_bundle_record(record).valid)

    def test_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            empty = root / "empty"
            empty.mkdir()
            self.assertEqual(export_lock(empty).error_code, "EXPORT_LAYOUT_REFUSED")
            historical = root / "historical"
            historical.mkdir()
            declaration = json.loads((PACK / "declaration.json").read_text(encoding="utf-8"))
            declaration["provenance_class"] = "HISTORICAL"
            (historical / "declaration.json").write_text(
                json.dumps(declaration, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            copy2(PACK / "obs_2026-08-07.json", historical / "obs_2026-08-07.json")
            write_pack_manifest(historical)
            self.assertEqual(export_lock(historical).error_code, "EXPORT_PROVENANCE_REFUSED")
            result = run_session_from_pack(PACK)
            assert result.session is not None
            snap_only = root / "snap-only.json"
            write_snapshot_file(snap_only, result.session.snapshot)
            self.assertEqual(bundle_lock(snap_only).error_code, "BUNDLE_SIDECAR_MISSING")

    def test_catalogs(self) -> None:
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)

    def test_cli_new_commands(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            snapshot = _write_bundle(Path(raw))
            commands = (
                ["export-lock", "--pack", str(PACK)],
                ["export-eq", "--pack", str(PACK)],
                ["compare-export-lock", "--left", str(PACK), "--right", str(PACK)],
                ["export-status", "--pack", str(PACK)],
                ["bundle-lock", "--snapshot", str(snapshot)],
                ["bundle-eq", "--snapshot", str(snapshot)],
                ["compare-bundle-lock", "--left", str(snapshot), "--right", str(snapshot)],
                ["bundle-status", "--snapshot", str(snapshot)],
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
