---
name: pks-setup
description: Fill a project's Product Knowledge System after `pks init` by exploring the project, migrating existing knowledge and asking what the code cannot tell. Use when the user asks to set up or fill PKS, or after `pks update` reports a docs structure change.
---

# PKS setup

Bring `docs/` to its initial state, so the agent and the user can rely on it. Read [the layout](references/pks-layout.md) first. For a project with history, also read [the migration protocol](references/migration-protocol.md) before any write.

## Safety rules

- Start read-only. Do not write until the user has approved a plan.
- Never delete, move or overwrite existing material without item-level approval.
- Never change a location the user marks read-only. Design folders are read-only by default. Never call design-sync tools such as `DesignSync`; link to design systems instead.
- Do not read secrets or copy them into Git. If a file looks secret-bearing by its name, do not open it; list it and ask.
- Do not invent product facts. Anything unknown stays `[unknown]`.
- Do not treat an inference as a decision. Decisions inferred from code or tickets go to `docs/decisions/proposed/`.
- Do not change application code, dependencies, branches, remotes or external systems.
- Do not commit without the user's yes.

## Pick the path

1. `.pks/version` must exist. If it does not, tell the user to run `pks init` and stop.
2. Ask which language the documentation should use, unless `docs/PROJECT.md` already states one. Record it there, and write everything in that language, including template headings.
3. Choose:
   - **New project** (no real code or documents yet): use the short path.
   - **Project with history:** use the full path.
   - **Re-run:** check what is still `[unknown]` or missing and continue from there. Do not redo approved work. After a docs structure change, compare `docs/` with the layout and propose the moves as a plan.

## Short path

Ask a few short questions: what the project is, who it is for, what comes first. Fill in `docs/PROJECT.md`, `docs/product.md` and `docs/roadmap.md`. Leave the rest as `[unknown]`. Then continue with "Turn off tool memory".

## Full path

### 1. Explore, read-only

Create the inventory outside the project:

```text
python3 <this-skill>/scripts/pks_inventory.py . --output <temp>/inventory-before.json
```

Use subagents freely for mapping the repository and reading large material, if your tool has them. This saves time and context. Otherwise read progressively.

Look at:

- documentation, notes, plans, decision records, research and instruction files;
- the code and Git history, for structure, tech stack and project state;
- Claude's memory for this project, read as ordinary files from `~/.claude/projects/<project>/memory/`. `<project>` is the repository path with non-alphanumeric characters replaced by `-`; list `~/.claude/projects/` to find it;
- any tracker or wiki the user names, limited to this project, with whatever access you have. Ask whether such sources exist.

### 2. Show what you found and ask

Summarize the project in a few lines. Then ask only about what the project cannot tell you: vision, target users, pricing, reasons behind decisions. Ask at most five questions at a time. Anything unanswered stays `[unknown]`.

### 3. Present one plan and wait

Follow the migration protocol. The plan must also list:

- a destination for every Claude memory file: `docs/`, global instruction files, or leave it;
- every location to treat as read-only, for the user to confirm;
- every collision left by `pks init`, for example an existing `docs/ARCHITECTURE.md`, with a proposal. Prefer keeping an existing document and linking to it from `docs/PROJECT.md`.

### 4. Write what was approved

- `docs/PROJECT.md`: purpose, current state, unknowns, language, and the "Other locations" table with read-only marks.
- `docs/architecture.md`: an overview and the tech stack, not implementation details that can be read from the code.
- `docs/development.md`: only if there is something to say about building, running, debugging or solved problems, or a pointer to a design system.
- `docs/roadmap.md`: what is planned and why. Tasks stay in the tracker, if there is one.
- `docs/decisions/` for decisions the project records as made; `docs/decisions/proposed/` for inferred ones. Use the record format in the layout reference.

### 5. Verify

```text
python3 <this-skill>/scripts/verify_pks_migration.py --project . \
  --before <temp>/inventory-before.json --mapping <temp>/migration-map.json --strict
```

Fix every error before continuing. Save the plan, map and report in `.pks/migrations/<migration-id>/`. Record only paths, hashes, classifications and decisions there, never secret contents.

## Turn off tool memory

Do this last, after anything worth keeping has been migrated. Merge `"autoMemoryEnabled": false` into `.claude/settings.json`, keeping all other settings. Tell the user that Claude's memory files stay on disk but no longer load in this project. If your tool refuses to edit the file, give the user the exact setting and say that memory is still on.

## Finish

Report what was created, what stays `[unknown]`, what was left in place and the verification result. Offer one commit containing only the PKS changes. Point the user to `pks-help`.
