"""Tests for RSS feed and sitemap output."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

class TestFeedAndSitemap:
    def test_sitemap_valid_xml(self, build_site: Path) -> None:
        sitemap_path = build_site / "sitemap.xml"
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = root.findall("sm:url", ns)
        assert len(urls) >= 4
        locs = [u.find("sm:loc", ns).text for u in urls]
        assert any("first-post" in loc for loc in locs if loc)

    def test_sitemap_contains_base_url(self, build_site: Path) -> None:
        text = (build_site / "sitemap.xml").read_text(encoding="utf-8")
        assert "https://example.com" in text

    def test_rss_valid_xml(self, build_site: Path) -> None:
        feed_path = build_site / "feed.xml"
        tree = ET.parse(feed_path)
        root = tree.getroot()
        assert root.tag == "rss"
        channel = root.find("channel")
        assert channel is not None
        title = channel.find("title")
        assert title is not None
        assert title.text == "Example Site"

    def test_rss_contains_items(self, build_site: Path) -> None:
        tree = ET.parse(build_site / "feed.xml")
        items = tree.getroot().find("channel").findall("item")
        assert len(items) >= 3
        titles = [item.find("title").text for item in items]
        assert "Third Post" in titles

    def test_rss_items_sorted_newest_first(self, build_site: Path) -> None:
        tree = ET.parse(build_site / "feed.xml")
        items = tree.getroot().find("channel").findall("item")
        titles = [item.find("title").text for item in items]
        assert titles[0] == "Third Post"

    def test_rss_item_has_link_and_guid(self, build_site: Path) -> None:
        tree = ET.parse(build_site / "feed.xml")
        item = tree.getroot().find("channel").findall("item")[0]
        link = item.find("link")
        guid = item.find("guid")
        assert link is not None and link.text.startswith("https://example.com/")
        assert guid is not None and guid.text == link.text
