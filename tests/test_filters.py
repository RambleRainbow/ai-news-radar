"""
Tests for filter modules.
"""

import pytest

from src.filters.ai_topic_filter import AITopicFilter
from src.filters.time_filter import TimeFilter
from src.filters.duplicate_filter import DuplicateFilter
from datetime import datetime, timedelta


class TestAITopicFilter:
    """Test AI topic filter functionality."""

    def test_init_default(self):
        """Test filter with default keywords."""
        filter = AITopicFilter()
        assert filter.keywords["primary"]
        assert filter.keywords["secondary"]
        assert filter.keywords["aliases"]

    def test_init_with_keywords(self):
        """Test filter with custom keywords."""
        keywords = {
            "primary": ["test keyword"],
            "secondary": ["secondary keyword"],
            "aliases": ["alias"],
        }
        filter = AITopicFilter(keywords=keywords)
        assert "test keyword" in filter.keywords["primary"]

    def test_score_with_primary_keyword(self):
        """Test scoring with primary keyword."""
        filter = AITopicFilter()
        article = {"title": "This is about artificial intelligence"}
        score = filter.score(article)
        assert score == 1.0

    def test_score_with_secondary_keyword(self):
        """Test scoring with secondary keyword."""
        filter = AITopicFilter()
        article = {"title": "News about chatgpt"}
        score = filter.score(article)
        assert score == 0.7

    def test_score_with_alias(self):
        """Test scoring with alias."""
        filter = AITopicFilter()
        article = {"title": "Latest in AI"}
        score = filter.score(article)
        assert score == 0.5

    def test_score_no_match(self):
        """Test scoring with no match."""
        filter = AITopicFilter()
        article = {"title": "News about cooking"}
        score = filter.score(article)
        assert score == 0.0

    def test_filter(self):
        """Test filtering articles."""
        filter = AITopicFilter()
        articles = [
            {"title": "AI news", "url": "https://example.com/1"},
            {"title": "Cooking tips", "url": "https://example.com/2"},
            {"title": "Machine learning", "url": "https://example.com/3"},
        ]
        filtered = filter.filter(articles, min_score=0.5)
        assert len(filtered) == 2

    def test_sort_by_relevance(self):
        """Test sorting by relevance."""
        filter = AITopicFilter()
        articles = [
            {"title": "Some news", "url": "https://example.com/1"},
            {"title": "Artificial intelligence breakthrough", "url": "https://example.com/2"},
            {"title": "AI news", "url": "https://example.com/3"},
        ]
        sorted_articles = filter.sort_by_relevance(articles)
        assert sorted_articles[0]["_ai_score"] >= sorted_articles[1]["_ai_score"]


class TestTimeFilter:
    """Test time filter functionality."""

    def test_init(self):
        """Test filter initialization."""
        filter = TimeFilter(hours=24)
        assert filter.hours == 24

    def test_filter_within_window(self):
        """Test filtering articles within time window."""
        filter = TimeFilter(hours=24)
        articles = [
            {
                "title": "Recent news",
                "url": "https://example.com",
                "date": datetime.now(),
            }
        ]
        filtered = filter.filter(articles)
        assert len(filtered) == 1

    def test_filter_outside_window(self):
        """Test filtering articles outside time window."""
        filter = TimeFilter(hours=24)
        articles = [
            {
                "title": "Old news",
                "url": "https://example.com",
                "date": datetime.now() - timedelta(days=2),
            }
        ]
        filtered = filter.filter(articles)
        assert len(filtered) == 0

    def test_is_within_window(self):
        """Test checking if date is within window."""
        filter = TimeFilter(hours=24)
        assert filter.is_within_window(datetime.now()) is True
        assert filter.is_within_window(datetime.now() - timedelta(days=2)) is False

    def test_update_window(self):
        """Test updating time window."""
        filter = TimeFilter(hours=24)
        filter.update_window(48)
        assert filter.hours == 48


class TestDuplicateFilter:
    """Test duplicate filter functionality."""

    def test_init(self):
        """Test filter initialization."""
        filter = DuplicateFilter()
        assert filter.by_url is True
        assert filter.by_title is True

    def test_filter_duplicates_by_url(self):
        """Test filtering duplicates by URL."""
        filter = DuplicateFilter(by_url=True, by_title=False)
        articles = [
            {"title": "Article 1", "url": "https://example.com/1"},
            {"title": "Article 2", "url": "https://example.com/1"},
        ]
        filtered = filter.filter(articles)
        assert len(filtered) == 1

    def test_filter_duplicates_by_title(self):
        """Test filtering duplicates by title."""
        filter = DuplicateFilter(by_url=False, by_title=True)
        articles = [
            {"title": "Test Article", "url": "https://example.com/1"},
            {"title": "Test Article", "url": "https://example.com/2"},
        ]
        filtered = filter.filter(articles)
        assert len(filtered) == 1

    def test_filter_no_duplicates(self):
        """Test filtering with no duplicates."""
        filter = DuplicateFilter()
        articles = [
            {"title": "Article 1", "url": "https://example.com/1"},
            {"title": "Article 2", "url": "https://example.com/2"},
        ]
        filtered = filter.filter(articles)
        assert len(filtered) == 2

    def test_reset(self):
        """Test resetting filter state."""
        filter = DuplicateFilter()
        articles = [{"title": "Test", "url": "https://example.com"}]
        filter.filter(articles)
        filter.reset()
        # Should not remember previous articles
        result = filter.filter(articles)
        assert len(result) == 1
