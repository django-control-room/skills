# Tests

Keep the generated `tests/base.py` (`PanelTestCase`) and `tests/conftest.py`. Extend or replace `tests/test_tools.py` and add view tests next to the generated ones. Follow official panel tests (e.g. [dj-urls-panel/tests](https://github.com/django-control-room/dj-urls-panel/tree/main/tests), [dj-cache-panel/tests](https://github.com/django-control-room/dj-cache-panel/tree/main/tests)).

## Rules

- Subclass `PanelTestCase` (staff superuser + logged-in client).
- Resolve URLs with `reverse("<package>:<name>")`.
- Cover: happy path, unauthenticated 302 to admin login, mutating POST, and each MCP handler via `PanelToolContext` (no MCP transport).
- Do not assert on `dj_control_room` hub admin proxies; panel tests drop the hub from `INSTALLED_APPS` (see generated `tests/conftest.py`).
- Do not leave `handle_hello_world` imports behind.

After tests pass, run `scripts/validate.py` on the project directory.
