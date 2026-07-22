"""Tests for plugin loading and build hooks."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from ssg.config import load_config
from ssg.exceptions import PluginError
from ssg.plugins import PluginManager


class TestPlugins:
    def test_page_rendered_plugin_can_transform_html(self, example_site: Path) -> None:
        plugin_dir = example_site / "plugins"
        plugin_dir.mkdir()
        (plugin_dir / "banner.py").write_text(
            "PLUGIN_NAME = 'banner'\n"
            "def page_rendered(context):\n"
            "    return context.data['html'].replace('</body>', '<aside>Plugin banner</aside></body>')\n",
            encoding="utf-8",
        )
        config = example_site / "ssg.yaml"
        config.write_text(
            config.read_text(encoding="utf-8") + "\nplugins:\n  - plugins/banner.py\n",
            encoding="utf-8",
        )

        result = subprocess.run(
            [sys.executable, "-m", "ssg.cli", "build", str(example_site)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, result.stderr
        html = (example_site / "dist" / "index.html").read_text(encoding="utf-8")
        assert "Plugin banner" in html

    def test_missing_plugin_fails_build(self, example_site: Path) -> None:
        config = example_site / "ssg.yaml"
        config.write_text(
            config.read_text(encoding="utf-8") + "\nplugins:\n  - plugins/missing.py\n",
            encoding="utf-8",
        )

        result = subprocess.run(
            [sys.executable, "-m", "ssg.cli", "build", str(example_site)],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "Plugin file not found" in result.stderr

    def test_unknown_hook_is_rejected(self, example_site: Path) -> None:
        manager = PluginManager(load_config(example_site))

        with pytest.raises(PluginError, match="Unknown plugin hook"):
            manager.dispatch("not_a_hook")
# rewrite commit 493
# rewrite commit 494
# rewrite commit 495
# rewrite commit 496
# rewrite commit 497
# rewrite commit 498
# rewrite commit 499
# rewrite commit 500
# rewrite commit 501
# rewrite commit 502
# rewrite commit 503
