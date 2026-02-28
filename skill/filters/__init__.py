"""
Filter modules for AI News Radar.

This package contains filters for processing aggregated news:
- ai_topic_filter: Filter by AI-related topics
- time_filter: Filter by time window
- duplicate_filter: Remove duplicate articles
"""

from .ai_topic_filter import AITopicFilter
from .duplicate_filter import DuplicateFilter
from .time_filter import TimeFilter

__all__ = [
    "AITopicFilter",
    "TimeFilter",
    "DuplicateFilter",
]
