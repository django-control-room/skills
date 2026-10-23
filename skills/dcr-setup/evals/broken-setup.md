# Eval: broken setup

## Setup

DCR was installed by hand and is wrong in three ways:

- `INSTALLED_APPS` lists `"dj_control_room"` but not `"dj_control_room_base"`
- `dj_cache_panel` is installed with pip and listed **after** `dj_control_room`
- In `urls.py`, `path("admin/", admin.site.urls)` comes **before** the DCR `include(...)` lines, so the dashboard URL falls into the admin catch-all

## Request

I installed Django Control Room but I get `'dcr_icons' is not a registered tag library`, and the dashboard URL gives me an admin 404.

## Expected approach

- The agent runs `scripts/doctor.py` (or reads the settings and URLs) and finds all three problems
- It explains each cause briefly, then fixes them

## Expected result

- `"dj_control_room_base"` added before the panels and the hub
- `"dj_cache_panel"` moved before `"dj_control_room"`
- The DCR `path(...)` lines moved above `path("admin/", admin.site.urls)`, keeping the project's other routes as they were
- `doctor.py` reports 0 errors, and `manage.py check` no longer reports `dj_control_room.E001`
- The report lists the three fixes

## Must not

- Reinstall or upgrade packages
- Remove or reorder unrelated apps or routes
- Add scope or MCP settings
