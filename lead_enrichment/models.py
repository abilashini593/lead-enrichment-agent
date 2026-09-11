# lead_enrichment/models.py
"""Pydantic data models for the structured output of the lead enrichment agent.
"""

from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field

class Leader(BaseModel):
    name: str = Field(..., description="Full name of the leader.")
    title: str = Field(..., description="Job title or role within the company.")
    linkedin: Optional[HttpUrl] = Field(None, description="Public LinkedIn profile URL if available.")

class CompanyInfo(BaseModel):
    domain: str = Field(..., description="The domain that was processed.")
    overview: str = Field(..., description="Two‑sentence summary of what the company does.")
    target_audience: str = Field(..., description="Brief description of the ideal customer profile.")
    contact_points: List[str] = Field(..., description="List of public email addresses discovered.")
    leadership: List[Leader] = Field(..., description="Key team members extracted from the site.")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Estimated quality/completeness of the data (0‑1).")
