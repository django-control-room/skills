---
name: dcr-modify-panel
description: >-
  Changes or extends an existing Django Control Room (DCR) panel or the staff
  admin tool built on it: add a page, column, search or filter, button or
  action, setting, permission scope, or MCP agent tool, or fix a bug. Works on
  reusable panel packages and internal dcr_startpanel apps, and keeps existing
  scopes, URL names, MCP tool names, and settings keys working. Use when the
  user wants to change, extend, fix, or add to a panel or dj-control-room tool
  that already exists; not to create a new one.
---

# dcr-modify-panel

Change a panel that already exists, without breaking the people already using it.

Shared DCR contract docs live in the sibling [`dcr-reference/`](../dcr-reference/) skill. If that folder is missing, tell the user to install the `dcr-reference` skill next to this one. Do not copy that folder into the panel.

This skill is **development-time guidance**. It is not part of the resulting application. Do not import from, or add a dependency on, this skills repository.

```
User request → locate + inspect → baseline → classify the change → implement in place → verify surface + tests
```

This skill does **not** scaffold. Never re-run `dcr_startpanel` or the Cookiecutter over an existing panel, and do not replace files with a regenerated copy. If there is no panel yet, use `dcr-create-package-panel` or `dcr-create-internal-panel`.

## When to read what

Read only what the change needs:

| If the change… | Read |
|---|---|
| Is anything beyond a one-line fix | [references/change-types.md](references/change-types.md) |
| Renames, removes, or re-scopes something | [references/compatibility.md](references/compatibility.md) |
| Adds or changes a page | [pages.md](../dcr-reference/pages.md) |
| Touches any markup | [design-system.md](../dcr-reference/design-system.md) |
| Adds or changes a table | [lists.md](../dcr-reference/lists.md) |
| Adds search or filters | [search.md](../dcr-reference/search.md) |
| Adds an operation (retry, flush, delete, run) | [actions.md](../dcr-reference/actions.md) |
| Adds agent-accessible functionality | [mcp-tools.md](../dcr-reference/mcp-tools.md) |
| Adds or changes who may do something | [scopes.md](../dcr-reference/scopes.md) |

Real examples to copy patterns from: [living-examples.md](../dcr-reference/living-examples.md). Authoritative contract: [Building Panels](https://django-control-room.github.io/dj-control-room-base/building-panels/).

## Workflow

```
Task progress:
- [ ] 1. Locate the panel and run inspect_panel.py
- [ ] 2. Baseline: read the panel, run its tests
- [ ] 3. Classify the change; flag anything breaking
- [ ] 4. Implement in place, following the panel's own conventions
- [ ] 5. Verify: tests, inspect_panel.py --base, check
- [ ] 6. Report what changed and what it affects
```

### 1. Locate and inspect

```bash
python scripts/inspect_panel.py PATH
```

`PATH` is the panel's Django app directory (the one with `panel.py` and `conf.py`), or a package root with exactly one such directory. The output tells you:

- **mode**: `package` (has the `dj_control_room.panels` entry point) or `internal` (registers from `AppConfig.ready()`). Stay in that mode. In a package, update `docs/`, `pyproject.toml` dependencies, and `tests/`. In an internal app, do not add `pyproject.toml`, Docker, MkDocs, or `docs/`.
- **PanelConfig / panel_base.html**: if either says `NO`, the panel is a legacy one with its own conf and base template. Match what is there. Do not migrate it to `dj-control-room-base` as a side effect; mention it in the report instead.
- **public surface**: the view scopes, MCP tool names and scopes, URL names, URL namespace, settings key and default keys, and entry point that other people depend on. See [references/compatibility.md](references/compatibility.md).

If the user did not say which panel, ask. Several panels in one repo is common.

### 2. Baseline

Read before editing: `panel.py`, `conf.py`, `urls.py`, `views.py`, `tools.py` if present, the templates, and one existing test file. Then run the panel's tests so you know what was green before you touched it. Fix nothing unrelated; note it.

Decide which ref the work will be compared against: `HEAD` for uncommitted work, or the branch point (for example `main`) if commits already exist.

### 3. Classify

Find the change in [references/change-types.md](references/change-types.md) and follow its list of files to touch. A change can be several types (an action usually adds a scope, a view, a template, a test, and a doc line).

Before editing, check [references/compatibility.md](references/compatibility.md). If the request would rename or remove something on the public surface, stop and ask unless the user already said they want that break.

### 4. Implement

- **Smallest diff that does the job.** Edit in place. Do not restructure, rename, reformat, or "modernize" files you do not need to change.
- **Follow the panel's conventions** over the generic ones: its helper module, its template partials, its test base class, its naming style. Open a neighbouring view or test and match it.
- **New view → new scope.** Name it for what it protects (`widget_detail`). Do not reuse an unrelated scope and do not use `"index"`.
- **New MCP tool → `agent_` scope**, distinct from the view scope.
- **New setting → add its default in `conf.py`**, read it with `panel_config.get_settings()`. Never `getattr(django.conf.settings, ...)`.
- **UI uses `dcr-*`.** No admin `.button`, no copied `design-system.css`, no hex colours.
- **Add a test for each new behaviour** next to the panel's existing tests. Package: subclass `PanelTestCase`. Internal: the host project's suite.
- **Update the docs the panel already has**: the scopes doc (`docs/scopes.md` in a package, `scopes.md` next to `panel.py` in an internal app), `PanelPlugin.features` for user-visible capability, and for a package `docs/features.md` / `docs/configuration.md` / README when the change is user-facing. Do not create docs the panel does not have.
- **Do not bump the version** or edit a changelog unless the user asked or the panel keeps an unreleased section there.
- **New runtime dependency?** Ask first. Package: `pyproject.toml`. Internal: the host project's requirements.

### 5. Verify

```bash
python scripts/inspect_panel.py PATH --base HEAD   # exit 1 means something was removed
```

Then:

- The panel's tests, and for the project containing it `python manage.py check`.
- If `dcr-create-package-panel` or `dcr-create-internal-panel` is installed alongside, run its `scripts/validate.py` too. Errors there are real. Warnings about generated stubs only matter if the panel still has stubs.

Every `BREAKING removed …` line from `inspect_panel.py` must be either undone or explicitly approved by the user. Every `added …` line must appear in the scopes doc (scopes, tools) or the configuration docs (settings), and have a test.

### 6. Report

Say what changed in plain terms, then list:

- **Added**: new scopes, MCP tools, URL names, settings keys.
- **Changed behaviour** for existing users, if any.
- **Breaking**: anything removed or renamed, and how users migrate. "None" is a valid answer once `inspect_panel.py --base` agrees.
- **Not done**: legacy-panel migration, unrelated failures you noticed, docs the panel lacks.

## Evals

Example requests used to check this skill: [evals/](evals/).
