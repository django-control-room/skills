#!/usr/bin/env python3
"""Check that the plugin manifests agree before tagging a release.

The same plugin is described in three places:

- plugin.json                      Agent Plugins manifest (Codex, Cursor, others)
- .claude-plugin/plugin.json       Claude Code manifest
- .claude-plugin/marketplace.json  Claude Code / Codex marketplace catalog

Name, version, and description must match, and every referenced asset must
exist. Exit code 1 on any mismatch. Standard library only.
"""

import json
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

    for error in errors:
        print(f"ERROR {error}")
    if not errors:
        print(f"OK {agent['name']} {agent['version']}: manifests agree")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
