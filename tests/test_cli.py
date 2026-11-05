#!/usr/bin/env python3
"""Tests for the pks command: every test drives it as a real subprocess."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PKS = REPO_ROOT / "bin" / "pks"
VERSION = (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
SKILLS = ["pks-audit", "pks-brainstorm", "pks-capture", "pks-help", "pks-setup"]


def run_git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), "-c", "user.name=Test", "-c", "user.email=test@example.com", *args],
        check=True,
        capture_output=True,
    )


class PksTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name) / "project"
        self.root.mkdir()

    def pks(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(PKS), *args],
            cwd=self.root,
            text=True,
            capture_output=True,
            stdin=subprocess.DEVNULL,
            check=False,
        )

    def write(self, relative: str, text: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def snapshot(self) -> dict[str, bytes]:
        return {
            path.relative_to(self.root).as_posix(): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file() and ".git" not in path.relative_to(self.root).parts
        }


class InitTest(PksTestCase):
    def test_empty_project_gets_full_installation(self) -> None:
        result = self.pks("init", "--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        for tool in (".claude", ".agents"):
            for skill in SKILLS:
                self.assertTrue((self.root / tool / "skills" / skill / "SKILL.md").is_file(), f"{tool}/{skill}")
        for name in ("PROJECT", "product", "business", "architecture", "roadmap"):
            self.assertTrue((self.root / "docs" / f"{name}.md").is_file(), name)
        self.assertEqual((self.root / ".pks/version").read_text(encoding="utf-8").strip(), VERSION)
        self.assertIn(".pks/brainstorms/", (self.root / ".gitignore").read_text(encoding="utf-8"))
        self.assertIn("## Product knowledge (PKS)", (self.root / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertIn("@AGENTS.md", (self.root / "CLAUDE.md").read_text(encoding="utf-8"))
        self.assertFalse((self.root / "docs/development.md").exists())
        self.assertFalse((self.root / "docs/INDEX.md").exists())

    def test_second_init_changes_nothing(self) -> None:
        self.pks("init", "--yes")
        before = self.snapshot()
        result = self.pks("init", "--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("pks update", result.stdout)
        self.assertEqual(self.snapshot(), before)

    def test_dry_run_changes_nothing(self) -> None:
        result = self.pks("init", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("docs/PROJECT.md", result.stdout)
        self.assertEqual(self.snapshot(), {})

    def test_without_terminal_or_yes_changes_nothing(self) -> None:
        result = self.pks("init")
        self.assertEqual(result.returncode, 1)
        self.assertIn("--yes", result.stderr)
        self.assertEqual(self.snapshot(), {})

    def test_existing_instruction_files_are_preserved(self) -> None:
        self.write("CLAUDE.md", "# My rules\n\nKeep this.\n")
        self.write("AGENTS.md", "# Agent rules\n")
        self.assertEqual(self.pks("init", "--yes").returncode, 0)
        claude = (self.root / "CLAUDE.md").read_text(encoding="utf-8")
        agents = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertTrue(claude.startswith("# My rules\n\nKeep this.\n"))
        self.assertIn("@AGENTS.md", claude)
        self.assertTrue(agents.startswith("# Agent rules\n"))
        self.assertIn("## Product knowledge (PKS)", agents)

    def test_symlinked_instruction_files_get_the_rule_once(self) -> None:
        self.write("AGENTS.md", "# Shared\n")
        (self.root / "CLAUDE.md").symlink_to("AGENTS.md")
        self.assertEqual(self.pks("init", "--yes").returncode, 0)
        agents = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual(agents.count("<!-- PKS:START -->"), 1)
        self.assertNotIn("@AGENTS.md", agents)

    def test_existing_docs_are_left_untouched_ignoring_case(self) -> None:
        self.write("docs/ARCHITECTURE.md", "# Existing architecture\n")
        self.write("design/tokens.css", ":root {}\n")
        result = self.pks("init", "--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("docs/ARCHITECTURE.md", result.stdout)
        self.assertEqual(
            (self.root / "docs/ARCHITECTURE.md").read_text(encoding="utf-8"),
            "# Existing architecture\n",
        )
        names = [path.name for path in (self.root / "docs").iterdir() if path.name.casefold() == "architecture.md"]
        self.assertEqual(names, ["ARCHITECTURE.md"])
        self.assertEqual((self.root / "design/tokens.css").read_text(encoding="utf-8"), ":root {}\n")

    def test_existing_skill_folder_blocks_installation(self) -> None:
        self.write(".claude/skills/pks-audit/SKILL.md", "mine\n")
        before = self.snapshot()
        result = self.pks("init", "--yes")
        self.assertEqual(result.returncode, 1)
        self.assertIn(".claude/skills/pks-audit", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_warns_when_git_ignores_pks_files(self) -> None:
        run_git(self.root, "init")
        self.write(".gitignore", ".claude/\n")
        result = self.pks("init", "--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Git ignores", result.stdout)
        self.assertIn(".claude/skills/pks-capture/SKILL.md", result.stdout)

    def test_does_not_commit(self) -> None:
        run_git(self.root, "init")
        self.pks("init", "--yes")
        log = subprocess.run(["git", "-C", str(self.root), "rev-list", "--all"], capture_output=True, text=True)
        self.assertEqual(log.stdout.strip(), "")


class UpdateTest(PksTestCase):
    def install_and_commit(self) -> None:
        run_git(self.root, "init")
        self.assertEqual(self.pks("init", "--yes").returncode, 0)
        run_git(self.root, "add", "-A")
        run_git(self.root, "commit", "-m", "Install PKS")

    def test_requires_installation(self) -> None:
        result = self.pks("update", "--yes")
        self.assertEqual(result.returncode, 1)
        self.assertIn("pks init", result.stderr)

    def test_up_to_date_changes_nothing(self) -> None:
        self.install_and_commit()
        before = self.snapshot()
        result = self.pks("update", "--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("up to date", result.stdout)
        self.assertEqual(self.snapshot(), before)

    def test_old_version_refreshes_package_files_only(self) -> None:
        self.install_and_commit()
        self.write("docs/product.md", "# My product\n")
        self.write("docs/decisions/0001-keep-it.md", "# Keep it\n")
        (self.root / "AGENTS.md").write_text(
            "# Mine\n\n<!-- PKS:START -->\nold rule\n<!-- PKS:END -->\n\n## After\n",
            encoding="utf-8",
        )
        self.write(".claude/skills/my-own/SKILL.md", "mine\n")
        self.write(".claude/skills/pks-old/SKILL.md", "retired\n")
        self.write(".agents/skills/pks-capture/extra.md", "stale\n")
        self.write(".pks/version", "0.9.0\n")
        run_git(self.root, "add", "-A")
        run_git(self.root, "commit", "-m", "Work")

        result = self.pks("update", "--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / ".pks/version").read_text(encoding="utf-8").strip(), VERSION)
        self.assertEqual((self.root / "docs/product.md").read_text(encoding="utf-8"), "# My product\n")
        self.assertTrue((self.root / "docs/decisions/0001-keep-it.md").is_file())
        self.assertTrue((self.root / ".claude/skills/my-own/SKILL.md").is_file())
        self.assertFalse((self.root / ".claude/skills/pks-old").exists())
        self.assertFalse((self.root / ".agents/skills/pks-capture/extra.md").exists())
        agents = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertTrue(agents.startswith("# Mine\n"))
        self.assertTrue(agents.rstrip().endswith("## After"))
        self.assertNotIn("old rule", agents)
        self.assertIn("## Product knowledge (PKS)", agents)

    def test_uncommitted_skill_changes_stop_the_update(self) -> None:
        self.install_and_commit()
        skill = self.root / ".claude/skills/pks-capture/SKILL.md"
        skill.write_text("local edit\n", encoding="utf-8")
        result = self.pks("update", "--yes")
        self.assertEqual(result.returncode, 1)
        self.assertIn("uncommitted", result.stderr)
        self.assertEqual(skill.read_text(encoding="utf-8"), "local edit\n")
        self.assertEqual(self.pks("update", "--yes", "--force").returncode, 0)
        self.assertNotEqual(skill.read_text(encoding="utf-8"), "local edit\n")

    def test_newer_project_version_is_refused(self) -> None:
        self.install_and_commit()
        self.write(".pks/version", "99.0.0\n")
        result = self.pks("update", "--yes")
        self.assertEqual(result.returncode, 1)
        self.assertIn("newer", result.stderr)

    def test_dry_run_changes_nothing(self) -> None:
        self.install_and_commit()
        self.write(".pks/version", "0.9.0\n")
        run_git(self.root, "add", "-A")
        run_git(self.root, "commit", "-m", "Old version")
        before = self.snapshot()
        result = self.pks("update", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.snapshot(), before)


class InstallScriptTest(unittest.TestCase):
    def setUp(self) -> None:
        tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(tempdir.cleanup)
        self.temp = Path(tempdir.name)
        self.bin_dir = self.temp / "bin"
        self.pks_home = self.temp / "share" / "pks"
        self.source = self.temp / "source"
        subprocess.run(["git", "clone", "-q", str(REPO_ROOT), str(self.source)], check=True, capture_output=True)
        # The clone has only committed files; give it this working tree so tests see uncommitted changes.
        for name in ("bin/pks", "VERSION"):
            (self.source / name).write_bytes((REPO_ROOT / name).read_bytes())
        self.env = {
            "PATH": "/usr/bin:/bin:/opt/homebrew/bin:/usr/local/bin",
            "HOME": str(self.temp),
            "PKS_BIN_DIR": str(self.bin_dir),
            "PKS_HOME": str(self.pks_home),
            "PKS_REPO_URL": self.source.as_uri(),
        }
        run_git(self.source, "add", "-A")
        run_git(self.source, "commit", "--allow-empty", "-m", "Current state")

    def run_piped(self) -> subprocess.CompletedProcess[str]:
        """Run the script the way `curl ... | sh` does: from stdin, in an unrelated folder."""
        return subprocess.run(
            ["sh"],
            input=(REPO_ROOT / "install.sh").read_text(encoding="utf-8"),
            cwd=self.temp,
            env=self.env,
            text=True,
            capture_output=True,
            check=False,
        )

    def commit_to_source(self, name: str) -> None:
        (self.source / name).write_text("x\n", encoding="utf-8")
        run_git(self.source, "add", "-A")
        run_git(self.source, "commit", "-m", f"Add {name}")

    def test_checkout_links_itself(self) -> None:
        for _ in range(2):
            result = subprocess.run(
                ["sh", str(REPO_ROOT / "install.sh")],
                env=self.env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.bin_dir / "pks").resolve(), PKS.resolve())
        self.assertFalse(self.pks_home.exists())

    def test_installs_latest_release_and_ignores_unreleased_commits(self) -> None:
        run_git(self.source, "tag", "v1.9.0")
        self.commit_to_source("after-1-9.txt")
        run_git(self.source, "tag", "v1.10.0")
        self.commit_to_source("unreleased.txt")

        result = self.run_piped()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.bin_dir / "pks").resolve(), (self.pks_home / "bin" / "pks").resolve())
        self.assertTrue((self.pks_home / "after-1-9.txt").exists(), "1.10 sorts after 1.9")
        self.assertFalse((self.pks_home / "unreleased.txt").exists())
        version = subprocess.run([str(self.bin_dir / "pks"), "--version"], text=True, capture_output=True, env=self.env)
        self.assertEqual(version.returncode, 0, version.stderr)

    def test_running_again_moves_to_a_new_release(self) -> None:
        run_git(self.source, "tag", "v1.0.0")
        self.assertEqual(self.run_piped().returncode, 0)
        self.assertFalse((self.pks_home / "new.txt").exists())
        self.commit_to_source("new.txt")
        run_git(self.source, "tag", "v1.1.0")
        result = self.run_piped()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.pks_home / "new.txt").exists())

    def test_repository_without_a_release_is_refused(self) -> None:
        result = self.run_piped()
        self.assertEqual(result.returncode, 1)
        self.assertIn("No PKS release", result.stderr)

    def test_foreign_install_folder_is_refused(self) -> None:
        self.pks_home.mkdir(parents=True)
        (self.pks_home / "mine.txt").write_text("keep\n", encoding="utf-8")
        result = self.run_piped()
        self.assertEqual(result.returncode, 1)
        self.assertIn("not a PKS checkout", result.stderr)
        self.assertEqual((self.pks_home / "mine.txt").read_text(encoding="utf-8"), "keep\n")

    def test_existing_command_file_is_refused(self) -> None:
        self.bin_dir.mkdir()
        (self.bin_dir / "pks").write_text("mine\n", encoding="utf-8")
        result = self.run_piped()
        self.assertEqual(result.returncode, 1)
        self.assertIn("not a link", result.stderr)
        self.assertFalse(self.pks_home.exists())


class ReleaseTest(unittest.TestCase):
    def test_changelog_describes_the_current_version(self) -> None:
        self.assertIn(f"## {VERSION}\n", (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))

    def test_every_skill_is_named_after_its_folder(self) -> None:
        for skill in SKILLS:
            text = (REPO_ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn(f"name: {skill}\n", text)


if __name__ == "__main__":
    unittest.main()
