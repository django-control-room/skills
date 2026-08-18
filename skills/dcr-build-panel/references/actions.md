# Actions

An **action** is a mutating operation (retry, flush, delete, execute, enable). Follow the POST + messages + redirect pattern in [dj-cache-panel](https://github.com/django-control-room/dj-cache-panel) `views.py` and `key_detail.html` — not a copy stored in this skill.

## Rules

- Actions are `POST` only. GET of an action URL redirects back to the list or detail page.
- Include `{% csrf_token %}`. Use `django.contrib.messages` and redirect after success or failure (PRG).
- Give the action its **own** view scope (`widget_retry`, not `widget_detail`). Destructive actions should be called out in `docs/scopes.md` with a tight `SCOPE_PERMISSIONS` example.
- Confirm in the UI (`onsubmit="return confirm(...)"` or equivalent) for irreversible work. Buttons are `dcr-btn dcr-btn--danger` (or `--primary`); wrap flush/delete blocks in `dcr-danger-zone`. See [design-system.md](design-system.md).
- Do not expose an action as an MCP tool unless the user asked for agent access. If they did, read [mcp-tools.md](mcp-tools.md) and give the tool a distinct `agent_*` scope.

Permissions model: [Control Room permissions and scopes](https://djangocontrolroom.com/guides/control-room-permissions-and-scopes).
