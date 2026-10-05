# Living examples

Do not vendor copies of panel code in a skill. When you need a pattern, open the current official source (local submodule in this playground, otherwise GitHub `main`):

| Pattern | Read |
|---|---|
| Cookiecutter stubs you are replacing | The panel you just baked |
| List + search UI (rules in [lists.md](lists.md) and [search.md](search.md)) | [dj-urls-panel](https://github.com/django-control-room/dj-urls-panel) `views.py`, `templates/admin/dj_urls_panel/index.html` |
| Paginated list with search | [dj-cache-panel](https://github.com/django-control-room/dj-cache-panel) `templates/admin/dj_cache_panel/key_search.html` |
| Step-by-step list and search in an internal panel | [Add an Internal Panel to Your Django Project](https://djangocontrolroom.com/guides/create-an-internal-panel) |
| POST actions (flush/delete/edit) | [dj-cache-panel](https://github.com/django-control-room/dj-cache-panel) `views.py`, `key_detail.html` |
| MCP tools | [dj-urls-panel](https://github.com/django-control-room/dj-urls-panel) `tools.py`, [dj-signals-panel](https://github.com/django-control-room/dj-signals-panel) `tools.py` |
| Design system + styleguide | [dj-control-room-base](https://github.com/django-control-room/dj-control-room-base) `design-system.css`; live gallery: `/admin/dj-control-room-base/` |
| Scopes docs | Any official panel `docs/scopes.md` (e.g. urls-panel). Write the equivalent into the package's `docs/scopes.md` or the local app's `scopes.md` |

Full panel contract: [Building Panels](https://django-control-room.github.io/dj-control-room-base/building-panels/).
