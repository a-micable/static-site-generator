"""XML sitemap generation."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Sequence
from xml.etree import ElementTree as ET

from ssg.parser import Page

logger = logging.getLogger(__name__)

SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def _format_lastmod(page: Page) -> str | None:
    if page.date:
        return page.date.strftime("%Y-%m-%d")
    return None


def build_sitemap_xml(base_url: str, pages: Sequence[Page]) -> str:
    """Generate sitemap XML for published pages."""
    urlset = ET.Element("urlset")
    urlset.set("xmlns", SITEMAP_NS)

    for page in pages:
        if not page.is_published or not page.url:
            continue

        url_elem = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url_elem, "loc")
        loc.text = f"{base_url.rstrip('/')}/{page.url.lstrip('/')}"

        lastmod = _format_lastmod(page)
        if lastmod:
            lm = ET.SubElement(url_elem, "lastmod")
            lm.text = lastmod

    ET.indent(urlset, space="  ")
    xml_bytes = ET.tostring(urlset, encoding="unicode", xml_declaration=False)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_bytes


def write_sitemap(output_path: Path, base_url: str, pages: Sequence[Page]) -> None:
    """Write sitemap.xml to the output directory."""
    xml = build_sitemap_xml(base_url, pages)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(xml, encoding="utf-8")
    logger.info("Wrote sitemap: %s (%d URLs)", output_path, len(pages))
# rewrite commit 349
# rewrite commit 350
# rewrite commit 351
# rewrite commit 352
# rewrite commit 353
# rewrite commit 354
