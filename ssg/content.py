"""Content discovery, URL assignment, taxonomy indexing, and querying."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from ssg.config import CollectionConfig, SiteConfig
from ssg.parser import Page, discover_markdown_files, parse_page, slugify


@dataclass(frozen=True)
class ContentQuery:
    """Filter criteria for selecting content pages."""

    collection: str | None = None
    taxonomy: str | None = None
    term: str | None = None
    include_drafts: bool = False


@dataclass
class ContentIndex:
    """Indexed content with collection and taxonomy lookup helpers."""

    pages: list[Page]
    collections: dict[str, list[Page]] = field(default_factory=dict)
    taxonomies: dict[str, dict[str, list[Page]]] = field(default_factory=dict)

    @classmethod
    def from_config(cls, config: SiteConfig) -> ContentIndex:
        pages = [_load_page(config, path) for path in discover_markdown_files(config.content_path)]
        index = cls(pages=pages)
        index.rebuild(config.taxonomies)
        return index

    @property
    def published(self) -> list[Page]:
        return [page for page in self.pages if page.is_published]

    def rebuild(self, taxonomy_names: Iterable[str]) -> None:
        self.collections = {}
        self.taxonomies = {name: {} for name in taxonomy_names}

        for page in self.pages:
            if page.collection:
                self.collections.setdefault(page.collection, []).append(page)
            for taxonomy, terms in page.taxonomies.items():
                if taxonomy not in self.taxonomies:
                    self.taxonomies[taxonomy] = {}
                for term in terms:
                    self.taxonomies[taxonomy].setdefault(term, []).append(page)

    def by_collection(self, collection: str, *, published_only: bool = True) -> list[Page]:
        pages = self.collections.get(collection, [])
        if published_only:
            return [page for page in pages if page.is_published]
        return list(pages)

    def taxonomy_terms(
        self,
        taxonomy: str,
        collection: str | None = None,
        *,
        published_only: bool = True,
    ) -> dict[str, list[Page]]:
        terms = self.taxonomies.get(taxonomy, {})
        result: dict[str, list[Page]] = {}
        for term, pages in terms.items():
            filtered = [
                page
                for page in pages
                if (not published_only or page.is_published)
                and (collection is None or page.collection == collection)
            ]
            if filtered:
                result[term] = filtered
        return result

    def query(self, query: ContentQuery) -> list[Page]:
        pages = self.pages if query.include_drafts else self.published
        if query.collection:
            pages = [page for page in pages if page.collection == query.collection]
        if query.taxonomy and query.term:
            pages = [
                page
                for page in pages
                if query.term in page.taxonomies.get(query.taxonomy, [])
            ]
        return list(pages)

    def stats(self) -> dict[str, object]:
        return {
            "pages": len(self.pages),
            "published": len(self.published),
            "drafts": len([page for page in self.pages if page.draft]),
            "collections": {name: len(pages) for name, pages in self.collections.items()},
            "taxonomies": {
                name: {term: len(pages) for term, pages in terms.items()}
                for name, terms in self.taxonomies.items()
            },
        }


def _collection_for(config: SiteConfig, relative: Path) -> CollectionConfig | None:
    for collection in config.collections:
        try:
            relative.relative_to(Path(collection.path))
            return collection
        except ValueError:
            continue
    return None


def _assign_url(page: Page, relative: Path, collection: CollectionConfig | None) -> None:
    if collection:
        slug_path = relative.with_suffix("").relative_to(Path(collection.path))
        if slug_path.parent == Path("."):
            page.url = f"{collection.output}/{page.slug}/index.html"
        else:
            page.url = f"{collection.output}/{slug_path.parent}/{page.slug}/index.html"
        return

    rel = relative.with_suffix("")
    if str(rel) == "index" or str(rel) == ".":
        page.url = "index.html"
    elif rel.parent == Path("."):
        page.url = f"{page.slug}/index.html"
    else:
        page.url = f"{rel.parent}/{page.slug}/index.html"


def _load_page(config: SiteConfig, md_path: Path) -> Page:
    relative = md_path.relative_to(config.content_path)
    collection = _collection_for(config, relative)
    default_layout: str | None = collection.layout if collection else "page.html"
    content = md_path.read_text(encoding="utf-8")
    page = parse_page(
        md_path,
        content,
        collection.name if collection else None,
        default_layout,
    )
    _assign_url(page, relative, collection)
    return page


def taxonomy_url(collection: CollectionConfig, taxonomy: str, term: str) -> str:
    return f"{collection.output}/{taxonomy}/{slugify(term)}/index.html"
# rewrite commit 265
# rewrite commit 266
# rewrite commit 267
# rewrite commit 268
# rewrite commit 269
# rewrite commit 270
# rewrite commit 271
# rewrite commit 272
# rewrite commit 273
# rewrite commit 274
# rewrite commit 275
