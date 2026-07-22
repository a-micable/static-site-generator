"""Tests for theme template and asset resolution."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _append_theme_config(site: Path) -> None:
    config = site / "ssg.yaml"
    config.write_text(
        config.read_text(encoding="utf-8") + "\ntheme: editorial\n",
        encoding="utf-8",
    )


def _write_theme(site: Path, marker: str = "Theme Base") -> None:
    theme = site / "themes" / "editorial"
    (theme / "templates").mkdir(parents=True)
    (theme / "assets").mkdir()
    (theme / "templates" / "base.html").write_text(
        "<!DOCTYPE html><html><body>"
        f"<header>{marker}</header>"
        "<main>{% block content %}{% endblock %}</main>"
        "</body></html>",
        encoding="utf-8",
    )
    (theme / "assets" / "theme.css").write_text(
        "body { color: #222; }\n",
        encoding="utf-8",
    )


class TestThemes:
    def test_theme_templates_are_used_as_fallback(self, example_site: Path) -> None:
        _append_theme_config(example_site)
        _write_theme(example_site)
        (example_site / "templates" / "base.html").unlink()

        result = subprocess.run(
            [sys.executable, "-m", "ssg.cli", "build", str(example_site)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, result.stderr
        html = (example_site / "dist" / "index.html").read_text(encoding="utf-8")
        manifest = json.loads(
            (example_site / "dist" / ".ssg-assets.json").read_text(encoding="utf-8")
        )
        assert "Theme Base" in html
        assert "theme.css" in manifest

    def test_site_templates_override_theme_templates(self, example_site: Path) -> None:
        _append_theme_config(example_site)
        _write_theme(example_site, marker="Theme Should Not Render")

        result = subprocess.run(
            [sys.executable, "-m", "ssg.cli", "build", str(example_site)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, result.stderr
        html = (example_site / "dist" / "index.html").read_text(encoding="utf-8")
        assert "Theme Should Not Render" not in html
        assert "Built with SSG" in html
# rewrite commit 517
# rewrite commit 518
# rewrite commit 519
# rewrite commit 520
