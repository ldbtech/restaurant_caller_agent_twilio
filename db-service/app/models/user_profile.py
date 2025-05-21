# models/user_profile.py
"""Pydantic model for User Profile data."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl

class UserProfile(BaseModel):
    """Core user profile information."""
    id: str = Field(..., description="Unique identifier for the user (e.g., Firebase Auth UID)")
    displayName: str = Field(..., min_length=1, description="User's preferred display name")
    email: str = Field(..., description="User's unique email address (often from Auth)")
    role: str = Field(default="student", description="User role (e.g., student, teacher, admin)")
    school: Optional[str] = Field(default=None, description="Educational institution the user belongs to")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences (e.g., notification methods, study hours)")
    bio: Optional[str] = Field(default=None, max_length=500, description="Short user biography")
    avatarUrl: Optional[HttpUrl] = Field(default=None, description="URL to the user's avatar image")
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the user account was created")
    updatedAt: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the profile was last updated")

    class Config:
        # If using with an ORM or specific backend adapters:
        # orm_mode = True
        # schema_extra = { ... example ... } # Can add example data for documentation
        orm_mode = True