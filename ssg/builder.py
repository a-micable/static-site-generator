"""Site build orchestration with collections, tags, archives, and pagination."""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from ssg.assets import AssetManifest, AssetProcessor, save_manifest
from ssg.config import CollectionConfig, SiteConfig
from ssg.content import ContentIndex, taxonomy_url
from ssg.feed import write_feed
from ssg.parser import Page, slugify
from ssg.plugins import PluginManager
from ssg.renderer import TemplateRenderer
from ssg.search import write_search_index
from ssg.sitemap import write_sitemap

logger = logging.getLogger(__name__)

CACHE_FILENAME = ".ssg-cache.json"
ASSET_MANIFEST_FILENAME = ".ssg-assets.json"


@dataclass
class BuildCache:
    """Tracks source file hashes for incremental builds."""

    file_hashes: dict[str, str] = field(default_factory=dict)
    template_hashes: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, dict[str, str]]:
        return {
            "file_hashes": self.file_hashes,
            "template_hashes": self.template_hashes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> BuildCache:
        file_hashes = data.get("file_hashes", {})
        template_hashes = data.get("template_hashes", {})
        return cls(
            file_hashes=dict(file_hashes) if isinstance(file_hashes, dict) else {},
            template_hashes=(
                dict(template_hashes) if isinstance(template_hashes, dict) else {}
            ),
        )


@dataclass
class BuildResult:
    """Result of a site build."""

    pages_built: int = 0
    pages_skipped: int = 0
    incremental: bool = False
    output_dir: Path = field(default_factory=lambda: Path("dist"))


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_cache(output_dir: Path) -> BuildCache:
    cache_path = output_dir / CACHE_FILENAME
    if not cache_path.is_file():
        return BuildCache()
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        return BuildCache.from_dict(data)
    except (json.JSONDecodeError, TypeError):
        logger.warning("Invalid build cache, rebuilding all")
        return BuildCache()


def _save_cache(output_dir: Path, cache: BuildCache) -> None:
    cache_path = output_dir / CACHE_FILENAME
    cache_path.write_text(json.dumps(cache.to_dict(), indent=2), encoding="utf-8")


def _collect_template_hashes(templates_dir: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    if not templates_dir.is_dir():
        return hashes
    for path in sorted(templates_dir.rglob("*")):
        if path.is_file() and not path.name.startswith("."):
            key = str(path.relative_to(templates_dir)).replace("\\", "/")
            hashes[key] = _file_hash(path)
    return hashes


def _templates_changed(cache: BuildCache, templates_dir: Path) -> bool:
    return _collect_template_hashes(templates_dir) != cache.template_hashes


def _needs_rebuild(path: Path, cache: BuildCache, force: bool) -> bool:
    if force:
        return True
    return cache.file_hashes.get(str(path)) != _file_hash(path)


def _sort_pages(pages: list[Page], sort_by: str, sort_order: str) -> list[Page]:
    reverse = sort_order.lower() == "desc"

    def sort_key(page: Page) -> Any:
        if sort_by == "date":
            return page.date or datetime.min
        if sort_by == "title":
            return page.title.lower()
        return page.metadata.get(sort_by, "")

    return sorted(pages, key=sort_key, reverse=reverse)


def _paginate(items: list[Any], per_page: int) -> list[list[Any]]:
    if per_page <= 0:
        return [items]
    return [items[i : i + per_page] for i in range(0, len(items), per_page)]


def _page_output_path(output_dir: Path, url: str) -> Path:
    clean = url.strip("/")
    if clean.endswith(".html") or not clean:
        return output_dir / clean if clean else output_dir / "index.html"
    return output_dir / clean / "index.html"


def _write_page(output_path: Path, html: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


class SiteBuilder:
    """Orchestrates the full static site build process."""

    def __init__(self, config: SiteConfig) -> None:
        self.config = config
        self.renderer = TemplateRenderer(config.templates_path, config.theme_templates_path)
        self.plugins = PluginManager(config)
        self.all_pages: list[Page] = []
        self.content_index = ContentIndex([])
        self.site_context: dict[str, Any] = {}

    def _build_site_context(self, asset_manifest: AssetManifest) -> dict[str, Any]:
        return {
            "title": self.config.title,
            "base_url": self.config.base_url,
            "description": self.config.description,
            "language": self.config.language,
            "author": self.config.author,
            "assets": asset_manifest.to_dict(),
        }

    def _load_pages(self) -> list[Page]:
        self.content_index = ContentIndex.from_config(self.config)
        self.plugins.dispatch("content_indexed", content_index=self.content_index)
        pages = self.content_index.pages
        self.all_pages = pages
        return pages

    def build(self, incremental: bool = False, clean: bool = False) -> BuildResult:
        """Build the entire site."""
        output_dir = self.config.output_path
        result = BuildResult(incremental=incremental, output_dir=output_dir)

        if clean and output_dir.exists():
            shutil.rmtree(output_dir)
            logger.info("Cleaned output directory: %s", output_dir)

        cache = _load_cache(output_dir) if incremental else BuildCache()
        templates_dirty = incremental and _templates_changed(
            cache, self.config.templates_path
        )

        asset_manifest = self._process_assets(output_dir, incremental)
        self.plugins.dispatch("assets_processed", manifest=asset_manifest)
        save_manifest(asset_manifest, output_dir / ASSET_MANIFEST_FILENAME)

        self.site_context = self._build_site_context(asset_manifest)
        pages = self._load_pages()
        published = [p for p in pages if p.is_published]

        for coll in self.config.collections:
            coll_pages = self.content_index.by_collection(coll.name)
            sorted_pages = _sort_pages(coll_pages, coll.sort_by, coll.sort_order)

            for page in sorted_pages:
                force = templates_dirty or not incremental
                if incremental and not force:
                    if not _needs_rebuild(page.source_path, cache, False):
                        result.pages_skipped += 1
                        continue

                html = self._render_page(page)
                out = _page_output_path(output_dir, page.url)
                _write_page(out, html)
                cache.file_hashes[str(page.source_path)] = _file_hash(page.source_path)
                result.pages_built += 1

            if coll.archive and sorted_pages:
                self._build_archive(coll, sorted_pages, output_dir, cache, templates_dirty, incremental, result)

            if coll.tags and sorted_pages:
                self._build_tags(coll, sorted_pages, output_dir, cache, templates_dirty, incremental, result)

            for taxonomy in self.config.taxonomies:
                if taxonomy != "tags" and sorted_pages:
                    self._build_taxonomy(coll, taxonomy, output_dir, templates_dirty, incremental, result)

            if coll.per_page > 0 and sorted_pages:
                self._build_pagination(coll, sorted_pages, output_dir, cache, templates_dirty, incremental, result)

        standalone = [p for p in published if not p.collection]
        for page in standalone:
            force = templates_dirty or not incremental
            if incremental and not force:
                if not _needs_rebuild(page.source_path, cache, False):
                    result.pages_skipped += 1
                    continue

            html = self._render_page(page)
            out = _page_output_path(output_dir, page.url)
            _write_page(out, html)
            cache.file_hashes[str(page.source_path)] = _file_hash(page.source_path)
            result.pages_built += 1

        write_sitemap(output_dir / "sitemap.xml", self.config.base_url, published)
        write_feed(
            output_dir / "feed.xml",
            self.config.title,
            self.config.base_url,
            self.config.description,
            self.config.language,
            published,
            self.config.author,
            self.config.feed_items,
        )
        if self.config.search_index:
            write_search_index(output_dir / "search.json", published, self.config.base_url)

        cache.template_hashes = _collect_template_hashes(self.config.templates_path)
        _save_cache(output_dir, cache)
        self.plugins.dispatch("build_finished", result=result, pages=published)

        logger.info(
            "Build complete: %d built, %d skipped",
            result.pages_built,
            result.pages_skipped,
        )
        return result

    def _process_assets(self, output_dir: Path, incremental: bool) -> AssetManifest:
        manifest = AssetManifest()
        asset_dirs = [self.config.theme_assets_path, self.config.assets_path]
        for asset_dir in asset_dirs:
            if asset_dir is None:
                continue
            processed = AssetProcessor(asset_dir, output_dir / "assets").process(
                incremental=incremental
            )
            manifest.mappings.update(processed.mappings)
        return manifest

    def _render_page(self, page: Page) -> str:
        html = self.renderer.render_page(page, self.site_context, page.layout)
        context = self.plugins.dispatch("page_rendered", page=page, html=html)
        result = context.data.get("result")
        return result if isinstance(result, str) else html

    def _build_archive(
        self,
        coll: CollectionConfig,
        pages: list[Page],
        output_dir: Path,
        cache: BuildCache,
        templates_dirty: bool,
        incremental: bool,
        result: BuildResult,
    ) -> None:
        archive_url = f"{coll.output}/archive/index.html"
        if incremental and not templates_dirty:
            archive_path = _page_output_path(output_dir, archive_url)
            if archive_path.is_file():
                result.pages_skipped += 1
                return

        html = self.renderer.render(
            "archive.html",
            {
                "site": self.site_context,
                "collection": coll,
                "pages": pages,
                "title": f"Archive - {self.config.title}",
            },
        )
        _write_page(_page_output_path(output_dir, archive_url), html)
        result.pages_built += 1

    def _build_tags(
        self,
        coll: CollectionConfig,
        pages: list[Page],
        output_dir: Path,
        cache: BuildCache,
        templates_dirty: bool,
        incremental: bool,
        result: BuildResult,
    ) -> None:
        tag_map: dict[str, list[Page]] = {}
        for page in pages:
            for tag in page.tags:
                tag_map.setdefault(tag, []).append(page)

        for tag, tagged_pages in sorted(tag_map.items()):
            tag_slug = slugify(tag)
            tag_url = f"{coll.output}/tags/{tag_slug}/index.html"

            if incremental and not templates_dirty:
                tag_path = _page_output_path(output_dir, tag_url)
                if tag_path.is_file():
                    result.pages_skipped += 1
                    continue

            html = self.renderer.render(
                "tag.html",
                {
                    "site": self.site_context,
                    "collection": coll,
                    "tag": tag,
                    "pages": tagged_pages,
                    "title": f"Tag: {tag} - {self.config.title}",
                },
            )
            _write_page(_page_output_path(output_dir, tag_url), html)
            result.pages_built += 1

        tags_index_url = f"{coll.output}/tags/index.html"
        html = self.renderer.render(
            "tags.html",
            {
                "site": self.site_context,
                "collection": coll,
                "tags": sorted(tag_map.keys()),
                "title": f"Tags - {self.config.title}",
            },
        )
        _write_page(_page_output_path(output_dir, tags_index_url), html)
        result.pages_built += 1

    def _build_taxonomy(
        self,
        coll: CollectionConfig,
        taxonomy: str,
        output_dir: Path,
        templates_dirty: bool,
        incremental: bool,
        result: BuildResult,
    ) -> None:
        term_map = self.content_index.taxonomy_terms(taxonomy, coll.name)
        if not term_map:
            return

        template_name = "taxonomy.html"
        if not self.renderer.template_exists(template_name):
            template_name = "tag.html"

        for term, term_pages in sorted(term_map.items()):
            url = taxonomy_url(coll, taxonomy, term)
            if incremental and not templates_dirty:
                term_path = _page_output_path(output_dir, url)
                if term_path.is_file():
                    result.pages_skipped += 1
                    continue

            html = self.renderer.render(
                template_name,
                {
                    "site": self.site_context,
                    "collection": coll,
                    "taxonomy": taxonomy,
                    "tag": term,
                    "term": term,
                    "pages": term_pages,
                    "title": f"{taxonomy.title()}: {term} - {self.config.title}",
                },
            )
            _write_page(_page_output_path(output_dir, url), html)
            result.pages_built += 1

        index_template = "taxonomies.html"
        if not self.renderer.template_exists(index_template):
            index_template = "tags.html"
        index_url = f"{coll.output}/{taxonomy}/index.html"
        html = self.renderer.render(
            index_template,
            {
                "site": self.site_context,
                "collection": coll,
                "taxonomy": taxonomy,
                "tags": sorted(term_map.keys()),
                "terms": sorted(term_map.keys()),
                "title": f"{taxonomy.title()} - {self.config.title}",
            },
        )
        _write_page(_page_output_path(output_dir, index_url), html)
        result.pages_built += 1

    def _build_pagination(
        self,
        coll: CollectionConfig,
        pages: list[Page],
        output_dir: Path,
        cache: BuildCache,
        templates_dirty: bool,
        incremental: bool,
        result: BuildResult,
    ) -> None:
        chunks = _paginate(pages, coll.per_page)
        total_pages = len(chunks)

        for idx, chunk in enumerate(chunks):
            page_num = idx + 1
            if page_num == 1:
                list_url = f"{coll.output}/index.html"
            else:
                list_url = f"{coll.output}/page/{page_num}/index.html"

            html = self.renderer.render(
                "list.html",
                {
                    "site": self.site_context,
                    "collection": coll,
                    "pages": chunk,
                    "page_num": page_num,
                    "total_pages": total_pages,
                    "title": f"{coll.name.title()} - {self.config.title}",
                },
            )
            _write_page(_page_output_path(output_dir, list_url), html)
            result.pages_built += 1


def build_site(
    source_root: Path,
    incremental: bool = False,
    clean: bool = False,
) -> BuildResult:
    """Build a site from the given source root."""
    from ssg.config import load_config

    config = load_config(source_root)
    builder = SiteBuilder(config)
    return builder.build(incremental=incremental, clean=clean)
# rewrite commit 229
# rewrite commit 230
# rewrite commit 231
# rewrite commit 232
# rewrite commit 233
# rewrite commit 234
