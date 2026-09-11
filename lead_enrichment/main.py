# lead_enrichment/main.py
"""Command‑line interface for the Autonomous Lead Enrichment Agent.

Usage example::

    python -m lead_enrichment.main --domains postman.com supabase.com vapi.ai

The script reads the list of domains, crawls each site, attempts to extract
structured information via the configured LLM, and writes a JSON file
``output.json`` in the current working directory.  If crawling fails or the LLM
returns an error (e.g., exhausted credits), a minimal placeholder record with a
confidence score of 0.0 is emitted so that the overall run never aborts.
"""

import argparse
import asyncio
import json
import logging
from pathlib import Path

from .config import load_config
from .crawler import process_domain
from .llm import get_llm_client
from .models import CompanyInfo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

# ---------------------------------------------------------------------------
# Helper to produce a placeholder when we cannot obtain real data.
# ---------------------------------------------------------------------------

def placeholder_record(domain: str) -> dict:
    return {
        "domain": domain,
        "overview": "",
        "target_audience": "",
        "contact_points": [],
        "leadership": [],
        "confidence_score": 0.0,
    }

async def run_domain(domain: str, llm_client) -> dict:
    """Crawl *domain*, extract data via the LLM, and return a dict.

    Any failure – network timeout, missing content, or LLM error – results in a
    placeholder record so that processing continues for the remaining domains.
    """
    try:
        content = await process_domain(domain)
        if not content:
            logging.warning("No content extracted for %s", domain)
            return placeholder_record(domain)
        try:
            info: CompanyInfo = await llm_client.extract_info(domain, content)
            return info.model_dump()
        except Exception as exc:  # LLM failure (e.g., rate‑limit, malformed response)
            logging.error("LLM extraction failed for %s: %s", domain, exc)
            return placeholder_record(domain)
    except Exception as exc:  # Unexpected failure in crawling or elsewhere
        logging.exception("Failed processing %s", domain)
        return placeholder_record(domain)

async def main_async(domains: list[str]):
    cfg = load_config()
    llm_client = get_llm_client(cfg)
    tasks = [run_domain(d, llm_client) for d in domains]
    results = await asyncio.gather(*tasks)
    out_path = Path("output.json")
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    logging.info("Results written to %s", out_path)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Autonomous Lead Enrichment Agent")
    parser.add_argument(
        "--domains",
        nargs="+",
        required=True,
        help="List of company domains to process",
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main_async(args.domains))
