# Eval: app packages

## Request

Add a DCR panel to this Django project that lets me look up the Python packages installed in the environment. Do not publish a package.

The data comes from `importlib.metadata`, so the agent has nothing to ask about. Nothing in this eval needs a database, an external service, or a mutating action.

## Expected scaffold

Run from the project root (next to `manage.py`):

```bash
python manage.py dcr_startpanel app_packages
```

| Field | Value |
|---|---|
| Command argument | `app_packages` |
| App label (prefix added by the command) | `dcr_app_packages` |
| Settings key | `DCR_APP_PACKAGES_SETTINGS` |

No `bake.py`, no Cookiecutter.

## Expected layout

A new Django app `dcr_app_packages/` next to existing apps. Not inside another app, not a `dj-…-panel/` package directory.

Must **not** appear: `pyproject.toml` for the panel, `example_project/`, Docker, MkDocs, `docs/` as a package docs site, `pypi_url` / `docs_url` on the panel class.

## Expected wiring

- `"dcr_app_packages"` in `INSTALLED_APPS`, listed **before** `dj_control_room`
- `path("admin/dcr-app-packages/", include("dcr_app_packages.urls"))` in the project `urls.py`
- `AppConfig.ready()` registers the panel; the hub lists it under Internal Panels

## Expected implementation

The starter `index` view and template are replaced:

- A list page of installed distributions (name, version, summary) with a search box that matches name (ignoring case and `-`/`_`/`.` differences) and summary
- UI from the DCR design system (`dcr-page-header`, `dcr-data-table`, `dcr-form`/`dcr-input-group`, `dcr-btn`, `dcr-empty` for no results) — not custom CSS or admin `.button`
- A helper module (for example `packages.py`) that gathers and filters packages, separate from the view
- Duplicate distributions (same package on several `sys.path` entries) listed once
- View scope with a descriptive name (for example `package_list`), not the generated `index`
- `panel.py` has a real `description` and an appropriate `icon`
- Tests: the helper functions, the page for a staff user, and unauthenticated redirect to admin login
- `scopes.md` next to `panel.py`
- No POST actions of any kind
- No MCP `tools.py` unless the user asked for agent access
- No import of the skills repo

The reference is `example_project/dcr_app_packages/` in the playground. It is the minimal version of this panel, so it is the floor: it has no `scopes.md`, and it still uses the `index` scope and generated description.

If the user asked for a reusable package instead, the agent must **not** use this skill — that is `dcr-create-package-panel`.
