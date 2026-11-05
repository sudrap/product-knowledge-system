# Contributing

To report a bug or suggest an idea, open an issue. To propose a change, fork the repository and open a pull request.

## Develop

Clone the repository and run `./install.sh` in it. This links your checkout, so `pks` uses your edits right away.

Run the tests before you open a pull request:

```bash
python3 -m unittest discover -s tests
```

## Release

Releases are made by the maintainer. The install command and `pks update` give people the latest tag, so work on `main` reaches nobody until it is released.

1. Set the new number in `VERSION`: the last part for fixes and wording, the middle part for a new skill or behaviour, the first part for a change to the `docs/` structure.
2. Describe it in `CHANGELOG.md`. Mark a change to the `docs/` structure with `[docs-structure]`, so `pks update` tells people to run `pks-setup`.
3. Commit, tag and push:

```bash
git tag vX.Y.Z
git push origin main --tags
```

4. Publish the release page, with the new section of `CHANGELOG.md` as its text. Updates read the tag, so this page is for people:

```bash
gh release create vX.Y.Z --verify-tag --title "PKS X.Y.Z" --latest --notes "..."
```
