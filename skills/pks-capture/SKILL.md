---
name: pks-capture
description: Record project knowledge in docs/ and keep it true. Use when the user asks to write down or remember something ("zapiš to", "zapamatuj si", "write this down"), at the end of a block of work, when the work changed the project's state or made a record untrue, or when asked what is worth recording.
---

# PKS capture

Keep the project's know-how in `docs/` true and complete, without interrupting the user and without writing to `docs/` behind their back.

## The user tells you to write

Always do it, whatever the content and even after an earlier "ne". Words like "write", "remember", "zapiš" and "zapamatuj si" all mean `docs/`, never tool memory.

Pick the place from the table below, write, and show the path with a one-line summary. Ask only if the place is truly unclear. The user can correct the wording straight away; nothing is committed yet.

## Working notes

Notes in `.pks/notes/` keep a conversation's knowledge until the user decides what goes to `docs/`, so nothing is lost when a conversation ends. Git ignores the folder.

- Write them on your own, without asking, and as you go: after a decision, a finding or a change of direction, not only at the end.
- One file per topic, `.pks/notes/YYYY-MM-DD-topic.md`, so parallel conversations do not overwrite each other. Continue an existing file on the same topic.
- Keep them short: decisions and why, open questions, where you stopped, the next step. No transcript and no secrets.
- Name the file once, at the first write.
- At the start of a conversation, if notes exist, say so in one line. Ask continue / move to `docs/` / delete only when they concern the task or the user asks, because another conversation may still be using them.
- Delete a file only after the user has decided about its content.

## Keep records true

When the work changes behaviour, structure or how the project is built and run, check what describes it:

- the feature in `docs/features/`;
- `docs/architecture.md` and `docs/development.md`;
- documents outside `docs/` that `docs/PROJECT.md` lists as not read-only, such as a user guide.

Every statement that no longer holds goes into the closing list, with the fix.

## Close a block of work

Do not interrupt while working. At the end of a topic or block of work, offer one list of every write the work needs, built from the notes, one line per item: what and where.

```text
Before we close this, I suggest these writes:
1. state: validator fixed, generator filter half-done, tests missing -> docs/PROJECT.md
2. outdated: limit 5 -> 10 -> docs/features/validator.md
3. decision: no subscriptions -> docs/decisions/
4. idea: tournament mode -> docs/discovery/inbox/

Write them? yes / no / show the exact wording / change something
```

What belongs in the list:

- **The current state**, whenever the work changed it: something finished, started or was left half-done, or a new trap or unverified point appeared.
- **Records the work made untrue**, from the check above.
- **New knowledge that matters:** would someone miss it in a month, and can it not be read from the code? That covers product, business and architectural decisions, conclusions, and ideas the user clearly stands behind. It does not cover passing thoughts or implementation details. This test applies only to new knowledge you offer, never to the state, to keeping records true, or to what the user tells you to write.
- **A code convention the work set**, such as a layer, a naming rule or how to test. Offer it for `docs/architecture.md` or `docs/development.md`, even though the code shows it: it is a rule for code not written yet.
- **A rule for agents** that seems to belong in `AGENTS.md`. Offer it here; never write it there without a yes.

How to ask:

- Use a structured question tool if you have one. Otherwise ask in plain text as the last thing in your reply and wait.
- Ask in the user's language and offer the commit in the same question.
- Show the exact wording only when the user asks for it. Write nothing before a yes. Then delete the notes the user has decided about.
- A "no" covers only the items in that list. A later change is a new item.
- If nothing qualifies, ask nothing.
- The user can also ask at any time what is worth recording.

## Where things go

| What | Where |
| --- | --- |
| New idea | `docs/discovery/inbox/` |
| Brainstorm result, research, an idea under consideration | `docs/discovery/` |
| Firm decision ("we decided", "it will be this way") | `docs/decisions/` |
| Tentative decision ("probably", "I'm considering") | `docs/decisions/proposed/` |
| Where the work stands | "Current state" in `docs/PROJECT.md` |
| Purpose, unknowns, other locations | `docs/PROJECT.md` |
| Vision, users, strategy | `docs/product.md` |
| Pricing, competitors, metrics | `docs/business.md` |
| Structure, tools and libraries in use, code conventions (layers, naming) | `docs/architecture.md` |
| How to build, run, test, debug; solved problems | `docs/development.md` (create it when first needed) |
| What is planned and why | `docs/roadmap.md` |
| What a feature should do | `docs/features/` |
| A rule for how agents work in this project, not knowledge about the code | `AGENTS.md`, only when the user says so |
| A rule for all the user's projects | `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`, only when the user says so |

Never change locations marked read-only in `docs/PROJECT.md`. Never write secrets.

## Current state

"Current state" in `docs/PROJECT.md` says where the work stands now, so an agent without context can continue. Rewrite it in place; it is not a log. Keep it to one screen. Finished work leaves it, and Git keeps the history.

```markdown
## Current state

**Updated:** YYYY-MM-DD

- **In progress:** what is being worked on and where it stopped.
- **Next:** the next concrete steps.
- **Watch out:** risks, known traps and what has not been verified yet.
```

If the section still has an older form, bring it to this one when you first update it.

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

`type` is `idea`, `brainstorm`, `research` or `hypothesis` in discovery, `product`, `business` or `technical` in decisions, and `feature` in features.

Decision records use these sections after the summary: context and problem, considered options, outcome.

Feature records use these sections after the summary: what it should do, rules, out of scope, open questions. Link the related decisions.

## Status is the folder

Move a record when its status changes, and fix links to it in the same step.

- **Conflicting decision:** show the conflict and propose moving the old record to `docs/decisions/superseded/`, with links both ways. Do not rewrite the old reasoning.
- **Confirmed proposal:** move it from `proposed/` to `docs/decisions/`.
- **Rejected idea:** move it to `docs/discovery/rejected/` with the reason. Do not delete it; the reason stops it from being proposed again.
- **Accepted idea:** move its content into `docs/roadmap.md` or `docs/features/` and delete its file.

## Brainstorms

When the user asks to brainstorm, follow `pks-brainstorm`.

If a longer product, business or architecture discussion is going nowhere conclusive and the user has not asked for a brainstorm, offer once in this conversation to turn it into one, then carry on according to the answer. Do not start one on your own.

## Git

Do not commit on your own. When something was written, offer the commit at the end of a block of work, not after every write.

- New knowledge gets its own commit, without code.
- A fix to a record that a code change made untrue goes into the same commit as that code change, so a revert takes the description back with it.
