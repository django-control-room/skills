# Eval: add a setting

## Request

I want to hide some packages from the app packages list, such as `pip` and `setuptools`. Make it configurable per project.

## Expected approach

- `inspect_panel.py` reports `settings_key: DCR_APP_PACKAGES_SETTINGS` and defaults `EXTRA_CSS`, `LOAD_DEFAULT_CSS`
- The agent adds a key under that existing settings key. It does not invent a new settings dict

## Expected implementation

- A new key in `conf.py`'s `defaults`, for example `"EXCLUDE_PACKAGES": []`. The default hides nothing, so existing projects see no change
- The value is read with `panel_config.get_settings()["EXCLUDE_PACKAGES"]`, never `getattr(django.conf.settings, ...)`
- Exclusion uses the same name normalization as search, so `Typing_Extensions` and `typing-extensions` are treated as the same name
- The count badge and the "Showing X of Y" text agree with what is hidden (total counts shown packages, not excluded ones)
- The key is documented. This app has no docs site, so a comment above the key in `conf.py` or a line in `scopes.md` is acceptable. The agent does not create a `docs/` tree
- Tests: default shows everything, an override hides the named packages, excluded names are normalized, the search still works with exclusions
- Use `override_settings` for the non-default case

## Expected `inspect_panel.py --base HEAD`

```
added  settings_defaults: EXCLUDE_PACKAGES
```

No `BREAKING` lines. Exit code 0.

## Must not

- Change `settings_key`
- Remove or rename `LOAD_DEFAULT_CSS` or `EXTRA_CSS`
- Add a model, migration, or admin form for the list
