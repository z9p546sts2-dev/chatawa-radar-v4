"""SOFTWARE CORRECTNESS — Phase 5 ruler sidecar."""

from __future__ import annotations

import importlib
import tempfile
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.dataset import DatasetDeclaration
from radar_v4.evidence import ProvenanceClass
from radar_v4.ruler import ruler_checksum
from radar_v4.ruler_file import read_ruler_sidecar, write_ruler_sidecar


class RulerFileTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "write_ruler_sidecar"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "ruler_file.py"), doraise=True)

    def test_write_and_read(self) -> None:
        declaration = DatasetDeclaration(
            dataset_id="phase5-ruler-file",
            provenance_class=ProvenanceClass.SYNTHETIC.value,
            provider="PHASE5_SOURCE",
            universe="SYN:AAA",
            interval="1d",
            timezone="UTC",
            transformation_version="phase5-v1",
            adjustment_policy="UNADJUSTED",
            locked_question="ordinary close-to-close changes for one symbol",
            primary_metric="close-to-close difference",
        )
        with tempfile.TemporaryDirectory() as raw:
            snapshot = Path(raw) / "snap.json"
            written = write_ruler_sidecar(snapshot, declaration)
            loaded = read_ruler_sidecar(snapshot)
        self.assertEqual(written.name, "snap.json.ruler.json")
        self.assertEqual(loaded["ruler_checksum"], ruler_checksum(declaration))
        self.assertEqual(loaded["document_kind"], "radar_v4.ruler")


if __name__ == "__main__":
    unittest.main()
