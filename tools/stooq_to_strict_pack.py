#!/usr/bin/env python3
"""Offline Stooq daily CSV → strict HISTORICAL workshop pack.

Charter: docs/governance/2026-09-24-authorize-stooq-strict-converter-TC.md
Design: docs/governance/2026-09-24-build-unit-stooq-strict-converter-TC.md
Universe: docs/governance/2026-09-25-maine-leg1-authorize-TC.md
          (amends the converter allowlist from SPY-only to SPY, QQQ, IWM)

This script lives outside radar_v4/. It does not download, does not open a
socket, and does not call a vendor. It may import pure radar_v4 types so
payload and envelope checksums stay library-identical.

Market timestamps are the bar's calendar date at 16:00:00.000000 in
America/New_York. The numeric offset comes from ZoneInfo (DST). A fixed
offset is not used. If America/New_York cannot be loaded, the convert
refuses. Install the tzdata package on platforms that do not ship the IANA
database (Windows). There is no UTC fallback.

--retrieved-at is required. It is the private CSV download/capture time, not
the converter wall clock. The same instant is written on every observation,
expressed in America/New_York so the declared timezone offset matches
timezone_offset_matches. Aware datetime equality with the supplied instant
is preserved.

--adjustment-policy is required. There is no default label. Todd supplies
the verified label for a real pack, or a provisional label for a synthetic
test. This tool does not choose UNADJUSTED or any other policy. A real
MEASURED run still requires the pre-run verification in the AUTHORIZE and
the runbook.

--out is refused when its resolved path is the git work tree that contains
this file, or any path inside that tree. The work tree root is the nearest
ancestor of this file that contains a .git entry (a directory in an
ordinary clone, or a file in a linked work tree). The walk starts at this
file, not at the process cwd, so the refusal still applies when the tool
is launched from another directory. If this file is not inside a work
tree, that check is skipped. The runbook already says keep packs outside
the repo; this makes an accidental in-repo write fail closed.

Named universe is exactly SPY, QQQ, and IWM. Provider remains STOOQ.
One symbol per invocation. Any other symbol is refused.

Accepted ticker column values, when a ticker column is present: the
requested symbol and the Stooq form SYMBOL.US (case-sensitive, after
strip). A row whose ticker does not match that one symbol refuses the
file.

Example:
  python tools/stooq_to_strict_pack.py \\
    --csv /PRIVATE/path/qqq_d.csv \\
    --out /PRIVATE/path/qqq_stooq_pack \\
    --symbol QQQ \\
    --provider STOOQ \\
    --retrieved-at 2026-09-24T16:30:00-04:00 \\
    --adjustment-policy <TODD_LABEL>
"""

from __future__ import annotations

import argparse
import csv
import io
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from json import dumps
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from radar_v4.evidence import EvidenceEnvelope, ProvenanceClass
from radar_v4.observation import Observation, ObservationPayload

ALLOWED_SYMBOLS = frozenset({"SPY", "QQQ", "IWM"})
PROVIDER = "STOOQ"
PROVENANCE = "HISTORICAL"
INTERVAL = "1d"
TIMEZONE_NAME = "America/New_York"
TRANSFORMATION_VERSION = "stooq-daily-ohlcv-v1"
LOCKED_QUESTION = "ordinary close-to-close changes for one symbol"
PRIMARY_METRIC = "close-to-close difference"
DEFAULT_DATASET_IDS = {
    "SPY": "spy-stooq-ha1-private",
    "QQQ": "qqq-stooq-ha1-private",
    "IWM": "iwm-stooq-ha1-private",
}
DEFAULT_DATASET_ID = DEFAULT_DATASET_IDS["SPY"]
REQUIRED_COLUMNS = ("date", "open", "high", "low", "close", "volume")
COLUMN_ALIASES = {
    "date": "date",
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "volume": "volume",
    "vol": "volume",
    "ticker": "ticker",
    "symbol": "ticker",
}

_PLAIN_DECIMAL = re.compile(r"-?(?:0|[1-9]\d*)(?:\.\d+)?\Z")
_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
_COMPACT_DATE = re.compile(r"\d{8}\Z")


class ConverterRefusal(Exception):
    """Conversion refused. No pack is published."""


@dataclass(frozen=True)
class _Bar:
    bar_date: date
    open: str
    high: str
    low: str
    close: str
    volume: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stooq_to_strict_pack",
        description=(
            "Convert a private Stooq-shaped daily CSV for one of SPY, QQQ, "
            "or IWM into a strict HISTORICAL pack. No network. Provider "
            "STOOQ only. One symbol per invocation."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "--adjustment-policy is required. Todd supplies the verified label\n"
            "for a real pack, or a provisional label for synthetic tests.\n"
            "This tool does not default the label to UNADJUSTED or anything\n"
            "else. Omitting the flag refuses. A real MEASURED run still\n"
            "requires the pre-run verification in the AUTHORIZE and runbook.\n"
            "\n"
            "Market timestamps are 16:00 America/New_York. The offset is the\n"
            "ZoneInfo DST offset for that date. --retrieved-at is required\n"
            "and is the private CSV capture time, not the converter clock.\n"
            "If America/New_York cannot be loaded, install tzdata. There is\n"
            "no UTC fallback. A nonempty --out is refused. There is no --force.\n"
            "A resolved --out inside the git work tree that contains this file\n"
            "is refused. That root is the nearest ancestor of this file with a\n"
            ".git entry. The process cwd is not used for the walk."
        ),
    )
    parser.add_argument("--csv", required=True, help="private Stooq-shaped daily CSV")
    parser.add_argument(
        "--out",
        required=True,
        help=(
            "pack directory (empty or new) outside the git work tree "
            "that contains this tool"
        ),
    )
    parser.add_argument(
        "--symbol",
        required=True,
        help="must be SPY, QQQ, or IWM (one symbol per invocation)",
    )
    parser.add_argument("--provider", required=True, help="must be STOOQ")
    parser.add_argument(
        "--retrieved-at",
        required=True,
        help="ISO-8601 timezone-aware CSV capture time (required)",
    )
    parser.add_argument(
        "--adjustment-policy",
        required=True,
        help=(
            "required declaration label; Todd supplies the verified or "
            "provisional value (no default; not a verified UNADJUSTED claim)"
        ),
    )
    parser.add_argument(
        "--dataset-id",
        default=None,
        help=(
            "declaration dataset_id (default depends on --symbol: "
            "spy-stooq-ha1-private, qqq-stooq-ha1-private, or "
            "iwm-stooq-ha1-private)"
        ),
    )
    parser.add_argument(
        "--max-staleness",
        default=None,
        help="optional declaration max_staleness; omitted when unset",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        return code if isinstance(code, int) else 2
    try:
        count = convert(
            csv_path=Path(args.csv),
            out_path=Path(args.out),
            symbol=args.symbol,
            provider=args.provider,
            retrieved_at=args.retrieved_at,
            adjustment_policy=args.adjustment_policy,
            dataset_id=args.dataset_id,
            max_staleness=args.max_staleness,
        )
    except ConverterRefusal as exc:
        print(f"stooq_to_strict_pack: {exc}", file=sys.stderr)
        return 2
    print(f"wrote {count} observations to {args.out}")
    return 0


def convert(
    *,
    csv_path: Path,
    out_path: Path,
    symbol: str,
    provider: str,
    retrieved_at: str,
    adjustment_policy: str,
    dataset_id: str | None = None,
    max_staleness: str | None = None,
) -> int:
    """Validate the CSV, then publish a pack. Refusals leave --out untouched.

    A resolved --out inside the git work tree that contains this file is
    refused before any pack bytes are written. See git_work_tree_root.
    """
    symbol_name = symbol.strip()
    if symbol_name not in ALLOWED_SYMBOLS or provider.strip() != PROVIDER:
        raise ConverterRefusal(
            "symbol/provider must be one of {SPY, QQQ, IWM}/STOOQ "
            "under Maine Leg 1; one symbol per invocation"
        )
    zone = require_new_york()
    retrieved = parse_retrieved_at(retrieved_at, zone)
    policy = require_line(adjustment_policy, "--adjustment-policy")
    identity = (
        DEFAULT_DATASET_IDS[symbol_name]
        if dataset_id is None
        else require_line(dataset_id, "--dataset-id")
    )
    staleness = None if max_staleness is None else require_line(max_staleness, "--max-staleness")
    bars = parse_bars(read_csv_text(csv_path), symbol_name)
    observations = [
        build_observation(bar, retrieved, zone, symbol_name) for bar in bars
    ]
    late = [
        item.envelope.market_timestamp.date().isoformat()
        for item in observations
        if item.envelope.market_timestamp is not None
        and retrieved < item.envelope.market_timestamp
    ]
    if late:
        raise ConverterRefusal(
            "--retrieved-at precedes market_timestamp for: " + ", ".join(late)
        )
    documents = pack_documents(observations, identity, policy, staleness, symbol_name)
    publish(out_path, documents)
    return len(observations)


def require_new_york() -> ZoneInfo:
    try:
        return ZoneInfo(TIMEZONE_NAME)
    except ZoneInfoNotFoundError as exc:
        raise ConverterRefusal(
            "America/New_York is unavailable; install tzdata "
            "(no UTC fallback)"
        ) from exc


def parse_retrieved_at(value: str, zone: ZoneInfo) -> datetime:
    text = value.strip()
    if text == "":
        raise ConverterRefusal("--retrieved-at is required")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ConverterRefusal(
            "--retrieved-at must be ISO-8601 and timezone-aware"
        ) from exc
    if parsed.tzinfo is None:
        raise ConverterRefusal(
            "--retrieved-at must be timezone-aware; UTC is not inferred"
        )
    # Same instant, declared-zone offset. Not the converter wall clock.
    return parsed.astimezone(zone)


def require_line(value: str, flag: str) -> str:
    text = value.strip()
    if text == "" or any(char in text for char in "\r\n"):
        raise ConverterRefusal(f"{flag} must be a non-empty single-line string")
    return text


def read_csv_text(path: Path) -> str:
    if not path.is_file():
        raise ConverterRefusal(f"CSV not found: {path}")
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ConverterRefusal(f"CSV unreadable: {path}") from exc
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ConverterRefusal("CSV is not UTF-8") from exc


def accepted_tickers(symbol: str) -> frozenset[str]:
    """Ticker column values that match this invocation's one symbol."""
    return frozenset({symbol, f"{symbol}.US"})


def parse_bars(text: str, symbol: str) -> tuple[_Bar, ...]:
    try:
        rows = list(csv.reader(io.StringIO(text)))
    except csv.Error as exc:
        raise ConverterRefusal(f"CSV could not be parsed: {exc}") from exc
    if not rows:
        raise ConverterRefusal("CSV is empty")
    indexes = column_indexes(rows[0])
    bars: list[_Bar] = []
    seen: set[date] = set()
    problems: list[str] = []
    for row in rows[1:]:
        if not row or all(cell.strip() == "" for cell in row):
            continue
        try:
            bar = parse_bar(row, indexes, symbol)
        except ConverterRefusal as exc:
            problems.append(str(exc))
            continue
        if bar.bar_date in seen:
            problems.append(f"duplicate date {bar.bar_date.isoformat()}")
            continue
        seen.add(bar.bar_date)
        bars.append(bar)
    if problems:
        shown = problems[:20]
        extra = len(problems) - len(shown)
        message = "; ".join(shown)
        if extra:
            message = f"{message}; and {extra} more"
        raise ConverterRefusal(message)
    if not bars:
        raise ConverterRefusal("CSV series is empty")
    bars.sort(key=lambda item: item.bar_date)
    return tuple(bars)


def column_indexes(header: list[str]) -> dict[str, int]:
    indexes: dict[str, int] = {}
    for index, raw in enumerate(header):
        canonical = COLUMN_ALIASES.get(normalize_header(raw))
        if canonical is None:
            continue
        if canonical in indexes:
            raise ConverterRefusal(f"duplicate column {canonical}")
        indexes[canonical] = index
    missing = [name for name in REQUIRED_COLUMNS if name not in indexes]
    if missing:
        raise ConverterRefusal("missing required columns: " + ", ".join(missing))
    return indexes


def normalize_header(name: str) -> str:
    text = name.strip().lstrip("\ufeff")
    if len(text) >= 2 and text[0] == "<" and text[-1] == ">":
        text = text[1:-1].strip()
    return text.casefold()


def parse_bar(row: list[str], indexes: dict[str, int], symbol: str) -> _Bar:
    def cell(name: str) -> str:
        index = indexes[name]
        if index >= len(row):
            raise ConverterRefusal(f"row is missing {name}")
        return row[index].strip()

    bar_date = parse_bar_date(cell("date"))
    if "ticker" in indexes:
        ticker = cell("ticker")
        allowed = accepted_tickers(symbol)
        if ticker not in allowed:
            shown = " or ".join(sorted(allowed))
            raise ConverterRefusal(
                f"ticker {ticker!r} on {bar_date.isoformat()} is not {shown}"
            )
    open_ = require_decimal(cell("open"), "open", bar_date)
    high = require_decimal(cell("high"), "high", bar_date)
    low = require_decimal(cell("low"), "low", bar_date)
    close = require_decimal(cell("close"), "close", bar_date)
    volume = require_decimal(cell("volume"), "volume", bar_date)
    if Decimal(volume) < 0:
        raise ConverterRefusal(f"negative volume on {bar_date.isoformat()}")
    open_number = Decimal(open_)
    high_number = Decimal(high)
    low_number = Decimal(low)
    close_number = Decimal(close)
    # Volume may be zero. Open, high, low, and close must be > 0.
    for field, number in (
        ("open", open_number),
        ("high", high_number),
        ("low", low_number),
        ("close", close_number),
    ):
        if number <= 0:
            raise ConverterRefusal(
                f"nonpositive {field} on {bar_date.isoformat()}"
            )
    if high_number < low_number:
        raise ConverterRefusal(
            f"OHLC contradiction on {bar_date.isoformat()}: high is below low"
        )
    if open_number > high_number or open_number < low_number:
        raise ConverterRefusal(
            f"OHLC contradiction on {bar_date.isoformat()}: open is outside high/low"
        )
    if close_number > high_number or close_number < low_number:
        raise ConverterRefusal(
            f"OHLC contradiction on {bar_date.isoformat()}: close is outside high/low"
        )
    return _Bar(
        bar_date=bar_date,
        open=open_,
        high=high,
        low=low,
        close=close,
        volume=volume,
    )


def parse_bar_date(value: str) -> date:
    if _ISO_DATE.fullmatch(value):
        year, month, day = (int(part) for part in value.split("-"))
    elif _COMPACT_DATE.fullmatch(value):
        year, month, day = int(value[0:4]), int(value[4:6]), int(value[6:8])
    else:
        raise ConverterRefusal(f"bad date {value!r}")
    try:
        return date(year, month, day)
    except ValueError as exc:
        raise ConverterRefusal(f"bad date {value!r}") from exc


def require_decimal(value: str, field: str, bar_date: date) -> str:
    if not _PLAIN_DECIMAL.fullmatch(value):
        raise ConverterRefusal(f"bad decimal {field} on {bar_date.isoformat()}")
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise ConverterRefusal(
            f"bad decimal {field} on {bar_date.isoformat()}"
        ) from exc
    if not number.is_finite():
        raise ConverterRefusal(f"bad decimal {field} on {bar_date.isoformat()}")
    return value


def build_observation(
    bar: _Bar,
    retrieved: datetime,
    zone: ZoneInfo,
    symbol: str,
) -> Observation:
    market = datetime(
        bar.bar_date.year,
        bar.bar_date.month,
        bar.bar_date.day,
        16,
        0,
        0,
        tzinfo=zone,
    )
    envelope = EvidenceEnvelope.create(
        provenance_class=ProvenanceClass.HISTORICAL,
        provider=PROVIDER,
        symbol_or_universe=symbol,
        market_timestamp=market,
        retrieval_timestamp=retrieved,
        interval=INTERVAL,
        timezone=TIMEZONE_NAME,
        transformation_version=TRANSFORMATION_VERSION,
    )
    payload = ObservationPayload(
        close=bar.close,
        open=bar.open,
        high=bar.high,
        low=bar.low,
        volume=bar.volume,
    )
    return Observation.create(envelope, payload)


def pack_documents(
    observations: tuple[Observation, ...] | list[Observation],
    dataset_id: str,
    adjustment_policy: str,
    max_staleness: str | None,
    symbol: str,
) -> list[tuple[str, str]]:
    declaration: dict[str, str] = {
        "adjustment_policy": adjustment_policy,
        "dataset_id": dataset_id,
        "interval": INTERVAL,
        "locked_question": LOCKED_QUESTION,
        "primary_metric": PRIMARY_METRIC,
        "provenance_class": PROVENANCE,
        "provider": PROVIDER,
        "timezone": TIMEZONE_NAME,
        "transformation_version": TRANSFORMATION_VERSION,
        "universe": symbol,
    }
    if max_staleness is not None:
        declaration["max_staleness"] = max_staleness
    documents = [("declaration.json", _dump(declaration))]
    width = max(4, len(str(len(observations))))
    for index, item in enumerate(observations, start=1):
        payload = item.payload.canonical_payload()
        document = {
            "envelope": item.envelope.serialize(),
            "payload": payload,
            "payload_checksum": item.payload_checksum,
        }
        documents.append((f"obs_{index:0{width}d}.json", _dump(document)))
    return documents


def _dump(document: dict[str, object]) -> str:
    return dumps(document, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def git_work_tree_root(start: Path) -> Path | None:
    """Nearest ancestor of start that contains a .git entry.

    The walk starts at start, not at the process cwd. When start is a file,
    it begins at that file's parent. A .git directory (ordinary clone) and
    a .git file (linked work tree) both count. Returns None when no ancestor
    has a .git entry, in which case the --out work-tree guard is skipped.
    """
    current = start.resolve()
    if not current.is_dir():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def require_out_outside_work_tree(out_path: Path) -> None:
    """Refuse a resolved --out inside the work tree that contains this tool."""
    root = git_work_tree_root(Path(__file__))
    if root is None:
        return
    resolved = out_path.resolve()
    if resolved == root or root in resolved.parents:
        raise ConverterRefusal(
            "--out resolves inside the git work tree that contains this "
            f"tool ({root}); write the pack outside the repo"
        )


def publish(out: Path, documents: list[tuple[str, str]]) -> None:
    require_out_outside_work_tree(out)
    if out.exists():
        if not out.is_dir() or any(out.iterdir()):
            raise ConverterRefusal("--out exists and is non-empty")
        _write_into(out, documents)
        return
    if not out.parent.is_dir():
        raise ConverterRefusal("parent directory of --out does not exist")
    temporary = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=str(out.parent)))
    try:
        _write_into(temporary, documents)
        temporary.rename(out)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def _write_into(directory: Path, documents: list[tuple[str, str]]) -> None:
    written: list[Path] = []
    try:
        for name, text in documents:
            path = directory / name
            path.write_text(text, encoding="utf-8", newline="\n")
            written.append(path)
    except Exception:
        for path in written:
            path.unlink(missing_ok=True)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
