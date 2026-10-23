#!/usr/bin/env python3
"""Check that Django Control Room is wired into a Django project.

Run it with the project's own Python environment (the one that has Django and
dj-control-room installed). It imports the project's settings and URLs, so it
sees exactly what ``runserver`` would.

Usage:
    python scripts/doctor.py                      # run from the project root
    python scripts/doctor.py --project-dir path/to/project
    python scripts/doctor.py --settings myproject.settings.local --json

The settings module is taken from --settings, then $DJANGO_SETTINGS_MODULE, then
the ``os.environ.setdefault("DJANGO_SETTINGS_MODULE", ...)`` line in manage.py.

Checks: Python/Django versions, django.contrib.admin and staticfiles,
dj_control_room_base and dj_control_room in INSTALLED_APPS, their order, panels
installed with pip but missing from INSTALLED_APPS, URLs that are missing or
shadowed by another route, and Django's own system checks.

Does not touch the database, change any file, or check permissions or scopes.
Exits 1 if any error is found, 2 if the project could not be loaded.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

HUB = "dj_control_room"
BASE = "dj_control_room_base"
ENTRY_POINT_GROUP = "dj_control_room.panels"


class Issue:
    def __init__(self, level: str, code: str, message: str, hint: str = ""):
        self.level = level
        self.code = code
        self.message = message
        self.hint = hint

    def as_dict(self) -> dict:
        return {"level": self.level, "code": self.code, "message": self.message, "hint": self.hint}


def find_settings_module(project_dir: Path, explicit: str | None) -> str | None:
    if explicit:
        return explicit
    if os.environ.get("DJANGO_SETTINGS_MODULE"):
        return os.environ["DJANGO_SETTINGS_MODULE"]
    manage = project_dir / "manage.py"
    if manage.is_file():
        match = re.search(
            r"""setdefault\(\s*['"]DJANGO_SETTINGS_MODULE['"]\s*,\s*['"]([\w.]+)['"]""",
            manage.read_text(encoding="utf-8", errors="replace"),
        )
        if match:
            return match.group(1)
    return None


def panel_entry_points() -> list[tuple[str, str]]:
    """(entry point name, top-level package) for every installed panel plugin."""
    from importlib.metadata import entry_points

    eps = entry_points()
    selected = eps.select(group=ENTRY_POINT_GROUP) if hasattr(eps, "select") else eps.get(ENTRY_POINT_GROUP, [])
    return [(ep.name, ep.value.split(":")[0].split(".")[0]) for ep in selected]


def app_index(installed: list[str], label: str) -> int | None:
    """Index of the INSTALLED_APPS entry for module ``label`` (handles AppConfig paths)."""
    for i, entry in enumerate(installed):
        if entry == label or entry.startswith(label + "."):
            return i
    return None


def mounted_correctly(namespace: str, url_name: str = "index") -> tuple[bool, str]:
    """Is ``namespace:url_name`` reversible, and does its path resolve back to it?"""
    from django.urls import NoReverseMatch, Resolver404, resolve, reverse

    try:
        path = reverse(f"{namespace}:{url_name}")
    except NoReverseMatch:
        return False, "missing"
    try:
        match = resolve(path)
    except Resolver404:
        return False, f"{path} does not resolve"
    if namespace not in match.namespaces:
        return False, f"{path} is handled by {match.view_name or match._func_path}, not {namespace}"
    return True, path


def run(project_dir: Path, settings_module: str) -> tuple[list[Issue], dict]:
    issues: list[Issue] = []
    info: dict = {"settings_module": settings_module, "project_dir": str(project_dir)}

    sys.path.insert(0, str(project_dir))
    os.environ["DJANGO_SETTINGS_MODULE"] = settings_module

    import django
    from django.conf import settings

    django.setup()

    info["python"] = ".".join(map(str, sys.version_info[:3]))
    info["django"] = django.get_version()
    if sys.version_info < (3, 9):
        issues.append(Issue("error", "python_version", f"Python {info['python']} is too old.", "dj-control-room needs Python 3.9+."))
    if django.VERSION < (4, 2):
        issues.append(Issue("error", "django_version", f"Django {info['django']} is too old.", "dj-control-room needs Django 4.2+."))

    installed = list(settings.INSTALLED_APPS)

    if app_index(installed, "django.contrib.admin") is None:
        issues.append(Issue("error", "no_admin", "django.contrib.admin is not in INSTALLED_APPS.", "Panels live inside Django admin."))
    if app_index(installed, "django.contrib.staticfiles") is None:
        issues.append(Issue("warning", "no_staticfiles", "django.contrib.staticfiles is not in INSTALLED_APPS.", "The design system CSS is served as a static file."))

    base_i = app_index(installed, BASE)
    hub_i = app_index(installed, HUB)

    if base_i is None:
        issues.append(Issue("error", "base_missing", f"'{BASE}' is not in INSTALLED_APPS.", "Without it you get \"'dcr_icons' is not a registered tag library\" and dj_control_room.E001."))
    if hub_i is None:
        issues.append(Issue("error", "hub_missing", f"'{HUB}' is not in INSTALLED_APPS.", "Add it after the panel apps."))
    if base_i is not None and hub_i is not None and base_i > hub_i:
        issues.append(Issue("error", "base_after_hub", f"'{BASE}' is listed after '{HUB}'.", f"Move '{BASE}' before '{HUB}'."))

    panels = panel_entry_points()
    info["panels_installed"] = sorted({pkg for _, pkg in panels})
    flagged_missing: set[str] = set()
    for _, pkg in panels:
        if pkg == BASE:  # checked on its own above
            continue
        idx = app_index(installed, pkg)
        if idx is None:
            flagged_missing.add(pkg)
            issues.append(Issue("warning", "panel_not_in_installed_apps", f"Panel package '{pkg}' is pip-installed but not in INSTALLED_APPS.", f"Add '{pkg}' before '{HUB}'."))
        elif hub_i is not None and idx > hub_i:
            issues.append(Issue("warning", "panel_after_hub", f"'{pkg}' is listed after '{HUB}'.", "Panels listed after the hub land outside the one \"DJ Control Room\" sidebar section. List panels before the hub."))

    if hub_i is not None:
        ok, detail = mounted_correctly(HUB)
        if not ok and detail == "missing":
            issues.append(Issue("error", "hub_urls_missing", "The hub's URLs are not included.", "Add path('admin/dj-control-room/', include('dj_control_room.urls')) to the root urls.py."))
        elif not ok:
            issues.append(Issue("error", "hub_urls_shadowed", f"Hub URL is shadowed: {detail}.", "Put the DCR paths before path('admin/', admin.site.urls)."))
        else:
            info["dashboard_url"] = detail

    if base_i is not None:
        ok, detail = mounted_correctly(BASE)
        if not ok and detail == "missing":
            issues.append(Issue("error", "base_urls_missing", f"The URLs of '{BASE}' are not included.", "Add path('admin/dj-control-room-base/', include('dj_control_room_base.urls')) to the root urls.py."))
        elif not ok:
            issues.append(Issue("error", "base_urls_shadowed", f"Base URL is shadowed: {detail}.", "Put the DCR paths before path('admin/', admin.site.urls)."))

    if hub_i is not None:
        from dj_control_room.registry import registry
        from dj_control_room.utils import get_panel_config_status

        panel_rows = []
        for panel in registry.get_panels():
            panel_id = panel._registry_id
            app_name = panel.app_name
            if app_name == BASE:  # checked on its own above
                continue
            status = get_panel_config_status(panel_id, app_name)
            row = {"id": panel_id, "app": app_name, "configured": status["is_configured"]}
            panel_rows.append(row)
            if status["is_configured"]:
                ok, detail = mounted_correctly(app_name, getattr(panel, "get_url_name", lambda: "index")())
                if not ok:
                    issues.append(Issue("error", "panel_urls_shadowed", f"Panel '{panel_id}': {detail}.", "Put the DCR paths before path('admin/', admin.site.urls)."))
            elif not status["in_installed_apps"]:
                if app_name in flagged_missing:
                    continue
                issues.append(Issue("warning", "panel_not_installed_app", f"Panel '{panel_id}' is registered but '{app_name}' is not in INSTALLED_APPS."))
            elif not status["urls_registered"]:
                issues.append(Issue("warning", "panel_urls_missing", f"Panel '{panel_id}' is registered but its URLs are not included.", f"Add path('admin/{app_name.replace('_', '-')}/', include('{app_name}.urls'))."))
        info["panels_registered"] = panel_rows

    from django.core import checks

    for message in checks.run_checks():
        if message.level >= checks.ERROR:
            level = "error" if (message.id or "").startswith("dj_control_room") else "warning"
            issues.append(Issue(level, f"check_{message.id}", f"manage.py check: {message.msg}", message.hint or ""))

    return issues, info


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check that Django Control Room is wired into a Django project.")
    parser.add_argument("--project-dir", type=Path, default=Path.cwd(), help="directory containing manage.py (default: cwd)")
    parser.add_argument("--settings", help="settings module, e.g. myproject.settings")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    project_dir = args.project_dir.resolve()
    settings_module = find_settings_module(project_dir, args.settings)
    if not settings_module:
        print("Could not find the settings module. Pass --settings or set DJANGO_SETTINGS_MODULE.", file=sys.stderr)
        return 2

    try:
        issues, info = run(project_dir, settings_module)
    except ImportError as exc:
        print(f"Could not load the project ({settings_module}): {exc}", file=sys.stderr)
        print("Run this with the project's environment. Is Django, or dj-control-room, installed there?", file=sys.stderr)
        return 2
    except Exception as exc:  # settings that fail to import, bad INSTALLED_APPS, and so on
        print(f"Could not load the project ({settings_module}): {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]

    if args.json:
        print(json.dumps({"info": info, "issues": [i.as_dict() for i in issues]}, indent=2))
    else:
        print(f"settings   {info['settings_module']}")
        print(f"python     {info['python']}    django {info['django']}")
        if info.get("dashboard_url"):
            print(f"dashboard  {info['dashboard_url']}")
        for row in info.get("panels_registered", []):
            print(f"panel      {row['id']:28} {'ready' if row['configured'] else 'NOT READY'}")
        for issue in issues:
            print(f"{issue.level.upper():7} {issue.code}: {issue.message}")
            if issue.hint:
                print(f"        {issue.hint}")
        print(f"{len(errors)} error(s), {len(warnings)} warning(s)")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
