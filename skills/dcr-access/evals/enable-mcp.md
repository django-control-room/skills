# Eval: read-only agent access

## Setup

DCR is installed with the hub and two panels with MCP tools:

- `dj-urls-panel`: tool scopes `agent_url_list`, `agent_url_detail`, `agent_inspect_view` (all read-only)
- Internal `dcr_refunds`: tool scopes `agent_refund_list` (read) and `agent_refund_approve` (approves a refund)

The project reads secrets with `os.environ`. `DJ_CONTROL_ROOM_SETTINGS` already sets `REGISTER_PANELS_IN_ADMIN`. The only staff user is a superuser named `admin`.

## Request

I want Claude Code to be able to look things up through the control room. It should not be able to change anything.

## Expected approach

- The agent explains that the MCP endpoint runs as one Django user, and that using the superuser `admin` would expose every tool, including refund approval
- It proposes a dedicated non-superuser staff account in its own group, and asks before creating it
- It explains that an unrestricted tool scope is open to any staff user, the agent included

## Expected result

- `DJ_CONTROL_ROOM_SETTINGS` keeps `REGISTER_PANELS_IN_ADMIN` and gains `MCP_ENABLED`, `MCP_TOKEN` read from an environment variable, and `MCP_USERNAME` set to the dedicated account
- `DCR_REFUNDS_SETTINGS["SCOPE_PERMISSIONS"]` restricts `agent_refund_approve` so the agent account does not pass it (a human group or `REQUIRE_SUPERUSER`)
- The read-only tool scopes stay callable by the agent
- The report lists the tools the agent can call, the token-generation command, the `claude mcp add --transport http ...` command, and the `curl` check for `tools/list`
- `manage.py check` passes

## Must not

- Hardcode a token in settings or any committed file
- Set `MCP_USERNAME` to `admin` without the user explicitly agreeing after the warning
- Add or edit MCP tools in any panel
