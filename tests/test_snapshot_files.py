"""SOFTWARE CORRECTNESS — Phase 5 local snapshot files. Not a vendor."""

from __future__ import annotations

import importlib
import tempfile
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.dataset import DatasetDeclaration
from radar_v4.evidence import ProvenanceClass
from radar_v4.observation import Observation, ObservationPayload
from radar_v4.session import run_dataset_session
from radar_v4.snapshot_files import (
    SnapshotFileError,
    read_snapshot_file,
    write_snapshot_file,
)
from tests.helpers import envelope


class SnapshotFileTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "write_snapshot_file"))
        self.assertTrue(hasattr(package, "read_snapshot_file"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "snapshot_files.py"), doraise=True)

    def test_write_and_read_round_trip(self) -> None:
        declaration = DatasetDeclaration(
            dataset_id="file.syn.1d",
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
        item = Observation.create(
            envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA"),
            ObservationPayload(close="1.00"),
        )
        session = run_dataset_session(declaration, (item.envelope,), (item,))

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "snap.json"
            written = write_snapshot_file(path, session.snapshot)
            self.assertEqual(written, path)
            loaded = read_snapshot_file(path)
            self.assertEqual(loaded.serialize(), session.snapshot.serialize())
            self.assertEqual(loaded.declaration.dataset_id, "file.syn.1d")
            self.assertEqual(loaded.observations[0].payload.close, "1.00")

    def test_unreadable_file_does_not_invent_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaises(SnapshotFileError) as ctx:
                read_snapshot_file(path)
            self.assertEqual(ctx.exception.code, "UNREADABLE_SNAPSHOT_FILE")

    def test_directory_path_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            declaration = DatasetDeclaration(
                dataset_id="dir.refused",
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
            item = Observation.create(
                envelope(provenance=ProvenanceClass.SYNTHETIC, symbol="SYN:AAA"),
                ObservationPayload(close="1.00"),
            )
            session = run_dataset_session(declaration, (item.envelope,), (item,))
            with self.assertRaises(SnapshotFileError) as ctx:
                write_snapshot_file(Path(tmp), session.snapshot)
            self.assertEqual(ctx.exception.code, "SNAPSHOT_PATH_IS_DIRECTORY")


if __name__ == "__main__":
    unittest.main()
