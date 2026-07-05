"""Gamification constants aligned with the Argus UI and master architecture spec."""

from enum import Enum

# Planet progression thresholds (Euro balance required)
PLANET_THRESHOLDS: dict[str, int] = {
    "Mercury": 0,
    "Venus": 500,
    "Earth": 1000,
    "Mars": 1500,
    "Jupiter": 2000,
    "Saturn": 2500,
    "Uranus": 3000,
    "Neptune": 3500,
    "Andromeda": 4500,
}

# Base Euro rewards by activity type
EURO_REWARD_WORKSHEET = 10
EURO_REWARD_QUIZ = 10
EURO_REWARD_CYP = 10
EURO_REWARD_PODCAST_BASE = 2
EURO_REWARD_PODCAST_ENGAGED = 4
EURO_REWARD_VIDEO_BASE = 5
EURO_REWARD_VIDEO_DISTRACTED = 2

PODCAST_ENGAGEMENT_THRESHOLD_SECONDS = 180
VIDEO_FOCUS_INTERRUPTION_THRESHOLD = 3


class ActivityType(str, Enum):
    WORKSHEET = "worksheet"
    QUIZ = "quiz"
    CYP = "cyp"
    PODCAST = "podcast"
    VIDEO = "video"
