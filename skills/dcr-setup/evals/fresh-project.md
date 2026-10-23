# Eval: fresh project

## Setup

A new project from `django-admin startproject shop .` with `pip` and a `requirements.txt`. `django.contrib.admin` is enabled and `path("admin/", admin.site.urls)` is the only route. No DCR packages.

## Request

Set up Django Control Room in this project.

## Expected approach

- The agent reads `settings.py`, `urls.py`, and `requirements.txt`
- It asks at most one question: which official panels, offering "none, just the hub". Since the project uses none of Redis, Celery, or a custom cache backend, it suggests nothing in particular
- If the user answers "just the hub", no extras are installed

## Expected result

- `requirements.txt` gains `dj-control-room`
- `INSTALLED_APPS` gains `"dj_control_room_base"` then `"dj_control_room"`, after the `django.contrib` apps
- `urls.py` mounts, above `path("admin/", admin.site.urls)`:
  - `admin/dj-control-room-base/` → `dj_control_room_base.urls`
  - `admin/dj-control-room/` → `dj_control_room.urls`
- `python scripts/doctor.py` shows the dashboard at `/admin/dj-control-room/`, 0 errors, 0 warnings
- The report tells the user to run `createsuperuser` if they have no staff user, and links the permissions guides
- No scope settings, no MCP settings

## Must not

- Place the DCR paths after the admin route
- Put `dj_control_room` before `dj_control_room_base`
- Run `migrate` or create a user on the user's behalf
- Add `DJ_CONTROL_ROOM_SETTINGS`
