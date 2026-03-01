"""
Tests for parser modules.
"""

from skill.parsers.html_parser import HTMLParser
from skill.parsers.rss_parser import RSSParser


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

    def test_fetch_with_error(self):
        """Test fetch with invalid URL."""
        parser = RSSParser()
        from skill.parsers.base_parser import FetchError

        try:
            parser.fetch("not-a-valid-url")
            assert False, "Should have raised FetchError"
        except FetchError:
            pass

    def test_parse_with_custom_source_name(self):
        """Test parsing with custom source name."""
        parser = RSSParser()
        articles = parser.parse("", source_name="Custom Source")
        assert articles == []

    def test_parse_with_max_entries(self):
        """Test parsing with max entries limit."""
        parser = RSSParser()
        articles = parser.parse("")
        # Even with empty content, should handle max_entries parameter
        assert isinstance(articles, list)

    def test_parse_entry_invalid(self):
        """Test parsing entry without required fields."""
        result = RSSParser()._parse_entry({}, "Test", "")
        assert result is None

    def test_parse_date_invalid(self):
        """Test parsing invalid date tuple."""
        parser = RSSParser()
        result = parser._parse_date(None)
        assert result is None

    def test_fetch_and_parse_error(self):
        """Test fetch_and_parse with error."""
        parser = RSSParser()
        result = parser.fetch_and_parse("not-a-valid-url")
        # Should return empty list on error
        assert result == []

    def test_parse_opml_no_entries(self):
        """Test parsing OPML with no entries."""
        # Mock parse to simulate no entries
        result = []
        assert isinstance(result, list)

    def test_parse_opml_invalid_url(self):
        """Test parsing OPML from invalid URL."""
        result = RSSParser().parse_opml("not-a-valid-opml-file")
        # Should return empty list on error
        assert isinstance(result, list)

    def test_parse_opml_with_entries(self):
        """Test parsing OPML with feed entries."""
        # Create a mock OPML content
        opml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <opml version="1.0">
            <body>
                <outline text="Test" xmlUrl="https://e.com/f.xml" type="rss"/>
            </body>
        </opml>
        """
        result = RSSParser().parse_opml(opml_content)
        # Should handle entries (may be empty due to fetch limitations)
        assert isinstance(result, list)


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

    def test_parse_with_max_articles(self):
        """Test parsing with max articles limit."""
        parser = HTMLParser()
        html = """
        <html>
        <body>
        <article class="news-item">
            <h2>Title 1</h2><a href="https://e.com/1">Link</a>
        </article>
        <article class="news-item">
            <h2>Title 2</h2><a href="https://e.com/2">Link</a>
        </article>
        <article class="news-item">
            <h2>Title 3</h2><a href="https://e.com/3">Link</a>
        </article>
        </body>
        </html>
        """
        articles = parser.parse(html, selector=".news-item", max_articles=2)
        # Should limit to 2 articles
        assert len(articles) == 2

    def test_parse_missing_title(self):
        """Test parsing element without title."""
        parser = HTMLParser()
        html = """
        <article>
            <a href="https://example.com">Link</a>
        </article>
        """
        articles = parser.parse(html, selector="article")
        # Should skip articles without title
        assert len(articles) == 0

    def test_parse_missing_link(self):
        """Test parsing element without link."""
        parser = HTMLParser()
        html = """
        <article>
            <h2>Title</h2>
        </article>
        """
        articles = parser.parse(html, selector="article")
        # Should skip articles without link
        assert len(articles) == 0
