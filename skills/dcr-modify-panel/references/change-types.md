# Change types

Find the row that matches the request, touch the listed files, and read the shared doc named. Paths are relative to the panel's Django app directory. Package-only paths are marked. Most requests are several rows at once.

| Change | Touch | Read |
|---|---|---|
| [New page](#new-page) | `views.py`, `urls.py`, `templates/admin/<app>/`, scopes doc, tests | [pages.md](../../dcr-reference/pages.md) |
| [New column or field](#new-column-or-field) | the data helper, the template, tests | [lists.md](../../dcr-reference/lists.md), [design-system.md](../../dcr-reference/design-system.md) |
| [Search or filter](#search-or-filter) | the data helper, `views.py`, the list template, tests | [search.md](../../dcr-reference/search.md) |
| [New action](#new-action) | `views.py`, `urls.py`, the template, scopes doc, tests | [actions.md](../../dcr-reference/actions.md) |
| [New MCP tool](#new-mcp-tool) | `tools.py`, `conf.py` (internal only), scopes doc, tests | [mcp-tools.md](../../dcr-reference/mcp-tools.md) |
| [New setting](#new-setting) | `conf.py`, the code that uses it, config docs, tests | [scopes.md](../../dcr-reference/scopes.md) for permission-style keys |
| [Change who may do what](#change-who-may-do-what) | `views.py` / `tools.py`, scopes doc, tests | [scopes.md](../../dcr-reference/scopes.md) |
| [Change the data source](#change-the-data-source) | the data helper, tests | |
| [Restyle or fix markup](#restyle-or-fix-markup) | templates, `static/**/styles.css` | [design-system.md](../../dcr-reference/design-system.md) |
| [Bug fix](#bug-fix) | the faulty file, a regression test | |

## New page

1. Add the view with `@panel_config.permission_required("<new_scope>")` and `panel_config.get_context(request, ...)`.
2. Add a `path(..., name="<name>")` in `urls.py`. Keep the existing `app_name`.
3. Add the template extending the panel's own `base.html` (or `panel_base.html` if that is what it extends).
4. Link to it from where users will find it. A detail page is linked from the list's first column.
5. Add the scope to the scopes doc.
6. Tests: renders for staff, anonymous is redirected, unknown id returns 404 (not a 500).

## New column or field

1. Add the value in the data helper, not in the template.
2. Match the column's type to the rules in `lists.md`: identifiers in `dcr-code`, numbers right-aligned, status as a badge.
3. Keep existing columns where they are unless asked. Do not reorder.
4. Test the helper returns the new value.

## Search or filter

1. If the list already has `q`, extend it. Do not add a second search box.
2. New filters are GET parameters, preserved by pagination and by CLEAR.
3. Put the matching logic in the data helper and test it directly: case, separators, empty query, no match.
4. A no-match result uses the "no results for this search" empty state, not the "nothing here" one.

## New action

1. POST only. GET redirects back.
2. Its **own** scope (`widget_retry`), not the detail page's scope.
3. `{% csrf_token %}`, a confirm for anything irreversible, `dcr-btn--danger` for destructive buttons, redirect after success or failure.
4. Add a restrictive `SCOPE_PERMISSIONS` example to the scopes doc.
5. Tests: POST succeeds and changes state, GET does nothing, anonymous is redirected, a user denied by `SCOPE_PERMISSIONS` gets 403.
6. Do not also expose it as an MCP tool unless asked.

## New MCP tool

1. **Package:** add the handler to the existing `tools.py` registry. `conf.py` is already wired.
2. **Internal:** if there is no `tools.py`, create it with a `ToolRegistry()` and add `tools=tool_registry.tools` to the `PanelConfig(...)` in `conf.py`. Do not touch anything else in `conf.py`.
3. `agent_` scope that differs from the human scope. Model imports inside the handler. Return `PanelToolResult`. `"additionalProperties": False`.
4. Add the tool to the scopes doc and, in a package, to `docs/features.md`.
5. Tests call the handler with a `PanelToolContext`, including a bad-input case that returns `success=False`.
6. A tool that mutates state needs the same care as an action: its own scope and a note in the scopes doc.

## New setting

1. Add the key and a default to `conf.py`'s `defaults`. The default must preserve today's behaviour, so existing projects see no change.
2. Read it only through `panel_config.get_settings()`.
3. Document it where the panel documents settings (`docs/configuration.md` in a package). Internal apps with no docs: a comment above the key in `conf.py`.
4. Test the default and one non-default value.
5. Never rename or remove an existing key; see [compatibility.md](compatibility.md).

## Change who may do what

1. Changing a scope's **name** is breaking. Changing what a scope protects is also a behaviour change for anyone who configured it. Read [compatibility.md](compatibility.md).
2. Tightening access by default (for example `REQUIRE_SUPERUSER`) changes behaviour for every existing user. Make it opt-in through a setting.
3. Moving a view from one scope to another: say so in the report, update the scopes doc.

## Change the data source

1. Keep the helper's return shape. If it must change, update every caller and its tests in the same change.
2. Keep the empty and error states working: no rows, backend unreachable, permission denied by the source.
3. Do not add a runtime dependency without asking.

## Restyle or fix markup

1. Replace custom CSS with `dcr-*` classes where one exists.
2. Panel `styles.css` only for layout the design system lacks, using `var(--dcr-*)` tokens.
3. Do not touch scope, URL, or context names while restyling.

## Bug fix

1. Write the failing test first, then the fix.
2. Fix at the cause. Do not widen an `except` or relax a permission check to make a symptom go away.
3. If the bug is in a shared contract (`PanelConfig`, `panel_base.html`, the design system), it belongs in `dj-control-room-base`, not in a local workaround. Say so.
