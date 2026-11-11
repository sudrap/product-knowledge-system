---
name: pks-audit
description: Review a project's knowledge in docs/ and report what is outdated, contradictory or ready to plan, or process the idea inbox. Use only when the user asks for it, for example "udělej audit", "projdi inbox", "audit the docs", "go through the inbox".
---

# PKS audit

Run only when the user asks. Do not offer or schedule it. Report first and change files only after the user approves. Use subagents freely if your tool has them, to save time and context.

Never change locations marked read-only in `docs/PROJECT.md`, and create no tasks anywhere. The user decides what to plan and where.

## Whole-project audit

Go through `docs/` and compare it with the code and Git history where that helps. Report, with file paths:

- **Outdated:** statements the project no longer matches, including documents outside `docs/` that `docs/PROJECT.md` lists as not read-only, and a stale current state or roadmap.
- **Contradictions:** between product, roadmap and decisions.
- **Waiting:** records in `docs/decisions/proposed/` and unprocessed `docs/discovery/inbox/`.
- **Ready to plan:** ideas and decisions concrete enough to become a story, each with a one-line reason.
- **Upkeep:** broken links, duplicates, leftover notes in `.pks/notes/`, rules repeated in `CLAUDE.md` and `AGENTS.md`, knowledge about the code kept in `AGENTS.md` instead of `docs/`, files long enough to be worth splitting.
- **Unknowns:** `[unknown]` items that now have an answer in the project.

End with a short list of proposed changes and ask which to apply.

## Inbox

When the user asks to go through the inbox, look only at `docs/discovery/inbox/`. For each idea propose one of:

- **Keep:** move to `docs/discovery/`.
- **Reject:** move to `docs/discovery/rejected/` and add the reason.
- **Merge:** combine with a named record.
- **Plan:** it is ready to go into `docs/roadmap.md` or `docs/features/`.

Show the proposals in one list, ask once, and apply what the user approves. Fix links when moving records. Write in the language stated in `docs/PROJECT.md`.

Do not commit on your own. Offer one commit containing only knowledge files.
