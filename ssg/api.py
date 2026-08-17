"""HTTP API backing the React dashboard."""

from __future__ import annotations

import json
import logging
import re
import threading
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from http import HTTPStatus
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

import yaml

from ssg.builder import SiteBuilder, build_site
from ssg.config import SiteConfig, load_config
from ssg.exceptions import ConfigError, SSGError
from ssg.parser import discover_markdown_files, parse_page, render_markdown, slugify, split_frontmatter

logger = logging.getLogger(__name__)

FRONTMATTER_PATTERN = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)

@dataclass
class BuildState:
    running: bool = False
    pages_built: int = 0
    pages_skipped: int = 0
    output_dir: str = ""
    error: str | None = None
    last_built_at: str | None = None

class SiteApi:
    """JSON API for site configuration, content, builds, and search."""

    def __init__(self, source_root: Path) -> None:
        self.source_root = source_root.resolve()
        self._build_state = BuildState()
        self._build_lock = threading.Lock()

    def _config_path(self) -> Path:
        return self.source_root / "ssg.yaml"

    def _load_config(self) -> SiteConfig:
        return load_config(self.source_root)

    def _page_to_summary(self, page_path: Path, page: Any) -> dict[str, Any]:
        relative = page_path.relative_to(self._load_config().content_path)
        return {
            "path": str(page_path),
            "relative": str(relative).replace("\\", "/"),
            "title": page.title,
            "collection": page.collection,
            "url": page.url,
            "date": page.date.isoformat() if page.date else None,
            "tags": page.tags,
            "categories": page.categories,
            "draft": page.draft,
        }

    def _parse_markdown_file(self, path: Path) -> Any:
        config = self._load_config()
        relative = path.relative_to(config.content_path)
        collection_name: str | None = None
        default_layout: str | None = "page.html"
        for coll in config.collections:
            try:
                relative.relative_to(Path(coll.path))
                collection_name = coll.name
                default_layout = coll.layout
                break
            except ValueError:
                continue
        content = path.read_text(encoding="utf-8")
        return parse_page(path, content, collection_name, default_layout)

    def get_config(self) -> dict[str, Any]:
        config = self._load_config()
        return {
            "title": config.title,
            "base_url": config.base_url,
            "description": config.description,
            "language": config.language,
            "author": config.author,
            "feed_items": config.feed_items,
            "search_index": config.search_index,
            "output_dir": config.output_dir,
            "content_dir": config.content_dir,
            "templates_dir": config.templates_dir,
            "assets_dir": config.assets_dir,
        }

    def save_config(self, payload: dict[str, Any]) -> dict[str, Any]:
        path = self._config_path()
        current = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(current, dict):
            current = {}
        for key in (
            "title",
            "base_url",
            "description",
            "language",
            "author",
            "feed_items",
            "search_index",
        ):
            if key in payload:
                current[key] = payload[key]
        path.write_text(
            yaml.dump(current, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
        return self.get_config()

    def list_posts(self, collection: str | None = None) -> list[dict[str, Any]]:
        config = self._load_config()
        posts: list[dict[str, Any]] = []
        for md_path in discover_markdown_files(config.content_path):
            page = self._parse_markdown_file(md_path)
            if collection and page.collection != collection:
                continue
            posts.append(self._page_to_summary(md_path, page))
        posts.sort(key=lambda item: item["title"].lower())
        return posts

    def get_post(self, path_str: str) -> dict[str, Any]:
        path = Path(unquote(path_str))
        if not path.is_file():
            raise FileNotFoundError(f"Post not found: {path}")
        page = self._parse_markdown_file(path)
        summary = self._page_to_summary(path, page)
        return {**summary, "content": page.raw_content}

    def save_post(self, path_str: str, content: str) -> dict[str, Any]:
        path = Path(unquote(path_str))
        if not path.is_file():
            raise FileNotFoundError(f"Post not found: {path}")
        path.write_text(content, encoding="utf-8")
        return self.get_post(path_str)

    def create_post(self, payload: dict[str, Any]) -> dict[str, Any]:
        config = self._load_config()
        title = str(payload.get("title", "Untitled Post"))
        collection_name = str(payload.get("collection", "posts"))
        coll = config.get_collection(collection_name)
        if not coll:
            raise ConfigError(f"Unknown collection: {collection_name}")

        slug = slugify(str(payload.get("slug", title)))
        post_path = config.content_path / coll.path / f"{slug}.md"
        if post_path.exists():
            raise ConfigError(f"Post already exists: {slug}")

        today = datetime.now(timezone.utc).date().isoformat()
        content = (
            f"---\ntitle: {title}\ndate: {today}\nlayout: {coll.layout}\ndraft: false\n---\n\n"
            f"# {title}\n\nNew post content.\n"
        )
        post_path.parent.mkdir(parents=True, exist_ok=True)
        post_path.write_text(content, encoding="utf-8")
        return self.get_post(str(post_path))

    def delete_post(self, path_str: str) -> None:
        path = Path(unquote(path_str))
        if not path.is_file():
            raise FileNotFoundError(f"Post not found: {path}")
        path.unlink()

    def toggle_draft(self, path_str: str) -> dict[str, Any]:
        path = Path(unquote(path_str))
        if not path.is_file():
            raise FileNotFoundError(f"Post not found: {path}")

        raw = path.read_text(encoding="utf-8")
        metadata, body = split_frontmatter(raw)
        draft = bool(metadata.get("draft", False))
        metadata["draft"] = not draft

        yaml_block = yaml.dump(metadata, default_flow_style=False, sort_keys=False).strip()
        path.write_text(f"---\n{yaml_block}\n---\n{body}", encoding="utf-8")
        return self.get_post(path_str)

    def preview_markdown(self, markdown: str) -> dict[str, str]:
        return {"html": render_markdown(markdown)}

    def list_collections(self) -> list[dict[str, Any]]:
        config = self._load_config()
        result: list[dict[str, Any]] = []
        for coll in config.collections:
            posts = self.list_posts(coll.name)
            result.append({"name": coll.name, "count": len(posts), "posts": posts})
        return result

    def list_taxonomies(self) -> dict[str, dict[str, list[dict[str, Any]]]]:
        posts = self.list_posts()
        tags: dict[str, list[dict[str, Any]]] = {}
        categories: dict[str, list[dict[str, Any]]] = {}
        for post in posts:
            for tag in post["tags"]:
                tags.setdefault(tag, []).append(post)
            for category in post["categories"]:
                categories.setdefault(category, []).append(post)
        return {"tags": tags, "categories": categories}

    def _run_build(self, incremental: bool, clean: bool) -> None:
        try:
            result = build_site(self.source_root, incremental=incremental, clean=clean)
            with self._build_lock:
                self._build_state.running = False
                self._build_state.pages_built = result.pages_built
                self._build_state.pages_skipped = result.pages_skipped
                self._build_state.output_dir = str(result.output_dir)
                self._build_state.error = None
                self._build_state.last_built_at = datetime.now(timezone.utc).isoformat()
        except SSGError as exc:
            with self._build_lock:
                self._build_state.running = False
                self._build_state.error = str(exc)

    def start_build(self, incremental: bool = False, clean: bool = False) -> dict[str, Any]:
        with self._build_lock:
            if self._build_state.running:
                return self.build_status()
            self._build_state.running = True
            self._build_state.error = None
        thread = threading.Thread(
            target=self._run_build,
            args=(incremental, clean),
            daemon=True,
        )
        thread.start()
        return self.build_status()

    def build_status(self) -> dict[str, Any]:
        with self._build_lock:
            return asdict(self._build_state)

    def get_search_index(self) -> list[dict[str, Any]]:
        config = self._load_config()
        search_path = config.output_path / "search.json"
        if search_path.is_file():
            data = json.loads(search_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data

        builder = SiteBuilder(config)
        pages = builder._load_pages()
        published = [p for p in pages if p.is_published]
        from ssg.search import build_search_index

        return build_search_index(published, config.base_url)

    def dispatch(self, method: str, path: str, body: bytes | None = None) -> tuple[int, Any]:
        parsed = urlparse(path)
        route = parsed.path
        query = parse_qs(parsed.query)

        try:
            if route == "/api/config" and method == "GET":
                return HTTPStatus.OK, self.get_config()
            if route == "/api/config" and method == "PUT":
                payload = json.loads(body.decode("utf-8")) if body else {}
                return HTTPStatus.OK, self.save_config(payload)
            if route == "/api/posts" and method == "GET":
                collection = query.get("collection", [None])[0]
                return HTTPStatus.OK, self.list_posts(collection)
            if route == "/api/posts" and method == "POST":
                payload = json.loads(body.decode("utf-8")) if body else {}
                return HTTPStatus.CREATED, self.create_post(payload)
            if route.startswith("/api/posts/") and route.endswith("/draft") and method == "PATCH":
                post_path = route.removeprefix("/api/posts/").removesuffix("/draft")
                return HTTPStatus.OK, self.toggle_draft(post_path)
            if route.startswith("/api/posts/") and method == "GET":
                post_path = route.removeprefix("/api/posts/")
                return HTTPStatus.OK, self.get_post(post_path)
            if route.startswith("/api/posts/") and method == "PUT":
                post_path = route.removeprefix("/api/posts/")
                payload = json.loads(body.decode("utf-8")) if body else {}
                content = str(payload.get("content", ""))
                return HTTPStatus.OK, self.save_post(post_path, content)
            if route.startswith("/api/posts/") and method == "DELETE":
                post_path = route.removeprefix("/api/posts/")
                self.delete_post(post_path)
                return HTTPStatus.NO_CONTENT, None
            if route == "/api/preview" and method == "POST":
                payload = json.loads(body.decode("utf-8")) if body else {}
                markdown = str(payload.get("markdown", ""))
                return HTTPStatus.OK, self.preview_markdown(markdown)
            if route == "/api/collections" and method == "GET":
                return HTTPStatus.OK, self.list_collections()
            if route == "/api/taxonomies" and method == "GET":
                return HTTPStatus.OK, self.list_taxonomies()
            if route == "/api/build/status" and method == "GET":
                return HTTPStatus.OK, self.build_status()
            if route == "/api/build" and method == "POST":
                payload = json.loads(body.decode("utf-8")) if body else {}
                incremental = bool(payload.get("incremental", False))
                clean = bool(payload.get("clean", False))
                return HTTPStatus.OK, self.start_build(incremental, clean)
            if route == "/api/search" and method == "GET":
                return HTTPStatus.OK, self.get_search_index()
        except FileNotFoundError as exc:
            return HTTPStatus.NOT_FOUND, {"error": str(exc)}
        except ConfigError as exc:
            return HTTPStatus.BAD_REQUEST, {"error": str(exc)}
        except json.JSONDecodeError as exc:
            return HTTPStatus.BAD_REQUEST, {"error": f"Invalid JSON: {exc}"}
        except SSGError as exc:
            return HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc)}

        return HTTPStatus.NOT_FOUND, {"error": "Not found"}
