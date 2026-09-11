# lead_enrichment/processor.py
"""Utilities for cleaning raw HTML and converting it to markdown.
The goal is to strip away navigation, scripts, styles, and other boilerplate
so that the LLM sees only the core textual content of a page.
"""

from bs4 import BeautifulSoup
import html2text
import re

# Heuristic patterns for elements that are usually not useful for intelligence extraction.
_NAV_FOOTER_SELECTORS = [
    "nav",
    "header",
    "footer",
    "[role=navigation]",
    "[role=banner]",
    "[role=contentinfo]",
    ".header",
    ".footer",
    ".nav",
    "#header",
    "#footer",
    "#nav",
]

def _remove_noise(soup: BeautifulSoup) -> None:
    """Remove navigation/footer and script/style tags in‑place."""
    for selector in _NAV_FOOTER_SELECTORS:
        for el in soup.select(selector):
            el.decompose()
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

def clean_html(html: str) -> str:
    """Return a markdown string containing the main textual content of *html*.

    Steps:
    1. Parse with BeautifulSoup.
    2. Strip out noisy elements.
    3. Convert remaining HTML to markdown via ``html2text``.
    4. Collapse excessive newlines.
    """
    soup = BeautifulSoup(html, "html.parser")
    _remove_noise(soup)
    text = html2text.html2text(str(soup))
    # Collapse repeated blank lines to a maximum of two.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
