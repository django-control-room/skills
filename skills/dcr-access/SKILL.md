---
name: dcr-access
description: >-
  Controls who can use internal tools built with Django Control Room (DCR):
  limit a tool, or one page or action in it, to a team (a Django group) or to
  superusers, or open it to all staff; and give AI agents (Cursor, Claude, and
  other MCP clients) access to those tools through DCR's MCP endpoint. Use
  for requests like "only finance can approve refunds", "lock down the flush
  button", "why does support get a 403", or "let Claude call our admin
  tools". Edits project settings only. Not for adding a scope or MCP tool to
  a panel's code (dcr-modify-panel) or installing DCR (dcr-setup).
---

# dcr-access

Decide who may use which DCR tool, in the project's settings, and turn on agent access over MCP.

This skill is **development-time guidance**. Nothing it produces may depend on this skills repository.

```
Read the project → list the panel's scopes → write settings → (MCP: enable, agent user, client) → verify → report
```

It changes **settings only**. Panel code decides which scopes exist; this skill decides who gets them. If the thing the user wants to restrict has no scope of its own, that is a code change: hand off to [dcr-modify-panel](../dcr-modify-panel/SKILL.md) to add one, then come back.

Authoritative docs: [Permissions and scopes](https://djangocontrolroom.com/guides/control-room-permissions-and-scopes), [dj-control-room-base configuration](https://django-control-room.github.io/dj-control-room-base/configuration/#permissions), [MCP endpoint](https://django-control-room.github.io/dj-control-room/configuration/#ai-agent-integration-mcp).

## How DCR decides

Every DCR view and MCP tool is checked in this order:

1. Not logged in: redirect to the admin login.
2. Not staff: 403. DCR never serves non-staff users. If the user wants non-staff people to use a tool, they must be made staff; say so.
3. Superuser: always allowed, whatever the settings say.
4. `REQUIRE_SUPERUSER` true for the scope: 403.
5. `ALLOWED_GROUPS` non-empty for the scope: 403 unless the user is in one of those groups.
6. Otherwise: allowed.

Settings live in each panel's own settings key (`DJ_URLS_PANEL_SETTINGS`, `DCR_REFUNDS_SETTINGS`, ...). `ALLOWED_GROUPS` and `REQUIRE_SUPERUSER` at the top level apply to the whole panel. `SCOPE_PERMISSIONS` overrides them for single scopes; scopes not listed fall back to the panel-wide rule. The hub itself uses `DJ_CONTROL_ROOM_SETTINGS` (scopes `dashboard` and `install`). Do not write `DJ_CONTROL_ROOM_SETTINGS["PANELS"]`: the hub does not read it.

## 1. Read the project

- **Which panel.** Match the user's words ("the refunds tool", "the flush button") to an installed panel. If several could match, ask.
- **Its settings key and scopes.** Run the modify skill's inspector on the panel's app directory (for an installed package, the directory of `python -c "import pkg; print(pkg.__path__[0])"`):

  ```bash
  python ../dcr-modify-panel/scripts/inspect_panel.py PATH
  ```

  It prints `settings_key`, `view_scopes`, and `tool_scopes`. The panel's scopes doc (`docs/scopes.md`, or `scopes.md` next to `panel.py`) says what each scope protects.
- **What is already configured.** Find the settings file that holds `INSTALLED_APPS` (the shared one if settings are split) and any existing `*_SETTINGS` dict for the panel. Merge into it; never replace or duplicate it.
- **Groups.** Search the code and fixtures for the group names the user mentioned. Groups are database rows, not settings.

## 2. Write the access rules

Translate the request into the smallest rule:

| They want | Write |
|---|---|
| Whole tool for one or more teams | `"ALLOWED_GROUPS": ["finance"]` at the top of the panel's settings |
| Whole tool for superusers only | `"REQUIRE_SUPERUSER": True` at the top |
| One page or action for a team, the rest open | `"SCOPE_PERMISSIONS": {"refund_approve": {"ALLOWED_GROUPS": ["finance"]}}` |
| One action for superusers only | `"SCOPE_PERMISSIONS": {"cache_flush": {"REQUIRE_SUPERUSER": True}}` |
| Agents may read but not change | Restrict the mutating `agent_*` scopes; leave the read ones |
| Who can see the hub dashboard | The same keys in `DJ_CONTROL_ROOM_SETTINGS`, scope `dashboard` |

```python
DCR_REFUNDS_SETTINGS = {
    # Any staff member can see the queue; only finance can approve or reject.
    "SCOPE_PERMISSIONS": {
        "refund_approve": {"ALLOWED_GROUPS": ["finance"]},
        "refund_reject": {"ALLOWED_GROUPS": ["finance"]},
    },
}
```

Rules:

- Use the scope names exactly as the inspector printed them. A misspelled scope is silently ignored, and the view stays open.
- If the action the user named shares a scope with something else (the approve button is protected by `refund_detail`), settings cannot separate them. Say so and hand off to `dcr-modify-panel` to give it its own scope.
- Restrict the matching `agent_*` scope too, or an agent can do through MCP what staff cannot do in the UI.
- If a group does not exist yet, tell the user to create it under **Authentication and Authorization → Groups** and add its members. If the project already creates groups in a data migration, offer to add it there. Do not create groups, users, or memberships without asking.
- Add a one-line comment above each rule saying who it is for.

## 3. Agent access over MCP (only if asked)

The endpoint is part of the hub. If `dj_control_room` is not in `INSTALLED_APPS`, set it up with [dcr-setup](../dcr-setup/SKILL.md) first.

It lists and calls every installed panel's MCP tools, as one Django user, and only the tools that user's scopes allow. A panel with no MCP tools exposes nothing; adding tools is [dcr-modify-panel](../dcr-modify-panel/SKILL.md).

1. **Settings**, in `DJ_CONTROL_ROOM_SETTINGS` (merge into the existing dict). All three are required:

   ```python
   import os

   DJ_CONTROL_ROOM_SETTINGS = {
       "MCP_ENABLED": True,
       "MCP_TOKEN": os.environ.get("DCR_MCP_TOKEN"),
       "MCP_USERNAME": "mcp-agent",  # matched against the user model's USERNAME_FIELD
   }
   ```

   Read the token from the environment, the way the project already reads secrets (`os.environ`, django-environ, and so on). Never write a token into a committed file. Tell the user how to generate one: `python -c "import secrets; print(secrets.token_urlsafe(32))"`.

2. **The agent user.** Recommend a dedicated, active, **non-superuser** staff account (for example `mcp-agent`) in its own group, such as `agents`. A superuser passes every scope, so every tool would be callable whatever the settings say. Do not create the user without asking; `createsuperuser` is the wrong command, since the account should be staff only.

3. **Which tools it may call.** Like any staff user, the agent passes every scope nobody restricted. So list the `agent_*` scopes of every installed panel (step 1) and decide each one:
   - **Agent may call it, people may not**: `{"ALLOWED_GROUPS": ["agents"]}`.
   - **Agent must not call it** (anything that mutates, unless the user asked): restrict it to a human group or `{"REQUIRE_SUPERUSER": True}`.
   - **Anyone on staff, agent included**: leave it out.

   Tell the user which tools the agent will be able to call. If they insist on an existing account, say what it can reach.

4. **Client.** The endpoint is `POST <admin prefix>/dj-control-room/mcp/` (usually `/admin/dj-control-room/mcp/`) with `Authorization: Bearer <token>`. For Cursor, `.cursor/mcp.json`:

   ```json
   {
     "mcpServers": {
       "dj-control-room": {
         "url": "http://localhost:8000/admin/dj-control-room/mcp/",
         "headers": { "Authorization": "Bearer ${env:DCR_MCP_TOKEN}" }
       }
     }
   }
   ```

   For Claude Code: `claude mcp add --transport http dj-control-room http://localhost:8000/admin/dj-control-room/mcp/ --header "Authorization: Bearer $DCR_MCP_TOKEN"`. Other clients: any MCP client that supports Streamable HTTP with a custom header.

5. **Outside development**, the endpoint must be served over HTTPS only, and the token rotated like any other credential. Say this in the report when the settings file is used in production.

## 4. Verify

```bash
python manage.py check
```

Check a rule as a given user without a browser, in `python manage.py shell`:

```python
from django.contrib.auth import get_user_model
from dcr_refunds.conf import panel_config
user = get_user_model().objects.get(username="alice")
panel_config._check_permission(user, "refund_approve")   # True or False
```

Check one user that should pass and one that should not. For MCP, with the server running:

```bash
curl -s -X POST http://localhost:8000/admin/dj-control-room/mcp/ \
  -H "Authorization: Bearer $DCR_MCP_TOKEN" -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

| Result | Cause |
|---|---|
| 404 | `MCP_ENABLED` is not true, or the hub URLs are not mounted (`dcr-setup`) |
| 401 | Wrong or missing token |
| 500, "Server misconfiguration" | `MCP_TOKEN` empty in this environment, or `MCP_USERNAME` is not an active staff user. The server log says which |
| Empty tool list | No installed panel has MCP tools, or the agent user passes none of the `agent_*` scopes |
| A tool listed that should not be | Its `agent_*` scope is unrestricted, or the agent user is a superuser |

Tool names come back as `<panel_id>__<tool_name>`.

## 5. Report

- The rules written, per panel and scope, in plain words ("only `finance` can approve or reject refunds; any staff can view the queue").
- Groups or users the user still has to create, and who should be in them.
- For MCP: the endpoint URL, where the token is read from, the agent user, which tools it can call, and the client config added.
- Anything that needed a code change and was handed to `dcr-modify-panel`.

## Evals

Example requests used to check this skill: [evals/](evals/).
