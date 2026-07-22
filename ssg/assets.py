"""Static asset handling with content fingerprinting."""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

FINGERPRINT_LENGTH = 8


@dataclass
class AssetManifest:
    """Tracks asset fingerprints for cache busting."""

    mappings: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, str]:
        return dict(self.mappings)

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> AssetManifest:
        return cls(mappings=dict(data))


def fingerprint_content(content: bytes) -> str:
    """Generate a short content hash for cache busting."""
    digest = hashlib.sha256(content).hexdigest()
    return digest[:FINGERPRINT_LENGTH]


def fingerprint_file(path: Path) -> str:
    """Generate fingerprint from file contents."""
    return fingerprint_content(path.read_bytes())


def fingerprinted_name(relative_path: Path, fingerprint: str) -> str:
    """Insert fingerprint before file extension."""
    stem = relative_path.stem
    suffix = relative_path.suffix
    return f"{stem}.{fingerprint}{suffix}"


@dataclass
class AssetProcessor:
    """Copies and fingerprints static assets."""

    source_dir: Path
    output_dir: Path

    def process(self, incremental: bool = False) -> AssetManifest:
        """Copy assets to output with fingerprinted filenames."""
        manifest = AssetManifest()
        if not self.source_dir.is_dir():
            logger.warning("Assets directory not found: %s", self.source_dir)
            return manifest

        self.output_dir.mkdir(parents=True, exist_ok=True)

        for asset_path in sorted(self.source_dir.rglob("*")):
            if not asset_path.is_file():
                continue
            if asset_path.name.startswith("."):
                continue

            relative = asset_path.relative_to(self.source_dir)
            fp = fingerprint_file(asset_path)
            fingerprinted = fingerprinted_name(relative, fp)
            dest = self.output_dir / fingerprinted
            dest.parent.mkdir(parents=True, exist_ok=True)

            if incremental and dest.is_file():
                existing_fp = fingerprint_file(dest)
                if existing_fp == fp:
                    manifest.mappings[str(relative).replace("\\", "/")] = (
                        str(Path(fingerprinted).as_posix())
                    )
                    continue

            shutil.copy2(asset_path, dest)
            manifest.mappings[str(relative).replace("\\", "/")] = (
                str(Path(fingerprinted).as_posix())
            )
            logger.debug("Processed asset: %s -> %s", relative, fingerprinted)

        logger.info("Processed %d assets", len(manifest.mappings))
        return manifest


def save_manifest(manifest: AssetManifest, path: Path) -> None:
    """Persist asset manifest to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")


def load_manifest(path: Path) -> AssetManifest:
    """Load asset manifest from disk."""
    if not path.is_file():
        return AssetManifest()
    data = json.loads(path.read_text(encoding="utf-8"))
    return AssetManifest.from_dict(data)


def resolve_asset_url(original: str, manifest: AssetManifest) -> str:
    """Resolve an asset path to its fingerprinted URL."""
    normalized = original.lstrip("/")
    if normalized in manifest.mappings:
        return manifest.mappings[normalized]
    return original
# rewrite commit 217
# rewrite commit 218
# rewrite commit 219
# rewrite commit 220
# rewrite commit 221
