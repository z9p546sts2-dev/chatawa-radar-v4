"""Software conversion: synthetic Stooq-shaped CSV → strict HISTORICAL pack.

Numbers in the fixture are fake. This file does not accept a MEASURED market
run and does not claim adjustment_policy was verified.
"""

from __future__ import annotations

import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from radar_v4.cli import main as workshop_main
from radar_v4.dataset_pack import load_dataset_pack
from radar_v4.evidence import format_canonical_timestamp
from radar_v4.local_session import run_session_from_pack
from radar_v4.observation import Observation, ObservationPayload
from radar_v4.record_check import inspect_unexpected_files

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "stooq_to_strict_pack.py"
FIXTURE = ROOT / "tests" / "fixtures" / "stooq_shaped" / "spy_synthetic_daily.csv"
RETRIEVED_AT = "2026-12-01T16:30:00-05:00"
SYNTHETIC_POLICY = "SYNTHETIC_TEST_POLICY"


def load_converter():
    spec = importlib.util.spec_from_file_location("stooq_to_strict_pack", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("converter module could not be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CONVERTER = load_converter()


def expected_market(day: str) -> str:
    year, month, day_number = (int(part) for part in day.split("-"))
    stamp = datetime(year, month, day_number, 16, 0, 0, tzinfo=ZoneInfo("America/New_York"))
    return format_canonical_timestamp(stamp)


class StooqStrictPackTests(unittest.TestCase):
    def convert(self, out: Path, csv_path: Path = FIXTURE, **overrides: str) -> int:
        args = [
            "--csv",
            str(csv_path),
            "--out",
            str(out),
            "--symbol",
            overrides.get("symbol", "SPY"),
            "--provider",
            overrides.get("provider", "STOOQ"),
        ]
        if "retrieved_at" not in overrides:
            args.extend(["--retrieved-at", RETRIEVED_AT])
        elif overrides["retrieved_at"] is not None:
            args.extend(["--retrieved-at", overrides["retrieved_at"]])
        if "adjustment_policy" not in overrides:
            args.extend(["--adjustment-policy", SYNTHETIC_POLICY])
        elif overrides["adjustment_policy"] is not None:
            args.extend(["--adjustment-policy", overrides["adjustment_policy"]])
        if "dataset_id" in overrides:
            args.extend(["--dataset-id", overrides["dataset_id"]])
        if "max_staleness" in overrides:
            args.extend(["--max-staleness", overrides["max_staleness"]])
        return CONVERTER.main(args)

    def test_fixture_is_synthetic_and_loads(self) -> None:
        text = FIXTURE.read_text(encoding="utf-8")
        self.assertIn("100.00", text)
        self.assertNotIn("stooq.com", text.casefold())
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw) / "pack"
            code = self.convert(out)
            self.assertEqual(code, 0)
            names = sorted(path.name for path in out.iterdir())
            self.assertEqual(
                names,
                [
                    "declaration.json",
                    "obs_0001.json",
                    "obs_0002.json",
                    "obs_0003.json",
                    "obs_0004.json",
                    "obs_0005.json",
                    "obs_0006.json",
                    "obs_0007.json",
                ],
            )
            declaration = json.loads((out / "declaration.json").read_text(encoding="utf-8"))
            self.assertEqual(declaration["provenance_class"], "HISTORICAL")
            self.assertEqual(declaration["provider"], "STOOQ")
            self.assertEqual(declaration["universe"], "SPY")
            self.assertEqual(declaration["interval"], "1d")
            self.assertEqual(declaration["timezone"], "America/New_York")
            self.assertEqual(declaration["transformation_version"], "stooq-daily-ohlcv-v1")
            self.assertEqual(declaration["primary_metric"], "close-to-close difference")
            self.assertEqual(
                declaration["locked_question"],
                "ordinary close-to-close changes for one symbol",
            )
            self.assertEqual(declaration["adjustment_policy"], SYNTHETIC_POLICY)
            self.assertEqual(declaration["dataset_id"], "spy-stooq-ha1-private")
            self.assertNotIn("max_staleness", declaration)

            loaded = load_dataset_pack(out, allow_historical=True)
            self.assertTrue(loaded.usable())
            self.assertEqual(loaded.observation_intake.accepted_count(), 7)
            self.assertEqual(loaded.observation_intake.quarantined_count(), 0)
            self.assertEqual(loaded.observation_intake.unreadable_count(), 0)
            unexpected = inspect_unexpected_files(out)
            self.assertTrue(unexpected.valid)
            self.assertEqual(unexpected.details["files"], [])

            retrieved = datetime.fromisoformat(RETRIEVED_AT)
            stamps = []
            for path in sorted(out.glob("obs_*.json")):
                document = json.loads(path.read_text(encoding="utf-8"))
                self.assertIsInstance(document["envelope"], str)
                payload = document["payload"]
                self.assertEqual(
                    set(payload),
                    {"close", "high", "low", "open", "volume"},
                )
                self.assertTrue(all(isinstance(value, str) for value in payload.values()))
                library_payload = ObservationPayload(
                    close=payload["close"],
                    open=payload["open"],
                    high=payload["high"],
                    low=payload["low"],
                    volume=payload["volume"],
                )
                self.assertEqual(
                    document["payload_checksum"],
                    library_payload.compute_checksum(),
                )
                raw_text = path.read_text(encoding="utf-8")
                self.assertNotRegex(raw_text, r'"close":\s*-?\d')
            accepted = loaded.observation_intake.accepted
            for item in accepted:
                created = Observation.create(item.envelope, item.payload)
                self.assertEqual(item.payload_checksum, created.payload_checksum)
                self.assertEqual(item.payload_checksum, item.payload.compute_checksum())
                self.assertEqual(item.envelope.retrieval_timestamp, retrieved)
                self.assertEqual(
                    format_canonical_timestamp(item.envelope.retrieval_timestamp),
                    format_canonical_timestamp(retrieved),
                )
                market = item.envelope.market_timestamp
                assert market is not None
                self.assertEqual(market.hour, 16)
                self.assertEqual(market.minute, 0)
                self.assertEqual(market.second, 0)
                self.assertEqual(market.microsecond, 0)
                self.assertEqual(item.envelope.timezone, "America/New_York")
                stamps.append(format_canonical_timestamp(market))
            self.assertEqual(
                stamps,
                [
                    expected_market("2026-01-15"),
                    expected_market("2026-01-16"),
                    expected_market("2026-03-06"),
                    expected_market("2026-03-09"),
                    expected_market("2026-07-15"),
                    expected_market("2026-10-30"),
                    expected_market("2026-11-02"),
                ],
            )
            by_day = {}
            for item in accepted:
                market = item.envelope.market_timestamp
                assert market is not None
                by_day[market.date().isoformat()] = market
            # 2026-03-08 is the US spring-forward; 2026-11-01 is the fall-back.
            # 16:00 local is after the 02:00 transition on those Sundays.
            self.assertEqual(by_day["2026-03-06"].utcoffset(), timedelta(hours=-5))
            self.assertEqual(by_day["2026-03-09"].utcoffset(), timedelta(hours=-4))
            self.assertEqual(by_day["2026-10-30"].utcoffset(), timedelta(hours=-4))
            self.assertEqual(by_day["2026-11-02"].utcoffset(), timedelta(hours=-5))
            self.assertNotEqual(
                by_day["2026-03-06"].utcoffset(),
                by_day["2026-03-09"].utcoffset(),
            )
            self.assertNotEqual(
                by_day["2026-10-30"].utcoffset(),
                by_day["2026-11-02"].utcoffset(),
            )
            self.assertNotIn("T14:00", stamps[0])

            changes = ("1.75", "1.50", "1.50", "5.75", "-3.25", "1.50")
            session = run_session_from_pack(out, allow_historical=True)
            self.assertIsNone(session.error_code)
            assert session.session is not None and session.session.baseline is not None
            self.assertEqual(session.session.baseline.status, "MEASURED")
            self.assertEqual(session.session.baseline.changes, changes)
            report_path = Path(raw) / "session_report.json"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                cli_code = workshop_main(
                    [
                        "session",
                        "--pack",
                        str(out),
                        "--allow-historical",
                        "--report",
                        str(report_path),
                    ]
                )
            self.assertEqual(cli_code, 0, stderr.getvalue())
            self.assertFalse(ROOT in report_path.resolve().parents)
            written = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(written["session"]["baseline"]["status"], "MEASURED")
            self.assertEqual(written["session"]["baseline"]["changes"], list(changes))

    def test_retrieved_at_other_offset_keeps_instant_and_loads(self) -> None:
        supplied = "2026-12-01T17:30:00-04:00"
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw) / "pack"
            code = self.convert(out, retrieved_at=supplied)
            self.assertEqual(code, 0)
            loaded = load_dataset_pack(out, allow_historical=True)
            self.assertEqual(loaded.observation_intake.quarantined_count(), 0)
            item = loaded.observation_intake.accepted[0]
            parsed = datetime.fromisoformat(supplied)
            self.assertEqual(item.envelope.retrieval_timestamp, parsed)
            zone = ZoneInfo("America/New_York")
            self.assertEqual(
                format_canonical_timestamp(item.envelope.retrieval_timestamp),
                format_canonical_timestamp(parsed.astimezone(zone)),
            )

    def test_adjustment_policy_and_dataset_id_flags(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw) / "pack"
            code = self.convert(
                out,
                adjustment_policy="STOOQ_AS_PUBLISHED",
                dataset_id="spy-stooq-ha1-private",
                max_staleness="P5D",
            )
            self.assertEqual(code, 0)
            declaration = json.loads((out / "declaration.json").read_text(encoding="utf-8"))
        self.assertEqual(declaration["adjustment_policy"], "STOOQ_AS_PUBLISHED")
        self.assertEqual(declaration["max_staleness"], "P5D")

    def test_native_stooq_header_and_spy_us_ticker(self) -> None:
        text = (
            "<TICKER>,<PER>,<DATE>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>\n"
            "SPY.US,D,20260115,100.00,101.00,99.00,100.50,1000\n"
            "SPY.US,D,2026-01-16,101.00,102.00,100.00,101.25,1100\n"
        )
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            csv_path = root / "native.csv"
            csv_path.write_text(text, encoding="utf-8")
            out = root / "pack"
            code = self.convert(out, csv_path)
            self.assertEqual(code, 0)
            loaded = load_dataset_pack(out, allow_historical=True)
            self.assertEqual(loaded.observation_intake.accepted_count(), 2)
            self.assertEqual(loaded.observation_intake.accepted[0].payload.close, "100.50")

    def test_empty_existing_out_is_used(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw) / "pack"
            out.mkdir()
            code = self.convert(out)
            self.assertEqual(code, 0)
            self.assertTrue((out / "declaration.json").is_file())

    def test_cli_import_path_from_other_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw) / "pack"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(TOOL),
                    "--csv",
                    str(FIXTURE),
                    "--out",
                    str(out),
                    "--symbol",
                    "SPY",
                    "--provider",
                    "STOOQ",
                    "--retrieved-at",
                    RETRIEVED_AT,
                    "--adjustment-policy",
                    SYNTHETIC_POLICY,
                ],
                cwd="/tmp",
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue((out / "obs_0001.json").is_file())

    def test_missing_retrieved_at_refuses_without_a_pack(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw) / "pack"
            code = self.convert(out, retrieved_at=None)
            self.assertNotEqual(code, 0)
            self.assertFalse(out.exists())

    def test_missing_adjustment_policy_refuses_without_a_pack(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw) / "pack"
            code = self.convert(out, adjustment_policy=None)
            self.assertNotEqual(code, 0)
            self.assertFalse(out.exists())
            self.assertNotIn("UNVERIFIED", CONVERTER.__dict__)
            self.assertFalse(hasattr(CONVERTER, "DEFAULT_ADJUSTMENT_POLICY"))

    def test_naive_retrieved_at_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw) / "pack"
            code = self.convert(out, retrieved_at="2026-09-24T16:30:00")
            self.assertEqual(code, 2)
            self.assertFalse(out.exists())

    def test_nonempty_out_refuses_and_leaves_contents(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw) / "pack"
            out.mkdir()
            sentinel = out / "keep.txt"
            sentinel.write_text("keep", encoding="utf-8")
            code = self.convert(out)
            self.assertEqual(code, 2)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")
            self.assertFalse((out / "declaration.json").exists())
            self.assertEqual(list(out.iterdir()), [sentinel])

    def test_git_work_tree_root_walks_from_the_given_path(self) -> None:
        self.assertEqual(CONVERTER.git_work_tree_root(TOOL), ROOT)
        with tempfile.TemporaryDirectory() as raw:
            outside = Path(raw) / "tools" / "stooq_to_strict_pack.py"
            self.assertIsNone(CONVERTER.git_work_tree_root(outside))
            linked = Path(raw) / "linked"
            linked.mkdir()
            (linked / ".git").write_text("gitdir: /unused\n", encoding="utf-8")
            self.assertEqual(
                CONVERTER.git_work_tree_root(linked / "tools" / "tool.py"),
                linked,
            )

    def test_out_inside_git_work_tree_refuses(self) -> None:
        # Root is the nearest .git ancestor of this tool file, not cwd.
        nested = ROOT / "_stooq_out_guard_pack"
        relative_name = "_stooq_out_guard_relative"
        from_tmp = ROOT / "_stooq_out_guard_from_tmp"
        targets = (nested, ROOT / relative_name, from_tmp)
        try:
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                code = self.convert(nested)
            self.assertEqual(code, 2, stderr.getvalue())
            self.assertIn("git work tree", stderr.getvalue())
            self.assertFalse(nested.exists())

            stderr = io.StringIO()
            with redirect_stderr(stderr):
                code = self.convert(ROOT)
            self.assertEqual(code, 2, stderr.getvalue())
            self.assertIn("git work tree", stderr.getvalue())
            self.assertFalse((ROOT / "declaration.json").exists())

            command = [
                sys.executable,
                str(TOOL),
                "--csv",
                str(FIXTURE),
                "--symbol",
                "SPY",
                "--provider",
                "STOOQ",
                "--retrieved-at",
                RETRIEVED_AT,
                "--adjustment-policy",
                SYNTHETIC_POLICY,
            ]
            from_other_cwd = subprocess.run(
                [*command, "--out", str(from_tmp)],
                cwd="/tmp",
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(from_other_cwd.returncode, 2, from_other_cwd.stderr)
            self.assertIn("git work tree", from_other_cwd.stderr)
            self.assertFalse(from_tmp.exists())

            relative = subprocess.run(
                [*command, "--out", relative_name],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(relative.returncode, 2, relative.stderr)
            self.assertIn("git work tree", relative.stderr)
            self.assertFalse((ROOT / relative_name).exists())
        finally:
            for path in targets:
                if path.exists():
                    shutil.rmtree(path)

    def test_out_outside_work_tree_succeeds_when_cwd_is_repo(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw) / "pack"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(TOOL),
                    "--csv",
                    str(FIXTURE),
                    "--out",
                    str(out),
                    "--symbol",
                    "SPY",
                    "--provider",
                    "STOOQ",
                    "--retrieved-at",
                    RETRIEVED_AT,
                    "--adjustment-policy",
                    SYNTHETIC_POLICY,
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue((out / "declaration.json").is_file())
            self.assertFalse(ROOT in out.resolve().parents)

    def test_missing_work_tree_skips_the_out_guard(self) -> None:
        real = CONVERTER.git_work_tree_root
        CONVERTER.git_work_tree_root = lambda start: None
        try:
            CONVERTER.require_out_outside_work_tree(ROOT)
            CONVERTER.require_out_outside_work_tree(ROOT / "pack")
        finally:
            CONVERTER.git_work_tree_root = real
        with self.assertRaises(CONVERTER.ConverterRefusal) as caught:
            CONVERTER.require_out_outside_work_tree(ROOT / "pack")
        self.assertIn("git work tree", str(caught.exception))

    def test_force_flag_is_not_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw) / "pack"
            code = CONVERTER.main(
                [
                    "--csv",
                    str(FIXTURE),
                    "--out",
                    str(out),
                    "--symbol",
                    "SPY",
                    "--provider",
                    "STOOQ",
                    "--retrieved-at",
                    RETRIEVED_AT,
                    "--adjustment-policy",
                    SYNTHETIC_POLICY,
                    "--force",
                ]
            )
            self.assertNotEqual(code, 0)
            self.assertFalse(out.exists())

    def test_symbol_and_provider_must_match_authorize(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            qqq = root / "qqq"
            yahoo = root / "yahoo"
            self.assertEqual(self.convert(qqq, symbol="QQQ"), 2)
            self.assertEqual(self.convert(yahoo, provider="YAHOO"), 2)
            self.assertFalse(qqq.exists())
            self.assertFalse(yahoo.exists())

    def test_ohlc_contradiction_refuses_whole_file(self) -> None:
        text = (
            "Date,Open,High,Low,Close,Volume\n"
            "2026-01-15,100.00,101.00,99.00,100.50,1000\n"
            "2026-01-16,100.00,90.00,99.00,100.50,1000\n"
        )
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            csv_path = root / "bad.csv"
            csv_path.write_text(text, encoding="utf-8")
            out = root / "pack"
            code = self.convert(out, csv_path)
            self.assertEqual(code, 2)
            self.assertFalse(out.exists())

    def test_open_and_close_outside_range_refuse(self) -> None:
        cases = (
            "2026-01-15,120.00,101.00,99.00,100.00,10\n",
            "2026-01-15,100.00,101.00,99.00,130.00,10\n",
        )
        for body in cases:
            with self.subTest(body=body):
                text = "Date,Open,High,Low,Close,Volume\n" + body
                with tempfile.TemporaryDirectory() as raw:
                    root = Path(raw)
                    csv_path = root / "bad.csv"
                    csv_path.write_text(text, encoding="utf-8")
                    out = root / "pack"
                    self.assertEqual(self.convert(out, csv_path), 2)
                    self.assertFalse(out.exists())

    def test_nonpositive_ohlc_refuses_whole_file(self) -> None:
        header = "Date,Open,High,Low,Close,Volume\n"
        good = "2026-01-15,100.00,101.00,99.00,100.50,1000\n"
        cases = {
            "zero-low": "2026-01-16,100.00,101.00,0,100.50,1000\n",
            "zero-close": "2026-01-16,100.00,101.00,0.00,0.00,1000\n",
            "zero-open": "2026-01-16,0,1.00,0,0.50,1000\n",
            "zero-high": "2026-01-16,0,0,0,0,1000\n",
            "negative-low": "2026-01-16,100.00,101.00,-0.01,100.00,1000\n",
            "negative-close": "2026-01-16,100.00,101.00,-1.00,-0.50,1000\n",
            "negative-open": "2026-01-16,-1.00,2.00,-2.00,1.00,1000\n",
            "negative-high": "2026-01-16,-3.00,-1.00,-4.00,-2.00,1000\n",
        }
        for name, row in cases.items():
            with self.subTest(name=name):
                text = header + good + row
                with tempfile.TemporaryDirectory() as raw:
                    root = Path(raw)
                    csv_path = root / "bad.csv"
                    csv_path.write_text(text, encoding="utf-8")
                    out = root / "pack"
                    stderr = io.StringIO()
                    with redirect_stderr(stderr):
                        code = self.convert(out, csv_path)
                    self.assertEqual(code, 2, stderr.getvalue())
                    self.assertFalse(out.exists())
                    self.assertIn("nonpositive", stderr.getvalue())
                    self.assertIn("2026-01-16", stderr.getvalue())

    def test_zero_volume_still_converts(self) -> None:
        text = (
            "Date,Open,High,Low,Close,Volume\n"
            "2026-01-15,100.00,101.00,99.00,100.50,0\n"
        )
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            csv_path = root / "zero-volume.csv"
            csv_path.write_text(text, encoding="utf-8")
            out = root / "pack"
            code = self.convert(out, csv_path)
            self.assertEqual(code, 0)
            document = json.loads((out / "obs_0001.json").read_text(encoding="utf-8"))
            self.assertEqual(document["payload"]["volume"], "0")
            self.assertEqual(document["payload"]["close"], "100.50")

    def test_missing_columns_empty_duplicate_bad_decimal_negative_volume(self) -> None:
        cases = {
            "missing": "Date,Open,High,Low,Close\n2026-01-15,1,1,1,1\n",
            "empty": "",
            "header-only": "Date,Open,High,Low,Close,Volume\n",
            "duplicate": (
                "Date,Open,High,Low,Close,Volume\n"
                "2026-01-15,100,101,99,100,10\n"
                "20260115,100,101,99,100,10\n"
            ),
            "scientific": (
                "Date,Open,High,Low,Close,Volume\n"
                "2026-01-15,1e2,101,99,100,10\n"
            ),
            "blank": (
                "Date,Open,High,Low,Close,Volume\n"
                "2026-01-15,100,101,99,,10\n"
            ),
            "negative-volume": (
                "Date,Open,High,Low,Close,Volume\n"
                "2026-01-15,100,101,99,100,-1\n"
            ),
            "ticker": (
                "Date,Ticker,Open,High,Low,Close,Volume\n"
                "2026-01-15,QQQ,100,101,99,100,10\n"
            ),
        }
        for name, text in cases.items():
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as raw:
                    root = Path(raw)
                    csv_path = root / "bad.csv"
                    csv_path.write_text(text, encoding="utf-8")
                    out = root / "pack"
                    self.assertEqual(self.convert(out, csv_path), 2, name)
                    self.assertFalse(out.exists(), name)

    def test_lowercase_ticker_and_non_utf8_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            ticker = root / "ticker.csv"
            ticker.write_text(
                "Date,Ticker,Open,High,Low,Close,Volume\n"
                "2026-01-15,spy,100,101,99,100,10\n",
                encoding="utf-8",
            )
            binary = root / "binary.csv"
            binary.write_bytes(
                b"Date,Open,High,Low,Close,Volume\n2026-01-15,1,1,1,1,1\xff\n"
            )
            missing = root / "missing.csv"
            for path in (ticker, binary, missing):
                out = root / f"out-{path.stem}"
                self.assertEqual(self.convert(out, path), 2)
                self.assertFalse(out.exists())

    def test_retrieved_at_before_any_bar_refuses_whole_file(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw) / "pack"
            code = self.convert(out, retrieved_at="2026-01-15T15:59:59-05:00")
            self.assertEqual(code, 2)
            self.assertFalse(out.exists())

    def test_zoneinfo_failure_refuses_without_utc_fallback(self) -> None:
        real = CONVERTER.ZoneInfo

        def fail(name: str):
            raise ZoneInfoNotFoundError(name)

        CONVERTER.ZoneInfo = fail
        try:
            with tempfile.TemporaryDirectory() as raw:
                out = Path(raw) / "pack"
                code = self.convert(out)
                self.assertEqual(code, 2)
                self.assertFalse(out.exists())
        finally:
            CONVERTER.ZoneInfo = real
        source = TOOL.read_text(encoding="utf-8")
        self.assertIn("install tzdata", source)
        self.assertNotIn("timezone.utc", source)
        self.assertNotIn("timedelta(hours=-4)", source)
        self.assertNotIn("timedelta(hours=-5)", source)

    def test_tool_has_no_network_client(self) -> None:
        source = TOOL.read_text(encoding="utf-8")
        for banned in ("urllib", "requests", "httpx", "http://", "https://", "stooq.com"):
            self.assertNotIn(banned, source)
        self.assertNotRegex(source, r"(?m)^\s*(import|from)\s+socket\b")


if __name__ == "__main__":
    unittest.main()
