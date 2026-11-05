# Product Knowledge System (PKS)

Keep a project's know-how in the project: ideas, brainstorms, decisions, the plan and why things are the way they are. Claude Code and Codex read and maintain the same plain Markdown in `docs/`, you can browse it yourself, and it travels with Git.

PKS is not a ticketing system and depends on none. If you use one, it keeps tracking tasks and progress; if you don't, the roadmap in `docs/` is enough.

## Install

You need Git and Python 3.9 or newer.

```bash
curl -fsSL https://raw.githubusercontent.com/sudrap/product-knowledge-system/main/install.sh | sh
```

This downloads the latest release to `~/.local/share/pks` and links the `pks` command into `~/.local/bin`. You can [read the script](install.sh) first. To use other folders, set `PKS_HOME` and `PKS_BIN_DIR`.

To uninstall, run `pks uninstall`. It removes the command and the download. Projects keep their own files and keep working.

## Add it to a project

In the project's folder:

```bash
pks init
```

It shows what it will create and asks first. It never overwrites anything and commits nothing. It adds:

- the `pks-*` skills in `.claude/skills/` and `.agents/skills/`,
- a short marked rule in `AGENTS.md`, imported from `CLAUDE.md`,
- starter files in `docs/`,
- `.pks/version` and a `.gitignore` entry for `.pks/brainstorms/`.

Then start a new agent session in the project and run the setup:

- Claude Code: `/pks-setup`
- Codex: `$pks-setup`

The agent leads you through it one question at a time, shows how many there are ("Question 2 of 5") and offers answers, or you can write your own.

- **New project:** at most five questions, only to capture what you want to say now. You can end at any time, and the rest stays `[unknown]`.
- **Project with history:** the agent explores the project first and asks at most ten questions about what matters most. The rest stays `[unknown]` and gets filled in as you work. Then it takes you through a short review, step by step: what will be written, which decisions it will record, and what happens to existing material. Nothing is written until you agree.

Once the knowledge is in place, the agent turns off Claude's automatic memory for this project, so everything stays in one place.

## Daily use

Just work. Ask for `/pks-help` or `$pks-help` any time.

- **"Write this down"** records something in `docs/` and shows you where.
- **On its own**, the agent checks `docs/` before related work. At the end of a topic it asks once whether to record anything important. It does not write without you.
- **"Let's brainstorm"** starts `pks-brainstorm`: one question at a time, with notes in `.pks/brainstorms/`, so you can continue in another conversation. At the end you decide what goes to `docs/`, and the notes are deleted.
- **"Run an audit"** and **"go through the inbox"** run `pks-audit`, only when you ask.

To read the documentation comfortably, run `pks view` in the project or ask the agent with `/pks-view` or `$pks-view`. It opens `docs/` in your browser, with all documents in a side panel and formatted text. It only reads, and it updates by itself when a document changes. Only this computer can reach it. Press Ctrl+C to stop it.

## What ends up in `docs/`

```text
docs/
├── PROJECT.md        # purpose, current state, unknowns, language, other locations
├── product.md        # vision, users, value, strategy
├── business.md       # monetization, pricing, competitors, metrics
├── architecture.md   # structure and tech stack
├── roadmap.md        # Now / Next / Later
├── development.md    # build, run, debug, solved problems (when needed)
├── discovery/        # ideas, brainstorms, research under consideration
│   ├── inbox/        # new and unprocessed
│   └── rejected/     # rejected, with the reason
├── decisions/        # valid decisions
│   ├── proposed/     # waiting for confirmation
│   └── superseded/   # replaced by a newer decision
└── features/         # feature specifications
```

Status is the folder, so a folder listing shows it. Folders appear when first needed.

## Update

In each project, when you want to:

```bash
pks update
```

`pks update` downloads the latest PKS release, so you don't need the install command again. Then it replaces the `pks-*` skills and PKS's marked blocks in `AGENTS.md` and `CLAUDE.md`, and records the new version. It never touches `docs/` and commits nothing. It stops if the skills have uncommitted changes.

Your own workflows are safe if their names don't start with `pks-`.

## Limits

- The rule and skills are instructions for agents, not technical locks. Agents can miss something or ask more than needed. Everything they write stays uncommitted until you decide, so you can review it in Git.
- Each project has its own copy of the skills and its own version.

## Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
