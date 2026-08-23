"""SOFTWARE CORRECTNESS — Phase 5 local CLI. No network."""

from __future__ import annotations

import importlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.cli import main


class CliTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4.cli")
        self.assertTrue(hasattr(package, "main"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "cli.py"), doraise=True)
        py_compile(str(root / "radar_v4" / "__main__.py"), doraise=True)

    def test_session_on_repo_synthetic_pack(self) -> None:
        root = Path(__file__).resolve().parents[1]
        pack = root / "fixtures" / "synthetic_one_symbol_1d"
        with tempfile.TemporaryDirectory() as raw:
            snapshot = Path(raw) / "snapshot.json"
            report = Path(raw) / "session_report.json"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(
                    [
                        "session",
                        "--pack",
                        str(pack),
                        "--snapshot",
                        str(snapshot),
                        "--report",
                        str(report),
                    ]
                )
            self.assertEqual(code, 0, stderr.getvalue())
            document = json.loads(stdout.getvalue())
            self.assertTrue(document["pack_usable"])
            session = document["session"]
            self.assertEqual(session["baseline"]["status"], "MEASURED")
            self.assertEqual(session["baseline"]["changes"], ["0.50", "-0.50"])
            self.assertEqual(len(session["baseline"]["change_records"]), 2)
            self.assertEqual(len(session["snapshot_checksum"]), 64)
            self.assertTrue(snapshot.is_file())
            self.assertTrue(report.is_file())

            replay_out = io.StringIO()
            with redirect_stdout(replay_out), redirect_stderr(io.StringIO()):
                replay_code = main(["replay", "--snapshot", str(snapshot)])
            self.assertEqual(replay_code, 0)
            replayed = json.loads(replay_out.getvalue())
            self.assertEqual(replayed["snapshot_checksum"], session["snapshot_checksum"])

            compare_out = io.StringIO()
            with redirect_stdout(compare_out), redirect_stderr(io.StringIO()):
                compare_code = main(
                    ["compare", "--left", str(snapshot), "--right", str(snapshot)]
                )
            self.assertEqual(compare_code, 0)
            self.assertTrue(json.loads(compare_out.getvalue())["equal"])

            verify_out = io.StringIO()
            with redirect_stdout(verify_out), redirect_stderr(io.StringIO()):
                verify_code = main(
                    [
                        "verify",
                        "--snapshot",
                        str(snapshot),
                        "--expect-checksum",
                        session["snapshot_checksum"],
                    ]
                )
            self.assertEqual(verify_code, 0)
            self.assertTrue(json.loads(verify_out.getvalue())["matched"])

            export_dir = Path(raw) / "exported"
            export_err = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(export_err):
                export_code = main(
                    [
                        "export-pack",
                        "--snapshot",
                        str(snapshot),
                        "--out",
                        str(export_dir),
                    ]
                )
            self.assertEqual(export_code, 0, export_err.getvalue())
            self.assertTrue((export_dir / "declaration.json").is_file())

            codes_out = io.StringIO()
            with redirect_stdout(codes_out), redirect_stderr(io.StringIO()):
                self.assertEqual(main(["codes"]), 0)
            self.assertIn("RULER_MISMATCH", json.loads(codes_out.getvalue())["codes"])

            sidecar_err = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(sidecar_err):
                sidecar_code = main(
                    ["verify", "--snapshot", str(snapshot), "--write-sidecar"]
                )
            self.assertEqual(sidecar_code, 0, sidecar_err.getvalue())
            self.assertTrue((Path(str(snapshot) + ".sha256")).is_file())

            journal = Path(raw) / "journal.json"
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(
                    main(["quarantine", "--pack", str(pack), "--out", str(journal)]),
                    0,
                )
            self.assertTrue(journal.is_file())

            registry_path = Path(raw) / "registry.json"
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(
                    main(
                        [
                            "registry-write",
                            "--snapshot",
                            str(snapshot),
                            "--out",
                            str(registry_path),
                        ]
                    ),
                    0,
                )
            self.assertTrue(registry_path.is_file())

            mismatch = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(mismatch):
                mismatch_code = main(
                    [
                        "replay",
                        "--snapshot",
                        str(snapshot),
                        "--expect-ruler",
                        "0" * 64,
                    ]
                )
            self.assertEqual(mismatch_code, 1)
            self.assertIn("RULER_MISMATCH", mismatch.getvalue())

            ruler_out = io.StringIO()
            with redirect_stdout(ruler_out), redirect_stderr(io.StringIO()):
                self.assertEqual(main(["show-ruler", "--pack", str(pack)]), 0)
            self.assertEqual(
                json.loads(ruler_out.getvalue())["document_kind"], "radar_v4.ruler"
            )
            verify_pack = io.StringIO()
            with redirect_stdout(verify_pack), redirect_stderr(io.StringIO()):
                self.assertEqual(main(["pack-verify", "--pack", str(pack)]), 0)
            self.assertIn("declaration.json", json.loads(verify_pack.getvalue())["files"])

            required = io.StringIO()
            with redirect_stdout(required), redirect_stderr(io.StringIO()):
                self.assertEqual(
                    main(["session", "--pack", str(pack), "--require-manifest"]),
                    0,
                )
            self.assertTrue(json.loads(required.getvalue())["pack_usable"])

            compare_pack = io.StringIO()
            with redirect_stdout(compare_pack), redirect_stderr(io.StringIO()):
                self.assertEqual(
                    main(["pack-compare", "--left", str(pack), "--right", str(pack)]),
                    0,
                )
            self.assertTrue(json.loads(compare_pack.getvalue())["equal"])

            bad_ruler = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(bad_ruler):
                self.assertEqual(
                    main(
                        [
                            "session",
                            "--pack",
                            str(pack),
                            "--expect-ruler",
                            "0" * 64,
                        ]
                    ),
                    2,
                )
            self.assertIn("RULER_MISMATCH", bad_ruler.getvalue())

            inventory_out = io.StringIO()
            with redirect_stdout(inventory_out), redirect_stderr(io.StringIO()):
                self.assertEqual(main(["pack-inventory", "--pack", str(pack)]), 0)
            listed = json.loads(inventory_out.getvalue())
            self.assertEqual(listed["document_kind"], "radar_v4.pack_inventory")
            self.assertEqual(listed["observation_count"], 3)

            bundle_out = io.StringIO()
            bundle_err = io.StringIO()
            with redirect_stdout(bundle_out), redirect_stderr(bundle_err):
                bundle_code = main(
                    [
                        "bundle-verify",
                        "--snapshot",
                        str(snapshot),
                        "--require-ruler",
                    ]
                )
            self.assertEqual(bundle_code, 0, bundle_err.getvalue())
            self.assertTrue(json.loads(bundle_out.getvalue())["matched"])

            exists = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(exists):
                self.assertEqual(
                    main(["session", "--pack", str(pack), "--snapshot", str(snapshot)]),
                    2,
                )
            self.assertIn("FILE_EXISTS", exists.getvalue())
            replaced = io.StringIO()
            with redirect_stdout(replaced), redirect_stderr(io.StringIO()):
                self.assertEqual(
                    main(
                        [
                            "session",
                            "--pack",
                            str(pack),
                            "--snapshot",
                            str(snapshot),
                            "--replace",
                        ]
                    ),
                    0,
                )
            self.assertTrue(json.loads(replaced.getvalue())["pack_usable"])

            exists_bundle = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(exists_bundle):
                self.assertEqual(
                    main(["write-bundle", "--snapshot", str(snapshot)]),
                    2,
                )
            self.assertIn("FILE_EXISTS", exists_bundle.getvalue())
            bundle_write = io.StringIO()
            with redirect_stdout(bundle_write), redirect_stderr(io.StringIO()):
                self.assertEqual(
                    main(["write-bundle", "--snapshot", str(snapshot), "--replace"]),
                    0,
                )
            self.assertTrue(json.loads(bundle_write.getvalue())["matched"])

            report_out = io.StringIO()
            with redirect_stdout(report_out), redirect_stderr(io.StringIO()):
                self.assertEqual(main(["show-report", "--report", str(report)]), 0)
            self.assertEqual(
                json.loads(report_out.getvalue())["document_kind"],
                "radar_v4.local_session_report",
            )

            journal_out = io.StringIO()
            with redirect_stdout(journal_out), redirect_stderr(io.StringIO()):
                self.assertEqual(main(["show-journal", "--journal", str(journal)]), 0)
            self.assertEqual(
                json.loads(journal_out.getvalue())["document_kind"],
                "radar_v4.quarantine_journal",
            )

            status_out = io.StringIO()
            with redirect_stdout(status_out), redirect_stderr(io.StringIO()):
                self.assertEqual(main(["status"]), 0)
            self.assertEqual(
                json.loads(status_out.getvalue())["highest_unit"],
                1050,
            )
            describe_out = io.StringIO()
            with redirect_stdout(describe_out), redirect_stderr(io.StringIO()):
                self.assertEqual(main(["pack-describe", "--pack", str(pack)]), 0)
            self.assertEqual(
                json.loads(describe_out.getvalue())["document_kind"],
                "radar_v4.pack_describe",
            )
            admission_out = io.StringIO()
            with redirect_stdout(admission_out), redirect_stderr(io.StringIO()):
                self.assertEqual(main(["admission", "--pack", str(pack)]), 0)
            self.assertFalse(json.loads(admission_out.getvalue())["measured"])
            determinism_out = io.StringIO()
            with redirect_stdout(determinism_out), redirect_stderr(io.StringIO()):
                self.assertEqual(main(["determinism", "--pack", str(pack)]), 0)
            self.assertTrue(json.loads(determinism_out.getvalue())["equal"])

    def test_missing_pack_exits_without_inventing_session(self) -> None:
        stderr = io.StringIO()
        stdout = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(["session", "--pack", "/tmp/radar-v4-no-such-cli-pack"])
        self.assertEqual(code, 2)
        self.assertIn("PACK_NOT_USABLE", stderr.getvalue())
        self.assertEqual(stdout.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
