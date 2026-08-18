# Design system

Every panel UI is built with the **existing** DCR design system from `dj-control-room-base`. Do not invent a parallel CSS language, copy `design-system.css` into the panel, or use Django admin classes (`.button`, `.submit-row`, `.grp-*`).

The stylesheet is already loaded when templates extend Cookiecutter `base.html` → `dj_control_room_base/panel_base.html` (`LOAD_DEFAULT_CSS`, default `True`). Dark mode is token-level; components follow `--dcr-*` automatically.

Start from the generated `index.html` (it already has `dcr-page-header`). Replace the welcome block with real content using the catalog below. For a full list/detail page, read current templates in [dj-urls-panel](https://github.com/django-control-room/dj-urls-panel) or [dj-cache-panel](https://github.com/django-control-room/dj-cache-panel).

Live gallery (baked `example_project`): `/admin/dj-control-room-base/`.

Source of truth: `dj_control_room_base/static/dj_control_room_base/css/design-system.css`. Do not paste it here or into the panel.

## Always

- `{% load i18n static dcr_icons %}`
- Content in `{% block panel_content %}`
- `{% dcr_icon "link" %}` for built-in icons (not inline SVG path soup)
- Semantic colour via modifiers (`dcr-btn--danger`, `dcr-badge--warning`, `dcr-icon-color--accent`), not hex
- Panel `styles.css` only for truly custom layout. Prefer utilities (`dcr-mt-md`, `dcr-text-muted`, `dcr-font-mono`). If you must write CSS, use `var(--dcr-color-*)` / `var(--dcr-space-*)` — never hardcoded colours

Remove Cookiecutter `.panel-welcome*` rules once the welcome page is gone.

## Catalog

Pick the closest component. Do not create a one-off equivalent.

| Need | Use |
|---|---|
| Page title | `dcr-page-header` + `__main` + `__icon` + `dcr-icon-color--*` + `__body` + `__title` + `__subtitle`. Actions: `__actions` |
| Back to list | `dcr-back-link` (before the header, or as first child of it) |
| Breadcrumb extra | `{% block panel_breadcrumbs %}` |
| List of records | `dcr-data-table` + `__header` + `__title` + `__scroll` + `<table>`. Row links: `dcr-data-table__link`. Numeric cols: `dcr-col--right` |
| Empty list | `dcr-empty` + `__title` + `__body` |
| Record fields | `dcr-dl` + `__row` + `__label` + `__value` (`__value--mono` for ids/keys) |
| Grouped info | `dcr-card` + `__header` + `__title` + `__body` + `__row` |
| KPI tiles | `dcr-metric-grid` + `dcr-metric` + `__label` + `__value` |
| Section title | `dcr-section-header` + `__title` |
| Primary / secondary / destructive click | `dcr-btn` + `--primary` / `--ghost` / `--danger` / `--warning` / `--sm`. Not admin `.button` |
| Status chip | `dcr-badge` or `dcr-pill` + `--success\|warning\|danger\|info\|muted` |
| Flash / inline error | `dcr-callout` + `--info\|success\|warning\|danger` (`__title`, `__body`). Django messages already render as callouts in `panel_base.html` |
| Irreversible block | `dcr-danger-zone` + `__title` + `__body` + a `--danger` button |
| Filter / search form | `dcr-form` + `dcr-form__row` + `dcr-field` + `dcr-field__label` + `dcr-input` / `dcr-select` |
| Tabs | `dcr-tabs` + `dcr-tabs__tab` (`active` or `aria-current="page"`) |
| Pagination | `dcr-pagination` (usually inside the table footer) |
| Inline code | `dcr-code`. Blocks: `dcr-code--block` or `dcr-code-viewer` |
| Source preview | `dcr-code-viewer` (highlight.js is already vendored on `dj_control_room_base`) |
| Yes/no capability | `dcr-ability-indicator--yes` / `--no` |

Icon wrap colours: `dcr-icon-color--accent|success|warning|danger|info|muted|purple|indigo` (add `-solid` for filled). Match `PanelPlugin.icon_color` when it makes sense.

## Icons

`{% dcr_icon "<key>" %}`. Built-in keys: `database`, `layers`, `chart`, `link`, `radio`, `alert`, `cog`, `default`. Unknown keys fall back to `default`. Cookiecutter only prompts a subset; `PanelPlugin.icon` may use any key (or a static image path).

## Tokens (custom CSS only)

`--dcr-color-text`, `--dcr-color-text-muted`, `--dcr-color-bg`, `--dcr-color-bg-subtle`, `--dcr-color-border`, `--dcr-color-accent` (+ `success|warning|danger|info|muted|purple|indigo` and `-bg` variants), `--dcr-space-xs|sm|md|lg|xl`, `--dcr-radius*`, `--dcr-font-mono`, `--dcr-font-size-*`.
