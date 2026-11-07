# Lists

Use this when a page shows many records of the same kind: packages, URLs, keys, workers, tasks. A list is one `dcr-data-table` card. Do not hand-roll a table, and do not use the admin changelist.

Class names and live markup come from [design-system.md](design-system.md) and the official panels (see [living-examples.md](living-examples.md)). This file covers how a list should be put together and what it should look like.

## Structure

Inside `{% block panel_content %}`, below the `dcr-page-header`, a list is one card with these zones in order:

| Zone | Class | Holds |
|---|---|---|
| Header | `dcr-data-table__header` > `__header-info` > `dcr-data-table__title` | Title and a count badge. Optional `dcr-data-table__meta` for status text and a CLEAR link |
| Controls (optional) | `dcr-data-table__controls` | The search or filter form. See [search.md](search.md) |
| Table | `dcr-data-table__scroll` > `<table>` | Column headers and rows |
| Footer (optional) | `dcr-pagination` | Page links, after the scroll area and still inside the card |

Reference implementations: `dj-urls-panel` `templates/admin/dj_urls_panel/index.html` for a full list with search, and `dj-cache-panel` `key_search.html` for a paginated one. The live gallery at `/admin/dj-control-room-base/` shows each variant.

## Rules

- **Page header first.** Every list page opens with `dcr-page-header` including the `__icon` from `{% dcr_icon "<key>" %}` and a subtitle that says what the records are. Use the same icon the panel's dashboard card uses.
- **Count in the title.** Put a `dcr-badge` in the title with the number and an uppercase word, such as `47 TOTAL` or `12 SHOWN`. Wrap the word in `{% trans %}`.
- **Identifiers are code.** Names, keys, paths, import strings and ids go in `<code class="dcr-code">`.
- **The row's subject links to its detail page.** Use `dcr-data-table__link` on the first column. Put the `<code>` inside the link when the value is an identifier.
- **Numbers align right.** Counts, sizes, durations and TTLs use `dcr-col--right`.
- **Status is a badge or pill.** Use `dcr-badge` or `dcr-pill` with `--success`, `--warning`, `--danger`, `--info` or `--muted`. Do not print raw status strings or colour them yourself.
- **Secondary detail is muted.** A second line or an alias next to a value uses `dcr-text-xs dcr-text-muted`.
- **Yes/no columns** use `dcr-ability-indicator--yes` and `--no`.
- **Never render a blank table.** When there are no rows, render a `dcr-empty` with a `__title` and a `__body`. Put it in a `colspan` cell of the `{% empty %}` row so the column headers stay visible, or in place of the table. The text must say why it is empty, and a list that is empty because of a search says so differently. See [search.md](search.md).
- **Paginate anything that can grow.** Do not render thousands of rows. Use `dcr-pagination` and keep every other query parameter (`q`, `per_page`, filters) in the page links.
- **Translate visible text** with `{% trans %}` or `{% blocktrans %}`.

Variants for denser lists: `dcr-data-table--no-stripe` and `dcr-data-table--no-hover` on the card. Expandable rows use `dcr-col--expand`, `dcr-data-table__expand-btn` and `dcr-data-table__expand-row`. Read the styleguide partial in `dj-control-room-base` before using them.

## Python side

- Gather and order the data in a plain function outside the view, for example `packages.py`, `inspector.py`, `services.py`. The view should call it and build context.
- Sort in Python so the order is stable and predictable. For keys that differ only by separators or case, sort on a normalized key.
- Keep a total count and a shown count as separate context values when a list can be filtered. The badge shows the total, and "Showing X of Y" shows the filtered count.
- Decorate the view with `@panel_config.permission_required(scope)`. A list is a read operation, so it uses the same read scope as the rest of the panel's pages. See [scopes.md](scopes.md).
- Test the data function directly, then test the view: anonymous users are redirected, a staff user sees the list, the empty state appears with no data. See the panel skill's `references/tests.md`.

## Checklist

- [ ] One `dcr-data-table` card under a `dcr-page-header` with an icon
- [ ] Count badge in the title
- [ ] Identifiers in `dcr-code`, statuses in badges or pills, numbers right-aligned
- [ ] Empty state with a reason, not a blank table
- [ ] Pagination if the list can grow, preserving other query parameters
- [ ] No custom CSS and no admin classes
- [ ] Data gathering outside the view, with a test
