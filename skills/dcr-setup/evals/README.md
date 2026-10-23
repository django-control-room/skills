# Evals

Example **user requests** used to check that this skill gets Django Control Room running in a project. They are not runtime fixtures.

To eval: start from the project described in each file, give the request to an agent that has `dcr-setup` loaded, and then run `scripts/doctor.py` with the project's Python environment.

A good result, for every eval:

- The agent read the project first (versions, dependency manager, where `INSTALLED_APPS` and `urls.py` live) before editing
- Dependencies were added with the project's own tool
- `INSTALLED_APPS` order is `dj_control_room_base`, then panels, then `dj_control_room`
- The base, panel, and hub URLs are mounted **above** the admin catch-all, including `dj_control_room_base.urls`
- Edits are minimal and idempotent: no reformatting, no duplicate entries
- No scopes, `ALLOWED_GROUPS`, `REQUIRE_SUPERUSER`, or MCP settings were added. The report points to the permissions guides
- No superuser was created and no DCR migration was invented
- `doctor.py` reports 0 errors and `manage.py check` passes

Evals are deliberately small:

- [fresh-project.md](fresh-project.md): a plain `startproject`, hub only
- [split-settings.md](split-settings.md): split settings, uv, and panel suggestions from the project's dependencies
- [broken-setup.md](broken-setup.md): an install that is already wrong
