"""SOFTWARE CORRECTNESS — Phase 5 units 551–600 inspectability."""

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
from radar_v4.disp_lock import (
    disposition_lock,
    disposition_lock_determinism,
    disposition_status_bind,
    verify_disposition_record,
    write_disposition_record,
)
from radar_v4.snapshot_lock import (
    compare_snapshot_lock,
    pack_snapshot_lock,
    snapshot_lock,
    snapshot_lock_determinism,
    snapshot_status_bind,
    verify_snapshot_record,
    write_snapshot_record,
)
from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT, workshop_status
from radar_v4.workshop_record import workshop_stop_record, write_disposition


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "fixtures" / "synthetic_one_symbol_1d"


class Units551To600Tests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        for name in ("snapshot_lock", "disposition_lock"):
            self.assertTrue(hasattr(package, name), name)
        for relative in ("radar_v4/snapshot_lock.py", "radar_v4/disp_lock.py"):
            py_compile(str(ROOT / relative), doraise=True)

    def test_highest_unit_is_600(self) -> None:
        self.assertEqual(PHASE5_HIGHEST_UNIT, 600)
        status = json.loads(workshop_status())
        self.assertEqual(status["highest_unit"], 600)
        self.assertFalse(status["measured"])
        self.assertNotIn("claim_level", status)
        stop = json.loads(workshop_stop_record())
        self.assertEqual(stop["highest_unit"], 600)
        self.assertFalse(stop["vendor_authorized"])

    def test_synthetic_snapshot_and_disposition(self) -> None:
        self.assertTrue(pack_snapshot_lock(PACK).valid)
        self.assertTrue(snapshot_lock_determinism(PACK).valid)
        self.assertTrue(compare_snapshot_lock(PACK, PACK).valid)
        self.assertTrue(snapshot_status_bind(PACK).valid)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            snap_path = root / "snap-lock.json"
            written = write_snapshot_record(PACK, snap_path)
            self.assertTrue(written.valid)
            self.assertTrue(verify_snapshot_record(snap_path).valid)
            disposition = root / "disposition.json"
            write_disposition(disposition, "UNREVIEWED")
            self.assertTrue(disposition_lock(disposition).valid)
            self.assertTrue(disposition_lock_determinism(disposition).valid)
            self.assertTrue(disposition_status_bind(disposition).valid)
            record = root / "disp-lock.json"
            written_disp = write_disposition_record(disposition, record)
            self.assertTrue(written_disp.valid)
            self.assertTrue(verify_disposition_record(record).valid)

    def test_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            empty = root / "empty.json"
            empty.write_text(
                '{"declaration":{"provenance_class":"SYNTHETIC"},"observations":[]}\n',
                encoding="utf-8",
            )
            self.assertEqual(snapshot_lock(empty).error_code, "SNAPSHOT_EMPTY_REFUSED")
            shape = root / "shape.json"
            shape.write_text('{"hello":"world"}\n', encoding="utf-8")
            self.assertEqual(snapshot_lock(shape).error_code, "SNAPSHOT_SHAPE_REFUSED")
            historical = root / "historical.json"
            historical.write_text(
                '{"declaration":{"provenance_class":"HISTORICAL"},"observations":[{"envelope":{},"payload":{}}]}\n',
                encoding="utf-8",
            )
            self.assertEqual(snapshot_lock(historical).error_code, "SNAPSHOT_PROVENANCE_REFUSED")
            edge = root / "edge.json"
            edge.write_text(
                '{"claim_level":"NONE","disposition":"EDGE","document_kind":"radar_v4.human_disposition","measured":false}\n',
                encoding="utf-8",
            )
            self.assertEqual(disposition_lock(edge).error_code, "FORBIDDEN_DISPOSITION")

    def test_catalogs(self) -> None:
        catalog = json.loads(audit_reason_catalog())
        self.assertTrue(catalog["valid"], catalog)
        kinds = json.loads(audit_document_kinds())
        self.assertTrue(kinds["valid"], kinds)

    def test_cli_new_commands(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            disposition = Path(raw) / "disposition.json"
            write_disposition(disposition, "ACKNOWLEDGED")
            commands = (
                ["snapshot-lock", "--pack", str(PACK)],
                ["snapshot-eq", "--pack", str(PACK)],
                ["compare-snapshot-lock", "--left", str(PACK), "--right", str(PACK)],
                ["snapshot-status", "--pack", str(PACK)],
                ["disp-lock", "--path", str(disposition)],
                ["disp-eq", "--path", str(disposition)],
                ["compare-disp-lock", "--left", str(disposition), "--right", str(disposition)],
                ["disp-status", "--path", str(disposition)],
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
