---
name: pks-capture
description: Record project knowledge in docs/. Use when the user asks to write down or remember something ("zapiš to", "zapamatuj si", "write this down"), during and after a brainstorm, at the end of a topic where something important came up, or when asked what is worth recording.
---

# PKS capture

Keep the project's know-how in `docs/`, without interrupting the user and without writing behind their back.

## The user tells you to write

Always do it, whatever the content and even after an earlier "ne". Words like "write", "remember", "zapiš" and "zapamatuj si" all mean `docs/`, never tool memory.

Pick the place from the table below, write, and show the path with a one-line summary. Ask only if the place is truly unclear. The user can correct the wording straight away; nothing is committed yet.

## The user did not ask

Do not interrupt and do not write. Keep candidates in mind and carry on with the work.

At the end of a topic or block of work, ask once and list all candidates together with what you would do with them:

```text
Before we close this, these look worth recording:
1. decision: no subscriptions -> docs/decisions/
2. tentative decision: Android later -> docs/decisions/proposed/
3. idea: tournament mode -> docs/discovery/inbox/

Record them? yes / no / add something
```

- Use a structured question tool if you have one. Otherwise ask in plain text as the last thing in your reply and wait.
- Ask in the user's language and offer the commit in the same question.
- Do not ask about something again in this conversation after a "no".
- If nothing qualifies, ask nothing.
- The user can also ask at any time what is worth recording.

**What qualifies:** would someone miss it in a month, and can it not be read from the code? That covers product, business and architectural decisions, conclusions, and ideas the user clearly stands behind. It does not cover passing thoughts or implementation details. This test limits only what you offer, never what the user tells you to write.

## Where things go

| What | Where |
| --- | --- |
| New idea | `docs/discovery/inbox/` |
| Brainstorm result, research, an idea under consideration | `docs/discovery/` |
| Firm decision ("we decided", "it will be this way") | `docs/decisions/` |
| Tentative decision ("probably", "I'm considering") | `docs/decisions/proposed/` |
| Purpose, current state, unknowns | `docs/PROJECT.md` |
| Vision, users, strategy | `docs/product.md` |
| Pricing, competitors, metrics | `docs/business.md` |
| Structure, tools and libraries in use | `docs/architecture.md` |
| How to build, run, debug; solved problems | `docs/development.md` (create it when first needed) |
| What is planned and why | `docs/roadmap.md` |
| What a feature should do | `docs/features/` |
| A rule for all the user's projects | `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`, only when the user says so |

Tasks, assignees and task status belong in the user's tracker. A decision or new knowledge from grooming or development still belongs in `docs/`, and a ticket links to it.

Never change locations marked read-only in `docs/PROJECT.md`. Never write secrets.

## Record format

Write in the language stated in `docs/PROJECT.md`. Use descriptive file names in that language. People browse these folders too.

- Decisions: `NNNN-slug.md`, numbered across `docs/decisions/` and its subfolders.
- Everything else: `slug.md`.

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

`type` is `idea`, `brainstorm`, `research` or `hypothesis` in discovery, and `product`, `business` or `technical` in decisions.

Decision records use these sections after the summary: context and problem, considered options, outcome.

## Status is the folder

Move a record when its status changes, and fix links to it in the same step.

- **Conflicting decision:** show the conflict and propose moving the old record to `docs/decisions/superseded/`, with links both ways. Do not rewrite the old reasoning.
- **Confirmed proposal:** move it from `proposed/` to `docs/decisions/`.
- **Rejected idea:** move it to `docs/discovery/rejected/` with the reason. Do not delete it; the reason stops it from being proposed again.
- **Accepted idea:** move its content into `docs/roadmap.md` or `docs/features/` and delete its file.

## Brainstorms

During a product, business or architecture brainstorm, keep notes without asking in `.pks/brainstorms/YYYY-MM-DD-topic.md`. Git ignores this folder and it is outside `docs/`, so it adds nothing to the documentation. Update the notes after each important point.

- **Resuming:** when the user wants to continue a brainstorm, read its notes and carry on. Claude Code and Codex share this path.
- **Ending:** list what came out in the question above. Afterwards delete the notes, whatever the answer.
- **Interrupted:** the notes simply stay. Never move them to `docs/` on your own.

## Git

Do not commit on your own. When something was written, offer one commit containing only knowledge files at the end of a block of work, not after every write. Do not mix it with code.
