"""Pydantic API models for Orion."""

from typing import List, Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Incoming analysis request payload."""

    question: str = Field(..., min_length=5, max_length=500)
    session_id: Optional[str] = None


class AnalyzeResponse(BaseModel):
    """Successful analysis response payload."""

    answer: str
    session_id: str
    steps: List[str]
    model_used: str


class HealthResponse(BaseModel):
    """Health check response payload."""

    status: str
    model: str
