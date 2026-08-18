# MCP tools

Replace the Cookiecutter `hello_world` stub in the generated `tools.py`. Keep that file's imports and `ToolRegistry()` — they are the current API. `conf.py` already wires `tools=tool_registry.tools`. For real tool shapes, read [dj-urls-panel](https://github.com/django-control-room/dj-urls-panel) `tools.py`.

## Rules

- One `ToolRegistry()` in `tools.py`. Decorate handlers with `@registry.register(name=..., scope=..., description=..., input_schema=...)`.
- Scope every tool with an `agent_` prefix, **different** from the human view scope even when the data is the same.
- Local-import Django models (and anything else that needs a ready app registry) **inside** handlers.
- Return `PanelToolResult(success=..., message=..., data=...)`. On bad input, `success=False` and a clear message; do not raise.
- `input_schema` is a JSON Schema object. Set `"additionalProperties": False`.
- If the panel has no agent API, delete `hello_world` and its test, leave an empty registry, and say so in `docs/scopes.md`.

API reference: [Panel tools](https://django-control-room.github.io/dj-control-room-base/building-panels/#panel-tools). Also read [scopes.md](scopes.md) and [tests.md](tests.md).
