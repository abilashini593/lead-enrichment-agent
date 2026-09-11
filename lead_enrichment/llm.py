import os
import json
import logging
import asyncio
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

logger = logging.getLogger(__name__)

class ContactPoints(BaseModel):
    emails: List[str] = Field(default_factory=list, description="Generic or public contact emails found")

class Leader(BaseModel):
    name: str = Field(description="Name of the key leader or team member")
    role: str = Field(description="Role or title of the key leader")
    linkedin: Optional[str] = Field(default=None, description="LinkedIn profile URL if found")

class CompanyInfo(BaseModel):
    company_overview: str = Field(description="Concise 2-sentence summary of what the company does")
    icp: str = Field(description="Target audience / Ideal Customer Profile")
    contact_points: List[str] = Field(default_factory=list, description="Public emails found on site")
    leadership: List[Leader] = Field(default_factory=list, description="Key leadership or team members")
    confidence_score: float = Field(description="Estimated score between 0.0 and 1.0 indicating data quality")

def load_config():
    return {"api_key": os.getenv("GEMINI_API_KEY")}

class GeminiClient:
    def __init__(self, config: dict):
        api_key = config.get("api_key") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing from environment/config.")
        self.client = genai.Client(api_key=api_key)

    async def extract_info(self, domain: str, text: str) -> CompanyInfo:
        prompt = f"""
        You are an expert market intelligence AI agent. Extract structured target data for the domain: {domain}.
        
        Website Scraped Context:
        {text[:15000]}
        """
        
        def _sync_call():
            return self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=CompanyInfo,
                    temperature=0.1,
                ),
            )
        
        # Retry up to 3 times on transient errors (e.g. HTTP 503)
        for attempt in range(3):
            try:
                response = await asyncio.to_thread(_sync_call)
                return CompanyInfo.model_validate_json(response.text)
            except Exception as exc:
                if attempt < 2:
                    logger.warning(f"Attempt {attempt + 1} failed for {domain} ({exc}). Retrying in 2 seconds...")
                    await asyncio.sleep(2)
                else:
                    logger.error(f"LLM extraction failed for {domain} after retries: {exc}")
                    raise exc

def get_llm_client(config: dict = None):
    if config is None:
        config = load_config()
    return GeminiClient(config)