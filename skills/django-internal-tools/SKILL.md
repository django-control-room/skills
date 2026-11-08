---
name: django-internal-tools
description: >-
  Start here to build an internal tool inside Django Admin: a customer support
  console or lookup tool, a billing or operations page, a staff approval or
  review workflow, an operational dashboard, or another custom staff-only
  page, even when the user never mentions Django Control Room (DCR) or panels.
  DCR is the framework these tools are built with; it calls each tool a panel.
  Reads the project, then hands off to dcr-setup (DCR missing or broken),
  dcr-create-internal-panel (new tool for this project),
  dcr-create-package-panel (reusable package), dcr-modify-panel (change an
  existing tool), or dcr-access (who can use a tool, AI agent access). Builds nothing itself. Not for ordinary ModelAdmin changes
  (fields, list_display, filters, inlines, admin actions), public or
  customer-facing pages, APIs, scripts, or background jobs, or when the user
  asks for another framework or a plain Django admin view.
---

# django-internal-tools

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
| "a tool for support to look up customers", "a support console", "a billing ops page", "an ops dashboard", "an internal tool / page / screen for staff" | A **panel**: a staff-facing page set in Django admin |
| "an approval workflow", "a review queue", "let staff approve / reject X" | A **panel** with list pages and **actions** |
| "let agents / Claude / the AI do X" | An **MCP tool**: a function a panel exposes to agents. It lives inside a panel and does not replace it |
| "a button to retry / flush / delete / run X" | An **action** on a panel page |
| "only finance can X", "who can see / do X", "lock down X" | **Scopes**, set per project in `SCOPE_PERMISSIONS` |

### Not a DCR job

Say so and carry on without DCR when the request is:

- **An ordinary ModelAdmin change**: fields, `list_display`, filters, search, inlines, or an admin action on a registered model.
- **Public or customer-facing**: a page end users or customers see, not staff.
- **Not a page**: a script, management command, API endpoint, Celery task, cron job, or standalone MCP server.
- **Explicitly another approach**: the user named a different framework or tool (a plain Django admin view, Unfold pages, Wagtail, Retool, Streamlit). Respect it, even if DCR is installed.

"Tool" alone is ambiguous. If nothing says staff need a page for it, **do not force DCR**. Say what you would build instead, or ask.

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
| They want to limit who can use a tool, or one of its actions, and it has a scope for it | [dcr-access](../dcr-access/SKILL.md) |
| They want agents to do X, and the panel already has an MCP tool for X | [dcr-access](../dcr-access/SKILL.md), turning on the MCP endpoint |
| They want agents to do X, and the panel has no MCP tool for it | [dcr-modify-panel](../dcr-modify-panel/SKILL.md) to add one, then [dcr-access](../dcr-access/SKILL.md) |
| Anything under [Not a DCR job](#not-a-dcr-job) | Say so and carry on without DCR |

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
