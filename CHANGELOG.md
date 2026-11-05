# Changelog

Mark a version that changes the `docs/` structure with `[docs-structure]`. `pks update` then tells people to run `pks-setup`.

## 1.2.0

Add `pks uninstall`, which removes the command and the download. Projects stay as they are.

## 1.1.0

Add the `pks-brainstorm` skill: the agent leads a brainstorm one question at a time, keeps notes that can be resumed in another conversation, and tells your points from its own suggestions. It starts when you ask, or after you accept its one offer.

Add a format for feature records. The install command now installs the latest release instead of the newest commit.

## 1.0.0

First release as a package: the `pks init` and `pks update` commands and the `pks-setup`, `pks-capture`, `pks-audit` and `pks-help` skills, for Claude Code and Codex.
