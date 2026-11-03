#!/usr/bin/env python3
"""Plan or create a non-destructive PKS scaffold.

The script creates missing files only. It is intentionally not a migration tool:
existing files are reported as conflicts and are never changed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from textwrap import dedent


WORKFLOWS = {
    "capture-discovery": (
        "Capture an unapproved product idea from the current conversation.",
        """# Capture discovery

Read `docs/INDEX.md`, `docs/discovery/INDEX.md`, and relevant related records.
Prepare a proposed inbox or discovery record, stable ID if applicable, and index change.
Do not write or promote the idea to a decision without explicit user approval.
""",
    ),
    "review-discovery": (
        "Review discovery items and propose classification or next steps.",
        """# Review discovery

Read the discovery index and only the candidate records. Identify duplicates, gaps,
research needs, hypotheses, and proposed status changes. Show a reversible proposal
and wait for explicit approval before changing canonical files.
""",
    ),
    "record-decision": (
        "Prepare a product, business, or technical decision record.",
        """# Record decision

Read relevant indexes, discovery, feature, and existing decision records. Draft a
decision with context, options, rationale, consequences, status, and links. The
user owns the decision: do not mark it accepted or write it without explicit approval.
""",
    ),
    "product-review": (
        "Review product knowledge for conflicts, gaps, and stale assumptions.",
        """# Product review

Navigate through the relevant indexes and compare vision, strategy, decisions,
features, business material, and planning. Report evidence, contradictions, stale
items, and open questions. Do not rewrite canonical knowledge without approval.
""",
    ),
    "knowledge-search": (
        "Find relevant product knowledge without loading the entire knowledge base.",
        """# Knowledge search

Start at `docs/INDEX.md`, then category indexes, then only relevant records. State
which files support the answer and distinguish approved decisions from proposals,
hypotheses, and inferences. Report conflicts or missing evidence.
""",
    ),
    "knowledge-audit": (
        "Audit PKS navigation, links, duplicate knowledge, and unresolved records.",
        """# Knowledge audit

Inspect indexes and records proportionately. Report orphaned documents, broken or
missing references, duplicate ideas, stale status, missing metadata, and unresolved
conflicts. Propose changes but do not apply them without explicit approval.
""",
    ),
}


def md(text: str) -> str:
    return dedent(text).lstrip()


def wrapper(name: str, description: str) -> str:
    return md(
        f"""
        ---
        name: {name}
        description: {description}
        ---

        # {name.replace('-', ' ').title()}

        Read and follow the canonical shared workflow:
        `docs/ai-workflows/{name}.md`.

        Canonical product knowledge is under `docs/`. Start with `docs/INDEX.md`,
        load only relevant indexes and records, and do not modify canonical knowledge
        without explicit user approval.
        """
    )


def scaffold() -> dict[str, str]:
    files: dict[str, str] = {
        "AGENTS.md": md(
            """
            # Product knowledge instructions

            Canonical project knowledge is portable Markdown under `docs/`.
            Start product work with `docs/INDEX.md` and `docs/PROJECT.md`, then read
            only the relevant category index and records. Do not load the whole tree.

            The user is the final decision maker. Never treat an idea, hypothesis,
            plan, or inference as an approved decision. Do not change accepted or
            rejected decisions, delete source knowledge, or alter canonical documents
            without explicit approval.

            Shared AI workflows live in `docs/ai-workflows/`. Tool-specific skills are
            thin wrappers only. Keep facts, decisions, and rationale out of tool memory
            and in the Git-tracked Markdown knowledge base.
            """
        ),
        "CLAUDE.md": md(
            """
            # Product knowledge instructions

            Canonical project knowledge is portable Markdown under `docs/`.
            Start product work with `docs/INDEX.md` and `docs/PROJECT.md`, then read
            only the relevant category index and records. Do not load the whole tree.

            The user is the final decision maker. Never treat an idea, hypothesis,
            plan, or inference as an approved decision. Do not change accepted or
            rejected decisions, delete source knowledge, or alter canonical documents
            without explicit approval.

            Shared AI workflows live in `docs/ai-workflows/`. Tool-specific skills are
            thin wrappers only. Keep facts, decisions, and rationale out of tool memory
            and in the Git-tracked Markdown knowledge base.
            """
        ),
        ".claude/rules/knowledge-management.md": md(
            """
            # Knowledge management rule

            Use `docs/INDEX.md` as the entry point to the portable product knowledge
            base. Read category indexes before records; do not load all documentation.
            Ask before writing canonical knowledge, changing decision status, replacing
            source material, or resolving a factual conflict. Keep shared procedures in
            `docs/ai-workflows/`, not in this tool-specific rule.
            """
        ),
        "docs/INDEX.md": md(
            """
            # Product Knowledge Index

            This is the canonical, Git-tracked product knowledge base. Indexes are
            navigation; read only the sections relevant to the task.

            | Area | Entry point | Use for |
            | --- | --- | --- |
            | Project | `PROJECT.md` | purpose, scope, current state, known unknowns |
            | Product | `product/INDEX.md` | vision, strategy, users, value, roadmap |
            | Discovery | `discovery/INDEX.md` | inbox, ideas, hypotheses, research, rejected items |
            | Decisions | `decisions/INDEX.md` | approved, proposed and superseded decisions |
            | Features | `features/INDEX.md` | feature specifications and open questions |
            | Business | `business/INDEX.md` | market, pricing, monetization, metrics |
            | Planning | `planning/INDEX.md` | current focus, backlog and milestones |
            | Workflows | `ai-workflows/` | shared procedures for AI-assisted work |
            | History | `changelog.md` | meaningful knowledge-base changes |

            ## Rules

            - The user is the final decision maker.
            - An idea or hypothesis is not an approved decision.
            - Preserve rejected material and its rationale.
            - Update the relevant index when adding a canonical record.
            - Report conflicts and missing evidence instead of inventing answers.
            """
        ),
        "docs/PROJECT.md": md(
            """
            # Project

            ## Purpose

            [To be defined with the project owner.]

            ## Current state

            [To be defined.]

            ## Scope and non-goals

            [To be defined.]

            ## Known unknowns

            [To be defined.]
            """
        ),
        "docs/changelog.md": md(
            """
            # Product Knowledge Changelog

            Record material changes to canonical knowledge. Do not use this as a copy
            of Git history.
            """
        ),
        "docs/product/INDEX.md": "# Product Index\n\nNavigate vision, strategy, target users, value proposition, and roadmap.\n",
        "docs/product/vision.md": "# Product Vision\n\n[To be defined.]\n",
        "docs/product/strategy.md": "# Product Strategy\n\n[To be defined.]\n",
        "docs/product/target-users.md": "# Target Users\n\n[To be defined.]\n",
        "docs/product/value-proposition.md": "# Value Proposition\n\n[To be defined.]\n",
        "docs/product/roadmap.md": "# Product Roadmap\n\n[To be defined.]\n",
        "docs/discovery/INDEX.md": md(
            """
            # Discovery Index

            | Collection | Location | Meaning |
            | --- | --- | --- |
            | Inbox | `inbox/` | unprocessed input |
            | Ideas | `ideas/` | evaluated or categorized ideas |
            | Hypotheses | `hypotheses/` | assumptions to validate |
            | Research | `research/` | evidence and findings |
            | Rejected | `rejected/` | rejected material and rationale |

            ## Active items

            | ID | Title | Status | File |
            | --- | --- | --- |
            """
        ),
        "docs/discovery/inbox/.gitkeep": "",
        "docs/discovery/ideas/.gitkeep": "",
        "docs/discovery/hypotheses/.gitkeep": "",
        "docs/discovery/research/.gitkeep": "",
        "docs/discovery/rejected/.gitkeep": "",
        "docs/decisions/INDEX.md": md(
            """
            # Decisions Index

            Decision records retain context, options, rationale and consequences.
            Do not rewrite an accepted or rejected record without explicit approval.

            | ID | Title | Status | Area | File |
            | --- | --- | --- | --- | --- |
            """
        ),
        "docs/decisions/product/.gitkeep": "",
        "docs/decisions/business/.gitkeep": "",
        "docs/decisions/technical/.gitkeep": "",
        "docs/features/INDEX.md": md(
            """
            # Features Index

            Feature directories hold an overview, requirements and open questions.
            Link each feature to related discovery and decisions.

            | ID | Feature | Status | Directory |
            | --- | --- | --- | --- |
            """
        ),
        "docs/business/INDEX.md": "# Business Index\n\nNavigate monetization, pricing, competitors, and metrics.\n",
        "docs/business/monetization.md": "# Monetization\n\n[To be defined.]\n",
        "docs/business/pricing.md": "# Pricing\n\n[To be defined.]\n",
        "docs/business/competitors.md": "# Competitors\n\n[To be defined.]\n",
        "docs/business/metrics.md": "# Metrics\n\n[To be defined.]\n",
        "docs/planning/INDEX.md": "# Planning Index\n\nNavigate current focus, backlog and milestones.\n",
        "docs/planning/current-focus.md": "# Current Focus\n\n[To be defined.]\n",
        "docs/planning/backlog.md": "# Backlog\n\n[To be defined.]\n",
        "docs/planning/milestones.md": "# Milestones\n\n[To be defined.]\n",
    }
    for name, (description, content) in WORKFLOWS.items():
        files[f"docs/ai-workflows/{name}.md"] = content
        for wrapper_root in (".agents/skills", ".claude/skills"):
            files[f"{wrapper_root}/{name}/SKILL.md"] = wrapper(name, description)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan or create missing PKS scaffold files.")
    parser.add_argument("project", nargs="?", default=".", help="Project root (default: current directory)")
    parser.add_argument("--apply", action="store_true", help="Create missing files; never overwrite existing files")
    parser.add_argument("--json", action="store_true", help="Emit the plan as JSON")
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")

    templates = scaffold()
    create = sorted(path for path in templates if not (root / path).exists())
    conflicts = sorted(path for path in templates if (root / path).exists())
    result = {
        "project": str(root),
        "mode": "apply" if args.apply else "plan",
        "would_create" if not args.apply else "created": create,
        "conflicts": conflicts,
        "overwrite_policy": "never",
    }

    if args.apply:
        for relative in create:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(templates[relative], encoding="utf-8")

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        verb = "Created" if args.apply else "Would create"
        print(f"{verb} {len(create)} PKS files in {root}")
        for path in create:
            print(f"  + {path}")
        if conflicts:
            print(f"Existing paths left untouched ({len(conflicts)}):")
            for path in conflicts:
                print(f"  ! {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
