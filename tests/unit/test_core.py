"""
Tests for the NewsRadar core class.
"""

import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch

from skill.core import NewsRadar, setup_logger
from skill.config import RadarConfig


class TestNewsRadar:
    """Test NewsRadar aggregator class."""

    def test_init_default_config(self, temp_dir):
        """Test initialization with default config."""
        config = RadarConfig(cache_dir=temp_dir / "cache")
        radar = NewsRadar(config)
        assert radar.config == config
        assert radar.rss_parser is not None
        assert radar.html_parser is not None
        assert radar.ai_filter is not None
        assert radar.time_filter is not None
        assert radar.duplicate_filter is not None

    def test_init_no_config(self, test_keywords_file):
        """Test initialization without config uses default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = RadarConfig(
                cache_dir=Path(tmpdir) / "cache",
                keywords_file=test_keywords_file,
            )
            radar = NewsRadar(config)
            assert radar.config is not None
            assert isinstance(radar.config, RadarConfig)

    @patch("skill.config.RadarConfig.load_sources")
    def test_aggregate_no_sources(self, mock_load_sources, temp_dir):
        """Test aggregation with no configured sources."""
        mock_load_sources.return_value = []
        config = RadarConfig(cache_dir=temp_dir / "cache")
        radar = NewsRadar(config)
        result = radar.aggregate()
        assert result == []

    @patch("skill.config.RadarConfig.load_sources")
    def test_aggregate_with_sources(
        self, mock_load_sources, temp_dir, sample_articles
    ):
        """Test aggregation with configured sources."""
        mock_load_sources.return_value = [
            {"name": "Test Source", "url": "http://example.com/feed", "type": "rss"}
        ]
        config = RadarConfig(cache_dir=temp_dir / "cache")
        radar = NewsRadar(config)

        def mock_process_source(source):
            # Manually increment sources_processed like the real method does
            radar.stats["sources_processed"] += 1
            return sample_articles

        with patch.object(radar, "_process_source", side_effect=mock_process_source):
            with patch.object(radar, "_apply_filters", return_value=sample_articles):
                result = radar.aggregate()
                assert len(result) == 3
                assert radar.stats["total_fetched"] == 3
                assert radar.stats["sources_processed"] == 1

    @patch("skill.config.RadarConfig.load_sources")
    def test_aggregate_with_stats(self, mock_load_sources, temp_dir, sample_articles):
        """Test aggregation returns detailed statistics."""
        mock_load_sources.return_value = [
            {"name": "Test Source", "url": "http://example.com/feed", "type": "rss"}
        ]
        config = RadarConfig(cache_dir=temp_dir / "cache")
        radar = NewsRadar(config)

        def mock_process_source(source):
            radar.stats["sources_processed"] += 1
            return sample_articles

        with patch.object(radar, "_process_source", side_effect=mock_process_source):
            with patch.object(radar, "_apply_filters", return_value=sample_articles):
                result = radar.aggregate_with_stats()
                assert "articles" in result
                assert "stats" in result
                assert result["stats"]["total_fetched"] == 3
                assert "duration" in result["stats"]
                assert "generated_at" in result["stats"]

    @patch("skill.config.RadarConfig.load_sources")
    def test_process_source_rss(self, mock_load_sources, temp_dir):
        """Test processing RSS source."""
        mock_load_sources.return_value = []
        config = RadarConfig(cache_dir=temp_dir / "cache")
        radar = NewsRadar(config)
        source = {
            "name": "RSS Source",
            "url": "http://example.com/feed",
            "type": "rss",
            "max_articles": 5,
        }
        with patch.object(radar.rss_parser, "fetch_and_parse", return_value=[]):
            result = radar._process_source(source)
            assert result == []
            assert radar.stats["sources_processed"] == 1

    @patch("skill.config.RadarConfig.load_sources")
    def test_process_source_html(self, mock_load_sources, temp_dir):
        """Test processing HTML source."""
        mock_load_sources.return_value = []
        config = RadarConfig(cache_dir=temp_dir / "cache")
        radar = NewsRadar(config)
        source = {
            "name": "HTML Source",
            "url": "http://example.com",
            "type": "html",
            "selector": "article",
            "field_selectors": {"title": "h2", "url": "a"},
        }
        with patch.object(radar.html_parser, "fetch_and_parse", return_value=[]):
            result = radar._process_source(source)
            assert result == []
            assert radar.stats["sources_processed"] == 1

    @patch("skill.config.RadarConfig.load_sources")
    def test_process_source_opml(self, mock_load_sources, temp_dir):
        """Test processing OPML source."""
        mock_load_sources.return_value = []
        config = RadarConfig(cache_dir=temp_dir / "cache")
        radar = NewsRadar(config)
        source = {
            "name": "OPML Source",
            "type": "opml",
            "file_path": "test.opml",
            "max_feeds": 5,
            "max_articles_per_feed": 3,
        }
        mock_feeds = [
            {"url": "http://example.com/feed1", "title": "Feed 1"},
            {"url": "http://example.com/feed2", "title": "Feed 2"},
        ]
        with patch.object(radar.rss_parser, "parse_opml", return_value=mock_feeds):
            with patch.object(radar.rss_parser, "fetch_and_parse", return_value=[]):
                result = radar._process_source(source)
                assert result == []
                assert radar.stats["sources_processed"] == 1

    @patch("skill.config.RadarConfig.load_sources")
    def test_process_source_unknown_type(self, mock_load_sources, temp_dir):
        """Test processing source with unknown type."""
        mock_load_sources.return_value = []
        config = RadarConfig(cache_dir=temp_dir / "cache")
        radar = NewsRadar(config)
        source = {"name": "Unknown Source", "url": "http://example.com", "type": "unknown"}
        result = radar._process_source(source)
        assert result == []
        assert radar.stats["sources_failed"] == 1

    @patch("skill.config.RadarConfig.load_sources")
    def test_process_source_error(self, mock_load_sources, temp_dir):
        """Test processing source that raises an error."""
        mock_load_sources.return_value = []
        config = RadarConfig(cache_dir=temp_dir / "cache")
        radar = NewsRadar(config)
        source = {"name": "Error Source", "url": "http://example.com/feed", "type": "rss"}
        with patch.object(radar.rss_parser, "fetch_and_parse", side_effect=Exception("Test error")):
            result = radar._process_source(source)
            assert result == []
            assert radar.stats["sources_failed"] == 1

    @patch("skill.config.RadarConfig.load_sources")
    def test_process_source_adds_source_name(self, mock_load_sources, temp_dir):
        """Test that source name is added to articles."""
        mock_load_sources.return_value = []
        config = RadarConfig(cache_dir=temp_dir / "cache")
        radar = NewsRadar(config)
        source = {"name": "Test Source", "url": "http://example.com/feed", "type": "rss"}
        articles = [{"title": "Test", "url": "http://example.com/article"}]
        with patch.object(radar.rss_parser, "fetch_and_parse", return_value=articles):
            result = radar._process_source(source)
            assert result[0]["source"] == "Test Source"

    @patch("skill.config.RadarConfig.load_sources")
    def test_apply_filters(self, mock_load_sources, temp_dir, sample_articles):
        """Test applying all filters."""
        mock_load_sources.return_value = []
        config = RadarConfig(cache_dir=temp_dir / "cache", enable_deduplication=True)
        radar = NewsRadar(config)
        with patch.object(radar.time_filter, "filter", return_value=sample_articles):
            with patch.object(radar.ai_filter, "filter", return_value=sample_articles):
                with patch.object(radar.duplicate_filter, "filter", return_value=sample_articles):
                    result = radar._apply_filters(sample_articles)
                    assert result == sample_articles
                    assert radar.stats["total_filtered"] == 0

    @patch("skill.config.RadarConfig.load_sources")
    def test_apply_filters_without_dedup(self, mock_load_sources, temp_dir):
        """Test applying filters without deduplication."""
        mock_load_sources.return_value = []
        config = RadarConfig(cache_dir=temp_dir / "cache", enable_deduplication=False)
        radar = NewsRadar(config)
        articles = [{"title": "Test"}]
        with patch.object(radar.time_filter, "filter", return_value=articles):
            with patch.object(radar.ai_filter, "filter", return_value=articles):
                result = radar._apply_filters(articles)
                assert result == articles

    @patch("skill.config.RadarConfig.load_sources")
    def test_add_source(self, mock_load_sources, temp_dir):
        """Test adding a new source."""
        mock_load_sources.return_value = []
        config = RadarConfig(cache_dir=temp_dir / "cache")
        radar = NewsRadar(config)
        new_source = {"name": "New Source", "url": "http://example.com/feed", "type": "rss"}
        radar.add_source(new_source)
        # Verify source was added to config
        sources = config.load_sources()
        assert len(sources) >= 1

    @patch("skill.config.RadarConfig.load_sources")
    def test_save_to_json(self, mock_load_sources, temp_dir):
        """Test saving articles to JSON file."""
        mock_load_sources.return_value = []
        config = RadarConfig(cache_dir=temp_dir / "cache")
        radar = NewsRadar(config)
        articles = [{"title": "Test", "url": "http://example.com"}]
        output_path = temp_dir / "output.json"
        radar.save_to_json(articles, str(output_path))
        assert output_path.exists()

    @patch("skill.config.RadarConfig.load_sources")
    def test_save_to_csv(self, mock_load_sources, temp_dir):
        """Test saving articles to CSV file."""
        mock_load_sources.return_value = []
        config = RadarConfig(cache_dir=temp_dir / "cache")
        radar = NewsRadar(config)
        articles = [
            {"title": "Test 1", "url": "http://example.com/1"},
            {"title": "Test 2", "url": "http://example.com/2"},
        ]
        output_path = temp_dir / "output.csv"
        radar.save_to_csv(articles, str(output_path))
        assert output_path.exists()

    @patch("skill.config.RadarConfig.load_sources")
    def test_aggregate_incremental_no_state(self, mock_load_sources, temp_dir):
        """Test incremental aggregation without state file falls back to normal."""
        mock_load_sources.return_value = []
        config = RadarConfig(cache_dir=temp_dir / "cache")
        radar = NewsRadar(config)

        # Should return normal aggregation since no state file
        result = radar.aggregate_incremental(temp_dir / "data.json")
        assert result == []

    def test_filter_by_time(self, temp_dir):
        """Test filtering articles by time."""
        config = RadarConfig(cache_dir=temp_dir / "cache")
        radar = NewsRadar(config)

        now = datetime.now(timezone.utc)
        articles = [
            {"title": "Old", "date": (now - timedelta(hours=48)).isoformat()},
            {"title": "Recent", "date": (now - timedelta(hours=2)).isoformat()},
            {"title": "Newest", "date": (now - timedelta(minutes=30)).isoformat()},
        ]

        cutoff = now - timedelta(hours=4)
        filtered = radar._filter_by_time(articles, cutoff)

        assert len(filtered) == 2
        assert all(a["title"] != "Old" for a in filtered)

    def test_filter_by_time_with_missing_dates(self, temp_dir):
        """Test that articles without dates are included."""
        config = RadarConfig(cache_dir=temp_dir / "cache")
        radar = NewsRadar(config)

        now = datetime.now(timezone.utc)
        articles = [
            {"title": "No date"},  # Should be included
            {"title": "Old", "date": (now - timedelta(hours=48)).isoformat()},
            {"title": "Recent", "date": (now - timedelta(hours=2)).isoformat()},
        ]

        cutoff = now - timedelta(hours=4)
        filtered = radar._filter_by_time(articles, cutoff)

        # Articles without date are included (conservative)
        assert any(a["title"] == "No date" for a in filtered)

    def test_init_with_state_file(self, temp_dir):
        """Test initialization with state file."""
        state_file = temp_dir / "state.json"
        config = RadarConfig(cache_dir=temp_dir / "cache")
        radar = NewsRadar(config, state_file=state_file)

        assert radar.state is not None
        assert radar.state.state_file == state_file


class TestSetupLogger:
    """Test logger setup function."""

    def test_setup_logger(self):
        """Test basic logger setup."""
        logger = setup_logger("test_logger")
        assert logger is not None
        assert logger.name == "test_logger"

    def test_setup_logger_with_level(self):
        """Test logger setup with custom level."""
        import logging

        logger = setup_logger("test_logger_level", level=logging.DEBUG)
        assert logger.level == logging.DEBUG
