#!/usr/bin/env python3
"""Tests for the pks command: every test drives it as a real subprocess."""

from __future__ import annotations

import http.client
import os
import pty
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.parse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PKS = REPO_ROOT / "bin" / "pks"
VERSION = (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
SKILLS = ["pks-audit", "pks-brainstorm", "pks-capture", "pks-help", "pks-setup", "pks-view"]


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

    def test_ctrl_d_at_the_question_changes_nothing(self) -> None:
        master, slave = pty.openpty()
        self.addCleanup(os.close, master)
        self.addCleanup(os.close, slave)
        os.write(master, b"\x04")
        result = subprocess.run(
            [sys.executable, str(PKS), "init"], cwd=self.root, text=True, capture_output=True, stdin=slave, timeout=30
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Nothing changed", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
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
        subprocess.run(["git", "clone", "-q", "--no-tags", str(REPO_ROOT), str(self.source)], check=True, capture_output=True)
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


    def installed_pks(self, project: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(self.bin_dir / "pks"), *args],
            cwd=project,
            env=self.env,
            text=True,
            capture_output=True,
            stdin=subprocess.DEVNULL,
            timeout=120,
        )

    def install_with_project(self) -> Path:
        run_git(self.source, "tag", f"v{VERSION}")
        self.assertEqual(self.run_piped().returncode, 0)
        project = self.temp / "project"
        project.mkdir()
        init = self.installed_pks(project, "init", "--yes")
        self.assertEqual(init.returncode, 0, init.stderr)
        return project

    def release_in_source(self) -> None:
        (self.source / "VERSION").write_text("9.9.9\n", encoding="utf-8")
        skill = self.source / "skills" / "pks-help" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\nNew in this release.\n", encoding="utf-8")
        self.commit_to_source("new-release.txt")
        run_git(self.source, "tag", "v9.9.9")

    def test_update_downloads_the_latest_release_first(self) -> None:
        project = self.install_with_project()
        (project / "docs" / "product.md").write_text("mine\n", encoding="utf-8")
        self.release_in_source()

        result = self.installed_pks(project, "update", "--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Downloaded PKS 9.9.9.", result.stdout)
        self.assertEqual((self.pks_home / "VERSION").read_text(encoding="utf-8").strip(), "9.9.9")
        self.assertEqual((project / ".pks" / "version").read_text(encoding="utf-8").strip(), "9.9.9")
        self.assertIn("New in this release", (project / ".claude/skills/pks-help/SKILL.md").read_text(encoding="utf-8"))
        self.assertEqual((project / "docs" / "product.md").read_text(encoding="utf-8"), "mine\n")

        again = self.installed_pks(project, "update", "--yes")
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertNotIn("Downloaded", again.stdout)
        self.assertIn("up to date", again.stdout)

    def test_update_ignores_unreleased_commits(self) -> None:
        project = self.install_with_project()
        self.commit_to_source("unreleased.txt")
        result = self.installed_pks(project, "update", "--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.pks_home / "unreleased.txt").exists())

    def test_update_without_a_connection_uses_what_it_has(self) -> None:
        project = self.install_with_project()
        self.source.rename(self.temp / "gone")
        result = self.installed_pks(project, "update", "--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Could not check for a newer PKS release", result.stdout)
        self.assertEqual((project / ".pks" / "version").read_text(encoding="utf-8").strip(), VERSION)

    def test_update_dry_run_only_reports_a_new_release(self) -> None:
        project = self.install_with_project()
        self.release_in_source()
        result = self.installed_pks(project, "update", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PKS 9.9.9 is available", result.stdout)
        self.assertEqual((self.pks_home / "VERSION").read_text(encoding="utf-8").strip(), VERSION)
        self.assertEqual((project / ".pks" / "version").read_text(encoding="utf-8").strip(), VERSION)

    def test_update_from_a_checkout_leaves_the_checkout(self) -> None:
        project = self.temp / "project"
        project.mkdir()
        command = [sys.executable, str(self.source / "bin" / "pks")]
        init = subprocess.run([*command, "init", "--yes"], cwd=project, env=self.env, text=True, capture_output=True)
        self.assertEqual(init.returncode, 0, init.stderr)
        run_git(self.source, "tag", "v9.9.9")
        result = subprocess.run([*command, "update", "--yes"], cwd=project, env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Downloaded", result.stdout)
        self.assertEqual((self.source / "VERSION").read_text(encoding="utf-8").strip(), VERSION)

    def test_release_with_a_wrong_version_file_does_not_loop(self) -> None:
        project = self.install_with_project()
        self.commit_to_source("mistagged.txt")
        run_git(self.source, "tag", "v9.9.9")
        result = self.installed_pks(project, "update", "--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("Downloaded PKS 9.9.9."), 1)

    def test_uninstall_removes_the_download_and_leaves_projects(self) -> None:
        run_git(self.source, "tag", "v1.0.0")
        self.assertEqual(self.run_piped().returncode, 0)
        command = str(self.bin_dir / "pks")
        project = self.temp / "project"
        project.mkdir()
        init = subprocess.run([command, "init", "--yes"], cwd=project, env=self.env, text=True, capture_output=True)
        self.assertEqual(init.returncode, 0, init.stderr)
        before = sorted(path.relative_to(project).as_posix() for path in project.rglob("*"))

        dry_run = subprocess.run([command, "uninstall", "--dry-run"], env=self.env, text=True, capture_output=True)
        self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
        self.assertTrue((self.bin_dir / "pks").is_symlink())
        self.assertTrue(self.pks_home.exists())

        no_answer = subprocess.run(
            [command, "uninstall"], env=self.env, text=True, capture_output=True, stdin=subprocess.DEVNULL
        )
        self.assertEqual(no_answer.returncode, 1)
        self.assertTrue(self.pks_home.exists())

        result = subprocess.run([command, "uninstall", "--yes"], env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.bin_dir / "pks").exists())
        self.assertFalse((self.bin_dir / "pks").is_symlink())
        self.assertFalse(self.pks_home.exists())
        self.assertEqual(sorted(path.relative_to(project).as_posix() for path in project.rglob("*")), before)

    def test_uninstall_from_a_checkout_keeps_the_checkout(self) -> None:
        installed = subprocess.run(["sh", str(REPO_ROOT / "install.sh")], env=self.env, text=True, capture_output=True)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        result = subprocess.run([str(self.bin_dir / "pks"), "uninstall", "--yes"], env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.bin_dir / "pks").is_symlink())
        self.assertTrue(PKS.is_file())
        self.assertIn("stays", result.stdout)

    def test_uninstall_leaves_things_that_are_not_pks(self) -> None:
        self.bin_dir.mkdir()
        (self.bin_dir / "pks").write_text("mine\n", encoding="utf-8")
        self.pks_home.mkdir(parents=True)
        (self.pks_home / "mine.txt").write_text("keep\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(PKS), "uninstall", "--yes"], env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Nothing changed", result.stdout)
        self.assertEqual((self.bin_dir / "pks").read_text(encoding="utf-8"), "mine\n")
        self.assertEqual((self.pks_home / "mine.txt").read_text(encoding="utf-8"), "keep\n")


class ViewTest(unittest.TestCase):
    def setUp(self) -> None:
        tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(tempdir.cleanup)
        self.temp = Path(tempdir.name)
        self.root = self.temp / "project"
        self.write("docs/PROJECT.md", "# My project\n\nSee [the product](product.md), [the readme](../README.md), [a site](https://example.com/?a=1&b=2) and [bad](javascript:alert(1)).\n\nOpen: [unknown]\n")
        self.write("docs/product.md", "# Product\n\n**Bold** and `code` and <script>alert(1)</script>.\n\n| Plan | Price |\n| --- | ---: |\n| Free | 0 |\n\n- one\n  - nested\n- [x] done\n\n```sql\nselect '<b>';\n```\n\n> A quote\n")
        self.write("docs/decisions/0001-valid.md", "---\ntype: product\nupdated: 2026-11-05\nrelated: [0002-waiting]\n---\n\n# A valid decision\n")
        self.write("docs/decisions/proposed/0002-waiting.md", "---\ntype: technical\n---\n\n# A waiting decision\n")
        self.write("docs/discovery/inbox/new-idea.md", "# A new idea\n")
        self.write("docs/guides/setup.md", "# A guide in another folder\n")
        self.process: subprocess.Popen[str] | None = None

    def write(self, relative: str, text: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def start(self, *args: str, env: dict[str, str] | None = None) -> str:
        self.process = subprocess.Popen(
            [sys.executable, str(PKS), "view", *args],
            cwd=self.root,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
        )
        self.addCleanup(self.stop)
        self.assertTrue(self.process.stdout.readline().startswith("Viewing "))
        url = self.process.stdout.readline().strip()
        self.assertTrue(url.startswith("http://127.0.0.1:"), url)
        self.process.stdout.readline()
        return url

    def stop(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.kill()
        if self.process:
            self.process.communicate(timeout=10)

    def get(self, url: str, method: str = "GET", headers: dict[str, str] | None = None) -> tuple[int, str]:
        parts = urllib.parse.urlsplit(url)
        connection = http.client.HTTPConnection(parts.hostname, parts.port, timeout=10)
        self.addCleanup(connection.close)
        connection.request(method, parts.path, headers=headers or {})
        response = connection.getresponse()
        return response.status, response.read().decode("utf-8", errors="replace")

    def test_page_shows_formatted_documents_grouped_by_status(self) -> None:
        status, page = self.get(self.start("--no-open"))
        self.assertEqual(status, 200)
        for expected in (
            "<h1>Product</h1>",
            "<strong>Bold</strong>",
            "<code>code</code>",
            '<th class="right">Price</th>',
            "<li>one<ul><li>nested</li></ul></li>",
            'class="task done"',
            "<blockquote>",
            "Waiting for a decision",
            "A guide in another folder",
            ">guides<",
            '<span class="unknown">not known yet</span>',
            "product decision",
            "updated 2026-11-05",
            "Related: <a",
        ):
            self.assertIn(expected, page)
        self.assertNotIn("type: product", page)
        self.assertLess(page.index(">My project<"), page.index(">Product<"))
        self.assertLess(page.index(">Valid<"), page.index(">Waiting for a decision<"))

    def test_labels_follow_the_browser_language(self) -> None:
        _, page = self.get(self.start("--no-open"), headers={"Accept-Language": "cs-CZ,cs;q=0.9"})
        self.assertIn("Čeká na rozhodnutí", page)
        self.assertIn("zatím nevíme", page)
        self.assertIn('lang="cs"', page)

    def test_labels_follow_the_documentation_language_first(self) -> None:
        self.write("docs/PROJECT.md", "# My project\n\n**Jazyk dokumentace:** čeština\n")
        url = self.start("--no-open")
        self.assertIn("Čeká na rozhodnutí", self.get(url, headers={"Accept-Language": "en-GB"})[1])
        self.write("docs/PROJECT.md", "# My project\n\n**Documentation language:** English\n")
        self.assertIn("Waiting for a decision", self.get(url, headers={"Accept-Language": "cs-CZ"})[1])

    def test_links_and_text_are_safe(self) -> None:
        _, page = self.get(self.start("--no-open"))
        self.assertIn('<a href="#product">the product</a>', page)
        self.assertIn('class="outside"', page)
        self.assertIn('href="https://example.com/?a=1&amp;b=2" target="_blank" rel="noopener noreferrer"', page)
        self.assertNotIn('href="javascript', page)
        self.assertNotIn("<script>alert", page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
        self.assertIn("select &#x27;&lt;b&gt;&#x27;;", page)

    def test_only_the_secret_link_on_this_computer_works(self) -> None:
        url = self.start("--no-open")
        origin = url[: url.index("/", len("http://"))]
        self.assertEqual(self.get(url)[0], 200)
        self.assertEqual(self.get(f"{origin}/")[0], 404)
        self.assertEqual(self.get(f"{origin}/wrong/")[0], 404)
        self.assertEqual(self.get(f"{url}../../etc/passwd")[0], 404)
        self.assertEqual(self.get(url, headers={"Host": "evil.example"})[0], 403)
        self.assertEqual(self.get(url, method="POST")[0], 501)

    def test_page_notices_changes_and_nothing_is_written(self) -> None:
        def snapshot() -> dict[str, bytes]:
            return {str(path): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}

        before = snapshot()
        url = self.start("--no-open")
        status, first = self.get(f"{url}stamp")
        self.assertEqual(status, 200)
        self.assertEqual(self.get(f"{url}stamp")[1], first)
        self.assertIn(f'data-stamp="{first}"', self.get(url)[1])
        self.assertEqual(snapshot(), before)

        self.write("docs/product.md", "# Changed title\n")
        self.assertNotEqual(self.get(f"{url}stamp")[1], first)
        self.assertIn("Changed title", self.get(url)[1])

    def test_opens_the_browser_unless_told_not_to(self) -> None:
        marker = self.temp / "opened.txt"
        script = self.temp / "fake-browser"
        script.write_text(f'#!/bin/sh\nprintf "%s" "$1" > "{marker}"\n', encoding="utf-8")
        script.chmod(0o755)
        url = self.start(env={**os.environ, "BROWSER": f"{script} %s"})
        deadline = time.monotonic() + 10
        while not marker.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertEqual(marker.read_text(encoding="utf-8"), url)

    def test_ctrl_c_stops_it_cleanly(self) -> None:
        self.start("--no-open")
        self.process.send_signal(signal.SIGINT)
        output, errors = self.process.communicate(timeout=10)
        self.assertEqual(self.process.returncode, 0, errors)
        self.assertIn("Stopped.", output)
        self.assertNotIn("Traceback", errors)

    def test_project_without_docs_is_refused(self) -> None:
        empty = self.temp / "empty"
        empty.mkdir()
        result = subprocess.run(
            [sys.executable, str(PKS), "view", str(empty), "--no-open"],
            text=True,
            capture_output=True,
            stdin=subprocess.DEVNULL,
            timeout=30,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("no docs/ folder", result.stderr)


class ReleaseTest(unittest.TestCase):
    def test_changelog_describes_the_current_version(self) -> None:
        self.assertIn(f"## {VERSION}\n", (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))

    def test_every_skill_is_named_after_its_folder(self) -> None:
        for skill in SKILLS:
            text = (REPO_ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn(f"name: {skill}\n", text)


if __name__ == "__main__":
    unittest.main()
