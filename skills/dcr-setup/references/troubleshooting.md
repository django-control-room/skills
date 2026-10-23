# Troubleshooting

Run `python scripts/doctor.py` first. It names most of these directly.

| Symptom | Cause | Fix |
|---|---|---|
| `'dcr_icons' is not a registered tag library`, or `dj_control_room.E001` | `dj_control_room_base` is not in `INSTALLED_APPS` | Add it before the panels and the hub |
| Dashboard is empty, or a panel is missing | The panel package is installed but not in `INSTALLED_APPS`, or not installed in this environment | Add the app before `dj_control_room`; check `pip list` in the environment that runs Django |
| Panel card says **Configure** or **Setup** | The app is listed but its URLs are not included | Add `path("admin/<panel-name>/", include("<app>.urls"))` |
| `NoReverseMatch` for a DCR URL | The URLs are not included, or are nested under another namespace | Include them at the root `urlpatterns`, not inside another `include` |
| A DCR URL shows the admin's "page not found" or a login redirect to the wrong place | The path is after `path("admin/", admin.site.urls)`, which has a catch-all | Move DCR paths above it (doctor: `*_urls_shadowed`) |
| Panels appear outside the "DJ Control Room" sidebar section | They are listed after `dj_control_room` | Move them before it |
| An in-project panel does not show in the sidebar | Its app is listed after `dj_control_room` | Move it before the hub |
| Dashboard unstyled in production | Static files not collected | `python manage.py collectstatic` |
| Dashboard loads in dev but not for a colleague | Not a staff user, or a scope restricts them | Staff status first; scopes are the user's configuration, see the permissions guide |
| Doctor exits 2: could not load the project | Wrong Python environment, bad settings module, or a settings import error | Use the project's environment; pass `--settings` |
| Nothing changes after installing | The dev server has not restarted | Restart it. Panels are discovered at startup |

## Still stuck

Check the versions: Django 4.2+, Python 3.9+. Then read [Installation](https://django-control-room.github.io/dj-control-room/installation/) and the troubleshooting section there.
