"""RSS feed generation."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence
from xml.etree import ElementTree as ET

from ssg.parser import Page

logger = logging.getLogger(__name__)


def _format_rfc822(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime("%a, %d %b %Y %H:%M:%S %z")


def _normalize_datetime(dt: datetime) -> datetime:
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def build_rss_xml(
    title: str,
    base_url: str,
    description: str,
    language: str,
    pages: Sequence[Page],
    author: str = "",
) -> str:
    """Generate RSS 2.0 feed XML from pages."""
    rss = ET.Element("rss")
    rss.set("version", "2.0")

    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = title
    ET.SubElement(channel, "link").text = base_url
    ET.SubElement(channel, "description").text = description
    ET.SubElement(channel, "language").text = language
    if author:
        ET.SubElement(channel, "author").text = author

    published = [p for p in pages if p.is_published and p.url]
    published.sort(
        key=lambda p: _normalize_datetime(p.date) if p.date else datetime.min,
        reverse=True,
    )

    for page in published:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = page.title
        ET.SubElement(item, "link").text = (
            f"{base_url.rstrip('/')}/{page.url.lstrip('/')}"
        )
        ET.SubElement(item, "description").text = page.content_html
        ET.SubElement(item, "guid").text = (
            f"{base_url.rstrip('/')}/{page.url.lstrip('/')}"
        )
        if page.date:
            ET.SubElement(item, "pubDate").text = _format_rfc822(page.date)

    ET.indent(rss, space="  ")
    xml_bytes = ET.tostring(rss, encoding="unicode", xml_declaration=False)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_bytes


def write_feed(
    output_path: Path,
    title: str,
    base_url: str,
    description: str,
    language: str,
    pages: Sequence[Page],
    author: str = "",
    max_items: int = 20,
) -> None:
    """Write RSS feed to the output directory."""
    limited = [p for p in pages if p.is_published]
    limited.sort(
        key=lambda p: _normalize_datetime(p.date) if p.date else datetime.min,
        reverse=True,
    )
    limited = limited[:max_items]
    xml = build_rss_xml(title, base_url, description, language, limited, author)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(xml, encoding="utf-8")
    logger.info("Wrote RSS feed: %s", output_path)
# rewrite commit 289
# rewrite commit 290
# rewrite commit 291
