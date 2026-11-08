# Trigger evals

The per-skill evals check what a skill produces once it has loaded. These check whether the **right skill loads at all**. Most real requests never say "DCR" or "panel": they say "a tool for support", "a billing page", "an approval workflow", or "a dashboard". Equally important, ordinary Django work must not pull DCR in.

## Setup

Install all seven skills, including `dcr-reference` (see the top-level README), in a Django project for the context named in each row:

| Context | Meaning |
|---|---|
| **A** | `dj-control-room` and `dj-control-room-base` installed, no panels yet |
| **B** | As A, plus at least one panel (for example `dcr_app_packages`, a webhook failures panel) |
| **C** | A Django project without DCR |

Run each prompt in a **fresh chat**, three times, because skill selection is not deterministic. Record which skill the agent read first, and what it did next.

Run the whole set twice: once without [`project-rule/dcr.mdc`](../project-rule/dcr.mdc) and once with it installed as a project rule. The difference is the rule's value.

## Scoring

- **Should load**: passes in at least 2 of 3 runs.
- **Must not load**: passes only if no DCR skill loads in 3 runs.
- **Either**: both outcomes pass, but a DCR skill that loads must not scaffold or add a dependency without the user agreeing.

`django-internal-tools` counts as correct for any "should load" row, as long as it then hands off to the expected skill. A row listing `django-internal-tools` as the expectation means the agent should ask the routing question rather than guess.

`dcr-reference` must never be the first skill read for any prompt in this file. It is loaded only through the other skills' links. If it loads first, tighten its description.

## 1. Plain-language requests, no DCR vocabulary

| # | Context | Prompt | Expected |
|---|---|---|---|
| 1 | A | Build a tool for support to look up a customer by email and see their recent orders. | `django-internal-tools` → `dcr-create-internal-panel` |
| 2 | A | I want to create a tool so support can look up a customer's failed webhooks. | `django-internal-tools` → `dcr-create-internal-panel` |
| 3 | A | We need a billing operations console: failed payments, refunds in progress, and a button to retry a charge. | `django-internal-tools` → `dcr-create-internal-panel` |
| 4 | A | Add a staff approval workflow for refund requests over $500: a queue with approve and reject buttons. | `django-internal-tools` → `dcr-create-internal-panel` |
| 5 | A | Build an ops dashboard that shows queue depth, worker status, and lets ops retry stuck jobs. | `django-internal-tools` → `dcr-create-internal-panel` |
| 6 | A | Add a dashboard for our feature flags. | `django-internal-tools` → `dcr-create-internal-panel` |
| 7 | A | We need a staff-only screen to search invoices by customer email. | `django-internal-tools` → `dcr-create-internal-panel` |
| 8 | A | Make a tool for the team to look up which Django settings are set. | `django-internal-tools` → `dcr-create-internal-panel` |

## 2. Explicit DCR requests

| # | Context | Prompt | Expected |
|---|---|---|---|
| 9 | A | Add a DCR panel that lists installed Python packages. | `dcr-create-internal-panel` |
| 10 | A | I want to build a control room panel that other teams can pip install. | `dcr-create-package-panel` |
| 11 | A | Write a plugin for dj-control-room that shows S3 bucket sizes. I'll publish it to PyPI. | `dcr-create-package-panel` |

## 3. Reusable package, no DCR vocabulary

| # | Context | Prompt | Expected |
|---|---|---|---|
| 12 | A | Build a support lookup tool we can pip install into all five of our Django services. | `django-internal-tools` → `dcr-create-package-panel` |
| 13 | A | Package our feature-flag admin tool so other teams can install it from our private index. | `django-internal-tools` → `dcr-create-package-panel` |

## 4. Adding to a tool that already exists

| # | Context | Prompt | Expected |
|---|---|---|---|
| 14 | B | Add a retry button to the webhook failures page. | `dcr-modify-panel` |
| 15 | B | Let me filter the cache panel by key prefix. | `dcr-modify-panel` |
| 16 | B | Make it possible to hide pip and setuptools from the packages list. | `dcr-modify-panel` |
| 17 | B | Let AI agents search the app packages. | `dcr-modify-panel` (adds an MCP tool), and its report points to `dcr-access` if the endpoint is off |
| 18 | B | The packages page lists some packages twice. Fix it. | `dcr-modify-panel` |
| 19 | B | Add a detail page for each package. | `dcr-modify-panel` |

## 5. Ambiguous requests

| # | Context | Prompt | Expected |
|---|---|---|---|
| 20 | A | I want a tool to do reporting for the team. | `django-internal-tools`, asks what the tool should do |
| 21 | A | Build a tool for managing our feature flags that we can reuse across our other apps. | `django-internal-tools` → `dcr-create-package-panel`, or asks the one routing question |
| 22 | A | Add a page where finance can review payouts. | `django-internal-tools` → `dcr-create-internal-panel`, or asks one project or many |
| 23 | C | I want a tool for support to look up customer webhooks. | Either |
| 24 | C | Add a custom admin page for sales reports. | Either |

## 6. Must not load a DCR skill

Run these in contexts A and B. They are ordinary Django work, public pages, a different DCR concept, or an explicit choice of something else.

| # | Prompt | Why |
|---|---|---|
| 25 | Add `list_filter` on status and a search box for customer email to the `Order` admin. | Ordinary ModelAdmin customization |
| 26 | Add a ModelAdmin action that marks selected orders as shipped. | Ordinary ModelAdmin action |
| 27 | Add a customer-facing page where users can see their invoices and download PDFs. | Public-facing, not staff |
| 28 | Build the support lookup page as a plain custom Django admin view. Don't add any packages. | Explicitly another approach |
| 29 | Build our ops dashboard in Streamlit. | Explicitly another framework |
| 30 | Write a management command that deletes expired sessions. | Not a page |
| 31 | Create a script that exports all users to CSV. | Not a page |
| 32 | Add a REST endpoint that returns open orders. | Not a page |
| 33 | Add a Celery task that emails a weekly report. | Not a page |
| 34 | Build an MCP server that answers questions about our docs. | "MCP" appears in DCR's vocabulary, but a standalone MCP server is not a panel |

## 7. Project without DCR

| # | Context | Prompt | Expected |
|---|---|---|---|
| 35 | C | Build a Django Control Room panel that shows our cache keys. | `django-internal-tools` → `dcr-setup`, then `dcr-create-internal-panel`. It must say DCR is not installed and ask before setting it up. It must not scaffold a panel first |
| 36 | C | Build an internal billing operations console in our Django admin. | `django-internal-tools`. It must say DCR is not installed and ask before adding it; a plain admin view is also acceptable if the user declines |

## 8. Installing and fixing a setup

| # | Context | Prompt | Expected |
|---|---|---|---|
| 37 | C | Set up Django Control Room in this project. | `dcr-setup` |
| 38 | C | How do I get started with dj-control-room? | `dcr-setup` |
| 39 | C | Add a control room dashboard to my Django admin. | `dcr-setup`, or `django-internal-tools` → `dcr-setup` |
| 40 | A | I get `'dcr_icons' is not a registered tag library`. | `dcr-setup` |
| 41 | B | I installed the cache panel but it doesn't show on the dashboard. | `dcr-setup` |
| 42 | A | Install dj-control-room with the redis and celery panels. | `dcr-setup`, without asking which panels |

Row 41 is easy to mistake for a modify request. Nothing in the panel's code is wrong; the wiring is.

## 9. Who can use a tool, and agent access

Context B here also has an internal `dcr_refunds` panel with scopes `refund_list`, `refund_approve`, and `agent_refund_list`.

| # | Context | Prompt | Expected |
|---|---|---|---|
| 43 | B | Only the finance team should be able to approve refunds. | `dcr-access` (settings only, no panel code) |
| 44 | B | Lock the cache panel down to superusers. | `dcr-access` |
| 45 | B | Why does someone on support get a 403 on the refunds page? | `dcr-access` |
| 46 | B | Let Claude Code look up refunds through the control room. | `dcr-access` (a tool exists: turn on the MCP endpoint) |
| 47 | B | Let AI agents retry failed webhooks. | `dcr-modify-panel` (no such tool yet), then `dcr-access` |
| 48 | B | Add a `refund_export` permission scope to the refunds panel's export view. | `dcr-modify-panel` (a code change, not settings) |

Row 47 differs from row 17 only in where it ends: a new tool is useless until the endpoint is on.

## When a row fails

| Symptom | Likely fix |
|---|---|
| Section 1 or 3 rows never load a skill | Add the user's words to the `description` of `django-internal-tools`. Keep it within 1024 characters |
| Section 1 rows load `dcr-create-internal-panel` directly in context C and it scaffolds | The internal skill's description is too broad. It should require a project that already uses DCR |
| Section 6 rows load a skill | The description is too broad. Tighten it, and add the case to "Not a DCR job" in `django-internal-tools` and in the project rule |
| Rows 28–29 load a skill only with the rule installed | The rule overrides an explicit choice. Strengthen its "another framework" sentence |
| Row 17 loads `dcr-create-internal-panel` | "Agent tool" is being read as "new panel". Strengthen the MCP-tool row in the glossary of `django-internal-tools` and in `dcr-modify-panel`'s description |
| Rows 43–46 load `dcr-modify-panel` or `dcr-setup` | `dcr-access`'s description lacks the user's words ("only X can", "403", "let Claude"), or the others claim permissions |
| Row 48 loads `dcr-access` | It is claiming code changes. Its description must say "settings only" |
| Section 8 rows load a create or modify skill | `dcr-setup`'s description lacks the user's words ("set up", "get started", "doesn't show up"), or `dcr-modify-panel` claims too much |
| Section 4 rows load a create skill | `dcr-modify-panel`'s description does not say "already exists" strongly enough |
| Selection is fine with the rule installed and poor without it | Expected. Recommend the rule in install docs |
