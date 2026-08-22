"""SOFTWARE CORRECTNESS — Phase 5 atomic file replace."""

from __future__ import annotations

import importlib
import tempfile
import unittest
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.atomic_write import write_text_atomic


class AtomicWriteTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "write_text_atomic"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "atomic_write.py"), doraise=True)

    def test_replace_leaves_no_temp_sibling(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "note.txt"
            write_text_atomic(path, "first\n")
            write_text_atomic(path, "second\n")
            self.assertEqual(path.read_text(encoding="utf-8"), "second\n")
            self.assertFalse((Path(raw) / "note.txt.tmp").exists())


if __name__ == "__main__":
    unittest.main()
