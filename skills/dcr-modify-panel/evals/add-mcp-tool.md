# Eval: add an MCP tool

## Request

Let AI agents search the installed packages through the app packages panel. They should be able to pass a search string and get back matching package names, versions, and summaries.

## Expected approach

- `inspect_panel.py` reports `tools.py: no`. The agent reads `mcp-tools.md` and follows its internal-panel instructions
- The tool reuses the existing `filter_packages` / `get_installed_packages` helpers instead of duplicating the search

## Expected implementation

- A new `tools.py` with one `ToolRegistry()` and one handler registered with `name`, `scope`, `description`, and `input_schema`
- The scope is `agent_`-prefixed and different from the view scope, for example `agent_package_list`
- `input_schema` is a JSON Schema object with `"additionalProperties": False`
- The handler returns `PanelToolResult(success=..., message=..., data=...)`. A missing or non-string query returns `success=False` with a clear message and does not raise
- `conf.py` gains `from .tools import registry as tool_registry` and `tools=tool_registry.tools` in `PanelConfig(...)`. The rest of `conf.py` is unchanged, including `settings_key`
- `scopes.md` lists the new tool and its scope, noting that agent access is granted separately from the staff UI
- Tests call the handler with a `PanelToolContext`: matching query, no match, bad input. They do not use an MCP transport
- No tool that changes state, and no `hello_world` stub

## Expected `inspect_panel.py --base HEAD`

```
added  tool_names: <the new tool>
added  tool_scopes: agent_package_list
```

No `BREAKING` lines. Exit code 0.

## Must not

- Reuse the `index` scope for the tool
- Read `django.conf.settings` directly
- Add a dependency
