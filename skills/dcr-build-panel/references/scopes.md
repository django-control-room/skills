# Scopes

Human views and MCP tools use the **same** `SCOPE_PERMISSIONS` machinery. Give them **different names** so staff UI access and agent access can be granted independently.

Rewrite the generated `docs/scopes.md` (do not leave Cookiecutter's `index` / `agent_hello_world` table). Match the structure of an official panel's `docs/scopes.md`, e.g. [dj-urls-panel](https://github.com/django-control-room/dj-urls-panel/blob/main/docs/scopes.md).

## Rules

- Views: descriptive names (`widget_list`, `widget_detail`, `widget_retry`), not `"index"`.
- Tools: `agent_widget_list`, `agent_widget_detail`, `agent_widget_retry`.
- Settings key is `<PACKAGE_NAME>_SETTINGS` (Cookiecutter). Do not invent a new one.
- Document a `SCOPE_PERMISSIONS` example for any dangerous action.

Full model: [Control Room permissions and scopes](https://djangocontrolroom.com/guides/control-room-permissions-and-scopes).
