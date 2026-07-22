"""Site configuration loading and validation."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ssg.exceptions import ConfigError

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_FILENAME = "ssg.yaml"


@dataclass
class CollectionConfig:
    """Configuration for a content collection."""

    name: str
    path: str
    output: str
    sort_by: str = "date"
    sort_order: str = "desc"
    per_page: int = 10
    layout: str = "post.html"
    archive: bool = True
    tags: bool = True


@dataclass
class SiteConfig:
    """Top-level site configuration."""

    title: str
    base_url: str
    output_dir: str = "dist"
    content_dir: str = "content"
    templates_dir: str = "templates"
    assets_dir: str = "assets"
    themes_dir: str = "themes"
    theme: str | None = None
    description: str = ""
    language: str = "en"
    author: str = ""
    feed_items: int = 20
    search_index: bool = True
    taxonomies: list[str] = field(default_factory=lambda: ["tags", "categories"])
    plugins: list[str] = field(default_factory=list)
    collections: list[CollectionConfig] = field(default_factory=list)
    source_root: Path = field(default_factory=lambda: Path("."))

    @property
    def output_path(self) -> Path:
        return self.source_root / self.output_dir

    @property
    def content_path(self) -> Path:
        return self.source_root / self.content_dir

    @property
    def templates_path(self) -> Path:
        return self.source_root / self.templates_dir

    @property
    def assets_path(self) -> Path:
        return self.source_root / self.assets_dir

    @property
    def themes_path(self) -> Path:
        return self.source_root / self.themes_dir

    @property
    def theme_path(self) -> Path | None:
        return self.themes_path / self.theme if self.theme else None

    @property
    def theme_templates_path(self) -> Path | None:
        return self.theme_path / "templates" if self.theme_path else None

    @property
    def theme_assets_path(self) -> Path | None:
        return self.theme_path / "assets" if self.theme_path else None

    def get_collection(self, name: str) -> CollectionConfig | None:
        for collection in self.collections:
            if collection.name == name:
                return collection
        return None


def _parse_collection(name: str, data: dict[str, Any]) -> CollectionConfig:
    per_page = int(data.get("per_page", 10))
    if per_page < 0:
        raise ConfigError(f"Collection '{name}' per_page must be >= 0")

    return CollectionConfig(
        name=name,
        path=str(data.get("path", name)),
        output=str(data.get("output", name)),
        sort_by=str(data.get("sort_by", "date")),
        sort_order=str(data.get("sort_order", "desc")),
        per_page=per_page,
        layout=str(data.get("layout", "post.html")),
        archive=bool(data.get("archive", True)),
        tags=bool(data.get("tags", True)),
    )


def _parse_taxonomies(raw: Any) -> list[str]:
    if raw is None:
        return ["tags", "categories"]
    if not isinstance(raw, list):
        raise ConfigError("Configuration 'taxonomies' must be a list")

    taxonomies: list[str] = []
    for item in raw:
        name = str(item).strip()
        if not name:
            raise ConfigError("Taxonomy names cannot be empty")
        if "/" in name or "\\" in name:
            raise ConfigError(f"Invalid taxonomy name: {name}")
        if name not in taxonomies:
            taxonomies.append(name)
    return taxonomies


def _validate_relative_path(name: str, value: str) -> None:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ConfigError(f"Configuration '{name}' must be a relative path")


def _parse_string_list(raw: Any, key: str) -> list[str]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ConfigError(f"Configuration '{key}' must be a list")
    values = [str(item).strip() for item in raw if str(item).strip()]
    if len(values) != len(raw):
        raise ConfigError(f"Configuration '{key}' cannot contain empty values")
    return values


def load_config(source_root: Path, config_path: Path | None = None) -> SiteConfig:
    """Load and validate site configuration from YAML."""
    root = source_root.resolve()
    path = config_path or (root / DEFAULT_CONFIG_FILENAME)

    if not path.is_file():
        raise ConfigError(f"Configuration file not found: {path}")

    logger.debug("Loading configuration from %s", path)

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigError(f"Configuration must be a mapping, got {type(raw).__name__}")

    title = raw.get("title")
    base_url = raw.get("base_url")
    if not title:
        raise ConfigError("Configuration requires 'title'")
    if not base_url:
        raise ConfigError("Configuration requires 'base_url'")

    for key in ("output_dir", "content_dir", "templates_dir", "assets_dir", "themes_dir"):
        _validate_relative_path(key, str(raw.get(key, key.replace("_dir", ""))))

    theme = raw.get("theme")
    if theme is not None:
        theme = str(theme).strip()
        if not theme or "/" in theme or "\\" in theme or theme in (".", ".."):
            raise ConfigError("Configuration 'theme' must be a simple theme name")

    feed_items = int(raw.get("feed_items", 20))
    if feed_items <= 0:
        raise ConfigError("Configuration 'feed_items' must be > 0")

    collections: list[CollectionConfig] = []
    raw_collections = raw.get("collections", {})
    if isinstance(raw_collections, dict):
        for name, coll_data in raw_collections.items():
            if isinstance(coll_data, dict):
                collections.append(_parse_collection(name, coll_data))
            else:
                collections.append(
                    CollectionConfig(name=name, path=str(name), output=str(name))
                )

    config = SiteConfig(
        title=str(title),
        base_url=str(base_url).rstrip("/"),
        output_dir=str(raw.get("output_dir", "dist")),
        content_dir=str(raw.get("content_dir", "content")),
        templates_dir=str(raw.get("templates_dir", "templates")),
        assets_dir=str(raw.get("assets_dir", "assets")),
        themes_dir=str(raw.get("themes_dir", "themes")),
        theme=theme,
        description=str(raw.get("description", "")),
        language=str(raw.get("language", "en")),
        author=str(raw.get("author", "")),
        feed_items=feed_items,
        search_index=bool(raw.get("search_index", True)),
        taxonomies=_parse_taxonomies(raw.get("taxonomies")),
        plugins=_parse_string_list(raw.get("plugins"), "plugins"),
        collections=collections,
        source_root=root,
    )

    logger.info("Loaded site config: %s (%s)", config.title, config.base_url)
    return config


def default_config_dict() -> dict[str, Any]:
    """Return default configuration for init command."""
    return {
        "title": "My Site",
        "base_url": "https://example.com",
        "description": "A site built with SSG",
        "language": "en",
        "author": "Site Author",
        "search_index": True,
        "taxonomies": ["tags", "categories"],
        "plugins": [],
        "output_dir": "dist",
        "content_dir": "content",
        "templates_dir": "templates",
        "assets_dir": "assets",
        "themes_dir": "themes",
        "theme": None,
        "feed_items": 20,
        "collections": {
            "posts": {
                "path": "posts",
                "output": "posts",
                "sort_by": "date",
                "sort_order": "desc",
                "per_page": 5,
                "layout": "post.html",
                "archive": True,
                "tags": True,
            }
        },
    }
# rewrite commit 253
# rewrite commit 254
# rewrite commit 255
# rewrite commit 256
# rewrite commit 257
