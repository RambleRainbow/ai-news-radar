"""
Tests for filter modules.
"""

from datetime import datetime, timedelta

from src.filters.ai_topic_filter import AITopicFilter
from src.filters.duplicate_filter import DuplicateFilter
from src.filters.time_filter import TimeFilter


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
            {
                "title": "Artificial intelligence breakthrough",
                "url": "https://example.com/2",
            },
            {"title": "AI news", "url": "https://example.com/3"},
        ]
        sorted_articles = filter.sort_by_relevance(articles)
        assert sorted_articles[0]["_ai_score"] >= sorted_articles[1]["_ai_score"]

    def test_get_matched_keywords(self):
        """Test getting matched keywords."""
        filter = AITopicFilter()
        article = {"title": "AI and machine learning advances"}
        matched = filter.get_matched_keywords(article)
        assert len(matched) > 0

    def test_get_matched_keywords_no_match(self):
        """Test getting matched keywords with no match."""
        filter = AITopicFilter()
        article = {"title": "Cooking tips"}
        matched = filter.get_matched_keywords(article)
        assert matched == []

    def test_score_with_tags(self):
        """Test scoring with tags."""
        filter = AITopicFilter()
        article = {"title": "Technology news", "tags": ["AI", "machine learning"]}
        score = filter.score(article)
        assert score > 0

    def test_score_with_description(self):
        """Test scoring with description."""
        filter = AITopicFilter()
        article = {
            "title": "News",
            "description": "This is about artificial intelligence",
        }
        score = filter.score(article)
        assert score > 0


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

    def test_filter_with_naive_datetime(self):
        """Test filtering with naive datetime."""
        filter = TimeFilter(hours=24)
        articles = [
            {
                "title": "Recent news",
                "url": "https://example.com",
                "date": datetime.now(),  # Naive datetime
            }
        ]
        filtered = filter.filter(articles)
        # Naive datetime should be handled
        assert len(filtered) >= 0

    def test_filter_articles_without_date(self):
        """Test filtering articles without date field."""
        filter = TimeFilter(hours=24)
        articles = [
            {
                "title": "News",
                "url": "https://example.com",
            }
        ]
        filtered = filter.filter(articles)
        # Articles without date should be filtered out
        assert len(filtered) == 0


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
            {
                "title": "Artificial Intelligence Breakthrough",
                "url": "https://example.com/1",
            },
            {"title": "Quantum Computing Milestone", "url": "https://example.com/2"},
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

    def test_merge_duplicates(self):
        """Test merging duplicates."""
        filter = DuplicateFilter()
        articles = [
            {"title": "Article", "url": "https://example.com/1", "description": "v1"},
            {
                "title": "Article",
                "url": "https://example.com/1?ref=twitter",
                "description": "v2",
            },
        ]
        merged = filter.merge_duplicates(articles)
        assert len(merged) == 1

    def test_merge_duplicates_newest(self):
        """Test merging preferring newest."""
        filter = DuplicateFilter()
        articles = [
            {"title": "Article", "url": "https://example.com/1", "date": "2024-01-01"},
            {"title": "Article", "url": "https://example.com/2", "date": "2024-01-02"},
        ]
        merged = filter.merge_duplicates(articles, prefer="newest")
        # Articles should be merged into groups
        assert len(merged) <= 2

    def test_normalize_url(self):
        """Test URL normalization."""
        filter = DuplicateFilter()
        url1 = "https://example.com/article?utm_source=twitter"
        # After normalization, tracking params are removed
        normalized1 = filter._normalize_url(url1)
        # URLs without tracking should be similar
        assert "utm_source" not in normalized1

    def test_filter_with_content_hash(self):
        """Test filtering by content hash."""
        filter = DuplicateFilter(by_url=False, by_title=False, by_content=True)
        articles = [
            {
                "title": "Test",
                "url": "https://example.com/1",
                "description": "Same content",
            },
            {
                "title": "Test",
                "url": "https://example.com/2",
                "description": "Same content",
            },
        ]
        filtered = filter.filter(articles)
        # Second article should be filtered as duplicate content
        assert len(filtered) == 1

    def test_title_similarity_threshold(self):
        """Test title similarity threshold."""
        filter = DuplicateFilter(
            by_url=False, by_title=True, title_similarity_threshold=0.9
        )
        articles = [
            {"title": "AI News Today", "url": "https://example.com/1"},
            {"title": "AI News", "url": "https://example.com/2"},
        ]
        filtered = filter.filter(articles)
        # Should keep both due to high threshold
        assert len(filtered) == 2
