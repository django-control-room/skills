# Eval: webhook failures

## Request

Build a DCR tool that displays failed webhook deliveries and lets administrators retry them.

## Expected bake

| Field | Value |
|---|---|
| `project_name` | Webhook Failures Panel |
| `project_slug` | `dj-webhook-failures-panel` |
| `package_name` | `dj_webhook_failures_panel` |
| `project_description` | Inspect and retry failed webhook deliveries |
| `panel_icon` | `link` |

The agent should ask where delivery records live and how retry works if that cannot be inferred from the repo.

## Expected implementation

Cookiecutter stubs replaced in place, patterns taken from official panels / the design system:

- List + detail pages, POST retry action
- Scopes `delivery_list`, `delivery_detail`, `delivery_retry` and matching `agent_delivery_*` tools
- UI from the DCR design system (`dcr-page-header`, `dcr-data-table`, `dcr-btn`) — not custom CSS or admin `.button`
- `docs/scopes.md` rewritten
- No `hello_world` or skills-repo import

If the user said "add this to my app", the agent must **not** bake a package.
