# Evals

Example **user requests** used to check that this skill produces a coherent in-project DCR panel. They are not runtime fixtures and are not copied into the Django app.

To eval: give the request to an agent that has `dcr-create-internal-panel` loaded, in a Django project that already has `dj-control-room` and `dj-control-room-base` installed. Then run `scripts/validate.py` on the new app and the host project's tests.

A good result:

- `manage.py dcr_startpanel` created a `dcr_`-prefixed sibling Django app
- The app is a **sibling** of existing apps, not nested inside one
- Implementation replaced the starter `index` view and template
- UI uses `dcr-*` from dj-control-room-base, not a parallel stylesheet
- The app is wired in `INSTALLED_APPS` (before `dj_control_room`) and `urls.py`
- `validate.py` reports 0 errors and no warnings
- `manage.py check` and the host test suite pass

Cookiecutter is not used by this skill. If the user asked for a reusable/PyPI package, the agent must **not** use this skill.

Evals are deliberately small, read-only panels over in-process data so they are cheap to run and easy to check:

- [app-packages.md](app-packages.md)
