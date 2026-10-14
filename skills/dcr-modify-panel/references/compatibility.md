# Compatibility

An existing panel has users, and they configured it and bookmarked it against names you can see in the code. Changing those names breaks them silently: a renamed scope stops matching the `SCOPE_PERMISSIONS` entry someone wrote for it and falls back to the panel-wide rule, which may be **more permissive** than they intended.

`scripts/inspect_panel.py PATH --base REF` lists everything below that exists at `REF` and is gone now.

## The public surface

| Item | Who depends on it | Safe change | If a break is requested |
|---|---|---|---|
| **View scope** (`permission_required("x")`) | `SCOPE_PERMISSIONS` in project settings | Add new scopes | Keep the old scope on the old behaviour, or document the rename and say a permissive fallback will apply |
| **Tool name** (`name=` on a tool) | Agent prompts, MCP client config | Add new tools | Keep the old tool as a thin alias for one release |
| **Tool scope** (`scope="agent_x"`) | `SCOPE_PERMISSIONS` | Add new scopes | As for view scopes |
| **URL name** (`name=` on `path`) | `reverse()` calls, templates, bookmarks of the panel | Add new routes | Keep the old route and redirect it to the new one |
| **URL namespace** (`app_name`) | Every `reverse("<ns>:...")`, including the hub card | Never change | Do not. It must match the app label |
| **Settings key** (`settings_key`) | The project's `DJ_*_SETTINGS` / `<APP>_SETTINGS` | Never change | Do not. Read the old key as a fallback if you must move |
| **Settings default key** | Project settings dicts | Add new keys with a behaviour-preserving default | Read the old key when the new one is absent; document the deprecation |
| **Entry point** (`dj_control_room.panels`) | The hub's registry id, and every config keyed on it | Never change | Do not |
| **App label / package name** | `INSTALLED_APPS`, imports, migrations, content types | Never change | Do not. Create a new panel instead |

`inspect_panel.py` tracks: view scopes, tool names, tool scopes, URL names, URL namespace, settings key, settings default keys, entry point. App label is the directory name; check it yourself if files moved.

## Behaviour that is not in the list

- A **default** that changes (for example `ENABLE_TESTING` from `True` to `False`) is breaking even though no name changed.
- A view that now needs a **different scope** than before changes who can reach it.
- A POST action turning into GET, or the reverse.
- A tool's `input_schema` becoming stricter, or its output shape changing.
- A context key renamed that a project's **template override** may read.

Treat these as breaking and ask.

## The generated `index` scope

Panels created from the starter keep the generated `"index"` scope. Do not rename it as part of an unrelated change. If the user wants it renamed, that is a scope rename like any other: see the table. For a brand-new internal panel nobody else has configured yet, a rename is safe, but confirm that it is new.

## What to do when a break is requested

1. Say what will break and for whom, in one or two sentences.
2. Offer the compatible version: keep the old name working alongside the new one.
3. Do what the user decides. If they accept the break, make it completely (code, scopes doc, tests, docs) and list it under **Breaking** in the report with the migration step.

## Not breaking

Adding a scope, tool, URL, or setting with a behaviour-preserving default. Fixing a bug. Changing markup that does not alter names the above depend on. Adding a column.
