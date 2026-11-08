# Eval: restrict one action to a team

## Setup

DCR is installed with the hub. The project has an internal panel `dcr_refunds` with:

- View scopes `refund_list`, `refund_detail`, `refund_approve`, `refund_reject`
- Tool scopes `agent_refund_list`, `agent_refund_approve`
- No `DCR_REFUNDS_SETTINGS` in settings yet
- A `finance` group that already exists in the database

## Request

Only the finance team should be able to approve or reject refunds. Everyone on staff can still see the queue.

## Expected result

- `DCR_REFUNDS_SETTINGS["SCOPE_PERMISSIONS"]` limits `refund_approve`, `refund_reject`, and `agent_refund_approve` to `["finance"]`
- No top-level `ALLOWED_GROUPS` or `REQUIRE_SUPERUSER`, so `refund_list` and `refund_detail` stay open to all staff
- `manage.py check` passes
- In `manage.py shell`, `panel_config._check_permission(...)` is `True` for a finance member and `False` for other staff on `refund_approve`, and `True` for both on `refund_list`

## Must not

- Edit `dcr_refunds` code
- Restrict `refund_detail` to hide the buttons (that would hide the whole page)
- Create or rename the `finance` group
