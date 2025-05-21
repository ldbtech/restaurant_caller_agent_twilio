# models/enums.py
"""Defines reusable Enum types for the Flikor application models."""

import enum

class PriorityLevel(str, enum.Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class DefaultView(str, enum.Enum):
    MONTH = "month"
    WEEK = "week"
    DAY = "day"
    AGENDA = "agenda"

class WeekDay(str, enum.Enum):
    SUNDAY = "sunday"
    MONDAY = "monday"

class Theme(str, enum.Enum):
    DARK_PURPLE_NEBULA = "dark_purple_nebula"
    LIGHT_SOLARPUNK = "light_solarpunk"
    CYBERPUNK_NEON = "cyberpunk_neon"
    MINIMALIST_MONO = "minimalist_mono"

class ReminderTime(str, enum.Enum):
    """Reminder time in minutes before the event, 'none' for no reminder."""
    NONE = "none"
    FIVE = "5"
    FIFTEEN = "15"
    THIRTY = "30"
    SIXTY = "60"

class TrustNetStatus(str, enum.Enum):
    NOMINAL = "Nominal"
    DEGRADED = "Degraded"
    OFFLINE = "Offline"

class AiSuggestionStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DISMISSED = "dismissed"
    EXPIRED = "expired"