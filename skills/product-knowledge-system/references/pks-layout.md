# PKS layout and ownership

Use this as the portable default. Extend it only when the project has a justified need; do not replace established project conventions without approval.

```text
project/
├── AGENTS.md                         # Thin Codex-facing navigator and safety rules
├── CLAUDE.md                         # Thin Claude Code-facing navigator and safety rules
├── .agents/skills/<workflow>/SKILL.md # Thin wrapper to docs/ai-workflows/
├── .claude/rules/knowledge-management.md
├── .claude/skills/<workflow>/SKILL.md # Thin wrapper to docs/ai-workflows/
└── docs/
    ├── INDEX.md
    ├── PROJECT.md
    ├── changelog.md
    ├── ai-workflows/
    │   ├── discovery-capture.md
    │   ├── discovery-review.md
    │   ├── decision-record.md
    │   ├── product-review.md
    │   ├── knowledge-search.md
    │   └── knowledge-audit.md
    ├── product/{INDEX.md,vision.md,strategy.md,target-users.md,value-proposition.md,roadmap.md}
    ├── discovery/{INDEX.md,inbox/,ideas/,hypotheses/,research/,rejected/}
    ├── decisions/{INDEX.md,product/,business/,technical/}
    ├── features/INDEX.md
    ├── business/{INDEX.md,monetization.md,pricing.md,competitors.md,metrics.md}
    └── planning/{INDEX.md,current-focus.md,backlog.md,milestones.md}
```

## Ownership boundaries

| Location | Owns |
| --- | --- |
| `docs/INDEX.md` | navigation, status and path to each knowledge category; no long-form content |
| `docs/PROJECT.md` | project purpose, current state, scope boundaries and known unknowns |
| `docs/product/` | durable product direction and product roadmap |
| `docs/discovery/` | unapproved inputs, evaluated ideas, hypotheses, research and rejected discovery material |
| `docs/decisions/` | explicit product, business and technical decisions with rationale and consequences |
| `docs/features/` | feature specifications, requirements and open questions |
| `docs/business/` | market, competition, pricing, monetization and product metrics |
| `docs/planning/` | current focus, prioritized backlog and milestones—not approval history |
| `docs/ai-workflows/` | tool-neutral workflow instructions shared by all AI tools |
| tool wrappers | where to find the canonical knowledge and workflows; no duplicated product facts |

## Index contract

An index is navigation, not a second copy of a document. It lists purpose, location, status and, where useful, a concise active-items table. Read a category index before its individual records. Update it when adding, retiring or relocating a canonical record.

## IDs and statuses

Use stable IDs when creating new records; do not renumber existing projects during migration.

| Record | Prefix | Example |
| --- | --- | --- |
| discovery item | `D` | `D-001` |
| hypothesis | `H` | `H-001` |
| research | `R` | `R-001` |
| decision record | `ADR` | `ADR-001` |
| feature | `F` | `F-001` |

Discovery statuses are `inbox`, `proposed`, `exploring`, `accepted`, `rejected`, `implemented`, and `archived`. `accepted` means approved for realization, not implemented. A decision record should state its own status (for example `proposed`, `accepted`, `superseded`, or `rejected`) and never silently rewrite prior rationale.

## Record metadata

New individual records should prefer portable YAML frontmatter:

```markdown
---
id: D-001
type: idea
title: Short title
status: proposed
created: YYYY-MM-DD
updated: YYYY-MM-DD
related: []
tags: []
---
```

Retain an existing project's metadata format during migration unless the user approves a conversion. Keep source files and create references/mapping records rather than rewriting them just to add frontmatter.

## Shared workflows and wrappers

The default shared workflows are `capture-discovery`, `review-discovery`, `record-decision`, `product-review`, `knowledge-search`, and `knowledge-audit`. Their canonical definitions live in `docs/ai-workflows/`. Both `.agents/skills/` and `.claude/skills/` wrappers should be materially identical, name the shared workflow they load, require explicit approval before writes, and contain no canonical knowledge.
