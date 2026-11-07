---
name: dcr-guide
description: >-
  Entry point for building staff-facing admin tools in Django with Django
  Control Room (DCR): an internal tool, admin page, dashboard, lookup page, or
  ops/support screen, or a change to one that already exists. Use when the user
  wants to create, add, extend, or change a tool, page, or panel for staff or
  admins in a Django project that uses dj-control-room, or mentions DCR,
  control room, or dj-control-room. Decides between installing DCR, a new
  in-project panel, a reusable panel package, and changing an existing panel,
  then hands off to dcr-setup, dcr-create-internal-panel,
  dcr-create-package-panel, or dcr-modify-panel.
---

# dcr-guide

Route a request to the right DCR skill. This skill builds nothing itself.

Shared DCR contract docs live in the sibling [`dcr-reference/`](../dcr-reference/) skill. If that folder is missing, tell the user to install the `dcr-reference` skill next to this one.

This skill is **development-time guidance**. It is not part of the resulting application, and nothing built from it may depend on this skills repository.

```
Request → read the project → is this a DCR job? → new or existing? → hand off
```

## Words people use

Users rarely say "panel". Map what they say to what DCR calls it:

| They say | In DCR |
|---|---|
| "a tool / page / screen / dashboard / lookup for staff, admins, support, ops" | A **panel**: a staff-facing page set in Django admin |
| "let agents / Claude / the AI do X" | An **MCP tool**: a function a panel exposes to agents. It lives inside a panel and does not replace it |
| "a button to retry / flush / delete / run X" | An **action** on a panel page |
| "who can see / do X" | **Scopes** and `SCOPE_PERMISSIONS` |

"Tool" alone is ambiguous. If the request could be a one-off script, a management command, a cron job, or a ModelAdmin action, and nothing says staff need a page for it, **do not force DCR**. Say what you would build instead, or ask.

## 1. Read the project

Run these checks before asking the user anything:

- **Is DCR installed and wired?** Look for `dj-control-room` and `dj-control-room-base` in `pyproject.toml`, `requirements*.txt`, or a lockfile, and `dj_control_room` and `dj_control_room_base` in `INSTALLED_APPS`. Installed but misconfigured counts as not installed.
- **Are there panels already?** Look for directories containing both `panel.py` and `conf.py`, for `PanelPlugin` subclasses, or for the `dj_control_room.panels` entry point in a `pyproject.toml`.
- **Where do first-party apps live?** Next to `manage.py`, under `apps/`, or elsewhere. The internal skill needs this.

## 2. Decide

| What you found and what they want | Go to |
|---|---|
| A panel exists and they want it changed, extended, or fixed | [dcr-modify-panel](../dcr-modify-panel/SKILL.md) |
| DCR is installed and they want a new tool for this project | [dcr-create-internal-panel](../dcr-create-internal-panel/SKILL.md) |
| They want something shared across projects, published, or installable with `pip` | [dcr-create-package-panel](../dcr-create-package-panel/SKILL.md) |
| DCR is **not** installed, or the setup is broken | [dcr-setup](../dcr-setup/SKILL.md). If they also asked for a panel, install first, then continue |
| They only want agents to be able to do X, and a panel for X exists | [dcr-modify-panel](../dcr-modify-panel/SKILL.md), adding an MCP tool |
| It is not a staff UI at all | Not a DCR job. Say so and carry on without DCR |

If it is still unclear whether the new tool is for one project or for many, ask exactly this and nothing more:

> Should this be a reusable panel package, or a new Django app in this project?

When the user did not name a panel but several exist, ask which one.

### DCR is not installed

Do not scaffold a panel and do not invent a standalone admin view. A tool built this way needs `dj-control-room` and `dj-control-room-base`, with `dj_control_room_base` in `INSTALLED_APPS`. Tell the user, and ask whether to set DCR up first. If yes, hand off to [dcr-setup](../dcr-setup/SKILL.md), then come back and continue with the create skill the user originally needed.

If they want a plain Django admin page and have no interest in DCR, do that. This skill is not a reason to add a dependency.

## 3. Hand off

Open the chosen skill's `SKILL.md` and follow it from its first step. Carry across what you already learned (project root, where apps live, which panel) so the user is not asked twice. Do not re-run the routing questions inside the next skill.

## Evals

Whether the right skill loads for plain-language requests is tested in `evals/triggers.md` at the top level of the skills repository. It is not copied into projects.
