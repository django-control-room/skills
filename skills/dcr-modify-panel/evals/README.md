# Evals

Example **user requests** used to check that this skill changes an existing panel cleanly. They are not runtime fixtures.

Each eval starts from the same baseline: the `dcr_app_packages` internal panel in the playground's `example_project/` (a read-only list of installed Python packages with a `q` search). Reset it to a clean checkout before each run so the agent sees an unmodified panel.

To eval: give the request to an agent that has `dcr-modify-panel` loaded, in a Django project that has `dj-control-room` and `dj-control-room-base` installed. Then run `scripts/inspect_panel.py <app> --base HEAD`, `manage.py check`, and the project's tests.

A good result, for every eval:

- The agent ran `inspect_panel.py` and read the panel before editing
- The change is **in place**: no `dcr_startpanel`, no Cookiecutter, no regenerated files
- Unrelated files are untouched (no reformatting, no renames, no new `pyproject.toml`, Docker, or MkDocs)
- UI uses `dcr-*`, not a parallel stylesheet or admin `.button`
- New scopes, tools, and settings are documented and have tests
- `inspect_panel.py --base HEAD` shows only `added …` lines, unless the eval says a break was approved
- The final report lists Added, Breaking, and Not done

Evals are deliberately small, so they are cheap to run and easy to check:

- [add-detail-page.md](add-detail-page.md): new view, scope, URL, link, and test
- [add-mcp-tool.md](add-mcp-tool.md): first tool in a panel with no `tools.py`
- [add-setting.md](add-setting.md): a new setting with a behaviour-preserving default
- [rename-scope.md](rename-scope.md): a request that would break existing configuration. The right move is to stop and ask
