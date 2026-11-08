# Evals

Example **user requests** used to check that this skill sets access to DCR tools correctly. They are not runtime fixtures.

To eval: start from the project described in each file, give the request to an agent that has `dcr-access` loaded, then run `python manage.py check` and the permission checks the file lists.

A good result, for every eval:

- The agent ran `inspect_panel.py` (or read the panel's scopes doc) and used scope names exactly as the panel defines them
- Rules were merged into the existing settings dict, with a one-line comment saying who each is for
- Only settings changed. No panel code was edited, and anything that needed a code change was handed to `dcr-modify-panel`
- No groups, users, or memberships were created without the user agreeing
- No secret was written into a committed file
- The report states the rules in plain words and lists what the user still has to create

Evals are deliberately small:

- [restrict-action.md](restrict-action.md): one action limited to a team, the rest open
- [enable-mcp.md](enable-mcp.md): agent access through the MCP endpoint, read-only
