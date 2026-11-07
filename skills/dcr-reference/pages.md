# Pages

Edit the panel's `views.py`, `urls.py`, and `templates/admin/<app>/` **in place**. The Cookiecutter stubs are the starting point. For list pages read [lists.md](lists.md), and add [search.md](search.md) if the list is searchable. For other markup, read a living official panel (see [living-examples.md](living-examples.md)) and [design-system.md](design-system.md). Do not invent `PanelConfig` usage or `dcr-*` class names from memory.

## Rules

- Keep `app_name` matching the Django app label. Name the main view `index`.
- Decorate every view with `@panel_config.permission_required("<scope>")`.
- Build template context only via `panel_config.get_context(request, **extra)`.
- Extend `admin/<app>/base.html`. Load `{% load i18n static dcr_icons %}`. Put markup in `{% block panel_content %}`.
- Populate `PanelPlugin.features`. Keep `get_config()` as a local import of `panel_config`.

Do not leave the generated `"index"` scope once there is more than a welcome page.

If a page **mutates** something, also read [actions.md](actions.md). If it should be callable by an agent, also read [mcp-tools.md](mcp-tools.md).
