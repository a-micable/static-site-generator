"""Static Site Generator - production-grade Python SSG."""

from ssg.config import SiteConfig
from ssg.content import ContentIndex, ContentQuery
from ssg.exceptions import (
    BuildError,
    ConfigError,
    ParseError,
    PluginError,
    RenderError,
    SSGError,
)

__version__ = "1.0.0"
__all__ = [
    "BuildError",
    "ConfigError",
    "ContentIndex",
    "ContentQuery",
    "ParseError",
    "PluginError",
    "RenderError",
    "SSGError",
    "SiteConfig",
    "__version__",
]
# rewrite commit 205
# rewrite commit 206
# rewrite commit 207
