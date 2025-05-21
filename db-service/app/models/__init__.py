# models/__init__.py
"""Make models easily importable from the models package."""

from .enums import (
    PriorityLevel,
    DefaultView,
    WeekDay,
    Theme,
    ReminderTime,
    TrustNetStatus,
    AiSuggestionStatus
)
from .user_profile import UserProfile
from .user_settings import UserSettings
from .event import Event, EventResource
from .ai_suggestions import AiSuggestion

# You can optionally define __all__ to control `from models import *`
__all__ = [
    "PriorityLevel", "DefaultView", "WeekDay", "Theme", "ReminderTime",
    "TrustNetStatus", "AiSuggestionStatus",
    "UserProfile", "UserSettings", "Event", "EventResource", "AiSuggestion",
]