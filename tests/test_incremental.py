"""Tests for incremental build behavior."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path


class TestIncrementalBuild:
    def test_incremental_skips_unchanged_files(self, example_site: Path) -> None:
        subprocess.run(
            [sys.executable, "-m", "ssg.cli", "build", str(example_site)],
            check=True,
            capture_output=True,
        )
        first_post = example_site / "dist" / "posts" / "first-post" / "index.html"
        mtime_before = first_post.stat().st_mtime

        time.sleep(0.05)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ssg.cli",
                "build",
                "--incremental",
                str(example_site),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "skipped" in result.stdout.lower() or "Built 0 pages" in result.stdout
        assert first_post.stat().st_mtime == mtime_before

    def test_incremental_rebuilds_changed_content(self, example_site: Path) -> None:
        subprocess.run(
            [sys.executable, "-m", "ssg.cli", "build", str(example_site)],
            check=True,
            capture_output=True,
        )
        md_path = example_site / "content" / "posts" / "first-post.md"
        original = md_path.read_text(encoding="utf-8")
        md_path.write_text(
            original.replace("First Post", "Updated First Post"),
            encoding="utf-8",
        )

        subprocess.run(
            [
                sys.executable,
                "-m",
                "ssg.cli",
                "build",
                "--incremental",
                str(example_site),
            ],
            check=True,
            capture_output=True,
        )
        html = (
            example_site / "dist" / "posts" / "first-post" / "index.html"
        ).read_text(encoding="utf-8")
        assert "Updated First Post" in html

    def test_incremental_rebuilds_on_template_change(self, example_site: Path) -> None:
        subprocess.run(
            [sys.executable, "-m", "ssg.cli", "build", str(example_site)],
            check=True,
            capture_output=True,
        )
        base = example_site / "templates" / "base.html"
        content = base.read_text(encoding="utf-8")
        base.write_text(content.replace("Built with SSG", "Built with SSG v2"), encoding="utf-8")

        subprocess.run(
            [
                sys.executable,
                "-m",
                "ssg.cli",
                "build",
                "--incremental",
                str(example_site),
            ],
            check=True,
            capture_output=True,
        )
        index = (example_site / "dist" / "index.html").read_text(encoding="utf-8")
        assert "Built with SSG v2" in index

    def test_build_cache_created(self, example_site: Path) -> None:
        subprocess.run(
            [sys.executable, "-m", "ssg.cli", "build", str(example_site)],
            check=True,
            capture_output=True,
        )
        cache = example_site / "dist" / ".ssg-cache.json"
        assert cache.is_file()
# rewrite commit 469
# rewrite commit 470
# rewrite commit 471
# rewrite commit 472
# rewrite commit 473
