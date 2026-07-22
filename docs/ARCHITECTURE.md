# Architecture

This project is organized around a build pipeline:

1. `ssg.config` loads and validates site configuration.
2. `ssg.content` discovers Markdown files, assigns URLs, and builds collection and taxonomy indexes.
3. `ssg.parser` extracts frontmatter and renders Markdown bodies.
4. `ssg.assets` fingerprints static assets and writes an asset manifest.
5. `ssg.renderer` renders Jinja2 templates from site templates first, then theme templates.
6. `ssg.builder` orchestrates page, collection, taxonomy, pagination, feed, sitemap, and search artifacts.
7. `ssg.cli` exposes build, serve, init, and inspect workflows.

## Content Index

`ContentIndex` is the internal metadata layer. It owns collection membership,
published/draft filtering, taxonomy term lookup, and query filtering. Build
features should prefer querying this index instead of rediscovering content.

## Generated Artifacts

A full build may generate:

- HTML pages for standalone content.
- HTML pages for collection items.
- Collection list and pagination pages.
- Archive pages.
- Tag pages and generic taxonomy pages.
- Fingerprinted assets plus `.ssg-assets.json`.
- Theme assets merged before site assets so local files can override reusable themes.
- `feed.xml`.
- `sitemap.xml`.
- `search.json`.
- `.ssg-cache.json`.

## Plugin Hooks

Site configuration can load local Python plugin files:

```yaml
plugins:
  - plugins/my_plugin.py
```

Plugin modules may define functions matching these hook names. Each hook receives
a `HookContext` with `config`, `phase`, and mutable `data`.

- content indexed
- assets processed
- page rendered
- build finished

`page_rendered` may return a string to replace the rendered HTML. Other hooks can
inspect build state and write side artifacts using paths from `context.config`.
<!-- rewrite commit 13 -->
<!-- rewrite commit 14 -->
<!-- rewrite commit 15 -->
<!-- rewrite commit 16 -->
<!-- rewrite commit 17 -->
<!-- rewrite commit 18 -->
<!-- rewrite commit 19 -->
<!-- rewrite commit 20 -->
