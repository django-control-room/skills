# Trigger evals

The per-skill evals check what a skill produces once it has loaded. These check whether the **right skill loads at all** when the user does not use DCR vocabulary. Most real requests say "tool", "page", or "dashboard", not "panel".

## Setup

Install all five skills and `common/` (see the top-level README), in a Django project for the context named in each row:

| Context | Meaning |
|---|---|
| **A** | `dj-control-room` and `dj-control-room-base` installed, no panels yet |
| **B** | As A, plus at least one panel (for example `dcr_app_packages`) |
| **C** | A Django project without DCR |

Run each prompt in a **fresh chat**, three times, because skill selection is not deterministic. Record which skill the agent read first.

Run the whole set twice: once without [`project-rule/dcr.mdc`](../project-rule/dcr.mdc) and once with it installed as a project rule. The difference is the rule's value.

## Scoring

- **Should load**: passes in at least 2 of 3 runs.
- **Must not load**: passes only if it never loads in 3 runs.
- **Either**: both outcomes pass, but a DCR skill that loads must not scaffold or add a dependency without the user agreeing.

`dcr-guide` counts as correct for any "should load" row, as long as it then hands off to the expected skill. A row listing `dcr-guide` as the expectation means the agent should ask the routing question rather than guess.

## Plain-language requests that should load a skill

| # | Context | Prompt | Expected |
|---|---|---|---|
| 1 | A | I want to create a tool so support can look up a customer's failed webhooks. | `dcr-guide` → `dcr-create-internal-panel` |
| 2 | A | Build me an admin page that shows queue depth and lets ops retry stuck jobs. | `dcr-guide` → `dcr-create-internal-panel` |
| 3 | A | Add a dashboard for our feature flags. | `dcr-guide` → `dcr-create-internal-panel` |
| 4 | A | We need a staff-only screen to search invoices by customer email. | `dcr-guide` → `dcr-create-internal-panel` |
| 5 | A | Make a tool for the team to look up which Django settings are set. | `dcr-guide` → `dcr-create-internal-panel` |
| 6 | A | Add a DCR panel that lists installed Python packages. | `dcr-create-internal-panel` |
| 7 | A | I want to build a control room panel that other teams can pip install. | `dcr-create-package-panel` |
| 8 | A | Write a plugin for dj-control-room that shows S3 bucket sizes. I'll publish it to PyPI. | `dcr-create-package-panel` |
| 9 | B | Add a retry button to the webhook failures page. | `dcr-modify-panel` |
| 10 | B | Let me filter the cache panel by key prefix. | `dcr-modify-panel` |
| 11 | B | Make it possible to hide pip and setuptools from the packages list. | `dcr-modify-panel` |
| 12 | B | Let AI agents search the app packages. | `dcr-modify-panel` (adds an MCP tool) |
| 13 | B | The packages page lists some packages twice. Fix it. | `dcr-modify-panel` |
| 14 | B | Add a detail page for each package. | `dcr-modify-panel` |
| 15 | A | I want a tool to do reporting for the team. | `dcr-guide`, asks what the tool should do |
| 16 | A | Build a tool for managing our feature flags that we can reuse across our other apps. | `dcr-guide` → `dcr-create-package-panel`, or asks the one routing question |

## Must not load a DCR skill

These are not staff UI jobs, or they are a different DCR concept. Run them in contexts A and B.

| # | Prompt |
|---|---|
| 17 | Write a management command that deletes expired sessions. |
| 18 | Add a ModelAdmin action that marks selected orders as shipped. |
| 19 | Create a script that exports all users to CSV. |
| 20 | Add a REST endpoint that returns open orders. |
| 21 | Add a Celery task that emails a weekly report. |
| 22 | Build an MCP server that answers questions about our docs. |

Row 22 matters because "MCP" appears in DCR's own vocabulary. A standalone MCP server is not a panel.

## Project without DCR

| # | Context | Prompt | Expected |
|---|---|---|---|
| 23 | C | I want a tool for support to look up customer webhooks. | Either |
| 24 | C | Build a Django Control Room panel that shows our cache keys. | `dcr-guide` → `dcr-setup`, then `dcr-create-internal-panel`. It must say DCR is not installed and ask before setting it up. It must not scaffold a panel first |
| 25 | C | Add a custom admin page for sales reports. | Either |

## Installing and fixing a setup

| # | Context | Prompt | Expected |
|---|---|---|---|
| 26 | C | Set up Django Control Room in this project. | `dcr-setup` |
| 27 | C | How do I get started with dj-control-room? | `dcr-setup` |
| 28 | C | Add a control room dashboard to my Django admin. | `dcr-setup`, or `dcr-guide` → `dcr-setup` |
| 29 | A | I get `'dcr_icons' is not a registered tag library`. | `dcr-setup` |
| 30 | B | I installed the cache panel but it doesn't show on the dashboard. | `dcr-setup` |
| 31 | A | Install dj-control-room with the redis and celery panels. | `dcr-setup`, without asking which panels |

Row 30 is easy to mistake for a modify request. Nothing in the panel's code is wrong; the wiring is.

## When a row fails

| Symptom | Likely fix |
|---|---|
| Plain-language rows 1–5 never load a skill | Add the user's words to the `description` of `dcr-guide`. Keep it within 1024 characters |
| Rows 17–22 load a skill | The description is too broad. Tighten it, and add the case to "not a DCR job" in `dcr-guide` |
| Row 12 loads `dcr-create-internal-panel` | "Agent tool" is being read as "new panel". Strengthen the MCP-tool row in the glossary of `dcr-guide` and in `dcr-modify-panel`'s description |
| Rows 26–31 load a create or modify skill | `dcr-setup`'s description lacks the user's words ("set up", "get started", "doesn't show up"), or `dcr-modify-panel` claims too much |
| Rows 9–14 load a create skill | `dcr-modify-panel`'s description does not say "already exists" strongly enough |
| Selection is fine with the rule installed and poor without it | Expected. Recommend the rule in install docs |
