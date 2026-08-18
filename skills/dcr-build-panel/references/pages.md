# Pages

Edit the generated `views.py`, `urls.py`, and `templates/admin/<package>/` **in place**. The Cookiecutter stubs are the starting point. For list/detail markup, read a living official panel (see [scaffolding.md](scaffolding.md)) and [design-system.md](design-system.md) — do not invent `PanelConfig` usage or `dcr-*` class names from memory.

## Rules

- Keep `app_name = "<package_name>"`. Name the main view `index`.
- Decorate every view with `@panel_config.permission_required("<scope>")`.
- Build template context only via `panel_config.get_context(request, **extra)`.
- Extend `admin/<package>/base.html`. Load `{% load i18n static dcr_icons %}`. Put markup in `{% block panel_content %}`.
- Populate `PanelPlugin.features`. Keep `get_config()` as a local import of `panel_config`.

Do not leave the generated `"index"` scope once there is more than a welcome page.

If a page **mutates** something, also read [actions.md](actions.md). If it should be callable by an agent, also read [mcp-tools.md](mcp-tools.md).
