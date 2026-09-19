"""Mechanical guard for keeping vendor data and credentials out of a public repo."""

from __future__ import annotations

from pathlib import Path
import re

FORBIDDEN_ROOT_NAMES = {
    ".radar_private",
    "private_vendor_data",
    "raw_vendor_data",
    "vendor_data",
    "market_data",
}

FORBIDDEN_CREDENTIAL_FILENAMES = {
    ".env",
    "credentials.json",
    "secrets.json",
    "api_key.txt",
    "apikey.txt",
}

SECRET_ASSIGNMENT = re.compile(
    r"(?i)\\b(api[_-]?key|apikey|access[_-]?token|secret)\\b\\s*[:=]\\s*"
    r"(?:[\"'][^\"'\\r\\n]{16,}[\"']|[A-Za-z0-9_./+=-]{16,})(?=\\s*(?:#|$))"
)


def scan_public_repo(root: str | Path) -> tuple[str, ...]:
    """Return human-readable violations found beneath a repository root.

    This deliberately errs on the side of refusing raw vendor-data locations
    and obvious credential artifacts. It is a repository safety check, not a
    market-data parser and not a vendor client.
    """
    base = Path(root)
    issues: list[str] = []
    for path in sorted(base.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(base)
        parts = rel.parts
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in parts):
            continue

        if any(part in FORBIDDEN_ROOT_NAMES for part in parts):
            issues.append(f"forbidden private/vendor-data path tracked or present: {rel.as_posix()}")

        name = path.name.lower()
        if name in FORBIDDEN_CREDENTIAL_FILENAMES or name.startswith(".env."):
            issues.append(f"credential-like filename present: {rel.as_posix()}")

        if (
            path.suffix.lower() in {".csv", ".json"}
            and any(token in name for token in ("twelve", "spy", "ohlcv", "market", "vendor", "raw"))
            and "fixtures" not in parts
        ):
            issues.append(f"vendor-data-shaped file present: {rel.as_posix()}")

        if path.suffix.lower() in {".py", ".toml", ".yaml", ".yml", ".ini", ".cfg", ".txt"}:
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if SECRET_ASSIGNMENT.search(text):
                issues.append(f"credential-like assignment present: {rel.as_posix()}")

    return tuple(issues)
