"""Tests for the React dashboard JSON API."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ssg.api import SiteApi

@pytest.fixture
def api(example_site: Path) -> SiteApi:
    return SiteApi(example_site)

class TestSiteApi:
    def test_get_config(self, api: SiteApi) -> None:
        config = api.get_config()
        assert config["title"] == "Example Site"
        assert config["base_url"] == "https://example.com"

    def test_list_posts(self, api: SiteApi) -> None:
        posts = api.list_posts("posts")
        assert len(posts) >= 3
        titles = {post["title"] for post in posts}
        assert "First Post" in titles

    def test_create_and_delete_post(self, api: SiteApi, tmp_path: Path) -> None:
        created = api.create_post({"title": "Temp Post", "collection": "posts"})
        assert created["title"] == "Temp Post"
        path = created["path"]
        api.delete_post(path)
        with pytest.raises(FileNotFoundError):
            api.get_post(path)

    def test_toggle_draft(self, api: SiteApi) -> None:
        posts = api.list_posts("posts")
        first = posts[0]
        updated = api.toggle_draft(first["path"])
        assert updated["draft"] is not first["draft"]

    def test_preview_markdown(self, api: SiteApi) -> None:
        result = api.preview_markdown("# Hello")
        assert "<h1" in result["html"]

    def test_build_status(self, api: SiteApi) -> None:
        status = api.build_status()
        assert status["running"] is False

    def test_dispatch_config(self, api: SiteApi) -> None:
        status, payload = api.dispatch("GET", "/api/config")
        assert status == 200
        assert payload["title"] == "Example Site"

    def test_dispatch_preview(self, api: SiteApi) -> None:
        body = json.dumps({"markdown": "**bold**"}).encode("utf-8")
        status, payload = api.dispatch("POST", "/api/preview", body)
        assert status == 200
        assert "strong" in payload["html"]
