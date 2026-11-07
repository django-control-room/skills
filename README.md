<img src="assets/glyph.png" alt="Django Control Room" width="36" align="left">

# Django Control Room skills


Agent skills for setting up [Django Control Room](https://djangocontrolroom.com) (DCR) in a Django project and building its panels.

Skills are **development-time guidance**. Generated panels depend on DCR packages at runtime (`dj-control-room-base`, and the hub if used). They do not depend on this repository.

## Install

### Claude Code

```
/plugin install dcr --marketplace django-control-room/skills
```

That adds the marketplace and installs the plugin in one step (Claude Code 2.1.275 or later). On older versions, run it in two steps:

```
/plugin marketplace add django-control-room/skills
/plugin install dcr@django-control-room
```

Skills appear as `/dcr:dcr-setup`, `/dcr:dcr-guide`, and so on, and load on their own when a request matches.

### Codex

```bash
codex plugin marketplace add django-control-room/skills
codex plugin add dcr@django-control-room
```

### Cursor

Cursor reads the same plugin manifest ([`plugin.json`](plugin.json)). Until the plugin is listed on the Cursor marketplace, copy the skills by hand (see [Copy the skills by hand](#copy-the-skills-by-hand)).

### Gemini CLI, Copilot, and other agents

The [`skills` CLI](https://github.com/vercel-labs/skills) installs to many agents:

```bash
npx skills add django-control-room/skills --skill '*'
```

Install **all** the skills. The create and modify skills read shared docs from the `dcr-reference` skill, and the CLI copies each skill on its own, so leaving `dcr-reference` out gives them dead links. `dcr-setup` works alone.

### Copy the skills by hand

Copy the skill directories from `skills/` into the place your agent loads skills from. Copy `dcr-reference/` too, next to the others, not inside them:

```
.cursor/skills/
  dcr-reference/              # needed by every skill except dcr-setup
  dcr-guide/                  # recommended: routes plain-language requests
  dcr-setup/                  # and/or the other skills below
  dcr-create-package-panel/   # and/or dcr-create-internal-panel/, dcr-modify-panel/
```

| Agent | Location |
|---|---|
| Cursor | `.cursor/skills/` |
| Claude Code | `.claude/skills/` |
| Codex, Gemini CLI, Copilot | `.agents/skills/` |

Keep each skill's `SKILL.md`, `references/`, `scripts/`, and `evals/` together. Every skill except `dcr-setup` links to `../dcr-reference/`. `dcr-guide` also links to its sibling skills, so install it alongside them.

## Skills

| Skill | Use when |
|---|---|
| [`dcr-guide`](skills/dcr-guide/) | The request is in plain language ("a tool / page / dashboard for staff to do X") and you want it routed to the right skill below. Builds nothing itself |
| [`dcr-setup`](skills/dcr-setup/) | DCR is **not installed yet** in the project, or the setup is broken (`dcr_icons` errors, `dj_control_room.E001`, panels missing from the dashboard). Installs, wires, and verifies. Does not create panels |
| [`dcr-create-package-panel`](skills/dcr-create-package-panel/) | You want a **reusable panel package** (PyPI, private wheel, or a repo installed into one or more Django projects) |
| [`dcr-create-internal-panel`](skills/dcr-create-internal-panel/) | You want a **new Django app** in the current project (no packaging, Docker, MkDocs, or example project). Never nested inside another app |
| [`dcr-modify-panel`](skills/dcr-modify-panel/) | You want to **change or add a feature to a panel that already exists**: a page, column, search, action, MCP tool, setting, or scope. Works on packages and internal apps |

[`dcr-reference`](skills/dcr-reference/) is not a skill you invoke. It holds the shared docs (pages, lists, search, actions, scopes, MCP tools, design system) that the create and modify skills link to, so install it with them.

If the intended distribution is unclear, the create skills will ask which of those you want rather than guessing.

- `dcr-setup` gets DCR running in a project: dependencies, `INSTALLED_APPS`, URLs, and a `scripts/doctor.py` that checks the result. It leaves scopes and permissions to the user.
- `dcr-guide` is the plain-language front door. People say "a tool for support to look up X", not "a panel". It reads the project and hands off to one of the other skills.
- `dcr-create-package-panel` bakes the [Cookiecutter](https://github.com/django-control-room/cookiecutter-dj-control-room-plugin) template. A human can run `scripts/bake.py` without an agent.
- `dcr-create-internal-panel` runs `python manage.py dcr_startpanel <name>`, a management command from `dj-control-room-base`. It does not use Cookiecutter.
- `dcr-modify-panel` edits either kind in place and checks that existing scopes, URL names, MCP tool names, and settings keys still work. `scripts/inspect_panel.py` lists them and compares against a git ref.

The two `create` skills use an official generator as their scaffolding engine, then implement the requested panel. They do not vendor a second copy of panel templates. The `modify` skill works on a panel that already exists and does not scaffold.

`dcr-create-package-panel` needs [cookiecutter](https://github.com/cookiecutter/cookiecutter) >= 2.0:

```bash
python -m pip install 'cookiecutter>=2.0.0'
```

Then ask the agent, for example:

> Set up Django Control Room in this project with the Redis and cache panels.

> Build a reusable DCR panel that lets me look up the settings of the project it is installed in.

> Add a panel to this Django project that lets me look up the installed Python packages. Do not publish a package.

> In the app packages panel, add a detail page for each package.

> Add an MCP tool to dj-cache-panel that lists keys matching a pattern.

## Add the project rule (recommended)

Skills load only when the agent judges the request relevant. A project rule is read every time, so it is the most reliable way to make "build me a tool for X" reach these skills. The plugin installs do **not** add it, because it should only exist in projects that use DCR. Copy [`project-rule/dcr.mdc`](project-rule/dcr.mdc) into the Django project:

| Agent | Where |
|---|---|
| Cursor | `.cursor/rules/dcr.mdc` (as is) |
| Claude Code | Paste the body, without the frontmatter, into `CLAUDE.md` |
| Other agents | Paste the body into `AGENTS.md` |

## Testing that the right skill loads

[`evals/triggers.md`](evals/triggers.md) lists plain-language prompts, including ones that must **not** load a skill, and how to run them with and without the rule. Each skill's own `evals/` checks what it produces once loaded.

## Releasing

The plugin is described by three manifests that must agree on name, version, and description:

- `plugin.json`: portable [Agent Plugins](https://agent-plugins.org) manifest, used by Codex, Cursor, and others. Listing metadata for the OpenAI directory is under `extensions.com.openai.interface`.
- `.claude-plugin/plugin.json`: Claude Code manifest.
- `.claude-plugin/marketplace.json`: the marketplace catalog. Claude Code reads it, and so does Codex.

To release, bump `version` in both `plugin.json` files, then run:

```bash
python scripts/check_manifests.py
claude plugin validate . --strict --profile directory
```

Commit, tag (`git tag v0.1.0`), and push. Users get the new version the next time they update the plugin.

## Layout

```
plugin.json               # portable plugin manifest (Codex, Cursor, others)
.claude-plugin/
  plugin.json             # Claude Code manifest
  marketplace.json        # marketplace catalog
assets/
  glyph.png               # plugin icon
scripts/
  check_manifests.py      # manifests agree, assets exist
skills/
  dcr-reference/          # shared DCR refs, installed as a skill (sibling of the others)
    SKILL.md              # index of the files below
    actions.md
    design-system.md
    lists.md
    living-examples.md
    mcp-tools.md
    pages.md
    search.md
    scopes.md
  dcr-guide/              # router: SKILL.md only
  dcr-setup/              # SKILL.md, references/troubleshooting.md, scripts/doctor.py, evals/
  dcr-create-package-panel/
  dcr-create-internal-panel/
  dcr-modify-panel/
    SKILL.md              # workflow and which reference to load
    references/           # create skills: scaffolding, tests. modify: change-types, compatibility
    scripts/              # validate.py (package skill also has bake.py); modify has inspect_panel.py; setup has doctor.py
    evals/                # example requests for checking the skill
project-rule/
  dcr.mdc                 # project rule to install in Django projects that use DCR
evals/
  triggers.md             # does the right skill load for plain-language requests?
```
