# Eval: PostgreSQL operations

## Request

Build a reusable PostgreSQL operations panel.

## Expected bake

| Field | Value |
|---|---|
| `project_name` | PostgreSQL Operations Panel |
| `project_slug` | `dj-postgres-ops-panel` |
| `package_name` | `dj_postgres_ops_panel` |
| `panel_icon` | `database` |

The agent should ask which operations are in scope (introspection vs. kill-backend vs. vacuum) and **not** invent destructive actions the user did not request.

## Expected implementation

- Overview page using `dcr-*` components (see `references/design-system.md`)
- Any mutating operation follows the cache-panel POST + CSRF + messages + own-scope pattern
- Read-only MCP tools are fine; mutating tools get distinct `agent_*` scopes and a tight `SCOPE_PERMISSIONS` example in `docs/scopes.md`
- Package depends on `dj-control-room-base`, not the skills repo
