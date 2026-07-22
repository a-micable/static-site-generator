"""Tests for CLI commands."""

from __future__ import annotations

import subprocess
import sys
import json
from pathlib import Path


class TestCLI:
    def test_help(self, ssg_cli: list[str]) -> None:
        result = subprocess.run(
            [*ssg_cli, "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "build" in result.stdout
        assert "init" in result.stdout
        assert "serve" in result.stdout

    def test_build_help(self, ssg_cli: list[str]) -> None:
        result = subprocess.run(
            [*ssg_cli, "build", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "incremental" in result.stdout

    def test_init_creates_site_structure(self, tmp_path: Path, ssg_cli: list[str]) -> None:
        target = tmp_path / "new-site"
        result = subprocess.run(
            [*ssg_cli, "init", str(target)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert (target / "ssg.yaml").is_file()
        assert (target / "content" / "index.md").is_file()
        assert (target / "templates" / "base.html").is_file()
        assert (target / "assets" / "style.css").is_file()

    def test_init_refuses_nonempty_directory(self, tmp_path: Path, ssg_cli: list[str]) -> None:
        target = tmp_path / "existing"
        target.mkdir()
        (target / "file.txt").write_text("x", encoding="utf-8")
        result = subprocess.run(
            [*ssg_cli, "init", str(target)],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

    def test_init_force_over_nonempty(self, tmp_path: Path, ssg_cli: list[str]) -> None:
        target = tmp_path / "existing"
        target.mkdir()
        (target / "file.txt").write_text("x", encoding="utf-8")
        result = subprocess.run(
            [*ssg_cli, "init", "--force", str(target)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert (target / "ssg.yaml").is_file()

    def test_build_example_site(self, example_site: Path, ssg_cli: list[str]) -> None:
        result = subprocess.run(
            [*ssg_cli, "build", str(example_site)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert (example_site / "dist" / "index.html").is_file()

    def test_build_missing_config_fails(self, tmp_path: Path, ssg_cli: list[str]) -> None:
        result = subprocess.run(
            [*ssg_cli, "build", str(tmp_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

    def test_inspect_outputs_content_stats(self, example_site: Path, ssg_cli: list[str]) -> None:
        result = subprocess.run(
            [*ssg_cli, "inspect", str(example_site)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["site"]["title"] == "Example Site"
        assert data["content"]["collections"] == {"posts": 3}
        assert data["content"]["taxonomies"]["categories"]["releases"] == 2
# rewrite commit 421
# rewrite commit 422
# rewrite commit 423
# rewrite commit 424
# rewrite commit 425
# rewrite commit 426
# rewrite commit 427
