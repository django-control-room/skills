# Django Control Room skills

Agent skills for building [Django Control Room](https://djangocontrolroom.com) panels.

Skills are **development-time guidance**. Generated panels depend on DCR packages at runtime (`dj-control-room-base`, and the hub if used). They do not depend on this repository.

The two `create` skills use an official generator as their scaffolding engine, then implement the requested panel. They do not vendor a second copy of panel templates. The `modify` skill works on a panel that already exists and does not scaffold.

- `dcr-setup` gets DCR running in a project: dependencies, `INSTALLED_APPS`, URLs, and a `scripts/doctor.py` that checks the result. It leaves scopes and permissions to the user.
- `dcr-create-package-panel` bakes the [Cookiecutter](https://github.com/django-control-room/cookiecutter-dj-control-room-plugin) template. A human can run `scripts/bake.py` without an agent.
- `dcr-create-internal-panel` runs `python manage.py dcr_startpanel <name>`, a management command from `dj-control-room-base`. It does not use Cookiecutter.
- `dcr-guide` is the plain-language front door. People say "a tool for support to look up X", not "a panel". It reads the project and hands off to one of the skills below.
- `dcr-modify-panel` edits either kind in place and checks that existing scopes, URL names, MCP tool names, and settings keys still work. `scripts/inspect_panel.py` lists them and compares against a git ref.

## Skills

| Skill | Status | Use when |
|---|---|---|
| [`dcr-guide`](skills/dcr-guide/) | Available | The request is in plain language ("a tool / page / dashboard for staff to do X") and you want it routed to the right skill below. Builds nothing itself |
| [`dcr-setup`](skills/dcr-setup/) | Available | DCR is **not installed yet** in the project, or the setup is broken (`dcr_icons` errors, `dj_control_room.E001`, panels missing from the dashboard). Installs, wires, and verifies. Does not create panels |
| [`dcr-create-package-panel`](skills/dcr-create-package-panel/) | Available | You want a **reusable panel package** (PyPI, private wheel, or a repo installed into one or more Django projects) |
| [`dcr-create-internal-panel`](skills/dcr-create-internal-panel/) | Available | You want a **new Django app** in the current project (no packaging, Docker, MkDocs, or example project). Never nested inside another app |
| [`dcr-modify-panel`](skills/dcr-modify-panel/) | Available | You want to **change or add a feature to a panel that already exists**: a page, column, search, action, MCP tool, setting, or scope. Works on packages and internal apps |

If the intended distribution is unclear, the create skills will ask which of those you want rather than guessing.

## Install

Copy a skill directory from `skills/` into the place your coding agent loads skills from, **and** copy `skills/common/` next to it (not inside it):

```
.cursor/skills/
  common/
  dcr-guide/                         # recommended: routes plain-language requests
  dcr-setup/                       # and/or the other skills below
  dcr-create-package-panel/          # and/or dcr-create-internal-panel/, dcr-modify-panel/
```

| Agent | Location |
|---|---|
| Cursor | `.cursor/skills/` |
| Claude Code | `.claude/skills/` |

Keep each skill's `SKILL.md`, `references/`, `scripts/`, and `evals/` together. Every skill links to `../common/`. `dcr-guide` also links to its three sibling skills, so install it alongside them. `dcr-setup` needs nothing else, and does not use `common/`.

### Add the project rule (recommended)

Skills load only when the agent judges the request relevant. A project rule is read every time, so it is the most reliable way to make "build me a tool for X" reach these skills. Copy [`rules/dcr.mdc`](rules/dcr.mdc) into the Django project:

| Agent | Where |
|---|---|
| Cursor | `.cursor/rules/dcr.mdc` (as is) |
| Claude Code | Paste the body, without the frontmatter, into `CLAUDE.md` |
| Other agents | Paste the body into `AGENTS.md` |

Only add it to projects that use Django Control Room.

`dcr-create-package-panel` needs [cookiecutter](https://github.com/cookiecutter/cookiecutter) >= 2.0:

```bash
python -m pip install 'cookiecutter>=2.0.0'
```

Then ask the agent to build a panel, for example:

> Build a reusable DCR panel that lets me look up the settings of the project it is installed in.

> Add a panel to this Django project that lets me look up the installed Python packages. Do not publish a package.

> In the app packages panel, add a detail page for each package.

> Add an MCP tool to dj-cache-panel that lists keys matching a pattern.

## Testing that the right skill loads

[`evals/triggers.md`](evals/triggers.md) lists plain-language prompts, including ones that must **not** load a skill, and how to run them with and without the rule. Each skill's own `evals/` checks what it produces once loaded.

## Layout

```
skills/
  common/                 # shared DCR refs (sibling of every skill)
    actions.md
    design-system.md
    lists.md
    living-examples.md
    mcp-tools.md
    pages.md
    search.md
    scopes.md
  dcr-guide/              # router: SKILL.md only
  dcr-setup/            # SKILL.md, references/troubleshooting.md, scripts/doctor.py, evals/
  dcr-create-package-panel/
  dcr-create-internal-panel/
  dcr-modify-panel/
    SKILL.md              # workflow and which reference to load
    references/           # create skills: scaffolding, tests. modify: change-types, compatibility
    scripts/              # validate.py (package skill also has bake.py); modify has inspect_panel.py; install has doctor.py
    evals/                # example requests for checking the skill
rules/
  dcr.mdc                 # project rule to install in Django projects that use DCR
evals/
  triggers.md             # does the right skill load for plain-language requests?
```
