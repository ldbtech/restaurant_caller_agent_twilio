# models/user_settings.py
"""Pydantic model for User Application Settings."""

from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field

# Import enums from the enums module within the same package
from .enums import Theme, DefaultView, WeekDay, ReminderTime

class UserSettings(BaseModel):
    """User-specific application settings."""
    # userId field might be implicit if stored as a subcollection or keyed by user ID
    # userId: str = Field(..., description="Identifier of the user these settings belong to")
    theme: Theme = Field(default=Theme.DARK_PURPLE_NEBULA, description="Selected UI theme")
    defaultView: DefaultView = Field(default=DefaultView.WEEK, description="Default view mode for the calendar")
    weekStartsOn: WeekDay = Field(default=WeekDay.MONDAY, description="Which day the week starts on in the calendar view")
    studyMode: str = Field(default="focus", description="Study mode (e.g., focus, break, exam)")
    academicYear: Optional[str] = Field(default=None, description="Academic year or semester (e.g., 2023-2024, Fall 2023)")
    notificationPreferences: Dict[str, bool] = Field(default_factory=lambda: {"email": True, "sms": False, "push": True}, description="User notification preferences")
    aiSuggestionsEnabled: bool = Field(default=True, description="User preference to enable/disable AI suggestion feature")
    blockchainVerifyDisplayEnabled: bool = Field(default=True, description="User preference to show/hide blockchain verification status")
    defaultReminderTime: ReminderTime = Field(default=ReminderTime.FIFTEEN, description="Default reminder setting for new events")
    updatedAt: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when settings were last updated")

    class Config:
        use_enum_values = True