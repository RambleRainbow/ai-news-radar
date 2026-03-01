"""
Tests for storage modules.
"""

from datetime import datetime, timezone, timedelta

from skill.storage import JSONStorage


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

    def test_load_metadata(self, temp_dir, sample_articles):
        """Test loading metadata from storage."""
        storage = JSONStorage(temp_dir / "test.json")
        storage.save(sample_articles)

        metadata = storage.load_metadata()
        assert metadata is not None
        assert metadata["count"] == 3
        assert metadata["version"] == "1.0"
        assert metadata["generated_at"] is not None

    def test_load_metadata_nonexistent(self, temp_dir):
        """Test loading metadata from nonexistent file."""
        storage = JSONStorage(temp_dir / "nonexistent.json")
        metadata = storage.load_metadata()
        assert metadata is None

    def test_backup_created(self, temp_dir, sample_articles):
        """Test that backup is created when saving."""
        storage = JSONStorage(temp_dir / "test.json")
        storage.save(sample_articles[:1])

        # Save again with backup
        storage.save(sample_articles)

        # Check backup file exists
        backup_files = list(temp_dir.glob("test.backup_*.json"))
        assert len(backup_files) > 0

        # Verify backup has old data
        backup_storage = JSONStorage(backup_files[0])
        backup_articles = backup_storage.load()
        assert len(backup_articles) == 1

    def test_save_without_backup(self, temp_dir, sample_articles):
        """Test saving without creating backup."""
        storage = JSONStorage(temp_dir / "test.json")
        storage.save(sample_articles[:1])

        # Save again without backup
        storage.save(sample_articles, backup=False)

        # Check no backup file exists
        backup_files = list(temp_dir.glob("test.backup_*.json"))
        assert len(backup_files) == 0

    def test_get_by_time_range(self, temp_dir):
        """Test filtering articles by time range."""
        storage = JSONStorage(temp_dir / "test.json")

        now = datetime.now(timezone.utc)
        articles = [
            {"title": "Article 1", "url": "https://example.com/1", "date": (now - timedelta(hours=48)).isoformat()},
            {"title": "Article 2", "url": "https://example.com/2", "date": (now - timedelta(hours=24)).isoformat()},
            {"title": "Article 3", "url": "https://example.com/3", "date": (now - timedelta(hours=1)).isoformat()},
        ]
        storage.save(articles)

        # Get articles from last 12 hours
        recent = storage.get_by_time_range(start=now - timedelta(hours=12))
        assert len(recent) == 1
        assert recent[0]["title"] == "Article 3"

        # Get articles from last 30 hours
        recent = storage.get_by_time_range(start=now - timedelta(hours=30))
        assert len(recent) == 2

    def test_get_by_keywords(self, temp_dir):
        """Test filtering articles by keywords."""
        storage = JSONStorage(temp_dir / "test.json")

        articles = [
            {"title": "AI Breakthrough in Machine Learning", "url": "https://example.com/1"},
            {"title": "Python Tutorial for Beginners", "url": "https://example.com/2"},
            {"title": "Deep Learning with TensorFlow", "url": "https://example.com/3"},
        ]
        storage.save(articles)

        # Search for "AI"
        ai_articles = storage.get_by_keywords(["AI"])
        assert len(ai_articles) == 1

        # Search for "Learning"
        learning_articles = storage.get_by_keywords(["Learning"])
        assert len(learning_articles) == 2

        # Search for multiple keywords
        multi_articles = storage.get_by_keywords(["AI", "Python"])
        assert len(multi_articles) == 2

    def test_get_keywords_case_insensitive(self, temp_dir):
        """Test keyword search is case insensitive by default."""
        storage = JSONStorage(temp_dir / "test.json")

        articles = [
            {"title": "AI Breakthrough in Machine Learning", "url": "https://example.com/1"},
        ]
        storage.save(articles)

        # Search with different case
        articles_lower = storage.get_by_keywords(["ai"])
        articles_upper = storage.get_by_keywords(["AI"])
        assert len(articles_lower) == 1
        assert len(articles_upper) == 1

    def test_get_keywords_custom_fields(self, temp_dir):
        """Test keyword search in custom fields."""
        storage = JSONStorage(temp_dir / "test.json")

        articles = [
            {"title": "AI Article", "url": "https://example.com/1", "summary": "This is about artificial intelligence"},
            {"title": "Tech Article", "url": "https://example.com/2", "summary": "About technology"},
        ]
        storage.save(articles)

        # Search in summary only
        summary_articles = storage.get_by_keywords(["artificial"], fields=["summary"])
        assert len(summary_articles) == 1
        assert summary_articles[0]["title"] == "AI Article"

    def test_get_sources(self, temp_dir, sample_articles):
        """Test getting list of unique sources."""
        storage = JSONStorage(temp_dir / "test.json")
        storage.save(sample_articles)

        sources = storage.get_sources()
        assert "Tech News" in sources
        assert "AI Weekly" in sources
        assert "General News" in sources

    def test_get_sources_empty(self, temp_dir):
        """Test getting sources from empty storage."""
        storage = JSONStorage(temp_dir / "test.json")
        storage.save([])

        sources = storage.get_sources()
        assert sources == []

    def test_get_latest_articles(self, temp_dir):
        """Test getting latest articles sorted by date."""
        storage = JSONStorage(temp_dir / "test.json")

        now = datetime.now(timezone.utc)
        articles = [
            {"title": "Oldest", "url": "https://example.com/1", "date": (now - timedelta(days=3)).isoformat()},
            {"title": "Middle", "url": "https://example.com/2", "date": (now - timedelta(days=2)).isoformat()},
            {"title": "Newest", "url": "https://example.com/3", "date": (now - timedelta(days=1)).isoformat()},
        ]
        storage.save(articles)

        # Get latest 2
        latest = storage.get_latest_articles(limit=2)
        assert len(latest) == 2
        assert latest[0]["title"] == "Newest"
        assert latest[1]["title"] == "Middle"

    def test_append_without_deduplication(self, temp_dir):
        """Test appending without URL deduplication."""
        storage = JSONStorage(temp_dir / "test.json")
        storage.save(
            [{"title": "Article 1", "url": "https://example.com/1"}]
        )

        storage.append(
            [{"title": "Duplicate", "url": "https://example.com/1"}],
            deduplicate=False
        )

        assert storage.get_count() == 2
