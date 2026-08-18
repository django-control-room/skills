# Evals

Example **user requests** used to check that this skill produces a coherent DCR panel. They are not runtime fixtures and are not copied into generated packages.

To eval: give the request to an agent that has `dcr-build-panel` loaded, then run `scripts/validate.py` and the generated test suite on the output.

A good result:

- Cookiecutter (via `scripts/bake.py`) created the package
- Implementation replaced Cookiecutter stubs in place (`hello_world` and the welcome page are gone)
- UI uses `dcr-*` from dj-control-room-base, not a parallel stylesheet
- Generated code depends on `dj-control-room-base`, not this repo
- `validate.py` reports 0 errors
- `pytest` and `manage.py check` pass
