# Static Site Generator

Production-grade Python static site generator with Markdown, Jinja2 templates, collections, tags, archives, pagination, RSS, sitemaps, asset fingerprinting, and incremental builds.

## Requirements

- Python 3.11+
- Dependencies listed in `requirements.txt`

## Installation

```bash
pip install -r requirements.txt
pip install .
```

## Quick Start

Initialize a new site:

```bash
ssg init my-site
cd my-site
ssg build
```

Build the included example site:

```bash
ssg build example-site
```

Serve with live reload:

```bash
ssg serve example-site
```

Open http://127.0.0.1:8000/ in your browser.

## Commands

| Command | Description |
|---------|-------------|
| `ssg init [target]` | Scaffold a new site with config, templates, and sample content |
| `ssg build [source]` | Generate static HTML into `dist/` |
| `ssg serve [source]` | Build, serve, and watch for changes |
| `ssg inspect [source]` | Print content, collection, draft, and taxonomy metadata as JSON |

### Build options

- `--incremental` / `-i` — rebuild only changed source files and pages affected by template changes
- `--clean` / `-c` — remove the output directory before building
- `--verbose` / `-v` — enable debug logging

## Site Structure

```
my-site/
├── ssg.yaml          # Site configuration
├── content/          # Markdown source files
├── templates/        # Jinja2 HTML templates
├── themes/           # Optional reusable theme templates and assets
├── assets/           # Static assets (CSS, JS, images)
└── dist/             # Generated output (created by build)
```

## Configuration

Example `ssg.yaml`:

```yaml
title: My Site
base_url: https://example.com
description: Site description
language: en
author: Author Name
output_dir: dist
content_dir: content
templates_dir: templates
assets_dir: assets
themes_dir: themes
theme: null
feed_items: 20
search_index: true
taxonomies:
  - tags
  - categories
collections:
  posts:
    path: posts
    output: posts
    sort_by: date
    sort_order: desc
    per_page: 5
    layout: post.html
    archive: true
    tags: true
```

## Features

- **Markdown rendering** with YAML frontmatter
- **Jinja2 templates** with template inheritance via `{% extends %}`
- **Theme fallback** for reusable templates and assets with site-level overrides
- **Collections** for grouping content (e.g. blog posts)
- **Archives** — chronological listing per collection
- **Tags** — tag index and per-tag pages
- **Taxonomies** — configurable metadata indexes such as categories or series
- **Pagination** — paginated collection listings
- **Asset fingerprinting** — content-hashed filenames for cache busting
- **Incremental builds** — skip unchanged pages; rebuild all when templates change
- **RSS feed** at `/feed.xml`
- **XML sitemap** at `/sitemap.xml`
- **Search index** at `/search.json` for client-side search
- **Content inspection** for collection and taxonomy metadata
- **Plugin hooks** for content indexing, asset processing, page rendering, and build completion
- **File watching** during `ssg serve` with debounced rebuilds

## Plugins

Add local plugin modules in `ssg.yaml`:

```yaml
plugins:
  - plugins/banner.py
```

Plugin functions receive a hook context. A `page_rendered` hook can return HTML
to transform output:

```python
def page_rendered(context):
    return context.data["html"].replace("</body>", "<p>Built by plugin</p></body>")
```

## Themes

Themes live under `themes/<name>/` and can provide `templates/` and `assets/`.
Site templates take precedence over theme templates, so a project can override
only the files it needs.

```yaml
theme: editorial
themes_dir: themes
```

## Architecture

See `docs/ARCHITECTURE.md` for the build pipeline, generated artifacts, and
extension points.

## Docker

Build and run:

```bash
docker build -t ssg .
docker run --rm ssg --help
docker run --rm ssg build
```

The Docker image includes the example site and runs `ssg build` by default.

## React Dashboard

The repository root contains a React + Vite dashboard that controls the Python SSG engine via a JSON API.

### Setup

```bash
npm install
pip install -e ".[dev]"
```

### Development

Run the API server and Vite dev server in separate terminals:

```bash
npm run server -- example-site
npm run dev
```

Open http://127.0.0.1:5173/ for the dashboard. Vite proxies `/api` requests to the Python server on port 8765.

### Dashboard features

- **Live Markdown Editor** — edit posts with instant HTML preview
- **Site Config Editor** — update `ssg.yaml` settings
- **Collection Browser** — browse posts, tags, and categories
- **Build Dashboard** — run and monitor site builds
- **Search Index Viewer** — inspect and filter `search.json`

### Frontend tests and build

```bash
npm test
npm run build
```

## Development

Run Python tests:

```bash
pip install -e ".[dev]"
pytest
pytest --cov=ssg --cov-report=term-missing
ruff check .
mypy ssg
```

Run all tests:

```bash
pytest
npm test
```

## Minerva issue

See `MINERVA_ISSUE.md` for the Markdown preview bug report. Apply the minimal fix with:

```bash
git apply fix.patch
```

## License

MIT
