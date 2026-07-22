"""Tests for asset fingerprinting."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


class TestAssets:
    def test_assets_copied_with_fingerprint(self, build_site: Path) -> None:
        assets = list((build_site / "assets").glob("*.css"))
        assert len(assets) == 1
        name = assets[0].name
        assert name.startswith("style.")
        assert name.endswith(".css")
        assert len(name) > len("style.css")

    def test_asset_manifest_written(self, example_site: Path) -> None:
        subprocess.run(
            [sys.executable, "-m", "ssg.cli", "build", str(example_site)],
            check=True,
            capture_output=True,
        )
        manifest_path = example_site / "dist" / ".ssg-assets.json"
        assert manifest_path.is_file()
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert "style.css" in data

    def test_new_asset_gets_new_fingerprint(self, example_site: Path) -> None:
        subprocess.run(
            [sys.executable, "-m", "ssg.cli", "build", str(example_site)],
            check=True,
            capture_output=True,
        )
        css_files = list((example_site / "dist" / "assets").glob("style.*.css"))
        old_name = css_files[0].name

        (example_site / "assets" / "extra.js").write_text(
            "console.log('hi');", encoding="utf-8"
        )
        subprocess.run(
            [sys.executable, "-m", "ssg.cli", "build", str(example_site)],
            check=True,
            capture_output=True,
        )
        js_files = list((example_site / "dist" / "assets").glob("extra.*.js"))
        assert len(js_files) == 1
        assert old_name in [p.name for p in (example_site / "dist" / "assets").glob("style.*.css")]
# rewrite commit 397
# rewrite commit 398
