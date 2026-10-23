# Eval: split settings and panel suggestions

## Setup

A project managed with **uv** (`pyproject.toml` and `uv.lock`). Settings are split: `config/settings/base.py` holds `INSTALLED_APPS`, and `local.py` and `production.py` import from it. `config/urls.py` mounts the admin at `django-admin/`. The project depends on `celery` and `redis`, and `CACHES` uses `django_redis`.

## Request

I'd like a control room dashboard for this project.

## Expected approach

- The agent notices the dependency manager is uv, that `INSTALLED_APPS` lives in `base.py`, and that the admin prefix is `django-admin/`
- It suggests the `celery`, `redis`, and `cache` panels because the project uses them, and asks once which to install. It does not install all of them by default
- Suppose the user answers "celery and redis"

## Expected result

- Dependencies added with `uv add 'dj-control-room[celery,redis]'`, so both `pyproject.toml` and `uv.lock` change. No bare `pip install`
- `INSTALLED_APPS` edited in `base.py` only, in the order `dj_control_room_base`, `dj_celery_panel`, `dj_redis_panel`, `dj_control_room`
- URLs mounted under the admin's own prefix, for example `django-admin/dj-control-room/`, and all above `path("django-admin/", admin.site.urls)`
- `doctor.py --settings config.settings.local` reports 0 errors. The dashboard path it prints starts with `/django-admin/`
- The report notes that the Celery and Redis panels can act on live infrastructure and links the permissions guides. It does not set any scopes

## Must not

- Edit `local.py` or `production.py` for `INSTALLED_APPS`
- Use `admin/` when the project's admin is at `django-admin/`
- Install the cache panel or the other extras the user did not choose
