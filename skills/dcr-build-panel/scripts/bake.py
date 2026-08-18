#!/usr/bin/env python3
"""Non-interactive Cookiecutter wrapper for dcr-build-panel.

Run this instead of composing Cookiecutter flags by hand. Extra context is
passed as --no-input KEY=VALUE pairs so the bake is deterministic.

Examples:

    python scripts/bake.py \\
        --output-dir ~/src \\
        --project-name "Webhook Failures Panel" \\
        --project-slug dj-webhook-failures-panel \\
        --package-name dj_webhook_failures_panel \\
        --project-description "Inspect and retry failed webhook deliveries" \\
        --author-name "Ada Lovelace" \\
        --author-email ada@example.com \\
        --github-username ada \\
        --panel-icon link

    python scripts/bake.py --output-dir . --project-name "Widgets Panel" \\
        --template /path/to/cookiecutter-dj-control-room-plugin
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

OFFICIAL_TEMPLATE = (
    "https://github.com/django-control-room/cookiecutter-dj-control-room-plugin"
)
ICON_CHOICES = ("database", "layers", "link", "chart", "radio", "cog")
LICENSE_CHOICES = ("MIT", "BSD", "Apache-2.0", "GPL-3.0", "No license file")


def _slugify(project_name: str) -> str:
    slug = project_name.lower().replace(" ", "-").replace("_", "-")
    slug = re.sub(r"[^a-z0-9-]+", "", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "panel"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bake a DCR panel package from the official Cookiecutter."
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory in which the new project folder will be created.",
    )
    parser.add_argument("--project-name", required=True)
    parser.add_argument(
        "--project-slug",
        default="",
        help="Defaults to a slug of --project-name. Prefer dj-<topic>-panel.",
    )
    parser.add_argument(
        "--package-name",
        default="",
        help="Defaults to --project-slug with hyphens turned into underscores.",
    )
    parser.add_argument("--project-description", default="")
    parser.add_argument("--author-name", default="")
    parser.add_argument("--author-email", default="")
    parser.add_argument("--github-username", default="")
    parser.add_argument("--version", default="0.1.0")
    parser.add_argument(
        "--django-app-verbose-name",
        default="",
        help="Defaults to --project-name.",
    )
    parser.add_argument("--panel-icon", choices=ICON_CHOICES, default="cog")
    parser.add_argument(
        "--license",
        dest="open_source_license",
        choices=LICENSE_CHOICES,
        default="MIT",
    )
    parser.add_argument(
        "--template",
        default="",
        help=(
            "Cookiecutter template path or URL. Defaults to the official "
            "GitHub repo, or $DCR_COOKIECUTTER_TEMPLATE if set."
        ),
    )
    parser.add_argument(
        "--checkout",
        default="",
        help="Git ref to check out when --template is a git URL.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the destination project directory if it already exists.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the Cookiecutter command and extra context, then exit.",
    )
    parser.add_argument(
        "--no-fix-class",
        action="store_true",
        help=(
            "Do not rename a generated *PanelPanel class. By default the "
            "script shortens it to *Panel in panel.py, pyproject.toml, and "
            "tests/test_panel.py."
        ),
    )
    return parser.parse_args(argv)


def _resolve_template(explicit: str) -> str:
    import os

    if explicit:
        return explicit
    env = os.environ.get("DCR_COOKIECUTTER_TEMPLATE", "").strip()
    if env:
        return env
    return OFFICIAL_TEMPLATE


def _build_context(args: argparse.Namespace) -> dict[str, str]:
    slug = args.project_slug or _slugify(args.project_name)
    package = args.package_name or slug.replace("-", "_")
    description = args.project_description or (
        f"A Django Admin panel: {args.project_name}"
    )
    context = {
        "project_name": args.project_name,
        "project_slug": slug,
        "package_name": package,
        "project_description": description,
        "version": args.version,
        "django_app_verbose_name": args.django_app_verbose_name or args.project_name,
        "panel_icon": args.panel_icon,
        "open_source_license": args.open_source_license,
    }
    if args.author_name:
        context["author_name"] = args.author_name
    if args.author_email:
        context["author_email"] = args.author_email
    if args.github_username:
        context["github_username"] = args.github_username
    return context


def _cookiecutter_cmd(
    template: str, args: argparse.Namespace, context: dict[str, str]
) -> list[str]:
    cmd = [
        sys.executable,
        "-m",
        "cookiecutter",
        template,
        "--no-input",
        "--output-dir",
        str(args.output_dir.resolve()),
    ]
    if args.checkout:
        cmd.extend(["--checkout", args.checkout])
    if args.overwrite:
        cmd.append("--overwrite-if-exists")
    for key, value in context.items():
        cmd.append(f"{key}={value}")
    return cmd


def _find_panel_class(project_dir: Path, package_name: str) -> str | None:
    panel_py = project_dir / package_name / "panel.py"
    if not panel_py.is_file():
        return None
    match = re.search(
        r"^class\s+(\w+)\s*\(", panel_py.read_text(encoding="utf-8"), re.M
    )
    return match.group(1) if match else None


def _fix_doubled_panel_class(
    project_dir: Path, package_name: str, panel_class: str
) -> str:
    """Rename FooPanelPanel → FooPanel in the files Cookiecutter emits."""
    new_class = panel_class[: -len("Panel")]
    targets = [
        project_dir / package_name / "panel.py",
        project_dir / "pyproject.toml",
        project_dir / "tests" / "test_panel.py",
    ]
    for path in targets:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if panel_class not in text:
            continue
        path.write_text(text.replace(panel_class, new_class), encoding="utf-8")
        print(f"Renamed {panel_class} → {new_class} in {path.relative_to(project_dir)}")
    return new_class


def _print_summary(
    project_dir: Path, context: dict[str, str], panel_class: str | None
) -> None:
    print("=" * 70)
    print("Baked DCR panel package")
    print("=" * 70)
    print(json.dumps(
        {
            "project_dir": str(project_dir),
            "context": context,
            "panel_class": panel_class,
        },
        indent=2,
    ))
    if panel_class and panel_class.endswith("PanelPanel"):
        suggested = panel_class[: -len("Panel")]  # FooPanelPanel → FooPanel
        print()
        print(
            f"WARNING: generated class is {panel_class} (template appends 'Panel' "
            f"to project_name). Rename it to {suggested} in panel.py, "
            "pyproject.toml, and tests/test_panel.py before implementing."
        )
    print()
    print("Next: inspect the generated tree, then implement the panel inside it.")
    print("Do not recreate files Cookiecutter already supplied.")
    print("=" * 70)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    template = _resolve_template(args.template)
    context = _build_context(args)
    output_dir = args.output_dir.resolve()
    project_dir = output_dir / context["project_slug"]
    cmd = _cookiecutter_cmd(template, args, context)

    if args.dry_run:
        print(json.dumps({"template": template, "context": context, "cmd": cmd}, indent=2))
        return 0

    if shutil.which("cookiecutter") is None:
        try:
            import cookiecutter  # noqa: F401
        except ImportError:
            print(
                "cookiecutter is not installed. Install with:\n"
                "  python -m pip install 'cookiecutter>=2.0.0'",
                file=sys.stderr,
            )
            return 1

    print("Running:", " ".join(cmd), file=sys.stderr)

    output_dir.mkdir(parents=True, exist_ok=True)
    if project_dir.exists() and not args.overwrite:
        print(
            f"Destination already exists: {project_dir}\n"
            "Pass --overwrite to replace it, or choose a different --output-dir.",
            file=sys.stderr,
        )
        return 1

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        return exc.returncode or 1

    if not project_dir.is_dir():
        print(
            f"Cookiecutter exited 0 but {project_dir} was not created.",
            file=sys.stderr,
        )
        return 1

    panel_class = _find_panel_class(project_dir, context["package_name"])
    if (
        panel_class
        and panel_class.endswith("PanelPanel")
        and not args.no_fix_class
    ):
        panel_class = _fix_doubled_panel_class(
            project_dir, context["package_name"], panel_class
        )
    _print_summary(project_dir, context, panel_class)
    return 0


if __name__ == "__main__":
    sys.exit(main())
