# Product Knowledge System (PKS)

Keep a project's know-how in the project: ideas, brainstorms, decisions, the plan and why things are the way they are. Claude Code and Codex read and maintain the same plain Markdown in `docs/`, you can browse it yourself, and it travels with Git.

PKS is not a ticketing system and depends on none. If you use one, it keeps tracking tasks and progress; if you don't, the roadmap in `docs/` is enough.

## Install

You need Git and Python 3.9 or newer.

```bash
curl -fsSL https://raw.githubusercontent.com/sudrap/product-knowledge-system/main/install.sh | sh
```

This downloads the latest release to `~/.local/share/pks` and links the `pks` command into `~/.local/bin`. You can [read the script](install.sh) first. To use other folders, set `PKS_HOME` and `PKS_BIN_DIR`.

To uninstall, delete `~/.local/bin/pks` and `~/.local/share/pks`. Projects keep their own files.

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

The agent explores the project, shows you a plan for moving existing knowledge, and asks only what it cannot find out itself. In a new project it just asks a few questions. Once you have approved the plan and the knowledge is in place, it turns off Claude's automatic memory for this project, so everything stays in one place.

## Daily use

Just work. Ask for `/pks-help` or `$pks-help` any time.

- **"Write this down"** records something in `docs/` and shows you where.
- **On its own**, the agent checks `docs/` before related work. At the end of a topic it asks once whether to record anything important. It does not write without you.
- **"Let's brainstorm"** starts `pks-brainstorm`: one question at a time, with notes in `.pks/brainstorms/`, so you can continue in another conversation. At the end you decide what goes to `docs/`, and the notes are deleted.
- **"Run an audit"** and **"go through the inbox"** run `pks-audit`, only when you ask.

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

Run the install command again to get the new version. Then update each project when you want to:

```bash
pks update
```

`pks update` replaces the `pks-*` skills and PKS's marked blocks in `AGENTS.md` and `CLAUDE.md`, and records the new version. It never touches `docs/` and commits nothing. It stops if the skills have uncommitted changes.

Your own workflows are safe if their names don't start with `pks-`.

## Limits

- The rule and skills are instructions for agents, not technical locks. Agents can miss something or ask more than needed. Everything they write stays uncommitted until you decide, so you can review it in Git.
- Each project has its own copy of the skills and its own version.

## Develop

Clone the repository and run `./install.sh` in it. This links your checkout, so `pks` uses your edits right away.

```bash
python3 -m unittest discover -s tests
```

### Release

The install command gives people the latest tag, so work on `main` reaches nobody until it is released.

1. Set the new number in `VERSION`: the last part for fixes and wording, the middle part for a new skill or behaviour, the first part for a change to the `docs/` structure.
2. Describe it in `CHANGELOG.md`. Mark a change to the `docs/` structure with `[docs-structure]`, so `pks update` tells people to run `pks-setup`.
3. Commit, tag and push:

```bash
git tag v1.2.0
git push origin main --tags
```

## License

[MIT](LICENSE)
