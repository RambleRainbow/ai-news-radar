"""
Tests for date utilities.
"""

from datetime import datetime, timedelta, timezone
from skill.utils.date_utils import (
    format_date,
    get_time_range,
    is_recent,
    parse_date,
    time_ago,
)


class TestParseDate:
    """Test date parsing."""

    def test_parse_string_date(self):
        """Test parsing string date."""
        result = parse_date("2024-01-15")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_iso_string(self):
        """Test parsing ISO format string."""
        result = parse_date("2024-01-15T10:30:00")
        assert result is not None
        assert result.hour == 10
        assert result.minute == 30

    def test_parse_datetime_object(self):
        """Test parsing datetime object."""
        dt = datetime(2024, 1, 15, 10, 30)
        result = parse_date(dt)
        assert result is not None
        assert result.tzinfo == timezone.utc

    def test_parse_datetime_with_timezone(self):
        """Test parsing datetime with timezone."""
        dt = datetime(2024, 1, 15, 10, 30, tzinfo=timezone.utc)
        result = parse_date(dt)
        assert result.tzinfo == timezone.utc

    def test_parse_naive_datetime(self):
        """Test parsing naive datetime adds UTC timezone."""
        dt = datetime(2024, 1, 15, 10, 30)
        result = parse_date(dt)
        assert result.tzinfo == timezone.utc

    def test_parse_none(self):
        """Test parsing None returns None."""
        result = parse_date(None)
        assert result is None

    def test_parse_invalid_string(self):
        """Test parsing invalid string returns None."""
        result = parse_date("not-a-date")
        assert result is None


class TestFormatDate:
    """Test date formatting."""

    def test_format_datetime(self):
        """Test formatting datetime."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        result = format_date(dt)
        assert result == "2024-01-15 10:30:45"

    def test_format_string(self):
        """Test formatting date string."""
        result = format_date("2024-01-15")
        assert result == "2024-01-15 00:00:00"

    def test_format_none(self):
        """Test formatting None returns empty string."""
        result = format_date(None)
        assert result == ""

    def test_format_custom_format(self):
        """Test formatting with custom format string."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        result = format_date(dt, "%Y/%m/%d")
        assert result == "2024/01/15"


class TestIsRecent:
    """Test recent date checking."""

    def test_is_recent_true(self):
        """Test recent date returns True."""
        dt = datetime.now(timezone.utc) - timedelta(hours=12)
        result = is_recent(dt, hours=24)
        assert result is True

    def test_is_recent_false(self):
        """Test old date returns False."""
        dt = datetime.now(timezone.utc) - timedelta(days=2)
        result = is_recent(dt, hours=24)
        assert result is False

    def test_is_recent_edge_case(self):
        """Test exactly at boundary."""
        # Slightly less than 24 hours to avoid timing issues
        dt = datetime.now(timezone.utc) - timedelta(hours=23, minutes=59)
        result = is_recent(dt, hours=24)
        assert result is True

    def test_is_recent_custom_window(self):
        """Test custom time window."""
        dt = datetime.now(timezone.utc) - timedelta(hours=36)
        result = is_recent(dt, hours=48)
        assert result is True

    def test_is_recent_none(self):
        """Test None returns False."""
        result = is_recent(None)
        assert result is False


class TestTimeAgo:
    """Test time ago formatting."""

    def test_time_ago_now(self):
        """Test just now."""
        dt = datetime.now(timezone.utc)
        result = time_ago(dt)
        assert result == "just now"

    def test_time_ago_minutes(self):
        """Test minutes ago."""
        dt = datetime.now(timezone.utc) - timedelta(minutes=5)
        result = time_ago(dt)
        assert result == "5 minutes ago"

    def test_time_ago_one_minute(self):
        """Test one minute (singular)."""
        dt = datetime.now(timezone.utc) - timedelta(minutes=1)
        result = time_ago(dt)
        assert result == "1 minute ago"

    def test_time_ago_hours(self):
        """Test hours ago."""
        dt = datetime.now(timezone.utc) - timedelta(hours=3)
        result = time_ago(dt)
        assert result == "3 hours ago"

    def test_time_ago_one_hour(self):
        """Test one hour (singular)."""
        dt = datetime.now(timezone.utc) - timedelta(hours=1)
        result = time_ago(dt)
        assert result == "1 hour ago"

    def test_time_ago_days(self):
        """Test days ago."""
        dt = datetime.now(timezone.utc) - timedelta(days=2)
        result = time_ago(dt)
        assert result == "2 days ago"

    def test_time_ago_one_day(self):
        """Test one day (singular)."""
        dt = datetime.now(timezone.utc) - timedelta(days=1)
        result = time_ago(dt)
        assert result == "1 day ago"

    def test_time_ago_weeks(self):
        """Test weeks ago."""
        dt = datetime.now(timezone.utc) - timedelta(weeks=2)
        result = time_ago(dt)
        assert result == "2 weeks ago"

    def test_time_ago_months(self):
        """Test months ago."""
        dt = datetime.now(timezone.utc) - timedelta(days=45)
        result = time_ago(dt)
        assert result == "1 month ago"

    def test_time_ago_none(self):
        """Test None returns unknown."""
        result = time_ago(None)
        assert result == "unknown"


class TestGetTimeRange:
    """Test time range calculation."""

    def test_get_time_range_hours(self):
        """Test getting time range for hours."""
        start, end = get_time_range(24)

        # Check time difference is approximately 24 hours
        time_diff = (end - start).total_seconds()
        assert abs(time_diff - 24 * 3600) < 1  # Allow 1 second tolerance
        assert start.tzinfo == timezone.utc
        assert end.tzinfo == timezone.utc

    def test_get_time_range_zero_hours(self):
        """Test getting time range for 0 hours."""
        start, end = get_time_range(0)

        time_diff = (end - start).total_seconds()
        assert abs(time_diff) < 1  # Should be essentially same time

    def test_get_time_range_negative_hours(self):
        """Test getting time range for negative hours."""
        start, end = get_time_range(-10)

        # With negative hours, start should be after end
        assert start > end
