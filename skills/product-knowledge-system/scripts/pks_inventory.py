#!/usr/bin/env python3
"""Create a content-free, JSON inventory of a project's working tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def git_summary(root: Path) -> dict[str, object]:
    def run(*args: str) -> tuple[int, str]:
        completed = subprocess.run(
            ["git", "-C", str(root), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return completed.returncode, completed.stdout.strip()

    code, inside = run("rev-parse", "--is-inside-work-tree")
    if code or inside != "true":
        return {"is_repository": False}
    _, head = run("rev-parse", "--verify", "HEAD")
    _, branch = run("branch", "--show-current")
    _, status = run("status", "--porcelain=v1")
    return {
        "is_repository": True,
        "head": head or None,
        "branch": branch or None,
        "porcelain_status_lines": len(status.splitlines()) if status else 0,
    }


def item(relative: str, candidate: Path) -> dict[str, object]:
    info = candidate.lstat()
    mode = info.st_mode
    entry: dict[str, object] = {"path": relative, "mode": stat.S_IMODE(mode)}
    if stat.S_ISLNK(mode):
        entry.update(kind="symlink", target=os.readlink(candidate))
    elif stat.S_ISREG(mode):
        entry.update(kind="file", size=info.st_size, sha256=digest(candidate))
    elif stat.S_ISDIR(mode):
        entry.update(kind="directory")
    else:
        entry.update(kind="special")
    return entry


def inventory(root: Path) -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    entries: list[dict[str, object]] = []
    errors: list[dict[str, str]] = []

    def visit(directory: Path, prefix: Path) -> None:
        try:
            children = sorted(directory.iterdir(), key=lambda path: path.name.casefold())
        except OSError as exc:
            errors.append({"path": prefix.as_posix() or ".", "error": str(exc)})
            return
        for child in children:
            relative_path = prefix / child.name
            relative = relative_path.as_posix()
            if child.name == ".git":
                continue
            try:
                entry = item(relative, child)
                entries.append(entry)
                if entry["kind"] == "directory":
                    visit(child, relative_path)
            except OSError as exc:
                errors.append({"path": relative, "error": str(exc)})

    visit(root, Path())
    return entries, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory every non-.git path in a project without printing contents.")
    parser.add_argument("project", nargs="?", default=".", help="Project root (default: current directory)")
    parser.add_argument("--output", type=Path, help="Write JSON to this path instead of stdout")
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")
    entries, errors = inventory(root)
    document = {
        "schemaVersion": "pks-inventory/v1",
        "generatedAt": datetime.now(UTC).isoformat(),
        "project": str(root),
        "excluded": [".git/ (Git object database and history; summarized separately)"],
        "git": git_summary(root),
        "entries": entries,
        "errors": errors,
    }
    rendered = json.dumps(document, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
