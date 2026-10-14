# Eval: add a detail page

## Request

In the app packages panel, make each package name a link to a page that shows its version, summary, license, Python requirement, and the packages it requires.

The data comes from `importlib.metadata`. Nothing needs a database or a mutating action.

## Expected approach

- `inspect_panel.py` reports mode `internal`, view scope `index`, URL name `index`
- Edits happen in `dcr_app_packages/`: `packages.py`, `views.py`, `urls.py`, `templates/admin/dcr_app_packages/`, `tests.py`

## Expected implementation

- A helper in `packages.py` returns one package's metadata, or `None` if it is not installed. It is separate from the view and tested directly
- A `package_detail` view, decorated with `@panel_config.permission_required("package_detail")`, building context with `panel_config.get_context(...)`
- A `path(...)` with `name="package_detail"` in `urls.py`. `app_name` is unchanged
- An unknown package returns 404, not a 500
- A detail template extending the same base as `index.html`, using `dcr-back-link`, `dcr-page-header`, `dcr-dl` for the fields, and `dcr-code` for identifiers. No custom CSS
- The first column of the list links to the detail page with `dcr-data-table__link`
- Requirements are shown as a list of links to other installed packages only when they exist
- The existing `index` scope and URL name are **kept**. The agent does not rename `index` as a side effect
- A `scopes.md` next to `panel.py` documents `package_detail` (and `index` as the list scope). The generated panel has none, so creating it is expected
- Tests: helper known and unknown package, page for a staff user, 404, anonymous redirect

## Expected `inspect_panel.py --base HEAD`

```
added  view_scopes: package_detail
added  url_names: package_detail
```

No `BREAKING` lines. Exit code 0.

## Must not

- Re-run `dcr_startpanel`
- Add `tools.py` or any POST action
- Touch `apps.py`, `admin.py`, `models.py`, or the `panel_base.html` extension
