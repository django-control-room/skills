#!/usr/bin/env python3
"""Inspect an existing DCR panel and check a change for breaking its public surface.

Works on a panel package (pyproject.toml with a ``dj_control_room.panels`` entry
point) and on an internal app created by ``dcr_startpanel``.

Usage:
    python scripts/inspect_panel.py PATH                  # what is here?
    python scripts/inspect_panel.py PATH --base HEAD      # what did I break?

PATH is the Django app directory (the one containing panel.py and conf.py), or
the package project root when that has exactly one such directory.

The "public surface" is what other people's configuration and bookmarks depend
on: view scopes, MCP tool names and scopes, URL names, the URL namespace, the
settings key and its default keys, and the entry point name. Anything in
``--base`` that is gone now is reported as BREAKING.

Does not import Django. Exits 1 if --base finds a removed surface item.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

ENTRY_POINT = re.compile(
    r'\[project\.entry-points\."dj_control_room\.panels"\]\s*\n\s*([\w.\-]+)\s*=\s*"([^"]+)"'
)
PANEL_CLASS = re.compile(r"^class\s+(\w+)\(\s*PanelPlugin\s*\)", re.M)

SURFACE_KEYS = (
    "view_scopes",
    "tool_names",
    "tool_scopes",
    "url_names",
    "url_namespace",
    "settings_key",
    "settings_defaults",
    "entry_point",
)
PYPROJECT_KEY = "__pyproject__"


def is_app_dir(path: Path) -> bool:
    return (path / "panel.py").is_file() and (path / "conf.py").is_file()


def find_app_dir(path: Path) -> tuple[Path | None, str]:
    path = path.resolve()
    if path.is_file():
        path = path.parent
    for candidate in (path, *path.parents):
        if is_app_dir(candidate):
            return candidate, ""
        if candidate == candidate.parent:
            break
    if path.is_dir():
        found = sorted(p for p in path.iterdir() if p.is_dir() and is_app_dir(p))
        if len(found) == 1:
            return found[0], ""
        if len(found) > 1:
            names = ", ".join(p.name for p in found)
            return None, f"Several panel apps here ({names}). Pass the app directory."
    return None, "No directory containing panel.py and conf.py found."


def _is_test_file(rel: str) -> bool:
    parts = rel.split("/")
    name = parts[-1]
    return (
        "tests" in parts[:-1]
        or "migrations" in parts[:-1]
        or name.startswith("test_")
        or name in ("tests.py", "conftest.py")
    )


def _call_name(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return ""


def _const_str(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _kw(node: ast.Call, name: str) -> ast.AST | None:
    for kw in node.keywords:
        if kw.arg == name:
            return kw.value
    return None


def surface(files: dict[str, str]) -> tuple[dict[str, set[str]], list[str]]:
    """Extract the public surface from {relative path: source}."""
    out: dict[str, set[str]] = {key: set() for key in SURFACE_KEYS}
    notes: list[str] = []

    for rel, text in files.items():
        if rel == PYPROJECT_KEY:
            match = ENTRY_POINT.search(text)
            if match:
                out["entry_point"].add(f"{match.group(1)} = {match.group(2)}")
            continue
        if not rel.endswith(".py") or _is_test_file(rel):
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            notes.append(f"{rel}: could not parse; surface from this file is missing")
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and rel.endswith("urls.py"):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "app_name":
                        value = _const_str(node.value)
                        if value:
                            out["url_namespace"].add(value)
            if not isinstance(node, ast.Call):
                continue
            name = _call_name(node)

            if name == "permission_required" and node.args:
                scope = _const_str(node.args[0])
                if scope:
                    out["view_scopes"].add(scope)
                else:
                    notes.append(f"{rel}:{node.lineno}: permission_required() scope is not a string literal")

            elif name == "register" and _kw(node, "scope") is not None:
                scope = _const_str(_kw(node, "scope"))
                tool = _const_str(_kw(node, "name"))
                if scope:
                    out["tool_scopes"].add(scope)
                if tool:
                    out["tool_names"].add(tool)

            elif name in ("path", "re_path") and rel.endswith("urls.py"):
                url_name = _const_str(_kw(node, "name"))
                if url_name:
                    out["url_names"].add(url_name)

            elif name == "PanelConfig":
                key = _const_str(_kw(node, "settings_key"))
                if key:
                    out["settings_key"].add(key)
                defaults = _kw(node, "defaults")
                if isinstance(defaults, ast.Dict):
                    for k in defaults.keys:
                        value = _const_str(k)
                        if value:
                            out["settings_defaults"].add(value)

    return out, notes


def read_working_tree(app_dir: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in app_dir.rglob("*.py"):
        files[path.relative_to(app_dir).as_posix()] = path.read_text(encoding="utf-8", errors="replace")
    pyproject = app_dir.parent / "pyproject.toml"
    if pyproject.is_file():
        files[PYPROJECT_KEY] = pyproject.read_text(encoding="utf-8", errors="replace")
    return files


def _git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def read_git_ref(app_dir: Path, ref: str) -> tuple[dict[str, str], bool]:
    """Return (files at ref, app existed at ref)."""
    top = Path(_git(["rev-parse", "--show-toplevel"], app_dir).strip()).resolve()
    rel = app_dir.resolve().relative_to(top).as_posix()
    names = _git(["ls-tree", "-r", "--name-only", ref, "--", rel], top).splitlines()
    files: dict[str, str] = {}
    prefix = f"{rel}/" if rel != "." else ""
    for name in names:
        if name.endswith(".py"):
            files[name[len(prefix):]] = _git(["show", f"{ref}:{name}"], top)
    parent_rel = Path(rel).parent.as_posix()
    pyproject_path = "pyproject.toml" if parent_rel == "." else f"{parent_rel}/pyproject.toml"
    try:
        files[PYPROJECT_KEY] = _git(["show", f"{ref}:{pyproject_path}"], top)
    except RuntimeError:
        pass
    return files, bool(names)


def describe(app_dir: Path, files: dict[str, str]) -> dict:
    panel_src = files.get("panel.py", "")
    conf_src = files.get("conf.py", "")
    apps_src = files.get("apps.py", "")

    if ENTRY_POINT.search(files.get(PYPROJECT_KEY, "")):
        mode = "package"
    elif "registry.register" in apps_src:
        mode = "internal"
    else:
        mode = "unknown"

    template_dir = app_dir / "templates"
    templates = sorted(p.relative_to(app_dir).as_posix() for p in template_dir.rglob("*.html")) if template_dir.is_dir() else []
    panel_base = any(
        "dj_control_room_base/panel_base.html" in p.read_text(encoding="utf-8", errors="replace")
        for p in template_dir.rglob("*.html")
    ) if template_dir.is_dir() else False

    tests: list[str] = []
    tests_dir = app_dir.parent / "tests" if mode == "package" else app_dir / "tests"
    if tests_dir.is_dir():
        tests = sorted(p.name for p in tests_dir.glob("test_*.py"))
    elif (app_dir / "tests.py").is_file():
        tests = ["tests.py"]

    scopes_doc = next(
        (str(p.relative_to(app_dir.parent)) for p in (app_dir / "scopes.md", app_dir.parent / "docs" / "scopes.md") if p.is_file()),
        None,
    )

    return {
        "app_dir": str(app_dir),
        "app_label": app_dir.name,
        "mode": mode,
        "panel_class": (PANEL_CLASS.search(panel_src).group(1) if PANEL_CLASS.search(panel_src) else None),
        "uses_panel_config": "PanelConfig" in conf_src and "dj_control_room_base" in conf_src,
        "extends_panel_base": panel_base,
        "has_features": "features" in panel_src,
        "has_tools_py": "tools.py" in files,
        "templates": templates,
        "tests": tests,
        "scopes_doc": scopes_doc,
    }


def diff_surface(base: dict[str, set[str]], cur: dict[str, set[str]]) -> tuple[dict, dict]:
    removed = {k: sorted(base[k] - cur[k]) for k in SURFACE_KEYS if base[k] - cur[k]}
    added = {k: sorted(cur[k] - base[k]) for k in SURFACE_KEYS if cur[k] - base[k]}
    return removed, added


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect a DCR panel and compare its public surface to a git ref.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--base", metavar="REF", help="git ref to compare against (e.g. HEAD, main)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    app_dir, problem = find_app_dir(args.path)
    if app_dir is None:
        print(problem, file=sys.stderr)
        return 2

    files = read_working_tree(app_dir)
    info = describe(app_dir, files)
    cur, notes = surface(files)
    report: dict = {**info, "surface": {k: sorted(v) for k, v in cur.items()}, "notes": notes}

    removed: dict = {}
    if args.base:
        try:
            base_files, existed = read_git_ref(app_dir, args.base)
        except (RuntimeError, ValueError, OSError) as exc:
            print(f"Could not read {args.base}: {exc}", file=sys.stderr)
            return 2
        base_surface, base_notes = surface(base_files)
        removed, added = diff_surface(base_surface, cur)
        report["base"] = {
            "ref": args.base,
            "app_existed": existed,
            "removed": removed,
            "added": added,
            "notes": base_notes,
        }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"{info['app_label']}  ({info['mode']})  {info['app_dir']}")
        print(f"  panel class        {info['panel_class'] or '-'}")
        print(f"  PanelConfig        {'yes' if info['uses_panel_config'] else 'NO (legacy conf)'}")
        print(f"  panel_base.html    {'yes' if info['extends_panel_base'] else 'NO (legacy base template)'}")
        print(f"  features listed    {'yes' if info['has_features'] else 'no'}")
        print(f"  tools.py           {'yes' if info['has_tools_py'] else 'no'}")
        print(f"  scopes doc         {info['scopes_doc'] or 'none'}")
        print(f"  tests              {', '.join(info['tests']) or 'none'}")
        print(f"  templates          {len(info['templates'])}")
        print("  public surface")
        for key in SURFACE_KEYS:
            values = report["surface"][key]
            print(f"    {key:18} {', '.join(values) if values else '-'}")
        for note in notes:
            print(f"  note: {note}")
        if args.base:
            base = report["base"]
            print(f"  vs {base['ref']}")
            if not base["app_existed"]:
                print("    app does not exist at that ref; nothing can be broken")
            for key, values in base["removed"].items():
                print(f"    BREAKING  removed {key}: {', '.join(values)}")
            for key, values in base["added"].items():
                print(f"    added     {key}: {', '.join(values)}")
            if not base["removed"] and not base["added"]:
                print("    surface unchanged")

    return 1 if removed else 0


if __name__ == "__main__":
    sys.exit(main())
