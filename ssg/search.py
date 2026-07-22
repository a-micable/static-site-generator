"""Search index generation for client-side site search."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Sequence

from ssg.parser import Page

TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")


def plain_text(html: str) -> str:
    text = TAG_RE.sub(" ", html)
    return SPACE_RE.sub(" ", text).strip()


def page_search_record(page: Page, base_url: str) -> dict[str, object]:
    return {
        "title": page.title,
        "url": f"{base_url.rstrip('/')}/{page.url.lstrip('/')}",
        "path": page.url,
        "collection": page.collection,
        "date": page.date.isoformat() if page.date else None,
        "tags": page.tags,
        "categories": page.categories,
        "taxonomies": page.taxonomies,
        "summary": str(page.metadata.get("description", "")),
        "content": plain_text(page.content_html),
    }


def build_search_index(pages: Sequence[Page], base_url: str) -> list[dict[str, object]]:
    records = [
        page_search_record(page, base_url)
        for page in pages
        if page.is_published and page.url
    ]
    return sorted(records, key=lambda item: str(item["path"]))


def write_search_index(output_path: Path, pages: Sequence[Page], base_url: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = build_search_index(pages, base_url)
    output_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
# rewrite commit 337
# rewrite commit 338
# rewrite commit 339
# rewrite commit 340
# rewrite commit 341
# rewrite commit 342
# rewrite commit 343
# rewrite commit 344
