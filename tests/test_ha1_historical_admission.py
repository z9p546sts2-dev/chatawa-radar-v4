"""HA-1 R1.3 — HISTORICAL pack admission is off unless session asks for it.

HISTORICAL-labeled packs in this file are built only in temporary directories.
They are not market bytes and are not fixture files.
"""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from radar_v4.cli import main
from radar_v4.dataset_pack import (
    DATASET_PACK_ALLOWED_PROVENANCE,
    DatasetPackReport,
    load_dataset_pack,
)
from radar_v4.evidence import ProvenanceClass
from radar_v4.export_lock import export_provenance_scan
from radar_v4.fixture_pack import PACK_ALLOWED_PROVENANCE, load_fixture_pack
from radar_v4.local_session import run_session_from_pack
from radar_v4.observation import Observation, ObservationPayload
from radar_v4.pack_export import PackExportError, export_snapshot_to_pack
from radar_v4.record_check import inspect_unexpected_files
from radar_v4.session_report import serialize_local_session_report
from radar_v4.snapshot_files import write_snapshot_file
from radar_v4.snapshot_lock import snapshot_lock
from tests.helpers import envelope


def _declaration(provenance: str, universe: str) -> dict[str, object]:
    return {
        "dataset_id": "ha1-temp-pack",
        "provenance_class": provenance,
        "provider": "PHASE5_SOURCE",
        "universe": universe,
        "interval": "1d",
        "timezone": "UTC",
        "transformation_version": "phase5-v1",
        "adjustment_policy": "UNADJUSTED",
        "locked_question": "ordinary close-to-close changes for one symbol",
        "primary_metric": "close-to-close difference",
    }


def _obs(day: int, close: str, provenance: ProvenanceClass, symbol: str) -> Observation:
    return Observation.create(
        envelope(provenance=provenance, symbol=symbol, day=day),
        ObservationPayload(close=close),
    )


def _write_obs(path: Path, item: Observation) -> None:
    path.write_text(
        json.dumps(
            {
                "envelope": item.envelope.serialize(),
                "payload": item.payload.canonical_payload(),
            }
        ),
        encoding="utf-8",
    )


def _write_pack(
    root: Path,
    declaration_provenance: str,
    observations: tuple[Observation, ...],
    *,
    universe: str,
) -> None:
    (root / "declaration.json").write_text(
        json.dumps(_declaration(declaration_provenance, universe)),
        encoding="utf-8",
    )
    for index, item in enumerate(observations, start=1):
        _write_obs(root / f"obs_{index:04d}.json", item)


class HistoricalAdmissionTests(unittest.TestCase):
    def test_flag_off_refuses_historical_pack(self) -> None:
        first = _obs(7, "10.00", ProvenanceClass.HISTORICAL, "HIST:AAA")
        second = _obs(8, "12.00", ProvenanceClass.HISTORICAL, "HIST:AAA")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            _write_pack(
                root,
                "HISTORICAL",
                (first, second),
                universe="HIST:AAA",
            )
            report = load_dataset_pack(root)
            session = run_session_from_pack(root)
            stderr = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                code = main(["session", "--pack", str(root)])
        self.assertFalse(report.usable())
        self.assertEqual(
            [issue.code for issue in report.pack_issues],
            ["PACK_PROVENANCE_NOT_ALLOWED"],
        )
        self.assertEqual(session.error_code, "PACK_NOT_USABLE")
        self.assertIsNone(session.session)
        self.assertEqual(code, 2)
        self.assertIn("PACK_PROVENANCE_NOT_ALLOWED", stderr.getvalue())

    def test_flag_on_loads_and_session_measures_historical_pack(self) -> None:
        first = _obs(7, "10.00", ProvenanceClass.HISTORICAL, "HIST:AAA")
        second = _obs(8, "12.00", ProvenanceClass.HISTORICAL, "HIST:AAA")
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            report_path = Path(raw) / "session_report.json"
            _write_pack(
                root,
                "HISTORICAL",
                (first, second),
                universe="HIST:AAA",
            )
            loaded = load_dataset_pack(root, allow_historical=True)
            result = run_session_from_pack(root, allow_historical=True)
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(
                    [
                        "session",
                        "--pack",
                        str(root),
                        "--allow-historical",
                        "--report",
                        str(report_path),
                    ]
                )
            self.assertEqual(code, 0, stderr.getvalue())
            self.assertFalse(repo in report_path.resolve().parents)
            self.assertTrue(report_path.is_file())
            written = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertTrue(loaded.usable())
        self.assertEqual(loaded.observation_intake.accepted_count(), 2)
        self.assertIsNone(result.error_code)
        assert result.session is not None and result.session.baseline is not None
        self.assertEqual(result.session.baseline.status, "MEASURED")
        self.assertEqual(result.session.baseline.claim_level, "LEVEL 0 — MEASURED")
        self.assertEqual(result.session.baseline.changes, ("2.00",))
        self.assertEqual(written["session"]["baseline"]["status"], "MEASURED")
        self.assertEqual(written["session"]["baseline"]["changes"], ["2.00"])

    def test_flag_on_refuses_live(self) -> None:
        live_declaration = _obs(7, "10.00", ProvenanceClass.LIVE, "LIVE:AAA")
        historical = _obs(7, "10.00", ProvenanceClass.HISTORICAL, "HIST:AAA")
        live_row = _obs(8, "11.00", ProvenanceClass.LIVE, "HIST:AAA")
        with tempfile.TemporaryDirectory() as raw:
            declared = Path(raw) / "declared"
            declared.mkdir()
            _write_pack(
                declared,
                "LIVE",
                (live_declaration,),
                universe="LIVE:AAA",
            )
            declaration_report = load_dataset_pack(declared, allow_historical=True)
            mixed = Path(raw) / "mixed"
            mixed.mkdir()
            _write_pack(
                mixed,
                "HISTORICAL",
                (historical, live_row),
                universe="HIST:AAA",
            )
            mixed_report = load_dataset_pack(mixed, allow_historical=True)
        self.assertFalse(declaration_report.usable())
        self.assertIn(
            "PACK_PROVENANCE_NOT_ALLOWED",
            [issue.code for issue in declaration_report.pack_issues],
        )
        self.assertTrue(mixed_report.usable())
        self.assertEqual(mixed_report.observation_intake.accepted_count(), 1)
        self.assertEqual(
            mixed_report.observation_intake.accepted[0].envelope.provenance_class,
            "HISTORICAL",
        )
        self.assertIn(
            "PACK_PROVENANCE_NOT_ALLOWED",
            mixed_report.observation_intake.quarantined[0].validation.issue_codes(),
        )
        self.assertEqual(
            mixed_report.observation_intake.quarantined[0].observation.envelope.provenance_class,
            "LIVE",
        )

    def test_load_fixture_pack_refuses_historical(self) -> None:
        historical = envelope(
            provenance=ProvenanceClass.HISTORICAL,
            symbol="HIST:PACK",
        )
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "historical.json"
            path.write_text(historical.serialize(), encoding="utf-8")
            report = load_fixture_pack(raw)
        self.assertEqual(report.accepted_count(), 0)
        self.assertEqual(report.quarantined_count(), 1)
        self.assertIn(
            "PACK_PROVENANCE_NOT_ALLOWED",
            report.quarantined[0].validation.issue_codes(),
        )
        self.assertEqual(PACK_ALLOWED_PROVENANCE, frozenset({"FIXTURE", "SYNTHETIC"}))
        self.assertEqual(
            DATASET_PACK_ALLOWED_PROVENANCE,
            frozenset({"FIXTURE", "SYNTHETIC", "HISTORICAL"}),
        )
        self.assertNotIn("LIVE", DATASET_PACK_ALLOWED_PROVENANCE)

    def test_fixture_and_synthetic_are_identical_with_or_without_flag(self) -> None:
        cases = (
            (ProvenanceClass.FIXTURE, "FIXTURE:AAA"),
            (ProvenanceClass.SYNTHETIC, "SYN:AAA"),
        )
        for provenance, symbol in cases:
            first = _obs(7, "10.00", provenance, symbol)
            second = _obs(8, "10.50", provenance, symbol)
            with self.subTest(provenance=provenance.value):
                with tempfile.TemporaryDirectory() as raw:
                    root = Path(raw)
                    _write_pack(
                        root,
                        provenance.value,
                        (first, second),
                        universe=symbol,
                    )
                    off = load_dataset_pack(root)
                    on = load_dataset_pack(root, allow_historical=True)
                    session_off = run_session_from_pack(root)
                    session_on = run_session_from_pack(root, allow_historical=True)
                self.assertEqual(_signature(off), _signature(on))
                self.assertEqual(
                    serialize_local_session_report(session_off),
                    serialize_local_session_report(session_on),
                )
                assert session_off.session is not None
                assert session_off.session.baseline is not None
                self.assertEqual(session_off.session.baseline.status, "MEASURED")
                self.assertEqual(session_off.session.baseline.changes, ("0.50",))

    def test_historical_declaration_with_fixture_observations_is_refused(self) -> None:
        first = _obs(7, "10.00", ProvenanceClass.FIXTURE, "HIST:AAA")
        second = _obs(8, "12.00", ProvenanceClass.FIXTURE, "HIST:AAA")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            _write_pack(root, "HISTORICAL", (first, second), universe="HIST:AAA")
            loaded = load_dataset_pack(root, allow_historical=True)
            result = run_session_from_pack(root, allow_historical=True)
        self.assertEqual(loaded.observation_intake.accepted_count(), 2)
        assert result.session is not None and result.session.baseline is not None
        self.assertEqual(result.session.kept_observation_count(), 0)
        self.assertNotEqual(result.session.baseline.status, "MEASURED")
        self.assertIn(
            "DATASET_DECLARATION_MISMATCH",
            result.session.admission.quarantined[0].validation.issue_codes(),
        )

    def test_fixture_declaration_with_historical_observations_is_refused(self) -> None:
        first = _obs(7, "10.00", ProvenanceClass.HISTORICAL, "FIXTURE:AAA")
        second = _obs(8, "12.00", ProvenanceClass.HISTORICAL, "FIXTURE:AAA")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            _write_pack(root, "FIXTURE", (first, second), universe="FIXTURE:AAA")
            loaded = load_dataset_pack(root, allow_historical=True)
            result = run_session_from_pack(root, allow_historical=True)
        self.assertEqual(loaded.observation_intake.accepted_count(), 2)
        assert result.session is not None and result.session.baseline is not None
        self.assertEqual(result.session.kept_observation_count(), 0)
        self.assertNotEqual(result.session.baseline.status, "MEASURED")
        self.assertIn(
            "DATASET_DECLARATION_MISMATCH",
            result.session.admission.quarantined[0].validation.issue_codes(),
        )

    def test_csv_in_pack_is_refused(self) -> None:
        item = _obs(7, "10.00", ProvenanceClass.HISTORICAL, "HIST:AAA")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            _write_pack(root, "HISTORICAL", (item,), universe="HIST:AAA")
            (root / "prices.csv").write_text("Date,Close\n2026-08-07,10\n", encoding="utf-8")
            check = inspect_unexpected_files(root)
            loaded = load_dataset_pack(root, allow_historical=True)
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                code = main(["unexpected-files", "--pack", str(root)])
        self.assertFalse(check.valid)
        self.assertEqual(check.error_code, "UNEXPECTED_PACK_FILE")
        self.assertIn("prices.csv", check.details["files"])
        self.assertEqual(loaded.observation_intake.accepted_count(), 1)
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(stdout.getvalue())["error_code"], "UNEXPECTED_PACK_FILE")

    def test_allow_historical_with_snapshot_is_refused(self) -> None:
        first = _obs(7, "10.00", ProvenanceClass.HISTORICAL, "HIST:AAA")
        second = _obs(8, "12.00", ProvenanceClass.HISTORICAL, "HIST:AAA")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "pack"
            root.mkdir()
            snapshot = Path(raw) / "snapshot.json"
            _write_pack(root, "HISTORICAL", (first, second), universe="HIST:AAA")
            stderr = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                code = main(
                    [
                        "session",
                        "--pack",
                        str(root),
                        "--allow-historical",
                        "--snapshot",
                        str(snapshot),
                    ]
                )
            self.assertEqual(code, 2)
            self.assertIn("SNAPSHOT_PROVENANCE_REFUSED", stderr.getvalue())
            self.assertFalse(snapshot.exists())

            measured = run_session_from_pack(root, allow_historical=True)
            assert measured.session is not None
            written = Path(raw) / "direct-snapshot.json"
            write_snapshot_file(written, measured.session.snapshot)
            locked = snapshot_lock(written)
            self.assertFalse(locked.valid)
            self.assertEqual(locked.error_code, "SNAPSHOT_PROVENANCE_REFUSED")
            scan = export_provenance_scan(root)
            self.assertFalse(scan.valid)
            self.assertEqual(scan.error_code, "EXPORT_PROVENANCE_REFUSED")
            with self.assertRaises(PackExportError) as ctx:
                export_snapshot_to_pack(measured.session.snapshot, Path(raw) / "exported")
            self.assertEqual(ctx.exception.code, "PACK_PROVENANCE_NOT_ALLOWED")

            export_err = io.StringIO()
            with redirect_stderr(export_err):
                with self.assertRaises(SystemExit) as export_exit:
                    main(
                        [
                            "export-pack",
                            "--snapshot",
                            str(written),
                            "--out",
                            str(Path(raw) / "via-cli"),
                            "--allow-historical",
                        ]
                    )
            self.assertEqual(export_exit.exception.code, 2)
            lock_err = io.StringIO()
            with redirect_stderr(lock_err):
                with self.assertRaises(SystemExit) as lock_exit:
                    main(
                        [
                            "export-lock",
                            "--pack",
                            str(root),
                            "--allow-historical",
                        ]
                    )
            self.assertEqual(lock_exit.exception.code, 2)


def _signature(report: DatasetPackReport) -> tuple[object, ...]:
    pack_issues = tuple(
        (issue.code, issue.reason, issue.field) for issue in report.pack_issues
    )
    accepted = tuple(
        item.envelope.checksum for item in report.observation_intake.accepted
    )
    quarantined = tuple(
        record.validation.issue_codes()
        for record in report.observation_intake.quarantined
    )
    return (report.usable(), pack_issues, accepted, quarantined)


if __name__ == "__main__":
    unittest.main()
