---
name: dcr-reference
description: >-
  Shared Django Control Room (DCR) reference docs that the other dcr-* skills
  link to: pages, lists, search, actions, scopes, MCP tools, design system, and
  living examples. Loaded through those skills, not on its own. Do not use it
  to answer a user request directly; use dcr-guide, dcr-setup,
  dcr-create-internal-panel, dcr-create-package-panel, or dcr-modify-panel.
---

# DCR reference

Reference docs for the `dcr-*` skills. Each of those skills has a table that says which file to read for the task at hand. Install this skill **next to** them: they link to it as `../dcr-reference/`.

Scaffolding, tests, bake (package only), and validate stay in each skill, because those differ between a package and an internal app. Do not copy these files into a generated panel.

## Files

| File | Read it when the panel |
|---|---|
| [pages.md](pages.md) | has list, detail, or other pages |
| [design-system.md](design-system.md) | renders any UI or markup (`dcr-*` classes, tokens, no custom CSS) |
| [lists.md](lists.md) | shows a table of records |
| [search.md](search.md) | lets the user search or filter a list |
| [actions.md](actions.md) | performs an operation (retry, flush, delete, run) |
| [mcp-tools.md](mcp-tools.md) | exposes functionality to AI agents |
| [scopes.md](scopes.md) | needs permission design |
| [living-examples.md](living-examples.md) | needs a real official panel to copy a pattern from |

## Vocabulary

Users say "tool" for two different things. Keep them apart in everything written here:

- **panel**: the staff-facing pages in Django admin. A user may call it a tool, page, screen, or dashboard.
- **MCP tool**: a function a panel exposes to AI agents (`tools.py`, `agent_*` scopes). It lives inside a panel and is not a panel.
