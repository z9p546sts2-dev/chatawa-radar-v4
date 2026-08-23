"""SOFTWARE CORRECTNESS — Phase 5 units 601–650 inspectability."""

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
from radar_v4.checksum_sidecar import sidecar_path, write_checksum_sidecar
from radar_v4.cli import main
from radar_v4.local_session import run_session_from_pack
from radar_v4.manifest_lock import (
    compare_manifest_lock,
    manifest_lock,
    manifest_lock_determinism,
    manifest_status_bind,
    verify_manifest_record,
    write_manifest_record,
)
from radar_v4.sidecar_lock import (
    compare_sidecar_lock,
    sidecar_lock,
    sidecar_lock_determinism,
    sidecar_snapshot_bind,
    sidecar_status_bind,
    verify_sidecar_record,
    write_sidecar_record,
)
from radar_v4.snapshot_files import write_snapshot_file
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


def _write_snapshot_sidecar(root: Path) -> tuple[Path, Path]:
    result = run_session_from_pack(PACK)
    assert result.session is not None
    snapshot = root / "snap.json"
    write_snapshot_file(snapshot, result.session.snapshot)
    sidecar = write_checksum_sidecar(snapshot)
    return snapshot, sidecar


class Units601To650Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("manifest_lock", "sidecar_lock"):
            self.assertTrue(hasattr(package, name), name)
        for relative in ("radar_v4/manifest_lock.py", "radar_v4/sidecar_lock.py"):
            py_compile(str(ROOT / relative), doraise=True)

    def test_highest_unit_is_650(self) -> None:
        self.assertEqual(PHASE5_HIGHEST_UNIT, 650)
        status = json.loads(workshop_status())
        self.assertEqual(status["highest_unit"], 650)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertEqual(stop["highest_unit"], 650)
        self.assertFalse(stop["vendor_authorized"])

    def test_synthetic_manifest_and_sidecar(self) -> None:
        self.assertTrue(manifest_lock(PACK).valid)
        self.assertTrue(manifest_lock_determinism(PACK).valid)
        self.assertTrue(compare_manifest_lock(PACK, PACK).valid)
        self.assertTrue(manifest_status_bind(PACK).valid)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest_path = root / "manifest-lock.json"
            written = write_manifest_record(PACK, manifest_path)
            self.assertTrue(written.valid)
            self.assertTrue(verify_manifest_record(manifest_path).valid)
            snapshot, sidecar = _write_snapshot_sidecar(root)
            self.assertTrue(sidecar_lock(sidecar).valid)
            self.assertTrue(sidecar_lock_determinism(sidecar).valid)
            self.assertTrue(compare_sidecar_lock(sidecar, sidecar).valid)
            self.assertTrue(sidecar_snapshot_bind(snapshot).valid)
            self.assertTrue(sidecar_status_bind(sidecar).valid)
            self.assertTrue(sidecar_status_bind(snapshot, snapshot=True).valid)
            record = root / "sidecar-lock.json"
            written_sidecar = write_sidecar_record(sidecar, record)
            self.assertTrue(written_sidecar.valid)
            self.assertTrue(verify_sidecar_record(record).valid)

    def test_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            empty = root / "empty.json"
            empty.write_text(
                '{"document_kind":"radar_v4.pack_manifest","files":{}}\n',
                encoding="utf-8",
            )
            self.assertEqual(manifest_lock(empty).error_code, "MANIFEST_EMPTY_REFUSED")
            kind = root / "kind.json"
            kind.write_text(
                '{"document_kind":"radar_v4.workshop_status","files":{"a":"'
                + ("0" * 64)
                + '"}}\n',
                encoding="utf-8",
            )
            self.assertEqual(manifest_lock(kind).error_code, "MANIFEST_KIND_REFUSED")
            digest = root / "digest.json"
            digest.write_text(
                '{"document_kind":"radar_v4.pack_manifest","files":{"a":"not-a-digest"}}\n',
                encoding="utf-8",
            )
            self.assertEqual(manifest_lock(digest).error_code, "MANIFEST_DIGEST_REFUSED")
            sidecar = root / "bad.sha256"
            sidecar.write_text("abc\n", encoding="utf-8")
            self.assertEqual(sidecar_lock(sidecar).error_code, "SIDECAR_DIGEST_REFUSED")
            snap_root = root / "ok"
            snap_root.mkdir()
            snapshot, _good = _write_snapshot_sidecar(snap_root)
            sidecar_path(snapshot).write_text(("f" * 64) + "\n", encoding="utf-8")
            self.assertEqual(
                sidecar_snapshot_bind(snapshot).error_code,
                "SIDECAR_SNAPSHOT_MISMATCH",
            )

    def test_catalogs(self) -> None:
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)

    def test_cli_new_commands(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            snapshot, sidecar = _write_snapshot_sidecar(Path(raw))
            commands = (
                ["manifest-lock", "--pack", str(PACK)],
                ["manifest-eq", "--pack", str(PACK)],
                ["compare-manifest-lock", "--left", str(PACK), "--right", str(PACK)],
                ["manifest-status", "--pack", str(PACK)],
                ["sidecar-lock", "--path", str(sidecar)],
                ["sidecar-eq", "--path", str(sidecar)],
                ["compare-sidecar-lock", "--left", str(sidecar), "--right", str(sidecar)],
                ["sidecar-status", "--path", str(sidecar)],
                ["sidecar-lock", "--snapshot", str(snapshot)],
                ["sidecar-status", "--snapshot", str(snapshot)],
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
