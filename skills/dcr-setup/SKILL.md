---
name: dcr-setup
description: >-
  Installs, configures, and troubleshoots Django Control Room (DCR), the
  framework for building internal tools inside Django Admin. Adds
  dj-control-room and any chosen official panels (Redis, cache, Celery, URLs,
  signals), orders INSTALLED_APPS, mounts the URLs, and verifies the dashboard
  loads. Use when the user asks to install, set up, or get started with DCR,
  dj-control-room, or a control room in their admin, or when a setup is
  broken: "dcr_icons is not a registered tag library", dj_control_room.E001,
  or an installed panel missing from the dashboard. Builds no tools itself;
  django-internal-tools sends a tool request here first when DCR is not installed.
---

# dcr-setup

Get Django Control Room running in a project: the hub dashboard, and optionally some official panels.

This skill is **development-time guidance**. Nothing it produces may depend on this skills repository.

```
Read the project → choose panels → install → INSTALLED_APPS + urls.py → verify
```

Out of scope: **scopes and permissions** and the **MCP endpoint** (off by default), which are [dcr-access](../dcr-access/SKILL.md), and writing panels.

## 1. Read the project

Before asking anything, find out:

- **Django and Python versions.** DCR needs Django 4.2+ and Python 3.9+.
- **Admin.** `django.contrib.admin` must be in `INSTALLED_APPS` and mounted in the root URLs. DCR lives inside it. If the admin is mounted somewhere other than `admin/`, mount DCR under the same prefix.
- **Dependency manager.** `uv.lock`, `poetry.lock`, `Pipfile`, `requirements*.txt`, or `pyproject.toml` dependencies. Use the project's own tool, not a bare `pip install`.
- **Which file holds `INSTALLED_APPS`** and which holds the root `urlpatterns` (`ROOT_URLCONF`). Settings are often split (`settings/base.py`, `local.py`). Edit the shared one.
- **What is already there.** Any DCR packages or entries. Make every edit idempotent: add what is missing, never duplicate.
- **Admin theme apps** (Unfold, Jazzmin, and so on). Nothing to do: themes are detected automatically.

If it is not a Django project, or `django.contrib.admin` is not used, stop and say so.

## 2. Choose panels

The hub works alone. Official panels are optional extras:

| Extra | Panel app | For |
|---|---|---|
| `redis` | `dj_redis_panel` | Redis instances and keys |
| `cache` | `dj_cache_panel` | The Django cache |
| `celery` | `dj_celery_panel` | Celery workers and tasks |
| `urls` | `dj_urls_panel` | URL patterns |
| `signals` | `dj_signals_panel` | Django signals |

Suggest from what the project already uses (Celery or Redis in its dependencies, a configured cache backend), and ask once which to install. "None, just the hub" is a valid answer. If the user already named panels, use those and do not ask.

## 3. Install

Add to the project's dependencies with its own tool. The package is `dj-control-room`; `dj-control-room-base` comes with it.

```bash
pip install dj-control-room                  # hub only
pip install 'dj-control-room[redis,cache]'   # hub and panels (quote the extras)
```

For uv, Poetry, or a requirements file, use the equivalent. Put it where the project's other runtime dependencies are. If you cannot tell how the project installs dependencies, ask.

## 4. `INSTALLED_APPS`

Order matters: the shared library, then the panels, then the hub last.

```python
INSTALLED_APPS = [
    # ... django.contrib.admin, auth, contenttypes, sessions, messages, staticfiles ...

    "dj_control_room_base",   # required: template tags and the design system
    "dj_redis_panel",         # each panel you installed
    "dj_cache_panel",
    "dj_control_room",        # hub, after the panels

    # your apps
]
```

Missing `dj_control_room_base` causes `'dcr_icons' is not a registered tag library` and system check `dj_control_room.E001`. A panel listed after the hub falls outside the one "DJ Control Room" sidebar section.

## 5. `urls.py`

Mount the base library, each panel, and the hub, **before** the admin catch-all:

```python
from django.urls import include, path

urlpatterns = [
    path("admin/dj-control-room-base/", include("dj_control_room_base.urls")),
    path("admin/dj-redis-panel/", include("dj_redis_panel.urls")),
    path("admin/dj-cache-panel/", include("dj_cache_panel.urls")),
    path("admin/dj-control-room/", include("dj_control_room.urls")),
    path("admin/", admin.site.urls),   # last
]
```

The admin site has a catch-all route, so DCR paths placed after it are silently shadowed. Panel paths are the package name with dashes (`dj_redis_panel` → `dj-redis-panel`). Keep the project's existing routes and ordering otherwise.

Do not run `migrate` for DCR (it has no migrations) and do not create a superuser. If the project has no staff user, tell the user to run `python manage.py createsuperuser`.

## 6. Permissions

Do not configure scopes or access control here. By default any staff user can open the dashboard and the panels. If the user wants to limit that, or to give AI agents access, that is [dcr-access](../dcr-access/SKILL.md). In the report, point them at it and at:

- [Control Room permissions and scopes](https://djangocontrolroom.com/guides/control-room-permissions-and-scopes)
- [Scopes in the dj-control-room docs](https://django-control-room.github.io/dj-control-room/scopes/)

Say this plainly when any installed panel can change things, such as flushing the cache or running requests.

## 7. Verify

Run the doctor with the project's own Python environment, from the project root:

```bash
python scripts/doctor.py
python manage.py check
```

`doctor.py` loads the project's settings and URLs and reports missing or misordered apps, panels that are installed but not listed, and DCR URLs that are missing or shadowed. Errors must be fixed. Read each warning: some describe panels the user did not ask for, and those can be ignored.

Then have the user start the server, sign in as a staff user, and open `/admin/dj-control-room/` (or the path the doctor printed). The sidebar should show a **DJ CONTROL ROOM** section. For production, `collectstatic` serves DCR's static files.

If something is off, see [references/troubleshooting.md](references/troubleshooting.md).

## 8. Report

List what was installed, the files edited (settings, urls, dependency file), the dashboard URL, and what the doctor said. Then the permissions pointer from step 6.

Next steps: `dcr-access` to limit who can use each panel or to connect an AI agent. If they want to build something: `django-internal-tools` (or `dcr-create-internal-panel` directly) to create a panel for this project.

## Evals

Example requests used to check this skill: [evals/](evals/).
