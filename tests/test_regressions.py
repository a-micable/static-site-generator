"""Regression tests for lower-level error paths and helpers."""

from __future__ import annotations

from pathlib import Path

import pytest
from watchdog.events import FileModifiedEvent

from ssg.assets import AssetManifest, load_manifest, resolve_asset_url, save_manifest
from ssg.exceptions import ParseError, RenderError
from ssg.parser import parse_page, split_frontmatter
from ssg.renderer import TemplateRenderer
from ssg.watcher import SiteWatcher


class TestRegressionCoverage:
    def test_invalid_frontmatter_raises_parse_error(self) -> None:
        with pytest.raises(ParseError):
            split_frontmatter("---\n:\n---\nBody")

    def test_date_parsing_and_custom_taxonomy_metadata(self, tmp_path: Path) -> None:
        path = tmp_path / "post.md"
        page = parse_page(
            path,
            "---\n"
            "title: Metadata\n"
            "date: 2024-01-01T12:30:00\n"
            "taxonomy_series: Launch Notes\n"
            "---\n\n"
            "Body",
        )

        assert page.date is not None
        assert page.taxonomies["series"] == ["Launch Notes"]

    def test_asset_manifest_round_trip_and_url_resolution(self, tmp_path: Path) -> None:
        manifest_path = tmp_path / "manifest.json"
        manifest = AssetManifest({"style.css": "style.abc123.css"})

        save_manifest(manifest, manifest_path)
        loaded = load_manifest(manifest_path)

        assert resolve_asset_url("/style.css", loaded) == "style.abc123.css"
        assert resolve_asset_url("/missing.css", loaded) == "/missing.css"

    def test_renderer_reports_missing_template(self, tmp_path: Path) -> None:
        renderer = TemplateRenderer(tmp_path)

        with pytest.raises(RenderError, match="Template not found"):
            renderer.render("missing.html", {})

    def test_watcher_ignores_untracked_extensions(self) -> None:
        called = False

        def callback() -> None:
            nonlocal called
            called = True

        watcher = SiteWatcher(callback, debounce_seconds=0.01)
        watcher.on_any_event(FileModifiedEvent("/tmp/file.tmp"))

        assert called is False
# rewrite commit 505
# rewrite commit 506
# rewrite commit 507
# rewrite commit 508
# rewrite commit 509
# rewrite commit 510
# rewrite commit 511
# rewrite commit 512
# rewrite commit 513
# rewrite commit 514
# rewrite commit 515
