"""Replace a file only after the new bytes are fully written."""

from __future__ import annotations

from pathlib import Path


def file_exists_without_replace(path: str | Path, replace: bool) -> bool:
    """True when a regular file is already there and overwrite is refused."""
    return Path(path).is_file() and not replace


def write_text_atomic(path: str | Path, text: str) -> Path:
    """Write text to a temp sibling, then replace the target.

    A crash mid-write must not leave a truncated destination file.
    """
    target = Path(path)
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(target)
    return target
