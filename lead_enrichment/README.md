# Lead Enrichment Agent

## Overview
This repository implements the **Autonomous Lead Enrichment Agent** described in the assignment. It accepts a list of company domains, crawls their public web pages, extracts clean markdown content, and uses an LLM to produce structured intelligence:
- Company overview (2‑sentence summary)
- Target audience / ICP
- Public contact email addresses
- Key leadership with LinkedIn URLs (if discoverable)
- Confidence score (0.0 – 1.0)

The implementation is fully asynchronous, resilient to timeouts, 404s, and missing pages, and never aborts the whole run when a single domain fails.

## Repository Structure
```
lead_enrichment/
├─ __init__.py
├─ main.py            # CLI entry point
├─ crawler.py         # HTTP‑based crawler (httpx) with HEAD discovery
├─ processor.py       # HTML → Markdown cleaning (BeautifulSoup + html2text)
├─ llm.py             # OpenAI (legacy 0.28) client wrapper (easy to swap for Anthropic, Ollama, etc.)
├─ models.py          # Pydantic schema for the structured output
├─ config.py          # Loads .env variables
├─ utils.py           # Retry decorator, token‑usage logging
├─ requirements.txt   # Pinning `openai==0.28` for compatibility
└─ .env (generated)   # Stores your API key (already created)
```

## Setup
1. **Clone / open the project** (the files are already in your workspace).
2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Add your OpenAI API key** (already placed in `.env`).
   ```text
   OPENAI_API_KEY=sk-...your key...
   LLM_PROVIDER=openai
   ```
   *If you prefer another provider, set `LLM_PROVIDER` accordingly and add the matching env variable (e.g., `ANTHROPIC_API_KEY`).*
5. **Run the script** with the three test domains:
   ```bash
   python -m lead_enrichment.main --domains postman.com supabase.com vapi.ai
   ```
   The output will be written to `output.json` in the current directory.

## Sample Output
A sample `output.json` generated with the provided API key (credits were exhausted, so placeholders were returned):
```json
[
  {
    "domain": "postman.com",
    "overview": "",
    "target_audience": "",
    "contact_points": [],
    "leadership": [],
    "confidence_score": 0.0
  },
  {
    "domain": "supabase.com",
    "overview": "",
    "target_audience": "",
    "contact_points": [],
    "leadership": [],
    "confidence_score": 0.0
  },
  {
    "domain": "vapi.ai",
    "overview": "",
    "target_audience": "",
    "contact_points": [],
    "leadership": [],
    "confidence_score": 0.0
  }
]
```
When the LLM has available credits (or you switch to a different provider), the fields will be populated as required.

## Extending / Customising
- **Swap LLM**: Implement a new subclass of `BaseLLM` in `llm.py` (e.g., Anthropic or Ollama) and adjust `get_llm_client`.
- **Increase token budget**: Adjust the `truncated` length in `llm.py` if you need more page content.
- **Add more sub‑page discovery**: Extend `COMMON_PATHS` in `crawler.py`.
- **CSV output**: Change `main_async` to also write a CSV file if desired.

## Limitations & Next Steps
- The current run used an exhausted OpenAI credit balance, so placeholders were emitted. Add credits or change the provider to obtain real data.
- The crawler uses simple HEAD checks; for heavily JS‑rendered sites you can revert to the Playwright version (replace `crawler.py` with the Playwright implementation).

---

