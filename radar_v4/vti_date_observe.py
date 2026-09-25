"""Offline, date-granularity description of one private Vanguard VTI capture.

This is separate from dataset packs: an effectiveDate is a session date, not
an exact market timestamp. No network access, persistence, or signal logic.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from json import loads
from pathlib import Path

SOURCE = "https://investor.vanguard.com/irr/funds/profile/VTI-AdditionalFundData"
MAX_SOURCE_BYTES = 15_000_000


def _money(value: object) -> Decimal:
    if not isinstance(value, (str, int, float)) or isinstance(value, bool):
        raise ValueError("price, NAV, and premium must be present")
    try:
        number = Decimal(str(value).strip().replace("$", "").replace(",", ""))
    except InvalidOperation as exc:
        raise ValueError("invalid monetary value") from exc
    if not number.is_finite() or number.as_tuple().exponent < -2:
        raise ValueError("invalid monetary precision")
    return number


def _read_json(path: Path, size_limit: int) -> tuple[object, bytes]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"missing or linked capture member: {path.name}")
    with path.open("rb") as stream:
        raw = stream.read(size_limit + 1)
    if len(raw) > size_limit:
        raise ValueError(f"capture member exceeds size limit: {path.name}")
    try:
        return loads(raw), raw
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError(f"invalid JSON in {path.name}") from exc


def observe_vti_capture(directory: str | Path) -> dict[str, object]:
    """Describe last two dated prices, refusing altered or inconsistent capture."""
    root = Path(directory)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("capture must be an existing local directory")
    receipt, _ = _read_json(root / "receipt.json", 100_000)
    source, raw = _read_json(root / "vanguard-response.json", MAX_SOURCE_BYTES)
    if not isinstance(receipt, dict) or not isinstance(source, dict):
        raise ValueError("capture members must be JSON objects")
    if (
        receipt.get("status") != "SOURCE_CAPTURE_ONLY_NOT_RADAR_ADMITTED"
        or receipt.get("instrument") != "VTI"
        or receipt.get("source_url") != SOURCE
        or receipt.get("market_timestamp") is not None
        or not isinstance(source.get("historicalPrice"), dict)
        or source["historicalPrice"].get("ticker") != "VTI"
    ):
        raise ValueError("capture identity or timestamp claim is invalid")
    try:
        retrieved_text = receipt["retrieved_at_utc"]
        if not isinstance(retrieved_text, str) or not retrieved_text.endswith("Z"):
            raise ValueError("retrieval time must be UTC")
        retrieved = datetime.fromisoformat(retrieved_text.replace("Z", "+00:00"))
        if retrieved.utcoffset() != timezone.utc.utcoffset(retrieved):
            raise ValueError("retrieval time must be UTC")
        entries = source["premiumDiscountDetails"][0]["pdDetails"]
        if not isinstance(entries, list):
            raise ValueError("source rows must be a list")
        parsed = []
        seen = set()
        for entry in entries:
            day = datetime.strptime(entry["effectiveDate"], "%m/%d/%Y").date()
            if day in seen:
                raise ValueError("duplicate source session date")
            seen.add(day)
            parsed.append((day, entry))
        parsed.sort(key=lambda row: row[0])
        if len(parsed) < 3:
            raise ValueError("fewer than three dated source rows")
        newest = []
        for day, entry in parsed[-3:]:
            price = _money(entry["marketPrice"])
            nav = _money(entry["nav"])
            premium = _money(entry["premiumDiscountAmount"])
            if price <= 0 or nav <= 0 or price - nav != premium:
                raise ValueError("source market price, NAV, or premium is inconsistent")
            newest.append((day, price, nav, premium))
        recorded = receipt["latest_three_rows"]
        if not isinstance(recorded, list) or len(recorded) != 3:
            raise ValueError("receipt must contain three source rows")
        for item, (_, price, nav, premium) in zip(recorded, newest):
            if (
                _money(item["MarketPrice"]) != price
                or _money(item["NAV"]) != nav
                or _money(item["Premium"]) != premium
            ):
                raise ValueError("receipt and source prices disagree")
        session = date.fromisoformat(receipt["session_date"])
        if (
            session != newest[-1][0]
            or root.name != f"vti-{session.isoformat()}"
            or session > retrieved.date()
        ):
            raise ValueError("receipt session, directory, or retrieval date disagrees")
    except (KeyError, IndexError, TypeError, AttributeError) as exc:
        raise ValueError("required capture field is missing or malformed") from exc
    previous, current = newest[-2:]
    return {
        "status": "PRIVATE_DATE_OBSERVATION_ONLY",
        "instrument": "VTI",
        "source_url": SOURCE,
        "source_sha256": sha256(raw).hexdigest(),
        "previous_session_date": previous[0].isoformat(),
        "session_date": current[0].isoformat(),
        "previous_market_price": str(previous[1]),
        "market_price": str(current[1]),
        "close_to_close_difference": str(current[1] - previous[1]),
        "retrieved_at_utc": retrieved_text,
        "market_timestamp": None,
        "radar_pack_admitted": False,
        "claim": "LEVEL 0 descriptive price difference only; no signal or edge claim",
    }
