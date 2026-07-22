"""Shared pytest fixtures."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_SITE = ROOT / "example-site"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def project_root() -> Path:
    return ROOT


@pytest.fixture
def example_site(tmp_path: Path) -> Path:
    dest = tmp_path / "site"
    shutil.copytree(EXAMPLE_SITE, dest)
    return dest


@pytest.fixture
def build_site(example_site: Path) -> Path:
    result = subprocess.run(
        [sys.executable, "-m", "ssg.cli", "build", str(example_site)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return example_site / "dist"


@pytest.fixture
def ssg_cli() -> list[str]:
    return [sys.executable, "-m", "ssg.cli"]
# rewrite commit 373
# rewrite commit 374
# rewrite commit 375
# rewrite commit 376
# rewrite commit 377
# rewrite commit 378
# rewrite commit 379
# rewrite commit 380
# rewrite commit 381
# rewrite commit 382
# rewrite commit 383
# rewrite commit 384
