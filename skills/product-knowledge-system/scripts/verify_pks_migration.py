#!/usr/bin/env python3
"""Verify that a PKS migration accounted for every pre-migration source item."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath

from pks_inventory import inventory


ALLOWED_DISPOSITIONS = {"retained", "copied", "referenced", "merged", "changed-with-approval"}


def load_json(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        result = json.load(handle)
    if not isinstance(result, dict):
        raise ValueError(f"JSON object required: {path}")
    return result


def safe_relative(value: object) -> bool:
    if not isinstance(value, str) or not value or value.startswith("/"):
        return False
    path = PurePosixPath(value)
    return ".." not in path.parts and "." not in path.parts


def same_fingerprint(before: dict[str, object], after: dict[str, object]) -> bool:
    if before.get("kind") != after.get("kind"):
        return False
    kind = before.get("kind")
    if kind == "file":
        return before.get("sha256") == after.get("sha256")
    if kind == "symlink":
        return before.get("target") == after.get("target")
    return True


def verify(before: dict[str, object], mapping: dict[str, object], current: list[dict[str, object]]) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    before_entries = before.get("entries")
    map_items = mapping.get("items")
    if not isinstance(before_entries, list):
        return {"errors": ["before inventory has no entries list"], "warnings": warnings}
    if mapping.get("schemaVersion") != "pks-migration-map/v1":
        errors.append("mapping schemaVersion must be pks-migration-map/v1")
    if not isinstance(mapping.get("approvalRef"), str) or not mapping["approvalRef"].strip():
        errors.append("mapping must contain a non-empty root approvalRef")
    if not isinstance(map_items, list):
        return {"errors": errors + ["mapping has no items list"], "warnings": warnings}

    prior_by_path = {entry.get("path"): entry for entry in before_entries if isinstance(entry, dict)}
    current_by_path = {entry.get("path"): entry for entry in current if isinstance(entry, dict)}
    map_by_source: dict[str, dict[str, object]] = {}
    for raw in map_items:
        if not isinstance(raw, dict):
            errors.append("mapping contains a non-object item")
            continue
        source = raw.get("source")
        if not safe_relative(source):
            errors.append(f"invalid mapping source: {source!r}")
            continue
        assert isinstance(source, str)
        if source in map_by_source:
            errors.append(f"duplicate mapping source: {source}")
        map_by_source[source] = raw
        if source not in prior_by_path:
            errors.append(f"mapping source was not in before inventory: {source}")

    for source in sorted(prior_by_path):
        if source not in map_by_source:
            errors.append(f"before-inventory item has no mapping: {source}")

    checked = 0
    for source, original in sorted(prior_by_path.items()):
        row = map_by_source.get(source)
        if not row:
            continue
        checked += 1
        disposition = row.get("disposition")
        destinations = row.get("destinations", [])
        if disposition not in ALLOWED_DISPOSITIONS:
            errors.append(f"{source}: unsupported disposition {disposition!r}")
            continue
        if not isinstance(destinations, list) or not all(safe_relative(value) for value in destinations):
            errors.append(f"{source}: destinations must be safe relative paths")
            continue
        if disposition in {"copied", "referenced", "merged", "changed-with-approval"} and not destinations:
            errors.append(f"{source}: {disposition} requires at least one destination")
        if disposition == "changed-with-approval":
            approval = row.get("approvalRef")
            if not isinstance(approval, str) or not approval.strip():
                errors.append(f"{source}: changed-with-approval requires approvalRef")

        current_source = current_by_path.get(source)
        if disposition != "changed-with-approval":
            if not current_source:
                errors.append(f"{source}: original source is missing")
            elif not same_fingerprint(original, current_source):
                errors.append(f"{source}: original source no longer has its before-migration fingerprint")

        for destination in destinations:
            assert isinstance(destination, str)
            present = current_by_path.get(destination)
            if not present:
                errors.append(f"{source}: destination is missing: {destination}")
                continue
            if disposition == "copied" and not same_fingerprint(original, present):
                errors.append(f"{source}: copied destination does not match source bytes: {destination}")
            if disposition in {"referenced", "merged"}:
                warnings.append(
                    f"{source}: {disposition} destination exists but needs human semantic review: {destination}"
                )

    return {
        "schemaVersion": "pks-migration-verification/v1",
        "checked_source_items": checked,
        "errors": errors,
        "warnings": warnings,
        "result": "pass" if not errors else "fail",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a PKS migration map against a pre-migration inventory.")
    parser.add_argument("--project", required=True, type=Path, help="Project root after migration")
    parser.add_argument("--before", required=True, type=Path, help="Pre-migration inventory JSON")
    parser.add_argument("--mapping", required=True, type=Path, help="Approved migration map JSON")
    parser.add_argument("--output", type=Path, help="Write report JSON to this path instead of stdout")
    parser.add_argument("--strict", action="store_true", help="Fail when warnings require human review")
    args = parser.parse_args()

    root = args.project.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")
    try:
        before = load_json(args.before)
        mapping = load_json(args.mapping)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    current, inventory_errors = inventory(root)
    report = verify(before, mapping, current)
    if inventory_errors:
        report["errors"].extend(f"post-migration inventory error at {row['path']}: {row['error']}" for row in inventory_errors)
        report["result"] = "fail"
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 1 if report["errors"] or (args.strict and report["warnings"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
