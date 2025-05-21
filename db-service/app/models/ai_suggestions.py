# models/ai_suggestion.py
"""Pydantic model for AI Suggestions."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

# Import enums from the enums module
from .enums import AiSuggestionStatus

class AiSuggestion(BaseModel):
    """Represents an AI-generated suggestion for the user."""
    id: str = Field(..., description="Unique identifier for the suggestion (e.g., Firestore Document ID)")
    userId: str = Field(..., description="Identifier of the user this suggestion is for")
    description: str = Field(..., description="Textual description of the suggestion")
    status: AiSuggestionStatus = Field(default=AiSuggestionStatus.PENDING, description="Current status of the suggestion")
    context: Optional[str] = Field(default=None, description="Context of the suggestion (e.g., exam prep, assignment due, group study)")
    priority: Optional[int] = Field(default=None, ge=1, le=5, description="Priority level of the suggestion (1-5)")
    feedback: Optional[Dict[str, Any]] = Field(default=None, description="User feedback on the suggestion (e.g., accepted, rejected, rating)")
    # Optional: Details if the suggestion proposes a specific event
    proposedTitle: Optional[str] = Field(default=None, description="Suggested event title")
    proposedStart: Optional[datetime] = Field(default=None, description="Suggested event start time (UTC)")
    proposedEnd: Optional[datetime] = Field(default=None, description="Suggested event end time (UTC)")
    # Optional: Metadata about the suggestion
    confidenceScore: Optional[float] = Field(default=None, ge=0, le=1, description="AI confidence in this suggestion")
    reason: Optional[str] = Field(default=None, description="Brief explanation for the suggestion")
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the suggestion was generated")
    # reviewedAt: Optional[datetime] = None # Timestamp when user accepted/dismissed

    class Config:
        use_enum_values = True