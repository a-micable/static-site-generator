"""Jinja2 template rendering with inheritance support."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape

from ssg.exceptions import RenderError
from ssg.parser import Page

logger = logging.getLogger(__name__)


class TemplateRenderer:
    """Renders pages using Jinja2 templates with inheritance."""

    def __init__(self, templates_dir: Path, theme_templates_dir: Path | None = None) -> None:
        self.templates_dir = templates_dir.resolve()
        search_paths = []
        if self.templates_dir.is_dir():
            search_paths.append(str(self.templates_dir))
        if theme_templates_dir and theme_templates_dir.is_dir():
            search_paths.append(str(theme_templates_dir.resolve()))
        if not search_paths:
            raise RenderError(f"Templates directory not found: {self.templates_dir}")

        self.env = Environment(
            loader=FileSystemLoader(search_paths),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.env.globals["range"] = range
        logger.debug("Template renderer initialized: %s", self.templates_dir)

    def render(self, template_name: str, context: dict[str, Any]) -> str:
        """Render a template with the given context."""
        try:
            template = self.env.get_template(template_name)
        except TemplateNotFound as exc:
            raise RenderError(f"Template not found: {template_name}") from exc

        try:
            return template.render(**context)
        except Exception as exc:
            raise RenderError(
                f"Failed to render template {template_name}: {exc}"
            ) from exc

    def render_page(
        self,
        page: Page,
        site: dict[str, Any],
        layout: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> str:
        """Render a content page with site context."""
        template_name = layout or page.layout or "page.html"
        context: dict[str, Any] = {
            "page": page,
            "site": site,
            "title": page.title,
            "content": page.content_html,
        }
        if extra:
            context.update(extra)
        return self.render(template_name, context)

    def template_exists(self, name: str) -> bool:
        """Check if a template file exists."""
        try:
            self.env.get_template(name)
        except TemplateNotFound:
            return False
        return True
# rewrite commit 325
# rewrite commit 326
# rewrite commit 327
# rewrite commit 328
# rewrite commit 329
# rewrite commit 330
# rewrite commit 331
# rewrite commit 332
# rewrite commit 333
# rewrite commit 334
# rewrite commit 335
