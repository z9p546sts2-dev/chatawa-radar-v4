"""Replace a file only after the new bytes are fully written."""

from __future__ import annotations

from pathlib import Path


def write_text_atomic(path: str | Path, text: str) -> Path:
    """Write text to a temp sibling, then replace the target.

    A crash mid-write must not leave a truncated destination file.
    """
    target = Path(path)
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(target)
    return target
