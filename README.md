# Django Control Room skills

Agent skills for building [Django Control Room](https://djangocontrolroom.com) panels.

Skills are **development-time guidance**. Generated tools depend on DCR packages at runtime (`dj-control-room-base`, and the hub if used). They do not depend on this repository.

The official [Cookiecutter](https://github.com/django-control-room/cookiecutter-dj-control-room-plugin) is the scaffolding engine. These skills bake it, then implement the requested tool inside the generated project. They do not vendor a second copy of panel templates.

## Skills

| Skill | Status | Use when |
|---|---|---|
| [`dcr-build-panel`](skills/dcr-build-panel/) | Available | You want a **reusable panel package** (PyPI, private wheel, or a repo installed into one or more Django projects) |
| `dcr-build-internal-tool` | Not yet | You want a DCR-powered tool **inside an existing Django application**, without packaging, Docker, MkDocs, or a separate example project |

If the intended distribution is unclear, the panel skill will ask which of those you want rather than guessing.

## Install

Copy a skill directory from `skills/` into the place your coding agent loads skills from:

| Agent | Location |
|---|---|
| Cursor | `.cursor/skills/dcr-build-panel/` |
| Claude Code | `.claude/skills/dcr-build-panel/` |

Keep `SKILL.md`, `references/`, `scripts/`, and `evals/` together.

`dcr-build-panel` needs [cookiecutter](https://github.com/cookiecutter/cookiecutter) >= 2.0:

```bash
python -m pip install 'cookiecutter>=2.0.0'
```

Then ask the agent to build a panel, for example:

> Build a reusable DCR panel that lists failed webhook deliveries and lets admins retry them.

## Layout

```
skills/
  dcr-build-panel/
    SKILL.md              # workflow and which reference to load
    references/           # DCR knowledge, loaded only when relevant
    scripts/              # bake.py, validate.py
    evals/                # example requests for checking the skill
```
