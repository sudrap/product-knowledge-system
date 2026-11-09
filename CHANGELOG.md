# Changelog

Mark a version that changes the `docs/` structure with `[docs-structure]`. `pks update` then tells people to run `pks-setup`.

## 1.6.0

PKS now keeps where the work stands, so an agent in a new conversation picks up where the last one stopped, with or without a tracker.

- `docs/PROJECT.md` has a fixed "Current state": when it was updated, what is in progress, the next steps and what to watch out for. Claude Code loads `docs/PROJECT.md` in every conversation, and Codex reads it by the rule. An older section is brought to this form the first time the agent updates it.
- While working, the agent keeps its own notes in `.pks/notes/`, one file per topic and outside Git. A new conversation mentions unfinished notes and asks whether to continue, move them to `docs/` or delete them. Brainstorm and setup notes live there too, and `pks update` moves them from `.pks/brainstorms/`.
- At the end of a block of work, the agent offers one list of writes, one line each: the current state, records the work made untrue, and anything important. Nothing goes to `docs/` without your yes. A fix to a record that a code change made untrue goes into the same commit as that change.
- The agent checks the related records before any work, not only product, business or architecture work.
- The project's rules for agents live only in `AGENTS.md`, and agents change them only when you ask. `pks init` and `pks update` tell you when `CLAUDE.md` repeats rules from `AGENTS.md`, and change nothing.
- `pks update` always replaces the `pks-*` skills, so it no longer stops right after `pks init` just because nothing is committed yet. `--force` is now only for a project with a newer PKS than the command.

## 1.5.0

Add the `pks view` command and the `pks-view` skill: read `docs/` in your browser, with all documents in a side panel and formatted text. It only reads, only this computer can reach it, and the page updates by itself when a document changes.

## 1.4.0

`pks update` now downloads the latest PKS release by itself, then updates the project, so the install command is only needed the first time. Without a connection it says so and uses what it has. A development checkout stays as it is. If you have an older version, run the install command one last time.

Ctrl+D at a question now ends with "Nothing changed" instead of an error listing.

## 1.3.0

`pks-setup` now leads you through the setup step by step. It asks one question at a time, shows how many there are ("Question 2 of 5"), and offers answers, or you can write your own. An interrupted setup can continue in another conversation.

A new project gets at most five questions, and you can end at any time. A project with history gets at most ten, about what matters most, followed by a short review: what will be written, which decisions get recorded, and what happens to existing material. Nothing is written until you agree. Decisions are settled in the review, so nothing waits for confirmation unless you are unsure about it.

## 1.2.0

Add `pks uninstall`, which removes the command and the download. Projects stay as they are.

## 1.1.0

Add the `pks-brainstorm` skill: the agent leads a brainstorm one question at a time, keeps notes that can be resumed in another conversation, and tells your points from its own suggestions. It starts when you ask, or after you accept its one offer.

Add a format for feature records. The install command now installs the latest release instead of the newest commit.

## 1.0.0

First release as a package: the `pks init` and `pks update` commands and the `pks-setup`, `pks-capture`, `pks-audit` and `pks-help` skills, for Claude Code and Codex.
