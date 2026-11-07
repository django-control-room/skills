#!/usr/bin/env python3
"""Check that the plugin manifests agree before tagging a release.

The same plugin is described in three places:

- plugin.json                      Agent Plugins manifest (Codex, Cursor, others)
- .claude-plugin/plugin.json       Claude Code manifest
- .claude-plugin/marketplace.json  Claude Code / Codex marketplace catalog

Name, version, and description must match, and every referenced asset must
exist. It also checks that each skill's name matches its folder and that every
relative link inside skills/ resolves. Exit code 1 on any problem. Standard
library only.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(rel):
    return json.loads((ROOT / rel).read_text())


def main():
    agent = load("plugin.json")
    claude = load(".claude-plugin/plugin.json")
    market = load(".claude-plugin/marketplace.json")
    entries = [p for p in market["plugins"] if p["name"] == agent["name"]]

    errors = []
    for field in ("name", "version", "description"):
        if agent.get(field) != claude.get(field):
            errors.append(
                f"{field}: plugin.json={agent.get(field)!r} "
                f".claude-plugin/plugin.json={claude.get(field)!r}"
            )
    if len(entries) != 1:
        errors.append(f"marketplace.json must list {agent['name']!r} exactly once")
    elif entries[0].get("description") != agent["description"]:
        errors.append("description: marketplace.json entry differs from plugin.json")

    interface = agent.get("extensions", {}).get("com.openai.interface", {})
    assets = [claude.get("icon")] + [
        interface.get(k) for k in ("logo", "composerIcon", "logoDark", "composerIconDark")
    ]
    for asset in filter(None, assets):
        if not (ROOT / asset).is_file():
            errors.append(f"missing asset: {asset}")

    errors += check_skills()

    for error in errors:
        print(f"ERROR {error}")
    if not errors:
        print(f"OK {agent['name']} {agent['version']}: manifests agree, skills and links resolve")
    return 1 if errors else 0


def check_skills():
    """Each skill's name matches its folder, and every relative link resolves."""
    errors = []
    skill_files = sorted((ROOT / "skills").glob("*/SKILL.md"))
    for skill_file in skill_files:
        match = re.search(r"^name:\s*(\S+)", skill_file.read_text(), re.MULTILINE)
        if not match or match.group(1) != skill_file.parent.name:
            errors.append(f"{skill_file.relative_to(ROOT)}: name must be {skill_file.parent.name!r}")
    for markdown_file in sorted((ROOT / "skills").rglob("*.md")):
        for target in re.findall(r"\]\(([^)\s]+)\)", markdown_file.read_text()):
            if re.match(r"[a-z]+:|#", target):
                continue
            if not (markdown_file.parent / target.split("#")[0]).exists():
                errors.append(f"{markdown_file.relative_to(ROOT)}: broken link {target}")
    return errors


if __name__ == "__main__":
    sys.exit(main())
