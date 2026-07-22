"""Tests for configuration validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from ssg.config import load_config
from ssg.exceptions import ConfigError


class TestConfigValidation:
    def test_rejects_parent_directory_output(self, tmp_path: Path) -> None:
        (tmp_path / "ssg.yaml").write_text(
            "title: Bad\nbase_url: https://example.com\noutput_dir: ../dist\n",
            encoding="utf-8",
        )

        with pytest.raises(ConfigError, match="output_dir"):
            load_config(tmp_path)

    def test_rejects_invalid_taxonomies(self, tmp_path: Path) -> None:
        (tmp_path / "ssg.yaml").write_text(
            "title: Bad\nbase_url: https://example.com\ntaxonomies: tags\n",
            encoding="utf-8",
        )

        with pytest.raises(ConfigError, match="taxonomies"):
            load_config(tmp_path)

    def test_defaults_enable_search_and_common_taxonomies(self, example_site: Path) -> None:
        config = load_config(example_site)

        assert config.search_index is True
        assert config.taxonomies == ["tags", "categories"]

    def test_rejects_theme_path_traversal(self, tmp_path: Path) -> None:
        (tmp_path / "ssg.yaml").write_text(
            "title: Bad\nbase_url: https://example.com\ntheme: ../outside\n",
            encoding="utf-8",
        )

        with pytest.raises(ConfigError, match="theme"):
            load_config(tmp_path)
# rewrite commit 433
# rewrite commit 434
# rewrite commit 435
# rewrite commit 436
