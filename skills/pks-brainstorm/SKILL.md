---
name: pks-brainstorm
description: Lead a product, business or architecture brainstorm one question at a time, with notes that survive the conversation. Use when the user says "pojďme brainstormovat" or "let's brainstorm", wants to continue an earlier brainstorm, or accepts an offer to turn a discussion into one.
---

# PKS brainstorm

Get what is in the user's head into clear ideas and decisions, one question at a time, and lose nothing if the conversation ends.

Start only when the user asks or accepts your offer. Do not start on your own.

## Start

1. List `.pks/notes/`. If notes on this topic exist, read them, say where things stand, and continue from there in the same file.
2. Otherwise create `.pks/notes/YYYY-MM-DD-topic.md`. These are the working notes from `pks-capture`, in the format below. Git ignores this folder and it is outside `docs/`.
3. Read what `docs/` already says about the topic. Tell the user in a few lines what applies or conflicts.

## Ask

- Ask one question at a time. Use a structured question tool if you have one. Otherwise ask in plain text as the last thing in your reply and wait.
- Offer two to four concrete answers where that makes sense, with your recommendation first and a one-line reason. Ask an open question when there are no real options.
- Settle what other answers depend on first.
- If `docs/` or the code can answer something, look it up instead of asking.
- If the user cannot answer, mark it as open and move on.
- If the user wants to talk something through, stop asking and discuss it. Record the outcome, then continue.
- Do not lecture. No long lists of your own ideas: turn an idea into an answer option or a one-sentence proposal.
- Say so when something contradicts an earlier answer or a decision in `docs/`, or when you disagree.

Ask in the user's language. Use the user's wording where it matters.

## Notes

After every answer, before the next question, update the notes. The file is the source of truth, not the conversation.

```markdown
# Topic

Started YYYY-MM-DD. Goal: one sentence.

## Where we are

A short running summary and the next question.

## Points

- [user] What the user said or decided.
- [agent, accepted] A suggestion of yours that the user agreed to.
- [agent, open] A suggestion of yours the user has not agreed to.

## Open

- A question nobody could answer yet, and who could.
```

A suggestion counts as accepted only when the user agreed to it.

## End

The brainstorm ends when the user says so. When the branches seem covered, ask whether anything is left.

1. Reread the notes and resolve contradictions with the user.
2. List what came out and ask once, as in `pks-capture`: yes / no / add something. Offer only `[user]` and `[agent, accepted]` points. Mark `[agent, open]` points clearly if you mention them.
3. Write what the user approved, using the record format in `pks-capture`, including its file header:
   - ideas and conclusions to `docs/discovery/`, with what is still open;
   - firm decisions to `docs/decisions/`, tentative ones to `docs/decisions/proposed/`;
   - a feature that became concrete to `docs/features/`.
4. Delete the notes, whatever the answer.

If the conversation stops earlier, the notes simply stay. Never move them to `docs/` on your own.
