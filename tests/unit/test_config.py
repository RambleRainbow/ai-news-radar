"""
Tests for configuration management.
"""

from pathlib import Path

from src.config import RadarConfig, load_default_config


class TestRadarConfig:
    """Test RadarConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = RadarConfig()
        assert config.update_interval_hours == 24
        assert config.max_articles_per_source == 20
        assert config.enable_cache is True
        assert config.enable_deduplication is True
        assert config.request_timeout == 30
        assert config.verbose is False
        assert config.dry_run is False

    def test_custom_values(self):
        """Test custom configuration values."""
        config = RadarConfig(
            update_interval_hours=48,
            max_articles_per_source=10,
            request_timeout=60,
        )
        assert config.update_interval_hours == 48
        assert config.max_articles_per_source == 10
        assert config.request_timeout == 60

    def test_ensure_directories(self, temp_dir):
        """Test directory creation."""
        config = RadarConfig(
            cache_dir=temp_dir / "cache",
            sources_file=temp_dir / "sources.yaml",
            keywords_file=temp_dir / "keywords.yaml",
        )
        config.ensure_directories()
        assert config.cache_dir.exists()
        assert config.sources_file.parent.exists()
        assert config.keywords_file.parent.exists()


class TestLoadDefaultConfig:
    """Test loading default configuration."""

    def test_load_default(self):
        """Test loading default configuration."""
        config = load_default_config()
        assert isinstance(config, RadarConfig)
        assert config.update_interval_hours == 24


class TestRadarConfigLoadMethods:
    """Test RadarConfig loading methods."""

    def test_load_sources_nonexistent(self, temp_dir):
        """Test loading from nonexistent sources file."""
        config = RadarConfig(sources_file=temp_dir / "nonexistent.yaml")
        sources = config.load_sources()
        assert sources == []

    def test_load_keywords_nonexistent(self, temp_dir):
        """Test loading from nonexistent keywords file."""
        config = RadarConfig(keywords_file=temp_dir / "nonexistent.yaml")
        keywords = config.load_keywords()
        assert keywords == {}

    def test_load_sources_from_yaml(self, temp_dir, test_keywords):
        """Test loading sources from YAML file."""
        import yaml

        sources_file = temp_dir / "sources.yaml"
        test_sources = [{"name": "Test", "url": "https://example.com", "type": "rss"}]
        with open(sources_file, "w", encoding="utf-8") as f:
            yaml.dump({"sources": test_sources}, f)

        config = RadarConfig(sources_file=sources_file)
        sources = config.load_sources()
        assert len(sources) == 1
        assert sources[0]["name"] == "Test"

    def test_load_keywords_from_yaml(self, temp_dir, test_keywords):
        """Test loading keywords from YAML file."""
        import yaml

        keywords_file = temp_dir / "keywords.yaml"
        with open(keywords_file, "w", encoding="utf-8") as f:
            yaml.dump({"keywords": test_keywords}, f)

        config = RadarConfig(keywords_file=keywords_file)
        keywords = config.load_keywords()
        assert "primary" in keywords

    def test_from_yaml_nonexistent(self, temp_dir):
        """Test from_yaml with nonexistent file."""
        config = RadarConfig.from_yaml(temp_dir / "nonexistent.yaml")
        assert isinstance(config, RadarConfig)
        # Should use defaults when file not found
        assert config.update_interval_hours == 24

    def test_from_yaml_with_values(self, temp_dir):
        """Test from_yaml with custom values."""
        import yaml

        config_file = temp_dir / "config.yaml"
        custom_config = {
            "update_interval_hours": 48,
            "max_articles_per_source": 15,
        }
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(custom_config, f)

        config = RadarConfig.from_yaml(config_file)
        assert config.update_interval_hours == 48
        assert config.max_articles_per_source == 15

    def test_from_yaml_with_path_strings(self, temp_dir):
        """Test that path strings are converted to Path objects."""
        import yaml

        config_file = temp_dir / "config.yaml"
        custom_config = {
            "sources_file": str(temp_dir / "sources.yaml"),
            "cache_dir": str(temp_dir / "cache"),
        }
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(custom_config, f)

        config = RadarConfig.from_yaml(config_file)
        assert isinstance(config.sources_file, Path)
        assert isinstance(config.cache_dir, Path)
