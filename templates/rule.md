<!-- PKS:START -->
## Product knowledge (PKS)

Know-how lives in `docs/`. At the start of every conversation, read `docs/PROJECT.md` unless it is already loaded, and list `.pks/notes/`. If notes are there, say so in one line. Ask whether to continue from them, move them to `docs/`, or delete them only when they concern the task or the user asks. Beyond that, read only what the task needs, never all of it:

- `docs/PROJECT.md`: purpose, current state, unknowns, other locations
- `docs/product.md`: vision, users, strategy
- `docs/business.md`: pricing, competitors, metrics
- `docs/architecture.md`: structure, tech stack and code conventions
- `docs/roadmap.md`: what is planned and why
- `docs/development.md`: build, run, test, debug, solved problems
- `docs/decisions/`: valid decisions; `proposed/` await confirmation, `superseded/` were replaced
- `docs/discovery/`: ideas under consideration; `inbox/` unprocessed, `rejected/` rejected
- `docs/features/`: feature specifications

Some of these appear only once they hold content. List a folder and open records by name. On questions and before any work, check the related records: the feature the work touches and decisions on that area. Before writing or changing code, read `docs/architecture.md` and `docs/development.md`; read `docs/development.md` also before building, running or debugging. Say when something applies or conflicts.

While you work, keep notes on your own in `.pks/notes/YYYY-MM-DD-topic.md`: decisions and why, open questions, where you stopped, the next step. A new topic gets a new file, so parallel conversations do not mix. Start the file at the first change, decision or finding, even in a short task, so nothing is lost if the conversation ends. Git ignores the folder. After changing behaviour, structure or how the project is built and run, check the records that describe it.

When told to write or remember something, write it to `docs/`, never to tool memory, and show where. Otherwise do not write to `docs/` on your own. At the end of a block of work, offer one list of every write the work needs, one line per item saying what and where: the current state in `docs/PROJECT.md` when it changed, records the work made untrue, and new knowledge that matters. Ask once: yes / no / show the exact wording / change something, and offer the commit in the same question. The `pks-capture` skill has the details.

When asked to brainstorm, follow the `pks-brainstorm` skill. Do not start one on your own: if a longer product, business or architecture discussion has no conclusion, offer it once.

The project's rules for every agent live in `AGENTS.md`. `CLAUDE.md` imports it and holds only what is for Claude alone. Never copy a rule between them. What an agent needs to know about the code, such as conventions, layers, naming and how to test, lives in `docs/architecture.md` and `docs/development.md`, not in `AGENTS.md`. Change either file only when the user asks, show the exact change first, and never edit inside this PKS block.

Write records in the language stated in `docs/PROJECT.md`. Never change locations listed as read-only there.
<!-- PKS:END -->
