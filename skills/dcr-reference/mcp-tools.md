# MCP tools

**Package panels:** replace the Cookiecutter `hello_world` stub in the panel's `tools.py`. Keep that file's imports and `ToolRegistry()` — they are the current API. `conf.py` already wires `tools=tool_registry.tools`.

**Internal panels** (`dcr_startpanel`): the generated app has no `tools.py`. Create one with a `ToolRegistry()` and add `tools=tool_registry.tools` to the `PanelConfig(...)` in `conf.py`. Only do this if the panel should be agent-accessible.

For real tool shapes, read [dj-urls-panel](https://github.com/django-control-room/dj-urls-panel) `tools.py`.

## Rules

- One `ToolRegistry()` in `tools.py`. Decorate handlers with `@registry.register(name=..., scope=..., description=..., input_schema=...)`.
- Scope every tool with an `agent_` prefix, **different** from the human view scope even when the data is the same.
- Local-import Django models (and anything else that needs a ready app registry) **inside** handlers.
- Return `PanelToolResult(success=..., message=..., data=...)`. On bad input, `success=False` and a clear message; do not raise.
- `input_schema` is a JSON Schema object. Set `"additionalProperties": False`.
- If the panel has no agent API, delete `hello_world` and any generated test for it, leave an empty registry (package) or do not create `tools.py` (internal), and say so in the panel's scopes doc (`docs/scopes.md` in a package, `scopes.md` next to `panel.py` in an internal app).

API reference: [Panel tools](https://django-control-room.github.io/dj-control-room-base/building-panels/#panel-tools). Also read [scopes.md](scopes.md) and this skill's `references/tests.md`.
