# Tests

`dcr_startpanel` leaves Django's stock `tests.py` stub in the app. Replace it with real tests, or move them into the **host project's existing suite** (follow that repo's layout: `tests/`, `app/tests/`, pytest-django, etc.). Do not add a second pytest config or an `example_project`.

A small staff-superuser + logged-in-client fixture is the right base. See [dj-urls-panel/tests](https://github.com/django-control-room/dj-urls-panel/tree/main/tests) for the idea.

## Rules

- Resolve URLs with `reverse("<app_label>:<name>")`, e.g. `reverse("dcr_app_packages:index")`.
- Cover: happy path, unauthenticated 302 to admin login, mutating POST (if any), and each MCP handler via `PanelToolContext` (no MCP transport).
- Test data-gathering helpers (for example a function that reads installed packages) directly, separately from the view.
- The host project **should** have `dj_control_room` installed. Do not unregister the hub in tests unless you are specifically testing the placeholder admin.
- Do not add `docs/`, Docker, or a nested `example_project` just to run tests.

After tests pass, run `scripts/validate.py` on the app directory.
