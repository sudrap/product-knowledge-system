---
name: pks-help
description: Explain how to use the Product Knowledge System in this project and list its skills and commands. Use when the user asks how PKS works, what it can do, or for PKS help.
---

# PKS help

Show this briefly, in the user's language, and adapt the invocation to the tool: `/name` in Claude Code, `$name` in Codex. Add the installed version from `.pks/version`.

**What it is:** the project's know-how lives in `docs/`, so people and agents can read it and it travels with Git.

**Works by itself**

- At the start of a conversation the agent reads `docs/PROJECT.md`, including where the work stands, and tells you about notes left from an earlier conversation.
- Before any work, and on questions, it checks the related records in `docs/` and tells you when something applies or conflicts.
- While working it keeps notes in `.pks/notes/`, so nothing is lost if the conversation ends.
- At the end of a block of work it offers one list of writes: the current state, records the work made untrue, and anything important. Nothing goes to `docs/` without your yes.
- When a longer product discussion has no conclusion, the agent offers once to turn it into a brainstorm.

**Just say it**

| Say | What happens |
| --- | --- |
| "Write this down", "zapiš to" | Recorded in `docs/`; the agent shows where (`pks-capture`) |
| "Let's brainstorm", "pojďme brainstormovat" | The agent asks one question at a time and keeps notes in `.pks/notes/`, so you can continue in another conversation (`pks-brainstorm`) |
| "Put it on the roadmap", "dej to do roadmapy" | Recorded in `docs/roadmap.md` (`pks-capture`) |
| "Where did we stop?", "co je rozdělané" | Answered from the current state in `docs/PROJECT.md` and the notes in `.pks/notes/` |
| "What are we planning?" | Answered from `docs/roadmap.md` |
| "What did we decide about X?" | Answered from `docs/decisions/` |
| "Go through the inbox", "projdi inbox" | Proposals for each new idea (`pks-audit`) |
| "Run an audit", "udělej audit" | Report on what is outdated or ready to plan (`pks-audit`) |
| "Show me the docs", "ukaž mi dokumentaci" | `docs/` opens in your browser, read-only (`pks-view`) |

**Skills:** `pks-setup` (initial fill), `pks-capture`, `pks-brainstorm`, `pks-audit`, `pks-view`, `pks-help`.

**Terminal commands:** `pks init` installs PKS into a project. `pks update` downloads the latest release, updates the project and never touches `docs/`. Both only change files; committing is up to you. `pks view` shows `docs/` in your browser and changes nothing. `pks uninstall` removes the command from this computer; projects stay as they are.

**Where things are:** `PROJECT.md`, `product.md`, `business.md`, `architecture.md`, `roadmap.md` and, once needed, `development.md`, plus `discovery/`, `decisions/` and `features/`. In `discovery/` and `decisions/`, what is current sits directly in the folder; subfolders hold what is waiting or finished. Working notes are in `.pks/notes/`, outside Git. The project's rules for agents are in `AGENTS.md`; `CLAUDE.md` only imports them.
