#!/usr/bin/env python3
"""Tests for the lossless migration inventory and verifier."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent / "skills" / "pks-setup" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import pks_inventory  # noqa: E402
import verify_pks_migration as verifier  # noqa: E402


class MigrationToolsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "notes").mkdir()
        (self.root / "notes" / "old-roadmap.md").write_text("original roadmap\n", encoding="utf-8")
        (self.root / ".hidden").write_text("keep me\n", encoding="utf-8")
        (self.root / ".git").mkdir()
        (self.root / ".git" / "config").write_text("not inventory content\n", encoding="utf-8")
        (self.root / "nested-project" / ".git").mkdir(parents=True)
        (self.root / "nested-project" / ".git" / "config").write_text("also excluded\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def before_document(self) -> dict[str, object]:
        entries, errors = pks_inventory.inventory(self.root)
        self.assertEqual(errors, [])
        return {"schemaVersion": "pks-inventory/v1", "entries": entries}

    def approved_map(self) -> dict[str, object]:
        return {
            "schemaVersion": "pks-migration-map/v1",
            "approvalRef": "migration plan approved in test",
            "items": [
                {"source": ".hidden", "disposition": "retained", "destinations": []},
                {"source": "nested-project", "disposition": "retained", "destinations": []},
                {"source": "notes", "disposition": "retained", "destinations": []},
                {
                    "source": "notes/old-roadmap.md",
                    "disposition": "copied",
                    "destinations": ["docs/planning/source-roadmap.md"],
                },
            ],
        }

    def test_inventory_includes_hidden_files_and_excludes_git_metadata(self) -> None:
        entries, errors = pks_inventory.inventory(self.root)
        self.assertEqual(errors, [])
        paths = {entry["path"] for entry in entries}
        self.assertIn(".hidden", paths)
        self.assertNotIn(".git", paths)
        self.assertNotIn(".git/config", paths)
        self.assertNotIn("nested-project/.git", paths)
        self.assertNotIn("nested-project/.git/config", paths)

    def test_verifier_accepts_retained_and_exact_copy(self) -> None:
        before = self.before_document()
        target = self.root / "docs" / "planning"
        target.mkdir(parents=True)
        (target / "source-roadmap.md").write_text("original roadmap\n", encoding="utf-8")
        current, errors = pks_inventory.inventory(self.root)
        self.assertEqual(errors, [])
        report = verifier.verify(before, self.approved_map(), current)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["result"], "pass")

    def test_verifier_detects_changed_source_and_missing_mapping(self) -> None:
        before = self.before_document()
        (self.root / "notes" / "old-roadmap.md").write_text("changed roadmap\n", encoding="utf-8")
        current, errors = pks_inventory.inventory(self.root)
        self.assertEqual(errors, [])
        mapping = self.approved_map()
        mapping["items"] = mapping["items"][:-1]
        report = verifier.verify(before, mapping, current)
        self.assertTrue(any("no mapping" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
