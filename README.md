# SoftwareBrio: Autonomous Lead Enrichment Agent

SoftwareBrio is a Python-based autonomous lead enrichment pipeline designed to extract, clean, and validate B2B company intelligence from web domains. By combining headless browser automation with structured LLM parsing, it transforms raw web content into standardized, schema-compliant JSON outputs.

## Architecture & Data Flow

1. **Web Crawling (`crawler.py`)**: Uses **Playwright** and **BeautifulSoup4** to headless-browse target domains, extract primary text contents, and filter out irrelevant structural noise (navbars, footers, scripts).
2. **Text Processing (`processor.py` & `utils.py`)**: Strips excess HTML tags and converts relevant page text to plain markdown to optimize token utilization and lower parsing latency.
3. **Structured Intelligence Extraction (`llm.py`)**: Interfaces with the `google-genai` SDK using strict schema constraints to systematically extract target audiences, company summaries, and key contact points.
4. **Data Validation (`models.py`)**: Enforces strict typing and data validation via **Pydantic** before saving the final output to `output.json`.

## Tech Stack

* **Language**: Python 3.10+
* **Web Automation**: Playwright, BeautifulSoup4, html2text
* **Intelligence Layer**: Google GenAI SDK (`google-genai`)
* **Data Validation**: Pydantic v2
* **Environment Management**: python-dotenv

## Project Structure

```text
lead-enrichment-agent/
├── lead_enrichment/
│   ├── __init__.py
│   ├── config.py          # Centralized configuration & environment loader
│   ├── crawler.py         # Async web scraper using Playwright
│   ├── llm.py             # Schema-enforced GenAI extraction client
│   ├── main.py            # Orchestrator & CLI entry point
│   ├── models.py          # Pydantic models for JSON validation
│   ├── processor.py       # HTML cleaning & text normalization
│   └── utils.py            # Helper functions
├── .gitignore
├── output.json            # Sample enriched output
├── README.md
└── requirements.txt

Setup & Installation
1. Prerequisites
Ensure you have Python 3.10+ installed on your system.

2. Install Dependencies
Clone the repository and install the required Python packages:

Bash
pip install -r lead_enrichment/requirements.txt
playwright install
3. Environment Configuration
Create a .env file in the root directory and add your Gemini API key:

Code snippet
GEMINI_API_KEY=your_gemini_api_key_here
Usage
To run the lead enrichment pipeline against a target domain, execute main.py:

Bash
python -m lead_enrichment.main
The output will be validated against the Pydantic schemas defined in models.py and saved directly to output.json.
