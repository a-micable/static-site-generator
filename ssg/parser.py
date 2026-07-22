"""Markdown and frontmatter parsing."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

import markdown
import yaml

from ssg.exceptions import ParseError

logger = logging.getLogger(__name__)

FRONTMATTER_PATTERN = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n",
    re.DOTALL,
)


@dataclass
class Page:
    """A parsed content page."""

    source_path: Path
    title: str
    content_html: str
    raw_content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    collection: str | None = None
    slug: str = ""
    url: str = ""
    date: datetime | None = None
    tags: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    taxonomies: dict[str, list[str]] = field(default_factory=dict)
    layout: str | None = None
    draft: bool = False

    @property
    def is_published(self) -> bool:
        return not self.draft


def _parse_date(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return None


def slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug.strip("-") or "untitled"


def _metadata_list(metadata: dict[str, Any], key: str) -> list[str]:
    value = metadata.get(key, [])
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def split_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Split YAML frontmatter from markdown body."""
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return {}, content

    yaml_text = match.group(1)
    body = content[match.end() :]

    try:
        metadata = yaml.safe_load(yaml_text) or {}
    except yaml.YAMLError as exc:
        raise ParseError(f"Invalid frontmatter YAML: {exc}") from exc

    if not isinstance(metadata, dict):
        raise ParseError("Frontmatter must be a YAML mapping")

    return metadata, body


def render_markdown(body: str) -> str:
    """Convert markdown body to HTML."""
    md = markdown.Markdown(
        extensions=[
            "extra",
            "codehilite",
            "toc",
            "meta",
            "sane_lists",
        ],
        extension_configs={
            "codehilite": {"css_class": "highlight"},
        },
    )
    return md.convert(body)


def parse_page(
    source_path: Path,
    content: str,
    collection: str | None = None,
    default_layout: str | None = None,
) -> Page:
    """Parse a markdown file into a Page."""
    metadata, body = split_frontmatter(content)

    title = str(metadata.get("title", source_path.stem.replace("-", " ").title()))
    slug = str(metadata.get("slug", slugify(source_path.stem)))
    tags = _metadata_list(metadata, "tags")
    categories = _metadata_list(metadata, "categories")
    taxonomies: dict[str, list[str]] = {}
    for key, value in metadata.items():
        if key.startswith("taxonomy_"):
            taxonomy_name = key.removeprefix("taxonomy_")
            values = _metadata_list(metadata, key)
            if taxonomy_name and values:
                taxonomies[taxonomy_name] = values
    if tags:
        taxonomies["tags"] = tags
    if categories:
        taxonomies["categories"] = categories

    layout = metadata.get("layout", default_layout)
    draft = bool(metadata.get("draft", False))
    page_date = _parse_date(metadata.get("date"))

    html = render_markdown(body)

    page = Page(
        source_path=source_path,
        title=title,
        content_html=html,
        raw_content=body,
        metadata=metadata,
        collection=collection,
        slug=slug,
        date=page_date,
        tags=tags,
        categories=categories,
        taxonomies=taxonomies,
        layout=str(layout) if layout else default_layout,
        draft=draft,
    )

    logger.debug("Parsed page: %s (%s)", page.title, source_path)
    return page


def discover_markdown_files(directory: Path) -> list[Path]:
    """Find all markdown files in a directory recursively."""
    if not directory.is_dir():
        return []
    return sorted(directory.rglob("*.md"))
# rewrite commit 301
# rewrite commit 302
# rewrite commit 303
