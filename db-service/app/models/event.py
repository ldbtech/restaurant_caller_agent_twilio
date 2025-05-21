# models/event.py
"""Pydantic models related to Calendar Events."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator

# Import enums from the enums module
from .enums import PriorityLevel

class EventResource(BaseModel):
    """Custom data associated with an event."""
    aiRecommended: bool = Field(default=False, description="Was this event suggested by AI?")
    verifiedOnChain: bool = Field(default=False, description="Is this event's integrity verified on TrustNet?")
    priority: Optional[PriorityLevel] = Field(default=None, description="Priority level of the event")
    category: Optional[str] = Field(default=None, description="Event category (e.g., lecture, exam, study group, assignment)")
    location: Optional[str] = Field(default=None, description="Location of the event (e.g., classroom, online link)")
    recurrence: Optional[Dict[str, Any]] = Field(default=None, description="Recurrence rules for the event (e.g., weekly, monthly)")
    # Example future fields:
    # tags: List[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True

class Event(BaseModel):
    """Represents a calendar event."""
    id: str = Field(..., description="Unique identifier for the event (e.g., Firestore Document ID)")
    userId: str = Field(..., description="Identifier of the user this event belongs to (for querying/rules)")
    title: str = Field(..., min_length=1, description="Title or name of the event")
    start: datetime = Field(..., description="Start date and time of the event (UTC recommended)")
    end: datetime = Field(..., description="End date and time of the event (UTC recommended)")
    allDay: bool = Field(default=False, description="Does the event span the entire day?")
    resource: EventResource = Field(default_factory=EventResource, description="Additional structured data for the event") # Use default_factory
    description: Optional[str] = Field(default=None, description="Optional longer description for the event")
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the event was created")
    updatedAt: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the event was last updated")

    @validator('end')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start' in values and v <= values['start']:
            raise ValueError('End datetime must be after start datetime')
        return v

    class Config:
        use_enum_values = True