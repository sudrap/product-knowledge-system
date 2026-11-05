# PKS layout and ownership

Use this as the default. Extend it only when the project has a justified need, and do not replace established project conventions without approval.

```text
project/
├── AGENTS.md                 # marked PKS block with the rule
├── CLAUDE.md                 # marked @AGENTS.md import
├── .pks/
│   ├── version               # installed PKS version, tracked in Git
│   ├── migrations/           # plans, maps and reports from migrations, tracked
│   └── brainstorms/          # working notes, ignored by Git
├── .claude/skills/pks-*/     # skills for Claude Code
├── .agents/skills/pks-*/     # skills for Codex
└── docs/
    ├── PROJECT.md
    ├── product.md
    ├── business.md
    ├── architecture.md
    ├── roadmap.md
    ├── development.md        # created when first needed
    ├── discovery/
    │   ├── inbox/
    │   └── rejected/
    ├── decisions/
    │   ├── proposed/
    │   └── superseded/
    └── features/
```

Folders appear when they first hold something. There are no index files: the rule holds the map of `docs/`, and descriptive file names make a folder listing the index.

## What belongs where

| Location | Holds |
| --- | --- |
| `docs/PROJECT.md` | purpose, current state, unknowns, documentation language, other locations and which are read-only |
| `docs/product.md` | vision, target users, value, strategy |
| `docs/business.md` | monetization, pricing, competitors, metrics |
| `docs/architecture.md` | structure and tech stack, not details that can be read from the code |
| `docs/roadmap.md` | what is planned and why, as Now / Next / Later |
| `docs/development.md` | how to build, run and debug, solved problems, pointers to design systems |
| `docs/discovery/` | ideas under consideration, brainstorm results, hypotheses, research |
| `docs/decisions/` | valid product, business and technical decisions |
| `docs/features/` | what a feature should do, when worth recording |

A long file can be split later, for example `docs/product.md` into `docs/product/`. Record the split in `docs/PROJECT.md` under other locations, because the rule's map stays the same.

**Tracker:** tasks, assignees and task status belong in a tracker if the project uses one. All know-how and decisions stay in `docs/`, whichever phase they come from. PKS depends on no specific tracker.

**Other material:** existing folders such as a design folder stay where they are. `docs/` links to them.

## Status is the folder

What is current sits directly in the folder; subfolders hold what is waiting or finished.

| Folder | Meaning |
| --- | --- |
| `docs/discovery/inbox/` | new, unprocessed |
| `docs/discovery/` | being considered |
| `docs/discovery/rejected/` | rejected, with the reason |
| `docs/decisions/proposed/` | awaiting the user's confirmation |
| `docs/decisions/` | valid |
| `docs/decisions/superseded/` | replaced, with a link to the newer decision |

An accepted idea moves into `docs/roadmap.md` or `docs/features/` and its file is deleted. Git keeps the history.

## Record format

Write in the language stated in `docs/PROJECT.md`. Use descriptive file names in that language. Decisions are `NNNN-slug.md`, numbered across `docs/decisions/` and its subfolders. Everything else is `slug.md`.

```markdown
---
type: idea
created: YYYY-MM-DD
updated: YYYY-MM-DD
related: []
---

# Title

One sentence that says what this is.

Details.
```

`type` is `idea`, `brainstorm`, `research` or `hypothesis` in discovery, and `product`, `business` or `technical` in decisions. Decision records use these sections after the summary: context and problem, considered options, outcome.

Mark what nobody knows yet as `[unknown]`. Do not invent it. An idea, hypothesis, plan or AI inference is not an approved decision.
