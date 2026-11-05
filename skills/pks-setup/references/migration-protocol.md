# Lossless migration protocol

## Scope and discovery

Treat project knowledge broadly: root instructions, documentation, notes, planning artifacts, local skills, templates, issue exports, design records, research, scripts that encode operating knowledge, and relevant Git state. Inventory all working-tree paths—not just tracked files—without following symlinks. The inventory tool deliberately excludes `.git` object internals and summarizes repository status instead.

Claude's memory for the project and any tracker or wiki the user names are sources too, but they sit outside the inventory. List them separately in the plan, each with a destination.

Generate the migration map with a script rather than by hand. Most paths in a project with code are `retained`, including the files `pks init` created.

Do not copy credentials, access tokens, private keys, or `.env` content into canonical Markdown or migration reports. Flag potentially secret-bearing material and ask whether it should remain local, be documented only by name, or be moved through an approved secret-management path.

Read-only locations, such as a design folder, are always `retained` and never edited. Verification then proves they did not change.

## Required migration plan

Before writes, prepare a complete plan with:

1. repository root, Git state and applicable instructions;
2. inventory totals and unreadable/ignored/nested-repository findings;
3. a source-to-destination map covering every inventory item;
4. exact duplicates and near duplicates, with hashes or comparison basis;
5. conflicting facts, ownership uncertainty and questions for the user;
6. every file to create, preserve, modify, move, archive or leave untracked;
7. Git-ignore and staging implications;
8. validation commands and the conditions for a successful migration;
9. the exact approval requested, including any source mutation and commit.

This plan is your working record, not something the user reads. The review in the skill shows them in plain words what they need to decide. Show the complete plan only if asked, and save it with the migration afterwards.

The review must name everything that changes, moves or removes the user's existing material. Filling a file that `pks init` created and that still holds only its starter text needs no such mention.

The user approves at the go-ahead step of the review, after all required questions have answers. That approval covers only what the review showed. It does not cover an unlisted source mutation, a Git commit, a branch change, or an external action.

Every canonical document, local skill, template, project instruction, and retained source item that contains project knowledge needs an explicit Git disposition. The normal disposition is **track and include in the approved PKS commit**, even when the original remains at its former path. An ignored or untracked knowledge item is an issue to resolve, not evidence that it can be dropped. Credentials, private keys, tokens, local secret files, and purely generated/cache material are exceptions: do not stage them; record only their classification and the user-approved handling.

## Migration map schema

Store a JSON map with one item per path listed in the before-inventory. The verification tool accepts this shape:

```json
{
  "schemaVersion": "pks-migration-map/v1",
  "approvalRef": "migration plan approved YYYY-MM-DD",
  "items": [
    {
      "source": "notes/old-roadmap.md",
      "disposition": "referenced",
      "destinations": ["docs/roadmap.md"],
      "approvalRef": "migration plan approved YYYY-MM-DD",
      "notes": "Original retained; canonical document links to it."
    }
  ]
}
```

Allowed dispositions are:

- `retained`: original stays unchanged; it is intentionally not duplicated.
- `copied`: original stays unchanged and each destination is an exact byte-for-byte copy.
- `referenced`: original stays unchanged; destination is a document that points to it.
- `merged`: original stays unchanged; destination consolidates it with other approved sources.
- `changed-with-approval`: use only for a specifically approved source overwrite or move. `approvalRef` is mandatory.

Do not use `merged` to conceal a conflict; name the competing sources and user decision in `notes`. Do not use `changed-with-approval` for bulk cleanup.

## Applying and verifying

Create only missing scaffolding unless an approved plan names a modification. Preserve existing names and location where they retain useful history. If a target already exists, stop and ask rather than choosing a suffix or replacement.

After writes, retain the before inventory and run:

```text
python3 <this-skill>/scripts/verify_pks_migration.py \
  --project <project-root> \
  --before <temp>/inventory-before.json \
  --mapping <temp>/migration-map.json \
  --strict
```

It checks that every original path is mapped, that unchanged sources retain their kind and hash, that required destinations exist, and that `copied` destinations match the original bytes. It cannot prove semantic completeness of a `referenced` or `merged` document; inspect those mappings and the final diff with the user.

Then check that canonical artifacts are not ignored, inspect `git status` and `git diff --check`, and report all staged/untracked files. Commit only approved PKS changes, not unrelated working-tree changes.
