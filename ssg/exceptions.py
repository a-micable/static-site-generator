"""Custom exceptions for the static site generator."""


class SSGError(Exception):
    """Base exception for all SSG errors."""


class ConfigError(SSGError):
    """Raised when site configuration is invalid or missing."""


class ParseError(SSGError):
    """Raised when content parsing fails."""


class RenderError(SSGError):
    """Raised when template rendering fails."""


class BuildError(SSGError):
    """Raised when the build process fails."""


class PluginError(SSGError):
    """Raised when plugin loading or execution fails."""
# rewrite commit 277
