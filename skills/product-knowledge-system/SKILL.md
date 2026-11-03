---
name: product-knowledge-system
description: Bootstrap a portable Markdown Product Knowledge System (PKS), or safely plan and migrate an existing project's knowledge into it. Use for product vision, discovery, decisions, features, business, and planning knowledge that must work in both Claude Code and Codex.
---

# Product Knowledge System

Create a Git-tracked, tool-neutral product knowledge base. Canonical knowledge lives in Markdown under `docs/`; `AGENTS.md`, `CLAUDE.md`, and local skill wrappers are short navigation and safety layers only.

## Select the mode

- **Bootstrap**: use only for a new or effectively empty project, or when the user explicitly wants the PKS scaffold alongside existing work.
- **Migration**: use whenever project knowledge, instructions, documentation, or skills already exist in a different shape. Never silently classify a non-empty project as new.
- **Audit/search/workflow work**: preserve the existing PKS layout and use the relevant shared workflow in `docs/ai-workflows/`; do not reorganize the knowledge base unless requested.

Read [the PKS layout](references/pks-layout.md) for ownership, templates, and the shared-workflow model. For a migration, read [the migration protocol](references/migration-protocol.md) before taking any repository-changing action.

## Non-negotiable safety rules

- Begin with a read-only discovery pass. Read applicable repository instructions, current index files, documentation, local skills, Git status/history, and all plausible project-knowledge locations. Do not access secrets or copy credential material into Git.
- Inventory every in-scope filesystem item before migration with `scripts/pks_inventory.py`. It inventories the working tree (including untracked and ignored files) but records Git metadata separately instead of copying `.git` internals.
- For every source item, record one disposition in a migration map: retained, exact copy, referenced/linked, or approved merge. Preserve the original path and bytes by default. Never delete, move, or overwrite source material; an exception needs explicit, item-level user approval and an approval reference in the map.
- Classify the Git state of every canonical or preserved knowledge item. Canonical Markdown, shared workflows, local skill definitions, templates, project instructions, and retained source knowledge must be tracked and included in an approved commit. If an item is ignored, untracked, generated, or potentially secret-bearing, explain it and ask whether to track it, amend ignore rules, retain it outside Git, or exclude it as a documented exception.
- Surface exact duplicates, near duplicates, conflicting facts, unclear ownership, generated/vendor material, ignored files, and candidate secrets. Ask the user to resolve them before the write phase; do not infer a canonical version.
- Present the complete migration plan before any write: scope, inventory summary, source-to-destination map, files to create, conflicts, Git implications, unresolved questions, verification plan, and the exact approval sought. Wait for explicit approval.
- Do not alter application code, dependencies, infrastructure, branches, remotes, or external systems as part of PKS work unless the user separately requests and approves it.

## Bootstrap

1. Inspect the project and determine whether a Git repository exists. If not, propose `git init` as a separate planned change; never initialize or commit before approval.
2. Run `scripts/bootstrap_pks.py <project>` (plan mode) to list missing PKS files and collisions. It never overwrites files.
3. Ask about any collision, project name, or unknown source-of-truth. Do not invent product facts; use clearly marked placeholders.
4. Present the exact files to create, Git tracking checks, and a verification checklist. After approval, run `scripts/bootstrap_pks.py <project> --apply` and create only the approved files.
5. Verify that `docs/`, `AGENTS.md`, `CLAUDE.md`, `.agents/skills/`, `.claude/rules/`, and `.claude/skills/` are not ignored; then stage and commit the approved PKS material only when the user has explicitly approved the commit. Report the commit ID.

## Migration

1. Perform read-only discovery and write the inventory and draft map to a temporary location outside the project. Do not use temporary artifacts as canonical knowledge.
2. Map every existing instruction, local skill, template, notes file, product document, backlog, decision record, research artifact, and relevant Git-tracked or untracked item. Preserve uncertain material in place and record a reference until the user decides.
3. Run the bootstrap script in plan mode. It may add missing PKS structure but must not replace a conflicting target.
4. Ask the user to resolve each duplicate, factual conflict, ownership ambiguity, ignored-file issue, and source-file overwrite/move. If anything is unresolved, stop before writes.
5. After explicit plan approval, create only approved missing PKS files. Keep shared workflow definitions in `docs/ai-workflows/`; make `.agents/skills/` and `.claude/skills/` thin wrappers that point to them. Preserve existing tool-specific instructions unless their replacement was specifically approved.
6. Save the approved plan, inventory, map, and verification report in `docs/migrations/<migration-id>/` and add its entry to `docs/INDEX.md`. Record only paths, hashes, classifications, and decisions there—never secret contents.
7. Run `scripts/verify_pks_migration.py` against the before-inventory and approved map. Resolve every error before saying the migration is complete. Verify Git tracking for every mapped knowledge item, inspect the final diff, and commit only if included in the approved plan.

## Knowledge maintenance

- Navigate progressively: `docs/INDEX.md` → category `INDEX.md` → relevant record. Do not load the entire knowledge base by default.
- Preserve the distinction between inbox ideas, evaluated discovery, hypotheses, accepted decisions, rejected material, feature specifications, and observed implementation status.
- Do not treat an idea, hypothesis, plan, or AI inference as an approved decision. Do not change an accepted or rejected decision without explicit approval.
- Update the relevant index in the same approved change as a new canonical document. Use the stable IDs and status vocabulary in the layout reference.

## Completion report

Report the mode, source and created files, unresolved items, source-accounting/verification result, Git tracking state, commit ID if created, and the starting files for Claude Code and Codex. Mention every limitation honestly.
