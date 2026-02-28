"""
Tests for storage modules.
"""

from datetime import datetime

from src.storage.json_storage import JSONStorage


class TestJSONStorage:
    """Test JSON storage functionality."""

    def test_init(self, temp_dir):
        """Test storage initialization."""
        storage = JSONStorage(temp_dir / "test.json")
        assert storage.file_path.name == "test.json"

    def test_save_articles(self, temp_dir, sample_articles):
        """Test saving articles to JSON."""
        storage = JSONStorage(temp_dir / "test.json")
        storage.save(sample_articles)
        assert storage.get_count() == 3

    def test_save_empty_articles(self, temp_dir):
        """Test saving empty list."""
        storage = JSONStorage(temp_dir / "test.json")
        storage.save([])
        assert storage.get_count() == 0

    def test_load_articles(self, temp_dir, sample_articles):
        """Test loading articles from JSON."""
        storage = JSONStorage(temp_dir / "test.json")
        storage.save(sample_articles)

        loaded = storage.load()
        assert len(loaded) == 3
        assert loaded[0]["title"] == "AI Breakthrough in Natural Language Processing"

    def test_load_nonexistent_file(self, temp_dir):
        """Test loading from nonexistent file."""
        storage = JSONStorage(temp_dir / "nonexistent.json")
        articles = storage.load()
        assert articles == []

    def test_append_articles(self, temp_dir, sample_articles):
        """Test appending articles."""
        storage = JSONStorage(temp_dir / "test.json")
        storage.save(sample_articles[:1])

        new_articles = sample_articles[1:]
        storage.append(new_articles)

        assert storage.get_count() == 3

    def test_append_deduplication_by_url(self, temp_dir):
        """Test that append deduplicates by URL."""
        storage = JSONStorage(temp_dir / "test.json")
        storage.save(
            [
                {"title": "Article 1", "url": "https://example.com/1"},
            ]
        )

        storage.append(
            [
                {"title": "Article 1", "url": "https://example.com/1"},
                {"title": "Article 2", "url": "https://example.com/2"},
            ]
        )

        assert storage.get_count() == 2

    def test_get_by_source(self, temp_dir, sample_articles):
        """Test filtering by source."""
        storage = JSONStorage(temp_dir / "test.json")
        storage.save(sample_articles)

        tech_news = storage.get_by_source("Tech News")
        assert len(tech_news) == 1
        assert tech_news[0]["title"] == "AI Breakthrough in Natural Language Processing"

    def test_get_by_source_empty(self, temp_dir):
        """Test getting articles for nonexistent source."""
        storage = JSONStorage(temp_dir / "test.json")
        storage.save([])

        results = storage.get_by_source("Nonexistent")
        assert results == []

    def test_clear(self, temp_dir, sample_articles):
        """Test clearing storage."""
        storage = JSONStorage(temp_dir / "test.json")
        storage.save(sample_articles)
        storage.clear()
        assert storage.get_count() == 0

    def test_save_with_datetime(self, temp_dir):
        """Test saving articles with datetime fields."""
        storage = JSONStorage(temp_dir / "test.json")
        articles = [
            {
                "title": "Test",
                "url": "https://example.com",
                "date": datetime.now(),
            }
        ]
        storage.save(articles)

        loaded = storage.load()
        assert loaded[0]["date"] is not None
        assert isinstance(loaded[0]["date"], str)

    def test_save_with_internal_keys(self, temp_dir):
        """Test that internal keys starting with _ are skipped."""
        storage = JSONStorage(temp_dir / "test.json")
        articles = [
            {
                "title": "Test",
                "url": "https://example.com",
                "_internal": "should be skipped",
                "_score": 0.95,
            }
        ]
        storage.save(articles)

        loaded = storage.load()
        assert "_internal" not in loaded[0]
        assert "_score" not in loaded[0]
