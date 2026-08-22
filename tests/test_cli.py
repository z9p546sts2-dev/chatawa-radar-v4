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
