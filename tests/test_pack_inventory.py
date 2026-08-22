"""SOFTWARE CORRECTNESS — Phase 5 pack inventory. No measurement."""

from __future__ import annotations

import importlib
import json
import unittest
from hashlib import sha256
from pathlib import Path
from py_compile import compile as py_compile

from radar_v4.pack_inventory import inventory_pack


class PackInventoryTests(unittest.TestCase):
    def test_import_and_parse(self) -> None:
        package = importlib.import_module("radar_v4")
        self.assertTrue(hasattr(package, "inventory_pack"))
        self.assertTrue(hasattr(package, "PackInventory"))
        root = Path(__file__).resolve().parents[1]
        py_compile(str(root / "radar_v4" / "pack_inventory.py"), doraise=True)

    def test_repo_synthetic_pack_lists_roles_without_measuring(self) -> None:
        root = Path(__file__).resolve().parents[1] / "fixtures" / "synthetic_one_symbol_1d"
        inventory = inventory_pack(root)
        self.assertTrue(inventory.present)
        self.assertIsNone(inventory.error_code)
        roles = {item.name: item.role for item in inventory.files}
        self.assertEqual(roles["declaration.json"], "declaration")
        self.assertEqual(roles["manifest.json"], "artifact")
        self.assertEqual(roles["README.md"], "other")
        self.assertEqual(len(inventory.observation_names()), 3)
        document = json.loads(inventory.serialize())
        self.assertEqual(document["document_kind"], "radar_v4.pack_inventory")
        self.assertEqual(document["observation_count"], 3)
        declaration = next(item for item in inventory.files if item.name == "declaration.json")
        self.assertEqual(len(declaration.digest), 64)
        self.assertEqual(
            declaration.digest,
            sha256((root / "declaration.json").read_bytes()).hexdigest(),
        )

    def test_missing_directory_does_not_invent_files(self) -> None:
        inventory = inventory_pack("/tmp/radar-v4-no-such-inventory-pack")
        self.assertFalse(inventory.present)
        self.assertEqual(inventory.error_code, "UNREADABLE_PACK")
        self.assertEqual(inventory.files, ())


if __name__ == "__main__":
    unittest.main()
