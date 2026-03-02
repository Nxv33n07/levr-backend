"""
Pydantic models for the Query Tagger service.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class FinancialTag(str, Enum):
    """Valid financial query categories."""
    LOAN = "loan"
    INSURANCE = "insurance"
    TAX = "tax"
    INVESTMENT = "investment"
    BANKING = "banking"
    PAYMENTS = "payments"
    BUDGETING = "budgeting"

    @classmethod
    def valid_tags(cls) -> list[str]:
        return [tag.value for tag in cls]


class TagRequest(BaseModel):
    """Request model for query tagging."""
    query: str = Field(..., min_length=1, max_length=5000)
    context: Optional[dict] = None
    include_reasoning: bool = False


class TagResult(BaseModel):
    """Result of query tagging."""
    tag: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning: Optional[str] = None


class TagResponse(BaseModel):
    """Response model for query tagging."""
    success: bool
    data: Optional[TagResult] = None
    error: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


# ============ Chat Response Models ============

class ChatRequest(BaseModel):
    """Request model for chat response."""
    query: str = Field(..., min_length=1, max_length=5000)


class ChatResult(BaseModel):
    """Result of chat response generation."""
    primary_tag: Optional[str] = None
    primary_confidence: float = 0.0
    secondary_tag: Optional[str] = None
    secondary_confidence: Optional[float] = None
    interpreted_query: str = ""
    response: str
    suggestions: list[str] = Field(default_factory=list)
    related_topics: list[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    """Response model for chat."""
    success: bool
    data: Optional[ChatResult] = None
    error: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
