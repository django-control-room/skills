---
name: dcr-create-package-panel
description: >-
  Creates a reusable, publishable Django Control Room (DCR) panel package
  (plugin) from the official Cookiecutter, then implements the admin UI,
  scopes, tests, and MCP agent tools. Use when the user wants a new
  dj-control-room panel or plugin that will be shared, installed into several
  Django projects, or published to PyPI or a private index. Not for a tool that
  only one project needs (use dcr-create-internal-panel) or for changing an
  existing panel (use dcr-modify-panel).
---

# dcr-create-package-panel

Build a **reusable, independently publishable** Django Control Room panel package.

Shared DCR contract docs live in the sibling [`common/`](../common/) directory. Do not copy that folder into the generated package.

This skill is **development-time guidance**. It is not part of the resulting application. The generated package must depend on DCR packages (`dj-control-room-base`, and `dj-control-room` if the hub is used) the normal way. It must **not** depend on this skills repository.

```
User request → infer metadata → bake Cookiecutter → inspect → implement → validate
```

The [official Cookiecutter](https://github.com/django-control-room/cookiecutter-dj-control-room-plugin) is the scaffolding engine. Do not recreate packaging, entry points, `PanelConfig`, admin placeholders, tests, docs, Docker, or `example_project`. Do not keep a second copy of those files in this skill — they will drift.

After baking, **edit the generated stubs in place**. For patterns Cookiecutter does not stub (list/detail, POST actions, extra MCP tools, `dcr-*` markup), read the **living** official panels and design system listed in [living-examples.md](../common/living-examples.md). Prefer those over inventing APIs from memory.

This skill does **not** add a panel as a new Django app inside an existing project. If that is what the user wants, stop and use `dcr-create-internal-panel`. When distribution is unclear, ask:

> Should this be a reusable panel package, or a new Django app in this project?

## When to read what

Do not load every reference for every task. Read only what the current step needs:

| If the panel… | Read |
|---|---|
| Is being scaffolded | [references/scaffolding.md](references/scaffolding.md) |
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
- [ ] 1. Confirm package mode
- [ ] 2. Infer metadata; ask only for identity, license, output dir
- [ ] 3. Bake with scripts/bake.py
- [ ] 4. Inspect the generated tree
- [ ] 5. Implement inside the generated package (read references + living examples)
- [ ] 6. Run scripts/validate.py, then pytest and manage.py check
```

### 1–2. Mode and metadata

Standalone package only. Infer `project_name` (include "Panel"), `project_slug` (`dj-<topic>-panel`), `package_name` (underscores), `project_description`, `django_app_verbose_name`, `panel_icon` (`database|layers|link|chart|radio|cog`). Always pass slug and package name explicitly. Ask for author, email, GitHub username, license, and output directory.

### 3. Bake

```bash
python scripts/bake.py \
  --output-dir "$OUTPUT_DIR" \
  --project-name "Settings Lookup Panel" \
  --project-slug "dj-settings-lookup-panel" \
  --package-name "dj_settings_lookup_panel" \
  --project-description "Look up Django settings" \
  --author-name "..." \
  --author-email "..." \
  --github-username "..." \
  --panel-icon cog
```

If this workspace contains `cookiecutter-dj-control-room-plugin/`, pass `--template` pointing at it. Do not run Cookiecutter interactively. See [references/scaffolding.md](references/scaffolding.md).

### 4. Inspect

Read the generated project before editing. Cookiecutter will evolve; do not assume a hardcoded file list. The stubs (`views.py`, `tools.py`, `index.html`, `tests/`) are the files you replace — everything else stays.

### 5. Implement

Work inside the generated package. Load references from the table above. Replace Cookiecutter stubs (`index` welcome page, `hello_world` tool). Populate `PanelPlugin.features`. Update `docs/scopes.md`. Any template work also reads [design-system.md](../common/design-system.md) — use `dcr-*` components, do not invent CSS.

### 6. Validate

```bash
python scripts/validate.py "$PROJECT_DIR"
python -m pip install -e ".[dev]"    # from $PROJECT_DIR
python -m pytest tests/ -v
cd example_project && python manage.py check
```

Fix `validate.py` errors before declaring done. Warnings should be addressed unless there is a stated reason not to.

## Evals

Example requests used to check this skill: [evals/](evals/).
