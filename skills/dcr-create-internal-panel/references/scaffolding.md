# Scaffolding

The generator is the `dcr_startpanel` management command from `dj-control-room-base` (source: `dj_control_room_base/management/commands/dcr_startpanel.py`, overlay templates in `dj_control_room_base/startpanel_overlay/`). Run it; do not hand-write an app tree and do not use the Cookiecutter template for internal panels.

```bash
python manage.py dcr_startpanel app_packages   # creates ./dcr_app_packages/
```

The name is prefixed with `dcr_` unless it already starts with it. `--prefix` overrides that; leave it alone unless the user asks.

## Always a new app

Create a sibling Django app. Never nest the panel inside another installed app.

```
myproject/
  manage.py
  billing/                 # existing domain app — import from it, do not write panel files here
  dcr_webhook_failures/    # new DCR app (dcr_startpanel)
    apps.py                # ready() calls registry.register(...)
    panel.py
    conf.py
    views.py
    urls.py
    admin.py
    models.py
    templates/admin/dcr_webhook_failures/index.html
    tests.py               # stock startapp stub
```

Add `tools.py`, `scopes.md`, helpers, extra views and templates as needed.

## Do not recreate

Leave these as generated unless the feature truly requires a change:

- `admin.py`, `models.py`, `apps.py` (`ready()` is already there)
- `conf.py` structure (`PanelConfig(settings_key=..., defaults=...)`)
- The `panel_base.html` extension in templates — do not replace it

Replace the starter `index` view/template, `PanelPlugin.icon`, and `description`. Add views, templates, helpers, and project tests freely.

## Wiring

Unpackaged apps have no setuptools entry point. The generated `AppConfig.ready()` registers the panel. That reaches the hub sidebar if the app is listed **before** `dj_control_room` in `INSTALLED_APPS`. The hub shows it under **Internal Panels**.

```python
# INSTALLED_APPS
"dj_control_room_base",
"dcr_webhook_failures",   # before the hub
"dj_control_room",

# urls.py
path("admin/dcr-webhook-failures/", include("dcr_webhook_failures.urls")),

# settings.py — PanelConfig settings_key is <APP_LABEL>_SETTINGS (optional)
DCR_WEBHOOK_FAILURES_SETTINGS = {}
```

`dcr_startpanel` prints the exact `INSTALLED_APPS` and `path(...)` lines to use. It does not edit either file.

Do not invent hub keys the hub does not read (`LOCAL_PANELS`, `PANELS`).

## Adding MCP tools

The generated `conf.py` has no tools wiring. To add agent tools, create `tools.py` with a `ToolRegistry()` (see [mcp-tools.md](../../dcr-reference/mcp-tools.md)) and pass it to the config:

```python
from .tools import registry as tool_registry

panel_config = PanelConfig(
    settings_key="DCR_WEBHOOK_FAILURES_SETTINGS",
    defaults={...},
    tools=tool_registry.tools,
)
```

If the panel has no agent API, do not create `tools.py`.

## Settings (leave room to collapse later)

Keep the generated `PanelConfig(settings_key="<APP>_SETTINGS")`. That is the same contract packaged panels use.

- Always `panel_config.get_settings()` / `get_context()` / `permission_required()`.
- Never `getattr(django.conf.settings, "DCR_WEBHOOK_FAILURES_SETTINGS")`.
- Do not add a second settings helper, a nested dict of your own, or a `panel_id=` argument `PanelConfig` does not accept yet.

A later hub-level `DJ_CONTROL_ROOM_SETTINGS["PANELS"]` merge can land inside `PanelConfig.get_settings()` without changing this app's `conf.py` call sites. `settings_key` stays the legacy/compat layer.

Living official panels and the design-system catalog: [living-examples.md](../../dcr-reference/living-examples.md). Write scopes into this app's `scopes.md`. Do not vendor copies in this skill.

## Dependencies

The host project must already depend on **`dj-control-room-base`** and **`dj-control-room`**. Add the new app to `INSTALLED_APPS`; do not add this skills repository as a dependency, path, or import.

## Class name

The command builds `{CamelCaseAppName}Panel` from the prefixed app name (`dcr_app_packages` → `DcrAppPackagesPanel`). Confirm `panel.py` before implementing.
