---
name: pks-help
description: Explain how to use the Product Knowledge System in this project and list its skills and commands. Use when the user asks how PKS works, what it can do, or for PKS help.
---

# PKS help

Show this briefly, in the user's language, and adapt the invocation to the tool: `/name` in Claude Code, `$name` in Codex. Add the installed version from `.pks/version`.

**What it is:** the project's know-how lives in `docs/`, so people and agents can read it and it travels with Git.

**Works by itself**

- Before work touching product, business or architecture, and on questions, the agent checks `docs/` and tells you when something applies or conflicts.
- At the end of a topic the agent asks once whether to record anything important: yes / no / add something.
- When a longer product discussion has no conclusion, the agent offers once to turn it into a brainstorm.

**Just say it**

| Say | What happens |
| --- | --- |
| "Write this down", "zapiš to" | Recorded in `docs/`; the agent shows where (`pks-capture`) |
| "Let's brainstorm", "pojďme brainstormovat" | The agent asks one question at a time and keeps notes in `.pks/brainstorms/`, so you can continue in another conversation (`pks-brainstorm`) |
| "Put it on the roadmap", "dej to do roadmapy" | Recorded in `docs/roadmap.md` (`pks-capture`) |
| "Prepare stories from features/x" | Stories proposed from the specification and decisions, for your tracker |
| "What are we planning?" | Answered from `docs/roadmap.md` |
| "What did we decide about X?" | Answered from `docs/decisions/` |
| "Go through the inbox", "projdi inbox" | Proposals for each new idea (`pks-audit`) |
| "Run an audit", "udělej audit" | Report on what is outdated or ready to plan (`pks-audit`) |
| "Update my tracker from the roadmap" | The agent uses whatever tracker access it has |

**Skills:** `pks-setup` (initial fill), `pks-capture`, `pks-brainstorm`, `pks-audit`, `pks-help`.

**Terminal commands:** `pks init` installs PKS into a project. `pks update` updates it and never touches `docs/`. Both only change files; committing is up to you.

**Where things are:** `PROJECT.md`, `product.md`, `business.md`, `architecture.md`, `roadmap.md` and, once needed, `development.md`, plus `discovery/`, `decisions/` and `features/`. In `discovery/` and `decisions/`, what is current sits directly in the folder; subfolders hold what is waiting or finished.
