# Changelog

Mark a version that changes the `docs/` structure with `[docs-structure]`. `pks update` then tells people to run `pks-setup`.

## 1.5.0

Add the `pks view` command and the `pks-view` skill: read `docs/` in your browser, with all documents in a side panel and formatted text. It only reads, only this computer can reach it, and the page updates by itself when a document changes.

## 1.4.0

`pks update` now downloads the latest PKS release by itself, then updates the project, so the install command is only needed the first time. Without a connection it says so and uses what it has. A development checkout stays as it is. If you have an older version, run the install command one last time.

Ctrl+D at a question now ends with "Nothing changed" instead of an error listing.

## 1.3.0

`pks-setup` now leads you through the setup step by step. It asks one question at a time, shows how many there are ("Question 2 of 5"), and offers answers, or you can write your own. An interrupted setup can continue in another conversation.

A new project gets at most five questions, and you can end at any time. A project with history gets at most ten, about what matters most, followed by a short review: what will be written, which decisions get recorded, and what happens to existing material. Nothing is written until you agree. Decisions are settled in the review, so nothing waits for confirmation unless you are unsure about it.

## 1.2.0

Add `pks uninstall`, which removes the command and the download. Projects stay as they are.

## 1.1.0

Add the `pks-brainstorm` skill: the agent leads a brainstorm one question at a time, keeps notes that can be resumed in another conversation, and tells your points from its own suggestions. It starts when you ask, or after you accept its one offer.

Add a format for feature records. The install command now installs the latest release instead of the newest commit.

## 1.0.0

First release as a package: the `pks init` and `pks update` commands and the `pks-setup`, `pks-capture`, `pks-audit` and `pks-help` skills, for Claude Code and Codex.
