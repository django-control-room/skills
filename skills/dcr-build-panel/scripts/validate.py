#!/usr/bin/env python3
"""Static checks for a DCR panel package produced by dcr-build-panel.

Usage:
    python scripts/validate.py /path/to/dj-webhook-failures-panel

Does not import Django. Exits 1 if any error is found.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILLS_IMPORT = re.compile(
    r"(?:from|import)\s+(?:skills|dcr_build_panel|dcr-build-panel)\b"
)
PERMISSION = re.compile(r"permission_required\s*\(")
GET_CONTEXT = re.compile(r"panel_config\.get_context\s*\(")
AGENT_SCOPE = re.compile(r'scope\s*=\s*"agent_')
VIEW_DEF = re.compile(r"^def\s+\w+\s*\(\s*request", re.M)


class Issue:
    def __init__(self, level: str, code: str, message: str, path: str = ""):
        self.level = level
        self.code = code
        self.message = message
        self.path = path

    def as_dict(self) -> dict:
        return {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "path": self.path,
        }


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _find_package_dir(project_dir: Path) -> Path | None:
    candidates = [
        p for p in project_dir.iterdir()
        if p.is_dir() and (p / "panel.py").is_file() and (p / "conf.py").is_file()
    ]
    return candidates[0] if len(candidates) == 1 else None


def validate(project_dir: Path) -> list[Issue]:
    issues: list[Issue] = []
    project_dir = project_dir.resolve()

    if not (project_dir / "pyproject.toml").is_file():
        issues.append(Issue("error", "not_a_package", "No pyproject.toml — is this a baked panel?", str(project_dir)))
        return issues

    pyproject = _read(project_dir / "pyproject.toml")
    if "dj-control-room-base" not in pyproject and "dj_control_room_base" not in pyproject:
        issues.append(Issue(
            "error", "missing_dcr_base",
            "pyproject.toml must depend on dj-control-room-base.",
            "pyproject.toml",
        ))
    if re.search(r"skills\s*@|django-control-room/skills", pyproject):
        issues.append(Issue(
            "error", "skills_runtime_dep",
            "The generated package must not depend on the skills repository.",
            "pyproject.toml",
        ))

    package_dir = _find_package_dir(project_dir)
    if package_dir is None:
        issues.append(Issue(
            "error", "no_package",
            "Expected exactly one directory containing panel.py and conf.py.",
            str(project_dir),
        ))
        return issues

    for rel in ("panel.py", "conf.py", "views.py", "urls.py", "tools.py"):
        if not (package_dir / rel).is_file():
            issues.append(Issue("error", "missing_file", f"Missing {rel}.", str(package_dir / rel)))

    for path in package_dir.rglob("*.py"):
        text = _read(path)
        if SKILLS_IMPORT.search(text):
            issues.append(Issue(
                "error", "skills_import",
                "Do not import from the skills repository. Depend on dj-control-room-base.",
                str(path.relative_to(project_dir)),
            ))

    views = _read(package_dir / "views.py")
    if views:
        if VIEW_DEF.search(views) and not PERMISSION.search(views):
            issues.append(Issue(
                "error", "no_permission_required",
                "Views must use @panel_config.permission_required(scope).",
                f"{package_dir.name}/views.py",
            ))
        if "render(" in views and not GET_CONTEXT.search(views):
            issues.append(Issue(
                "error", "no_get_context",
                "Build template context with panel_config.get_context(request, ...).",
                f"{package_dir.name}/views.py",
            ))
        if 'permission_required("index")' in views or "permission_required('index')" in views:
            issues.append(Issue(
                "warning", "stub_index_scope",
                'Replace the Cookiecutter "index" scope with a descriptive name.',
                f"{package_dir.name}/views.py",
            ))

    tools = _read(package_dir / "tools.py")
    if tools:
        if "hello_world" in tools or "handle_hello_world" in tools:
            issues.append(Issue(
                "warning", "hello_world_stub",
                "Replace or delete the hello_world Cookiecutter stub.",
                f"{package_dir.name}/tools.py",
            ))
        if "@registry.register" in tools and not AGENT_SCOPE.search(tools):
            issues.append(Issue(
                "error", "missing_agent_scope",
                'MCP tools must use scope="agent_...".',
                f"{package_dir.name}/tools.py",
            ))

    conf = _read(package_dir / "conf.py")
    if conf and "tool_registry" not in conf and "tools=" not in conf:
        issues.append(Issue(
            "warning", "tools_not_wired",
            "conf.py should pass tools=tool_registry.tools to PanelConfig.",
            f"{package_dir.name}/conf.py",
        ))

    templates = package_dir / "templates" / "admin" / package_dir.name
    if templates.is_dir():
        for html in templates.rglob("*.html"):
            text = _read(html)
            rel = str(html.relative_to(project_dir))
            if re.search(r'class="[^"]*\bbutton\b', text):
                issues.append(Issue(
                    "warning", "admin_button_class",
                    "Use dcr-btn, not Django admin .button. See references/design-system.md.",
                    rel,
                ))
            if html.name == "index.html":
                if "panel-welcome" in text or "welcome_graphic" in text:
                    issues.append(Issue(
                        "warning", "welcome_stub",
                        "index.html still looks like the Cookiecutter welcome page.",
                        rel,
                    ))
                if "dcr-page-header" not in text:
                    issues.append(Issue(
                        "warning", "missing_dcr_header",
                        "List page should use dcr-page-header. See references/design-system.md.",
                        rel,
                    ))

    styles = package_dir / "static" / package_dir.name / "css" / "styles.css"
    if styles.is_file():
        css = _read(styles)
        if "DJ CONTROL ROOM - Design System" in css or "--dcr-color-text:" in css:
            issues.append(Issue(
                "error", "copied_design_system",
                "Do not copy design-system.css into the panel. Extend panel_base.html.",
                str(styles.relative_to(project_dir)),
            ))
        elif re.search(r"#[0-9a-fA-F]{3,8}\b", css) and "panel-welcome" not in css:
            issues.append(Issue(
                "warning", "hardcoded_color",
                "Panel CSS should use var(--dcr-*) tokens, not hex colours.",
                str(styles.relative_to(project_dir)),
            ))

    scopes_doc = _read(project_dir / "docs" / "scopes.md")
    if "agent_hello_world" in scopes_doc or (
        "`index`" in scopes_doc and "hello_world" in scopes_doc
    ):
        issues.append(Issue(
            "warning", "stub_scopes_doc",
            "docs/scopes.md still documents Cookiecutter stub scopes.",
            "docs/scopes.md",
        ))

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a baked DCR panel package.")
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if not args.project_dir.is_dir():
        print(f"Not a directory: {args.project_dir}", file=sys.stderr)
        return 2

    issues = validate(args.project_dir)
    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]

    if args.json:
        print(json.dumps([i.as_dict() for i in issues], indent=2))
    else:
        if not issues:
            print(f"OK  {args.project_dir}")
        for issue in issues:
            loc = f"  ({issue.path})" if issue.path else ""
            print(f"{issue.level.upper():7} {issue.code}: {issue.message}{loc}")
        print(f"{len(errors)} error(s), {len(warnings)} warning(s)")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
