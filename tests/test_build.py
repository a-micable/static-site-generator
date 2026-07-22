"""Integration tests for site builds."""

from __future__ import annotations

import subprocess
import sys
import json
from pathlib import Path

import pytest


class TestSiteBuild:
    def test_build_creates_output_directory(self, example_site: Path) -> None:
        subprocess.run(
            [sys.executable, "-m", "ssg.cli", "build", str(example_site)],
            check=True,
            capture_output=True,
        )
        assert (example_site / "dist").is_dir()

    def test_build_generates_home_page(self, build_site: Path) -> None:
        index = build_site / "index.html"
        assert index.is_file()
        content = index.read_text(encoding="utf-8")
        assert "Welcome" in content
        assert "Example Site" in content

    def test_build_generates_post_pages(self, build_site: Path) -> None:
        first = build_site / "posts" / "first-post" / "index.html"
        assert first.is_file()
        assert "First Post" in first.read_text(encoding="utf-8")

    def test_build_generates_collection_list(self, build_site: Path) -> None:
        listing = build_site / "posts" / "index.html"
        assert listing.is_file()
        text = listing.read_text(encoding="utf-8")
        assert "Third Post" in text
        assert "Second Post" in text

    def test_build_generates_pagination(self, build_site: Path) -> None:
        page2 = build_site / "posts" / "page" / "2" / "index.html"
        assert page2.is_file()
        assert "First Post" in page2.read_text(encoding="utf-8")

    def test_build_generates_archive(self, build_site: Path) -> None:
        archive = build_site / "posts" / "archive" / "index.html"
        assert archive.is_file()
        text = archive.read_text(encoding="utf-8")
        assert "First Post" in text
        assert "Third Post" in text

    def test_build_generates_tag_pages(self, build_site: Path) -> None:
        tags_index = build_site / "posts" / "tags" / "index.html"
        assert tags_index.is_file()
        python_tag = build_site / "posts" / "tags" / "python" / "index.html"
        assert python_tag.is_file()
        assert "First Post" in python_tag.read_text(encoding="utf-8")

    def test_build_generates_category_taxonomy_pages(self, build_site: Path) -> None:
        categories_index = build_site / "posts" / "categories" / "index.html"
        release_category = build_site / "posts" / "categories" / "releases" / "index.html"
        assert categories_index.is_file()
        assert release_category.is_file()
        text = release_category.read_text(encoding="utf-8")
        assert "Second Post" in text
        assert "Third Post" in text

    def test_build_generates_search_index(self, build_site: Path) -> None:
        search = build_site / "search.json"
        assert search.is_file()
        data = json.loads(search.read_text(encoding="utf-8"))
        titles = {item["title"] for item in data}
        first = next(item for item in data if item["title"] == "First Post")
        assert {"Welcome", "First Post", "Second Post", "Third Post"} <= titles
        assert first["categories"] == ["engineering"]
        assert "First post content" in first["content"]

    def test_build_generates_sitemap(self, build_site: Path) -> None:
        sitemap = build_site / "sitemap.xml"
        assert sitemap.is_file()
        text = sitemap.read_text(encoding="utf-8")
        assert "<urlset" in text
        assert "https://example.com/" in text

    def test_build_generates_rss_feed(self, build_site: Path) -> None:
        feed = build_site / "feed.xml"
        assert feed.is_file()
        text = feed.read_text(encoding="utf-8")
        assert "<rss" in text
        assert "First Post" in text
        assert "Third Post" in text

    def test_build_fingerprints_assets(self, build_site: Path) -> None:
        assets_dir = build_site / "assets"
        css_files = list(assets_dir.glob("style.*.css"))
        assert len(css_files) == 1

    def test_template_inheritance_in_output(self, build_site: Path) -> None:
        index = build_site / "index.html"
        text = index.read_text(encoding="utf-8")
        assert "<html" in text
        assert "<main>" in text
        assert "Built with SSG" in text

    def test_markdown_rendered_to_html(self, build_site: Path) -> None:
        post = build_site / "posts" / "first-post" / "index.html"
        text = post.read_text(encoding="utf-8")
        assert "<strong>markdown</strong>" in text or "<p>" in text

    def test_clean_build_removes_old_output(self, example_site: Path) -> None:
        subprocess.run(
            [sys.executable, "-m", "ssg.cli", "build", str(example_site)],
            check=True,
            capture_output=True,
        )
        stale = example_site / "dist" / "stale-marker.txt"
        stale.write_text("old", encoding="utf-8")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "ssg.cli",
                "build",
                "--clean",
                str(example_site),
            ],
            check=True,
            capture_output=True,
        )
        assert not stale.exists()
# rewrite commit 409
# rewrite commit 410
# rewrite commit 411
# rewrite commit 412
