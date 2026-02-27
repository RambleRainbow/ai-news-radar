"""
Date and time utilities for AI News Radar.

This module provides functions for parsing, formatting, and comparing dates.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)


def parse_date(date_value: Optional[Union[str, datetime]]) -> Optional[datetime]:
    """
    Parse a date value into a datetime object.

    Args:
        date_value: Date value (string or datetime)

    Returns:
        datetime object with UTC timezone, or None if parsing fails
    """
    if date_value is None:
        return None

    if isinstance(date_value, datetime):
        # Ensure timezone-aware
        if date_value.tzinfo is None:
            return date_value.replace(tzinfo=timezone.utc)
        # Convert to UTC
        return date_value.astimezone(timezone.utc)

    if isinstance(date_value, str):
        try:
            parsed = date_parser.parse(date_value)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except (ValueError, TypeError) as e:
            logger.debug(f"Could not parse date string '{date_value}': {e}")

    return None


def format_date(date_value: Optional[Union[str, datetime]], format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a date value as a string.

    Args:
        date_value: Date value (string or datetime)
        format_string: Format string (default: ISO format with time)

    Returns:
        Formatted date string, or empty string if parsing fails
    """
    parsed = parse_date(date_value)
    if parsed:
        return parsed.strftime(format_string)
    return ""


def is_recent(
    date_value: Optional[Union[str, datetime]],
    hours: int = 24,
) -> bool:
    """
    Check if a date is within the recent time window.

    Args:
        date_value: Date value (string or datetime)
        hours: Time window in hours (default: 24)

    Returns:
        True if date is within window, False otherwise
    """
    parsed = parse_date(date_value)
    if not parsed:
        return False

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    return parsed >= cutoff


def time_ago(date_value: Optional[Union[str, datetime]]) -> str:
    """
    Get human-readable time ago string.

    Args:
        date_value: Date value (string or datetime)

    Returns:
        Time ago string (e.g., "2 hours ago", "1 day ago")
    """
    parsed = parse_date(date_value)
    if not parsed:
        return "unknown"

    now = datetime.now(timezone.utc)
    delta = now - parsed

    seconds = int(delta.total_seconds())

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:
        weeks = seconds // 604800
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    else:
        months = seconds // 2592000
        return f"{months} month{'s' if months != 1 else ''} ago"


def get_time_range(hours: int) -> tuple[datetime, datetime]:
    """
    Get time range for the specified hours window.

    Args:
        hours: Time window in hours

    Returns:
        Tuple of (start_time, end_time) both timezone-aware in UTC
    """
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=hours)
    return start_time, end_time
