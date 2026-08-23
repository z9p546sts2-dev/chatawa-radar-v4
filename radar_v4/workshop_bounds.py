"""Workshop bounds and local-only import scan. Not a method claim."""

from __future__ import annotations

from ast import Import, ImportFrom, parse
from json import dumps
from pathlib import Path

from radar_v4.workshop_check import PHASE5_HIGHEST_UNIT

FORBIDDEN_IMPORTS = frozenset(
    {
        "aiohttp",
        "ftplib",
        "http.client",
        "http.server",
        "httpx",
        "requests",
        "urllib.request",
        "websocket",
        "websockets",
    }
)


def _dump(document: dict[str, object]) -> str:
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def workshop_bounds() -> str:
    """State what this workshop may and may not do. Does not measure."""
    return _dump(
        {
            "authorized": [
                "local FIXTURE/SYNTHETIC pack intake",
                "ordinary close-to-close description",
                "local integrity, inspect, compare, and audit copy",
            ],
            "available_claim_level": "LEVEL 0 — MEASURED",
            "document_kind": "radar_v4.workshop_bounds",
            "highest_unit": PHASE5_HIGHEST_UNIT,
            "measured": False,
            "not_authorized": [
                "vendor or purchased historical API",
                "live download",
                "Phase 6 method research",
                "paper trading",
                "signals, scores, thresholds, or edge",
            ],
            "notes": [
                "units 851-900 are inspectability, not a research result",
                "authorization does not earn data correctness",
                "SYNTHETIC and FIXTURE numbers are not HISTORICAL evidence",
            ],
            "paper_trading_authorized": False,
            "phase": 5,
            "vendor_authorized": False,
        }
    )


def scan_package_network_imports(package_dir: str | Path | None = None) -> str:
    """Refuse vendor-style network libraries in the local package."""
    root = Path(package_dir) if package_dir is not None else Path(__file__).resolve().parent
    found: list[dict[str, str]] = []
    for path in sorted(root.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        tree = parse(source, filename=str(path))
        for node in tree.body:
            names: list[str] = []
            if isinstance(node, Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                if name in FORBIDDEN_IMPORTS or name.startswith("urllib.request"):
                    found.append({"file": path.name, "import": name})
    valid = not found
    return _dump(
        {
            "document_kind": "radar_v4.no_network",
            "error_code": None if valid else "NETWORK_IMPORT",
            "found": found,
            "notes": [
                "this scan is not a live connectivity test",
                "the workshop must not grow a vendor client by import",
            ],
            "valid": valid,
        }
    )
