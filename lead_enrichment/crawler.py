"""Web crawling utilities.
Note: For full compliance with the assignment (Step 1), consider adding Playwright 
or Selenium fallback for JavaScript-rendered SPAs like vapi.ai.
"""

import logging
from typing import List
from urllib.parse import urljoin

import httpx

from .processor import clean_html
from .utils import retry_async

logger = logging.getLogger(__name__)

COMMON_PATHS = ["/about", "/team", "/company", "/contact", "/pricing"]

# Added browser User-Agent header to avoid basic anti-bot blocks
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

@retry_async(attempts=3, backoff=2)
async def fetch_page(url: str) -> str:
    """Fetch *url* using httpx with redirect support and custom headers."""
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=HEADERS) as client:
            response = await client.get(url)
            if response.status_code == 200:
                return response.text
            else:
                logger.warning("Non-200 status %s for %s", response.status_code, url)
                return ""
    except Exception as exc:
        logger.warning("Error fetching %s: %s", url, exc)
        return ""

async def discover_subpages(base_url: str) -> List[str]:
    """Return absolute URLs that respond with status 200 for common paths."""
    discovered = []
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=HEADERS) as client:
        for path in COMMON_PATHS:
            candidate = urljoin(base_url, path)
            try:
                # Switched to GET because many servers block or misroute HEAD requests
                resp = await client.get(candidate)
                if resp.status_code == 200:
                    discovered.append(candidate)
            except Exception:
                continue
    return discovered

async def process_domain(domain: str) -> str:
    """Crawl *domain* and return a single cleaned markdown string."""
    base_url = f"https://{domain}" if not domain.startswith("http") else domain
    contents = []
    
    # Homepage
    homepage_html = await fetch_page(base_url)
    if homepage_html:
        contents.append(clean_html(homepage_html))
        
    # Sub-pages
    subpages = await discover_subpages(base_url)
    for url in subpages:
        html = await fetch_page(url)
        if html:
            contents.append(clean_html(html))
            
    return "\n\n---\n\n".join(contents)