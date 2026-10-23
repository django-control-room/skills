# Shared DCR skill references

Used by `dcr-guide`, `dcr-create-package-panel`, `dcr-create-internal-panel`, and `dcr-modify-panel`. Keep this directory a **sibling** of those skill folders so links like `../common/design-system.md` resolve.

Scaffolding, tests, bake (package only), and validate stay in each skill — those differ by package vs internal app. Do not copy these files into a generated panel.

## Vocabulary

Users say "tool" for two different things. Keep them apart in everything written here:

- **panel**: the staff-facing pages in Django admin. A user may call it a tool, page, screen, or dashboard.
- **MCP tool**: a function a panel exposes to AI agents (`tools.py`, `agent_*` scopes). It lives inside a panel and is not a panel.
