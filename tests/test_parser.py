"""Tests for frontmatter and markdown parsing via build output."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


class TestContentParsing:
    def test_yaml_frontmatter_title_used(self, example_site: Path) -> None:
        subprocess.run(
            [sys.executable, "-m", "ssg.cli", "build", str(example_site)],
            check=True,
            capture_output=True,
        )
        html = (
            example_site / "dist" / "posts" / "second-post" / "index.html"
        ).read_text(encoding="utf-8")
        assert "<h1>Second Post</h1>" in html

    def test_draft_posts_excluded_from_feed(self, example_site: Path) -> None:
        draft = example_site / "content" / "posts" / "draft-post.md"
        draft.write_text(
            "---\ntitle: Draft Post\ndate: 2024-04-01\ndraft: true\nlayout: post.html\n---\n\nHidden.\n",
            encoding="utf-8",
        )
        subprocess.run(
            [sys.executable, "-m", "ssg.cli", "build", str(example_site)],
            check=True,
            capture_output=True,
        )
        feed = (example_site / "dist" / "feed.xml").read_text(encoding="utf-8")
        assert "Draft Post" not in feed

    def test_tags_rendered_in_post(self, example_site: Path) -> None:
        subprocess.run(
            [sys.executable, "-m", "ssg.cli", "build", str(example_site)],
            check=True,
            capture_output=True,
        )
        html = (
            example_site / "dist" / "posts" / "first-post" / "index.html"
        ).read_text(encoding="utf-8")
        assert "python" in html
        assert "ssg" in html
# rewrite commit 481
# rewrite commit 482
# rewrite commit 483
# rewrite commit 484
# rewrite commit 485
# rewrite commit 486
# rewrite commit 487
# rewrite commit 488
# rewrite commit 489
