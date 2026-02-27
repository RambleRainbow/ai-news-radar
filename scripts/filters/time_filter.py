"""
Time filter for AI News Radar.

This module filters articles by publication time window.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class TimeFilter:
    """
    Filter articles by time window.

    Supports filtering articles within a specified time range from now.
    """

    def __init__(self, hours: int = 24):
        """
        Initialize the time filter.

        Args:
            hours: Time window in hours (default: 24)
        """
        self.hours = hours
        self.cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

    def filter(self, articles: List[Dict]) -> List[Dict]:
        """
        Filter articles by publication time.

        Args:
            articles: List of article dictionaries

        Returns:
            Filtered list of articles published within the time window
        """
        filtered = []

        for article in articles:
            article_date = self._parse_date(article.get("date"))
            if article_date and article_date >= self.cutoff_time:
                filtered.append(article)

        logger.info(
            f"Time Filter: {len(filtered)}/{len(articles)} articles "
            f"within last {self.hours} hours"
        )
        return filtered

    def _parse_date(self, date_value: Optional[datetime]) -> Optional[datetime]:
        """
        Parse date value to datetime object.

        Args:
            date_value: Date value (datetime or string)

        Returns:
            datetime object or None
        """
        if isinstance(date_value, datetime):
            # Ensure timezone-aware
            if date_value.tzinfo is None:
                return date_value.replace(tzinfo=timezone.utc)
            return date_value

        if isinstance(date_value, str):
            try:
                from dateutil import parser

                parsed = parser.parse(date_value)
                if parsed.tzinfo is None:
                    return parsed.replace(tzinfo=timezone.utc)
                return parsed
            except (ValueError, TypeError) as e:
                logger.debug(f"Could not parse date string '{date_value}': {e}")

        return None

    def is_within_window(self, date_value: Optional[datetime]) -> bool:
        """
        Check if a date is within the time window.

        Args:
            date_value: Date value to check

        Returns:
            True if date is within window, False otherwise
        """
        article_date = self._parse_date(date_value)
        return article_date is not None and article_date >= self.cutoff_time

    def update_window(self, hours: int) -> None:
        """
        Update the time window.

        Args:
            hours: New time window in hours
        """
        self.hours = hours
        self.cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        logger.debug(f"Time window updated to last {hours} hours")

    def get_cutoff_time(self) -> datetime:
        """
        Get the current cutoff time.

        Returns:
            Cutoff datetime
        """
        return self.cutoff_time
