# Search and filters

Use this when a list needs to be narrowed by a text query or by a few fields. It builds on [lists.md](lists.md). Read that first.

Official panels filter on the server with a plain GET form. Follow that. Do not add JavaScript filtering or a POST form for search.

Reference implementations: `dj-urls-panel` (`views.py` and `templates/admin/dj_urls_panel/index.html`) and `dj-cache-panel` (`key_search.html`). The canonical markup is in `dj-control-room-base` under the styleguide partial `sg_partials/data.html`. The internal panel guide builds the same thing step by step: [Add an Internal Panel to Your Django Project](https://djangocontrolroom.com/guides/create-an-internal-panel).

## Behaviour

- The form uses `method="get"` and the text field is named `q`. The URL after searching is `?q=term`, so it can be bookmarked and shared, and no CSRF token is needed.
- The view reads it with `request.GET.get("q", "").strip()` and passes it back to the template as `search_query`.
- An empty query returns the full list.
- The input is repopulated with `value="{{ search_query }}"`. Django escapes it. Do not mark it safe.
- Matching is case-insensitive substring by default.

## Markup

Everything lives inside the list's `dcr-data-table`. Class names and nesting follow `sg_partials/data.html`:

| Part | Classes |
|---|---|
| Zone, between the header and the table | `dcr-data-table__controls` |
| Form | `dcr-form` with `method="get"` |
| Label and field | `dcr-form__group` > `dcr-form__label` (with `for`) and `dcr-form__row--stretch` |
| Text input with icon | `dcr-input-group` > `dcr-input-group__icon` (SVG) + `dcr-input-group__input` (`<input name="q">`) |
| Submit | `dcr-btn dcr-btn--primary`, text "Search" |
| Status while searching | in the header, `dcr-data-table__meta` > `dcr-data-table__meta-info` with "Showing X of Y" |
| Clear | in `dcr-data-table__meta`, an `<a>` with `dcr-btn dcr-btn--ghost dcr-btn--sm` and text "CLEAR", linking to the panel URL without `q` |

The status line and CLEAR link render only when `search_query` is set. The count badge in the title keeps showing the total.

`dcr_icon` has no search or close icon. The official panels use a small inline SVG for the magnifier (`dcr-input-group__icon`) and the X (`dcr-btn__icon`). Copy those from `dj-urls-panel` rather than drawing new ones.

## Python side

- Put the matching in a plain function such as `filter_packages(packages, query)` next to the code that gathers the data. Keep it out of the view so it can be unit tested.
- If names have separators that people type either way (`foo_bar` and `foo-bar`), normalize the query the same way as the data before comparing.
- For querysets, filter with `Q(field__icontains=query)` combined with `|`. Never build SQL or filter expressions by concatenating the query.
- The view passes the total (`package_count`), the shown count (`result_count`) and `search_query` to the template.

## Empty results

A list that is empty because of the search is different from a list that has no data. In the `dcr-empty` body, branch on `search_query`:

- With a query: say nothing matched, for example "No installed packages match your search."
- Without a query: say there is nothing to show, and why.

Keep the `dcr-empty` inside the table so the column headers stay visible. The search form sits above the table, so it stays on screen and the user can edit the query.

## Combining with other parameters

- Add extra filters to the same form so they submit together with `q`. Use `dcr-form__row` with `dcr-field`, `dcr-field__label` and `dcr-select`.
- Every link that changes another parameter (pagination, sort, per-page) must carry `q`: `?q={{ search_query|urlencode }}&page=2`. `dj-cache-panel` `key_search.html` shows the pattern.
- Changing the query should go back to page 1. A plain form submit does this because the form does not include `page`.

## Permissions and tools

- Search is a read operation. It uses the same scope as the list it filters. Do not add a scope for it.
- If the panel exposes an MCP tool for the same data, give it a `query` argument and call the same filter function as the view. See [mcp-tools.md](mcp-tools.md).

## Tests

- The filter function: empty and whitespace queries return everything, case is ignored, separators are normalized, the summary or secondary field matches, and no match returns an empty list.
- The view with `?q=`: the context contains only matching rows, the total is unchanged, the search term is kept in the input, CLEAR appears, and a no-match query shows the search-specific empty message.
- Escaping: a query containing `<script>` does not appear unescaped in the response.

## Checklist

- [ ] GET form with `name="q"` inside `dcr-data-table__controls`
- [ ] `dcr-input-group` with icon, and a `dcr-btn--primary` Search button
- [ ] "Showing X of Y" and a ghost CLEAR link only while searching
- [ ] Total in the badge, shown count separate
- [ ] Different empty text for no matches and for no data
- [ ] `q` preserved in pagination and other links
- [ ] Filter function outside the view, with tests
