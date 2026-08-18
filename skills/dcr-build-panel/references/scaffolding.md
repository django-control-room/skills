# Scaffolding

The official generator is the source of truth:

https://github.com/django-control-room/cookiecutter-dj-control-room-plugin

Run it through `scripts/bake.py`, not an interactive Cookiecutter prompt.

## Do not recreate

Leave these as Cookiecutter wrote them unless the feature truly requires a change:

- `pyproject.toml` (entry-point class name is already fixed by `bake.py`)
- `admin.py`, `models.py`, `apps.py`
- `conf.py` structure (`PanelConfig(..., tools=tool_registry.tools)`)
- Docker, Makefile, GitHub Actions, MkDocs config, `example_project/` wiring
- `templates/admin/<package>/base.html` — extend it; do not replace `panel_base.html`

Add views, templates, helpers, and tests freely.

## Living examples

Do not vendor copies of panel code in this skill. When you need a pattern, open the current official source (local submodule in this playground, otherwise GitHub `main`):

| Pattern | Read |
|---|---|
| Cookiecutter stubs you are replacing | The project you just baked |
| List + search UI | [dj-urls-panel](https://github.com/django-control-room/dj-urls-panel) `views.py`, `templates/admin/dj_urls_panel/` |
| POST actions (flush/delete/edit) | [dj-cache-panel](https://github.com/django-control-room/dj-cache-panel) `views.py`, `key_detail.html` |
| MCP tools | [dj-urls-panel](https://github.com/django-control-room/dj-urls-panel) `tools.py`, [dj-signals-panel](https://github.com/django-control-room/dj-signals-panel) `tools.py` |
| Design system + styleguide | [dj-control-room-base](https://github.com/django-control-room/dj-control-room-base) `design-system.css`; baked example: `/admin/dj-control-room-base/` |
| Scopes docs | Any official panel `docs/scopes.md` (e.g. urls-panel) |

## Dependencies

The generated package depends on **`dj-control-room-base`** (already in Cookiecutter `pyproject.toml`). The hub (`dj-control-room`) is an optional runtime extra for the dashboard, already wired in `example_project`.

Never add this skills repository as a dependency, path, or import. Skills are development-time only.

## Class name

Cookiecutter builds `{ProjectName}Panel`. If `project_name` ends in "Panel", it would emit `FooPanelPanel`. `bake.py` renames that to `FooPanel` unless `--no-fix-class` is passed. Confirm `panel.py` before implementing.

## Private packages

The template always sets `docs_url` / `pypi_url` on `PanelPlugin`. Clear or rewrite them if they would be misleading.

Full panel contract: [Building Panels](https://django-control-room.github.io/dj-control-room-base/building-panels/).
