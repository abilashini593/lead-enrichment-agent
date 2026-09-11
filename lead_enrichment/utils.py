# lead_enrichment/utils.py
"""Utility helpers used across the Lead Enrichment project.
- retry_async: simple async retry decorator with exponential backoff.
- setup_logger: configure a module‑level logger (already used via logging.basicConfig in main).
- log_token_usage: optional helper to store token usage per domain.
"""

import asyncio
import logging
import json
from pathlib import Path
from functools import wraps
from typing import Callable, Any

_logger = logging.getLogger(__name__)


def retry_async(attempts: int = 3, backoff: float = 2.0):
    """Decorator to retry an async function on exception.
    Parameters
    ----------
    attempts: int
        Number of total attempts (first try + retries).
    backoff: float
        Multiplier for exponential back‑off in seconds.
    """
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = 1
            for attempt in range(1, attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    if attempt == attempts:
                        _logger.exception("All %d attempts failed for %s", attempts, func.__name__)
                        raise
                    _logger.warning("Attempt %d/%d failed for %s: %s – retrying in %s seconds",
                                    attempt, attempts, func.__name__, exc, delay)
                    await asyncio.sleep(delay)
                    delay *= backoff
        return wrapper
    return decorator


def log_token_usage(domain: str, provider: str, prompt_tokens: int, completion_tokens: int):
    """Append a JSON line with token usage information.
    The file ``token_log.jsonl`` will be created in the project root.
    """
    entry = {
        "domain": domain,
        "provider": provider,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
    }
    log_path = Path(__file__).resolve().parents[2] / "token_log.jsonl"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
