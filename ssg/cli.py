"""Command-line interface for the static site generator."""

from __future__ import annotations

import argparse
import http.server
import json
import logging
import socketserver
import sys
from pathlib import Path
from typing import Sequence

import yaml

from ssg.builder import build_site
from ssg.config import default_config_dict, load_config
from ssg.content import ContentIndex
from ssg.exceptions import ConfigError, SSGError
from ssg.watcher import WatchService

logger = logging.getLogger(__name__)

INIT_TEMPLATES: dict[str, str] = {
    "templates/base.html": """<!DOCTYPE html>
<html lang="{{ site.language }}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}{{ title }}{% endblock %} | {{ site.title }}</title>
  <meta name="description" content="{{ site.description }}">
  <link rel="alternate" type="application/rss+xml" href="{{ site.base_url }}/feed.xml">
  {% block head %}{% endblock %}
</head>
<body>
  <header>
    <h1><a href="{{ site.base_url }}/">{{ site.title }}</a></h1>
    <nav>
      <a href="{{ site.base_url }}/">Home</a>
      <a href="{{ site.base_url }}/posts/">Posts</a>
      <a href="{{ site.base_url }}/posts/archive/">Archive</a>
      <a href="{{ site.base_url }}/posts/tags/">Tags</a>
    </nav>
  </header>
  <main>
    {% block content %}{% endblock %}
  </main>
  <footer>
    <p>&copy; {{ site.author }} — Built with SSG</p>
  </footer>
</body>
</html>
""",
    "templates/page.html": """{% extends "base.html" %}
{% block content %}
<article>
  <h1>{{ page.title }}</h1>
  {{ content | safe }}
</article>
{% endblock %}
""",
    "templates/post.html": """{% extends "base.html" %}
{% block content %}
<article>
  <h1>{{ page.title }}</h1>
  {% if page.date %}<time datetime="{{ page.date.isoformat() }}">{{ page.date.strftime('%B %d, %Y') }}</time>{% endif %}
  {% if page.tags %}
  <ul class="tags">
    {% for tag in page.tags %}<li><a href="{{ site.base_url }}/posts/tags/{{ tag | lower | replace(' ', '-') }}/">{{ tag }}</a></li>{% endfor %}
  </ul>
  {% endif %}
  {{ content | safe }}
</article>
{% endblock %}
""",
    "templates/list.html": """{% extends "base.html" %}
{% block content %}
<h1>{{ title }}</h1>
<ul>
  {% for page in pages %}
  <li><a href="{{ site.base_url }}/{{ page.url.replace('index.html', '') }}">{{ page.title }}</a></li>
  {% endfor %}
</ul>
{% if total_pages > 1 %}
<nav class="pagination">
  {% if page_num > 1 %}<a href="{{ site.base_url }}/posts/{% if page_num > 2 %}page/{{ page_num - 1 }}/{% endif %}">Previous</a>{% endif %}
  <span>Page {{ page_num }} of {{ total_pages }}</span>
  {% if page_num < total_pages %}<a href="{{ site.base_url }}/posts/page/{{ page_num + 1 }}/">Next</a>{% endif %}
</nav>
{% endif %}
{% endblock %}
""",
    "templates/archive.html": """{% extends "base.html" %}
{% block content %}
<h1>Archive</h1>
<ul>
  {% for page in pages %}
  <li>
    {% if page.date %}<time>{{ page.date.strftime('%Y-%m-%d') }}</time> — {% endif %}
    <a href="{{ site.base_url }}/{{ page.url.replace('index.html', '') }}">{{ page.title }}</a>
  </li>
  {% endfor %}
</ul>
{% endblock %}
""",
    "templates/tag.html": """{% extends "base.html" %}
{% block content %}
<h1>Posts tagged &ldquo;{{ tag }}&rdquo;</h1>
<ul>
  {% for page in pages %}
  <li><a href="{{ site.base_url }}/{{ page.url.replace('index.html', '') }}">{{ page.title }}</a></li>
  {% endfor %}
</ul>
{% endblock %}
""",
    "templates/tags.html": """{% extends "base.html" %}
{% block content %}
<h1>All Tags</h1>
<ul>
  {% for tag in tags %}
  <li><a href="{{ site.base_url }}/posts/tags/{{ tag | lower | replace(' ', '-') }}/">{{ tag }}</a></li>
  {% endfor %}
</ul>
{% endblock %}
""",
    "content/index.md": """---
title: Welcome
layout: page.html
---

# Welcome to your new site

Edit `content/index.md` to get started.
""",
    "content/posts/first-post.md": """---
title: First Post
date: 2024-01-15
tags:
  - hello
  - ssg
layout: post.html
---

This is your first blog post. Write in **Markdown** and publish with `ssg build`.
""",
    "content/posts/second-post.md": """---
title: Second Post
date: 2024-02-20
tags:
  - updates
layout: post.html
---

Another post demonstrating collections, tags, and pagination.
""",
}


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def cmd_build(args: argparse.Namespace) -> int:
    source = Path(args.source).resolve()
    try:
        result = build_site(
            source,
            incremental=args.incremental,
            clean=args.clean,
        )
        print(
            f"Built {result.pages_built} pages"
            + (f", skipped {result.pages_skipped}" if result.incremental else "")
            + f" -> {result.output_dir}"
        )
        return 0
    except SSGError as exc:
        logger.error("%s", exc)
        return 1


def cmd_init(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    if target.exists() and any(target.iterdir()) and not args.force:
        logger.error("Target directory is not empty. Use --force to initialize.")
        return 1

    target.mkdir(parents=True, exist_ok=True)

    config_path = target / "ssg.yaml"
    config_path.write_text(
        yaml.dump(default_config_dict(), default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )

    for rel_path, content in INIT_TEMPLATES.items():
        file_path = target / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    assets_dir = target / "assets"
    assets_dir.mkdir(exist_ok=True)
    (assets_dir / "style.css").write_text(
        "body { font-family: system-ui, sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; }\n",
        encoding="utf-8",
    )

    print(f"Initialized site at {target}")
    print("Run 'ssg build' to generate your site.")
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    source = Path(args.source).resolve()
    port = args.port

    try:
        config = load_config(source)
    except ConfigError as exc:
        logger.error("%s", exc)
        return 1

    def rebuild() -> None:
        build_site(source, incremental=True)

    build_site(source, clean=False)
    print(f"Serving {config.output_path} at http://127.0.0.1:{port}/")

    watch_paths = [
        config.content_path,
        config.templates_path,
        config.assets_path,
        source / "ssg.yaml",
    ]

    watch = WatchService(watch_paths, rebuild)
    watch.start()

    handler = http.server.SimpleHTTPRequestHandler
    output = str(config.output_path)

    class ReusableServer(socketserver.TCPServer):
        allow_reuse_address = True

    original_dir = Path.cwd()
    try:
        import os

        os.chdir(output)
        with ReusableServer(("127.0.0.1", port), handler) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nShutting down...")
            finally:
                watch.stop()
    finally:
        import os

        os.chdir(original_dir)

    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    source = Path(args.source).resolve()
    try:
        config = load_config(source)
        index = ContentIndex.from_config(config)
    except SSGError as exc:
        logger.error("%s", exc)
        return 1

    payload = {
        "site": {
            "title": config.title,
            "base_url": config.base_url,
            "source_root": str(config.source_root),
        },
        "content": index.stats(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ssg",
        description="Production-grade Python static site generator",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    sub = parser.add_subparsers(dest="command", required=True)

    build_p = sub.add_parser("build", help="Build the static site")
    build_p.add_argument(
        "source",
        nargs="?",
        default=".",
        help="Site source directory (default: current directory)",
    )
    build_p.add_argument(
        "-i",
        "--incremental",
        action="store_true",
        help="Only rebuild changed files",
    )
    build_p.add_argument(
        "-c",
        "--clean",
        action="store_true",
        help="Clean output directory before building",
    )
    build_p.set_defaults(func=cmd_build)

    init_p = sub.add_parser("init", help="Initialize a new site")
    init_p.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target directory (default: current directory)",
    )
    init_p.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Initialize even if directory is not empty",
    )
    init_p.set_defaults(func=cmd_init)

    serve_p = sub.add_parser("serve", help="Build and serve the site with live reload")
    serve_p.add_argument(
        "source",
        nargs="?",
        default=".",
        help="Site source directory (default: current directory)",
    )
    serve_p.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Port to serve on (default: 8000)",
    )
    serve_p.set_defaults(func=cmd_serve)

    inspect_p = sub.add_parser("inspect", help="Inspect content metadata")
    inspect_p.add_argument(
        "source",
        nargs="?",
        default=".",
        help="Site source directory (default: current directory)",
    )
    inspect_p.set_defaults(func=cmd_inspect)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    _configure_logging(args.verbose)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
# rewrite commit 241
# rewrite commit 242
# rewrite commit 243
# rewrite commit 244
# rewrite commit 245
# rewrite commit 246
# rewrite commit 247
# rewrite commit 248
# rewrite commit 249
# rewrite commit 250
# rewrite commit 251
# rewrite commit 252
