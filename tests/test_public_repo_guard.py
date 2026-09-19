"""SOFTWARE CORRECTNESS — public-repository vendor-data guard."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from radar_v4.public_repo_guard import scan_public_repo


class PublicRepoGuardTests(unittest.TestCase):
    def test_current_repository_has_no_guard_violations(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(scan_public_repo(root), ())

    def test_forbidden_vendor_data_path_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "vendor_data" / "spy.json"
            target.parent.mkdir(parents=True)
            target.write_text('{"close":"100.00"}', encoding="utf-8")
            issues = scan_public_repo(root)
            self.assertTrue(any("forbidden private/vendor-data path" in item for item in issues))

    def test_credential_like_file_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".env").write_text("TOKEN=placeholder", encoding="utf-8")
            issues = scan_public_repo(root)
            self.assertTrue(any("credential-like filename" in item for item in issues))

    def test_embedded_secret_assignment_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "config.py"
            source.write_text(
                "api" + "_key = " + repr("abcdefghijklmnop123456"),
                encoding="utf-8",
            )
            issues = scan_public_repo(root)
            self.assertTrue(any("credential-like assignment" in item for item in issues))


if __name__ == "__main__":
    unittest.main()
