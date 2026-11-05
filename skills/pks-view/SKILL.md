---
name: pks-view
description: Open the project's `docs/` in a read-only viewer in the browser, with all documents in a side panel and formatted text. Use when the user asks to see, open or browse the documentation, or says "ukaž mi dokumentaci" or "otevři docs".
---

# PKS view

Run this in the background from the project's root, because it keeps running until stopped:

```text
pks view
```

It opens the browser and prints a link. Give the user the link in case the browser did not open, and say that the page updates by itself when a document changes. If your tool cannot open a browser, add `--no-open`.

The viewer only reads. Do not change any files for this. If the user asks to stop it, stop the background process.

If `pks` is not found, tell the user that the viewer needs the `pks` command, and point them to the install command in the PKS README: https://github.com/sudrap/product-knowledge-system
