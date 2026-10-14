# Eval: settings lookup

## Request

Build a reusable DCR panel package that lets me look up the Django settings of the project it is installed in.

Everything it needs is in-process (`django.conf.settings`), so the agent has no data source to ask about. Nothing in this eval needs a database, an external service, or a mutating action.

## Expected bake

| Field | Value |
|---|---|
| `project_name` | Settings Lookup Panel |
| `project_slug` | `dj-settings-lookup-panel` |
| `package_name` | `dj_settings_lookup_panel` |
| `project_description` | Look up Django settings |
| `panel_icon` | `cog` |

The agent should ask only for author, email, GitHub username, license, and output directory.

## Expected implementation

Cookiecutter stubs replaced in place, patterns taken from official panels / the design system:

- A list page of settings (name, value, type) with a search box (case-insensitive match on the setting name), built from `dcr-page-header`, `dcr-data-table`, and the search form patterns in [`common/search.md`](../../common/search.md)
- Only upper-case settings are listed
- Values for names that look sensitive (`SECRET`, `PASSWORD`, `TOKEN`, `KEY`, `DSN`, and similar) are redacted and never rendered. This is the interesting requirement: the agent should do it without being told which names
- A helper module that gathers and filters settings, separate from the view, with tests of its own
- View scope `setting_list` and a read-only MCP tool with scope `agent_setting_list`, which applies the same redaction as the page
- `docs/scopes.md` rewritten; no `index` / `agent_hello_world` rows left
- No POST actions of any kind
- Package depends on `dj-control-room-base`, not the skills repo
- No `hello_world`, no welcome page

If the user said "add this to my project" / "my app", the agent must **not** bake a package — that is `dcr-create-internal-panel`.
