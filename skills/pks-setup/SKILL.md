---
name: pks-setup
description: Fill a project's Product Knowledge System after `pks init` by leading the user through a short interview and review, one question at a time, while exploring the project and migrating existing knowledge. Use when the user asks to set up or fill PKS, or after `pks update` reports a docs structure change.
---

# PKS setup

Bring `docs/` to its initial state, so the agent and the user can rely on it. Read [the layout](references/pks-layout.md) first. For a project with history, also read [the migration protocol](references/migration-protocol.md) before any write.

## Safety rules

- Start read-only. In a project with history, write nothing before the user has approved, apart from your interview notes.
- Never delete, move or overwrite existing material without item-level approval.
- Never change a location the user marks read-only. Design folders are read-only by default. Never call design-sync tools such as `DesignSync`; link to design systems instead.
- Do not read secrets or copy them into Git. If a file looks secret-bearing by its name, do not open it; list it and ask.
- Do not invent product facts. Anything unknown stays `[unknown]`.
- Do not treat an inference as a decision. Record a decision you inferred only after the user has agreed to it.
- Do not change application code, dependencies, branches, remotes or external systems.
- Do not commit without the user's yes.

## Lead the user

The user does not know how PKS works inside. Lead them through the setup step by step.

- Work in small blocks: a few lines of explanation, then one question. Never send a long summary.
- Use plain words. Say what the user gets, not what you do to files. Do not mention templates, starter files, inventories, hashes, dispositions or migration maps unless asked.
- At the start, say in two or three lines how this will go: how many questions at most, and when something gets written.

## Pick the path

1. `.pks/version` must exist. If it does not, tell the user to run `pks init` and stop.
2. Choose:
   - **New project** (no real code or documents yet): use the short path.
   - **Project with history:** use the full path.
   - **Re-run:** read `.pks/notes/setup.md` if it exists and continue from its first open question. Otherwise interview only about what is still `[unknown]` or missing. Do not redo approved work. After a docs structure change, compare `docs/` with the layout and propose the moves in the review.

## Interview

Both paths use this interview. Its first question is the documentation language, unless `docs/PROJECT.md` already states one. Recommend the language of the conversation or of the project's existing documents. Everything depends on this answer, so it offers neither "I don't know yet" nor "End here". Record it in `docs/PROJECT.md` when you write, and write everything in that language, including template headings.

- Make the list of questions before asking the first one, and save it in the notes.
- Ask one question at a time, in the user's language. Use a structured question tool if you have one. Otherwise ask in plain text as the last thing in your reply and wait.
- Start every question with its position: "Question 2 of 5". Take both numbers from the list in the notes. If an answer makes a later question unnecessary or raises a new one, update and renumber the list first, then say why the total changed.
- Offer concrete answers, with your recommendation first and a one-line reason, then "I don't know yet", and let the user write their own. Add "Does not apply" where that is a real answer. Do not make up answers just to have some, and do not list "I'll write my own" as an answer. Keep to four answers, because question tools allow no more, and do not add a free-text answer if the tool adds one itself.
- Put everything needed to answer into the question, because a question tool may hide what you wrote before it.
- "I don't know yet" leaves the item `[unknown]`. Move on without pressing. Record "Does not apply" as that, not as `[unknown]`.
- If the user wants to talk something through, stop asking and discuss it. Record the outcome, then continue.

In plain text, a question looks like this:

```text
Question 3 of 5: Who is it for?

A. Only you (recommended: the README talks only about personal use)
B. A specific group of people
C. I don't know yet

Or write your own answer.
```

### Notes

After every answer, before the next question, update `.pks/notes/setup.md`, including answers in the review. These are working notes as in `pks-capture`, and Git ignores this folder. The file is the source of truth, so the setup can continue if the conversation ends.

```markdown
# PKS setup

Path: new project. Language: Czech.

## Questions

1. [answered] Who is it for? "Hobby darts players." → `docs/product.md`
2. [unknown] How will it make money? → `docs/business.md`
3. [open] What comes first? → `docs/roadmap.md`
```

## Short path

The user may not know much yet, and that is fine. Capture what they want to say, nothing more. Do not brainstorm the project, and do not ask follow-up questions unless you cannot understand an answer.

Ask only these:

1. The documentation language, as described above.
2. What is this project, in a sentence or two?
3. Who is it for?
4. What do you want to have working first?
5. Is there anything else you want written down now, such as how it will make money, a technical choice or an idea?

From the second question on, always offer "End here" as one of the four answers, which leaves room for two concrete ones. It ends the interview, and everything not yet answered stays `[unknown]`.

Write what the user said, close to their wording: `docs/PROJECT.md`, `docs/product.md`, `docs/roadmap.md`, and anything else where the layout says it belongs. Leave the rest as `[unknown]`. Then continue with "Turn off tool memory".

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
- Claude's memory for this project, read as ordinary files from `~/.claude/projects/<project>/memory/`. `<project>` is the repository path with non-alphanumeric characters replaced by `-`; list `~/.claude/projects/` to find it.

### 2. Pick the questions

Compare what you found with what the documentation should cover:

| Goes to | Covers |
| --- | --- |
| `docs/PROJECT.md` | purpose, current state (in progress, next, watch out), other locations |
| `docs/product.md` | vision, target users, value, strategy |
| `docs/business.md` | monetization, pricing, competitors, metrics |
| `docs/architecture.md` | structure, tech stack, reasons for the main choices |
| `docs/roadmap.md` | Now, Next, Later, and why |
| `docs/decisions/` | which decisions are really made, and why |

Ask at most ten questions in total. Ask nothing the project answers clearly and nothing that can be read from the code. From the rest, pick what would mislead later work if guessed wrong: usually who the project is for, what it aims at, what comes next, whether it should earn money, conflicts between sources, and important decisions that are unclear.

- **You only infer it:** ask for confirmation, with your inference as the recommended answer.
- **Sources conflict:** name them and ask which one holds.
- **Nothing says it:** ask directly.

What you do not ask stays `[unknown]`, and gets filled in during later work.

### 3. Interview

After the language question:

1. Give your summary of the project in a few lines and ask whether it is right. A correction can change the list.
2. Ask whether a tracker, wiki or other source exists for this project. Read what the user names, limited to this project and with whatever access you have, before going on. It may answer other questions.
3. Ask the rest, starting with what other answers depend on.

Do not offer "End here". If the user asks to stop, stop and say what is left: those items stay `[unknown]`. Ask whether to go on to the review or to continue later.

### 4. Review

Prepare the complete plan from the migration protocol and keep it to yourself. Show it only if the user asks.

Say that the questions are finished and nothing has been written yet. Then lead the user through these steps, one at a time, under the same rules as the interview. Start each with its position: "Review 1 of 4". Skip a step with nothing to show, and lower the total. Use short lines rather than tables, which a question tool may not show well. When the user changes something, adjust it and go on. Do not show everything again.

1. **What will be written.** One line per file: the file and, in a few words, what it will hold. Leave out files that stay empty. Say that the user can read the details in the files afterwards.
2. **Decisions.** One line per decision, with its reason. List only what someone would miss in a month and cannot read from the code. What the user agrees to goes to `docs/decisions/`. A decision they are unsure about goes to `docs/decisions/proposed/`; tell them it simply waits until they decide. Leave nothing else for later.
3. **Existing material.** Name anything that would change. Then list what needs the user's word, each with your proposal:
   - a document that overlaps a PKS one, for example an existing `docs/ARCHITECTURE.md`. Prefer keeping it and linking to it from `docs/PROJECT.md`;
   - every Claude memory file, with its destination: `docs/`, global instruction files, or leave it;
   - rules in `CLAUDE.md` that repeat `AGENTS.md`. Propose keeping shared rules only in `AGENTS.md` and leaving in `CLAUDE.md` only what is for Claude alone, plus the PKS block;
   - rules in instruction files that point to material being migrated, or that PKS now covers, such as "read this first" or "update the docs in the same change". Propose removing them or pointing them to `docs/`;
   - locations to treat as read-only;
   - secret-looking files.
4. **Go-ahead.** Say in a few lines what happens on yes: the files get written, existing files stay as agreed, Claude's automatic memory is turned off for this project because everything now lives in `docs/`, and nothing is committed.

End steps 1 to 3 with "Is this OK?" and the answers "Yes", "Something is wrong" and "Add something". End step 4 with "Shall I write it?" and the answers "Yes" and "Not yet".

```text
Review 1 of 4: what will be written

The questions are finished and nothing has been written yet. You can read the details in the files afterwards.

- `docs/product.md`: who it is for, the goal
- `docs/roadmap.md`: what comes next
- `docs/development.md`: running and deployment

Is this OK?

A. Yes
B. Something is wrong
C. Add something
```

### 5. Write what was approved

- `docs/PROJECT.md`: purpose, the current state in the form from `pks-capture` (updated, in progress, next, watch out), unknowns, language, and the "Other locations" table with read-only marks. Mark a document outside `docs/` that describes the project, such as a user guide, as not read-only, so it is kept true.
- `docs/product.md` and `docs/business.md`: what the project and the interview established.
- `docs/architecture.md`: an overview and the tech stack, not implementation details that can be read from the code.
- `docs/development.md`: only if there is something to say about building, running, debugging or solved problems, or a pointer to a design system.
- `docs/roadmap.md`: the direction and the reasons, not a task list.
- `docs/decisions/` and `docs/decisions/proposed/`: as agreed in the review. Use the record format in the layout reference.

### 6. Verify

```text
python3 <this-skill>/scripts/verify_pks_migration.py --project . \
  --before <temp>/inventory-before.json --mapping <temp>/migration-map.json --strict
```

Fix every error before continuing. Save the plan, map and report in `.pks/migrations/<migration-id>/`. Record only paths, hashes, classifications and decisions there, never secret contents.

## Turn off tool memory

Do this last, after anything worth keeping has been migrated. Merge `"autoMemoryEnabled": false` into `.claude/settings.json`, keeping all other settings. Tell the user that Claude's memory files stay on disk but no longer load in this project. If your tool refuses to edit the file, give the user the exact setting and say that memory is still on.

## Finish

Delete `.pks/notes/setup.md`. In a short block, say what was written, what stays `[unknown]`, and, after a migration, whether verification passed. Mention in one line that `[unknown]` items get filled in during later work or by running `pks-setup` again, and that `pks-help` shows the rest. Then ask whether to commit only the PKS changes: "Yes" or "No".
