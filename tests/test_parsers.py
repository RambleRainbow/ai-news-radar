"""
Tests for parser modules.
"""

import pytest
from datetime import datetime

from scripts.parsers.rss_parser import RSSParser
from scripts.parsers.html_parser import HTMLParser


class TestRSSParser:
    """Test RSS parser functionality."""

    def test_init(self):
        """Test parser initialization."""
        parser = RSSParser()
        assert parser.timeout == 30
        assert parser.max_entries is None

    def test_init_with_config(self):
        """Test parser with custom config."""
        config = {"timeout": 60, "max_entries": 10}
        parser = RSSParser(config)
        assert parser.timeout == 60
        assert parser.max_entries == 10

    def test_parse_empty_content(self):
        """Test parsing empty content."""
        parser = RSSParser()
        articles = parser.parse("")
        assert articles == []

    def test_normalize_articles(self):
        """Test article normalization."""
        parser = RSSParser()
        articles = [
            {
                "title": "Test Article",
                "url": "https://example.com",
                "description": "Test description",
                "date": "2024-01-01",
            }
        ]
        normalized = parser.normalize(articles)
        assert len(normalized) == 1
        assert normalized[0]["title"] == "Test Article"
        assert normalized[0]["source"] == "RSSParser"

    def test_validate_article_valid(self):
        """Test validating a valid article."""
        parser = RSSParser()
        article = {"title": "Test", "url": "https://example.com"}
        assert parser.validate_article(article) is True

    def test_validate_article_invalid(self):
        """Test validating an invalid article."""
        parser = RSSParser()
        assert parser.validate_article({}) is False
        assert parser.validate_article({"title": "Test"}) is False
        assert parser.validate_article({"url": "https://example.com"}) is False


class TestHTMLParser:
    """Test HTML parser functionality."""

    def test_init(self):
        """Test parser initialization."""
        parser = HTMLParser()
        assert parser.timeout == 30
        assert parser.default_selector == "article"

    def test_parse_empty_content(self):
        """Test parsing empty HTML."""
        parser = HTMLParser()
        articles = parser.parse("", selector="article")
        assert articles == []

    def test_parse_with_selector(self):
        """Test parsing with custom selector."""
        parser = HTMLParser()
        html = """
        <html>
        <body>
        <article class="news-item">
            <h2>Test Title</h2>
            <a href="https://example.com">Link</a>
            <p>Test description</p>
        </article>
        </body>
        </html>
        """
        articles = parser.parse(html, selector=".news-item")
        assert len(articles) > 0

    def test_normalize_articles(self):
        """Test article normalization."""
        parser = HTMLParser()
        articles = [
            {
                "title": "Test Article",
                "url": "https://example.com",
                "description": "Test description",
                "date": "2024-01-01",
            }
        ]
        normalized = parser.normalize(articles)
        assert len(normalized) == 1
        assert normalized[0]["title"] == "Test Article"
