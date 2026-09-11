# lead_enrichment/config.py
"""Configuration loader for environment variables.
Expected variables (set in a .env file or system env):
- OPENAI_API_KEY (required for OpenAI provider)
- ANTHROPIC_API_KEY (optional if you choose Anthropic)
- LLM_PROVIDER (optional, defaults to "openai")
- SERPAPI_KEY (optional, used for optional LinkedIn search)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root (two levels up from this file)
project_root = Path(__file__).resolve().parents[2]
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    # Fallback to default env loading (system env only)
    load_dotenv()

def load_config():
    """Return a simple dict with configuration values."""
    return {
        "llm_provider": os.getenv("LLM_PROVIDER", "openai").lower(),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
        "serpapi_key": os.getenv("SERPAPI_KEY"),
    }
