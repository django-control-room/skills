---
name: dcr-create-internal-panel
description: >-
  Scaffolds a Django Control Room (DCR) panel as a new Django app inside an
  existing project (not a publishable package) using the dcr_startpanel
  management command, then implements the requested admin UI, scopes, tests,
  and MCP tools. Use when the user wants an in-project, internal, or unpackaged
  control-room panel — not a PyPI/cookiecutter package repo. Never nest the
  panel inside another Django app.
---

# dcr-create-internal-panel

Build an **internal panel**: a new Django app, inside the current project, that is a Django Control Room panel.

Shared DCR contract docs live in the sibling [`common/`](../common/) directory. Do not copy that folder into the Django app.

This skill is **development-time guidance**. It is not part of the resulting application. The app must depend on DCR packages (`dj-control-room-base` and `dj-control-room`) the normal way. It must **not** depend on this skills repository.

The scaffolding engine is the `dcr_startpanel` management command shipped by `dj-control-room-base`. It runs Django's `startapp`, then overlays the panel files (`apps.py`, `admin.py`, `models.py`, `views.py`, `panel.py`, `conf.py`, `urls.py`, `templates/admin/<app>/index.html`). Do not recreate `PanelConfig`, admin placeholders, or `dcr-*` markup by hand, and do not use the Cookiecutter template for this skill.

```
User request → confirm internal mode → dcr_startpanel → wire the project → implement → validate
```

This skill does **not** create a publishable panel package. If that is what the user wants, stop and use `dcr-create-package-panel`. When distribution is unclear, ask:

> Should this be a reusable panel package, or a new Django app in this project?

Always create a **brand-new Django app**. Do not nest panel files inside an existing domain app (for example `billing/dcr/`). If the user said "add this to my app," create a sibling app and import domain models from the existing one.

## When to read what

Do not load every reference for every task. Read only what the current step needs:

| If the panel… | Read |
|---|---|
| Is being scaffolded or wired | [references/scaffolding.md](references/scaffolding.md) |
| Has list/detail (or other) pages | [pages.md](../common/pages.md) |
| Renders any UI | [design-system.md](../common/design-system.md) |
| Shows a table or list of records | [lists.md](../common/lists.md) |
| Lets the user search or filter a list | [search.md](../common/search.md) |
| Performs an operation (retry, flush, delete, run) | [actions.md](../common/actions.md) |
| Exposes agent-accessible functionality | [mcp-tools.md](../common/mcp-tools.md) |
| Needs permission design | [scopes.md](../common/scopes.md) |
| Needs tests | [references/tests.md](references/tests.md) |

Authoritative DCR contract (do not copy it into this skill): [Building Panels](https://django-control-room.github.io/dj-control-room-base/building-panels/).

## Workflow

```
Task progress:
- [ ] 1. Confirm internal-app mode (not a package)
- [ ] 2. Pick the app name + check DCR is installed
- [ ] 3. Run manage.py dcr_startpanel <name>
- [ ] 4. Wire INSTALLED_APPS (before dj_control_room) and urls.py
- [ ] 5. Inspect the app; implement inside it
- [ ] 6. Run scripts/validate.py, then the project's tests and manage.py check
```

### 1–2. Mode and name

Internal Django app only. Pick a short snake_case name **without** the prefix (`webhook_failures`, `app_packages`). The command adds `dcr_` itself (`dcr_webhook_failures`), so the app label you work with from here on is the prefixed one.

The project must already have `dj-control-room` and `dj-control-room-base` installed and `dj_control_room_base` in `INSTALLED_APPS`. If they are missing, stop and say so; do not invent a standalone admin view.

Run the command from the project root (next to `manage.py`), so the app lands as a sibling of the existing apps. Do not pass a `directory` that is inside another app.

### 3. Scaffold

```bash
python manage.py dcr_startpanel app_packages
```

It does not edit `INSTALLED_APPS` or `urls.py`. It prints the snippets to add. Use those.

### 4. Wire

Apply the printed snippets. List the new app **before** `dj_control_room` in `INSTALLED_APPS` so `AppConfig.ready()` registration is visible to the hub sidebar. Include the app's URLs the same way other panels are mounted. See [references/scaffolding.md](references/scaffolding.md).

### 5. Implement

Work inside the generated app. Load references from the table above. Replace the starter `index` view and template. Set a descriptive `icon` and populate `PanelPlugin.features` in `panel.py`. Write a `scopes.md` next to `panel.py`. Any template work also reads [design-system.md](../common/design-system.md) — use `dcr-*` components, do not invent CSS.

The generated app has no MCP `tools.py`. Add one only if the panel should be agent-accessible (see [mcp-tools.md](../common/mcp-tools.md)).

Always read config through `panel_config.get_settings()`. Do not `getattr(django.conf.settings, "DCR_APP_PACKAGES_SETTINGS")`.

### 6. Validate

```bash
python scripts/validate.py "$PROJECT_ROOT/$APP_NAME"
python manage.py check
# then the project's existing test runner, e.g. pytest
```

Fix `validate.py` errors before declaring done. Warnings should be addressed unless there is a stated reason not to.

## Evals

Example requests used to check this skill: [evals/](evals/).
