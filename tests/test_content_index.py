"""Tests for content indexing, querying, and taxonomy metadata."""

from __future__ import annotations

from pathlib import Path
import json

from ssg.config import load_config
from ssg.content import ContentIndex, ContentQuery


class TestContentIndex:
    def test_index_counts_collections_and_taxonomies(self, example_site: Path) -> None:
        config = load_config(example_site)
        index = ContentIndex.from_config(config)

        stats = index.stats()

        assert stats["pages"] == 4
        assert stats["published"] == 4
        assert stats["collections"] == {"posts": 3}
        assert stats["taxonomies"]["categories"]["releases"] == 2

    def test_query_filters_by_collection_and_taxonomy(self, example_site: Path) -> None:
        config = load_config(example_site)
        index = ContentIndex.from_config(config)

        pages = index.query(
            ContentQuery(collection="posts", taxonomy="categories", term="releases")
        )

        assert [page.title for page in pages] == ["Second Post", "Third Post"]

    def test_frontmatter_slug_controls_collection_output_url(self, example_site: Path) -> None:
        post = example_site / "content" / "posts" / "custom-slug.md"
        post.write_text(
            "---\n"
            "title: Custom Slug\n"
            "slug: explicit-url\n"
            "date: 2024-04-01\n"
            "categories: engineering\n"
            "---\n\n"
            "Body.\n",
            encoding="utf-8",
        )

        config = load_config(example_site)
        index = ContentIndex.from_config(config)

        page = next(page for page in index.pages if page.title == "Custom Slug")
        assert page.url == "posts/explicit-url/index.html"

    def test_content_stats_match_golden_file(self, example_site: Path) -> None:
        config = load_config(example_site)
        index = ContentIndex.from_config(config)
        golden = json.loads(
            (Path(__file__).parent / "golden" / "inspect_example.json").read_text(
                encoding="utf-8"
            )
        )

        actual = {
            "site": {
                "title": config.title,
                "base_url": config.base_url,
            },
            "content": index.stats(),
        }

        assert actual == golden
# rewrite commit 445
# rewrite commit 446
# rewrite commit 447
