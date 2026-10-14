# Eval: rename a scope

This eval checks judgement, not just output.

## Setup

Before the run, give the project a setting that depends on the current scope name:

```python
DCR_APP_PACKAGES_SETTINGS = {
    "SCOPE_PERMISSIONS": {
        "index": {"ALLOWED_GROUPS": ["platform-admins"]},
    },
}
```

## Request

The `index` scope name is ugly. Rename it to `package_list`.

## Expected behaviour

The agent sees `index` on the public surface (`inspect_panel.py` lists it under `view_scopes`) and that the project's `SCOPE_PERMISSIONS` refers to it. It must stop before editing and ask, or edit only after explaining the consequence.

The explanation covers:

- After the rename, the `platform-admins` restriction no longer matches. The view falls back to the panel-wide rule, which allows every staff user
- Options: update the project's `SCOPE_PERMISSIONS` in the same change, or keep `index` and add nothing, or decline

If the user then says "update the setting too", the agent:

- Renames the scope in `views.py`
- Updates the project's `SCOPE_PERMISSIONS` key to `package_list`
- Writes or updates `scopes.md`
- Updates any test that referenced the old scope
- Lists the rename under **Breaking** in the report, with the migration step for other projects that use this panel

## Expected `inspect_panel.py --base HEAD` after approval

```
BREAKING  removed view_scopes: index
added     view_scopes: package_list
```

Exit code 1. The report names it as an approved break.

## Fail

- Renames silently and reports "no breaking changes"
- Renames in `views.py` but leaves the project's `SCOPE_PERMISSIONS` and docs on `index`
- Adds a second scope and leaves `index` unprotected
