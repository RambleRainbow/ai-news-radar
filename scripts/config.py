"""
Configuration management for AI News Radar.

This module handles loading and managing configuration from YAML files
and provides a structured configuration object.
"""

import os
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class RadarConfig:
    """
    Configuration data class for AI News Radar.

    Attributes:
        sources_file: Path to sources configuration YAML
        keywords_file: Path to keywords configuration YAML
        cache_dir: Directory for caching fetched data
        update_interval_hours: Time window for incremental updates
        max_articles_per_source: Maximum articles to fetch per source
        request_timeout: HTTP request timeout in seconds
        output_format: Output format (json, csv, rss)
        enable_cache: Enable caching mechanism
        enable_deduplication: Enable article deduplication
        proxies: Proxy configuration for requests
        user_agent: User agent string for HTTP requests
    """

    sources_file: Path
    keywords_file: Path
    cache_dir: Path
    update_interval_hours: int = 24
    max_articles_per_source: int = 20
    request_timeout: int = 30
    output_format: str = "json"
    enable_cache: bool = True
    enable_deduplication: bool = True
    proxies: Optional[Dict[str, str]] = None
    user_agent: str = "AI News Radar/1.0 (+https://github.com/yourname/ai-news-radar)"

    # Runtime settings
    verbose: bool = False
    dry_run: bool = False

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_yaml(cls, path: Path) -> "RadarConfig":
        """
        Load configuration from a YAML file.

        Args:
            path: Path to the YAML configuration file

        Returns:
            RadarConfig instance

        Raises:
            FileNotFoundError: If configuration file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        # Extract paths
        base_dir = path.parent
        sources_file = base_dir / config_data.get(
            "sources_file", "assets/data/sources.yaml"
        )
        keywords_file = base_dir / config_data.get(
            "keywords_file", "assets/data/keywords.yaml"
        )
        cache_dir = base_dir / config_data.get("cache_dir", "cache")

        # Create config instance
        config = cls(
            sources_file=sources_file,
            keywords_file=keywords_file,
            cache_dir=cache_dir,
            update_interval_hours=config_data.get("update_interval_hours", 24),
            max_articles_per_source=config_data.get("max_articles_per_source", 20),
            request_timeout=config_data.get("request_timeout", 30),
            output_format=config_data.get("output_format", "json"),
            enable_cache=config_data.get("enable_cache", True),
            enable_deduplication=config_data.get("enable_deduplication", True),
            proxies=config_data.get("proxies"),
            user_agent=config_data.get(
                "user_agent",
                "AI News Radar/1.0 (+https://github.com/yourname/ai-news-radar)",
            ),
        )

        # Load additional metadata
        config.metadata = config_data.get("metadata", {})

        return config

    @classmethod
    def from_env(cls) -> "RadarConfig":
        """
        Load configuration from environment variables.

        Environment Variables:
            AI_NEWS_SOURCES_FILE: Path to sources file
            AI_NEWS_KEYWORDS_FILE: Path to keywords file
            AI_NEWS_CACHE_DIR: Cache directory
            AI_NEWS_UPDATE_INTERVAL: Update interval in hours
            AI_NEWS_MAX_ARTICLES: Max articles per source
            AI_NEWS_TIMEOUT: Request timeout
            AI_NEWS_OUTPUT_FORMAT: Output format
            AI_NEWS_ENABLE_CACHE: Enable cache (true/false)
            AI_NEWS_ENABLE_DEDUP: Enable deduplication (true/false)
            AI_NEARS_VERBOSE: Enable verbose mode (true/false)

        Returns:
            RadarConfig instance
        """
        base_dir = Path(os.getcwd())

        return cls(
            sources_file=Path(
                os.getenv("AI_NEWS_SOURCES_FILE", "assets/data/sources.yaml")
            ),
            keywords_file=Path(
                os.getenv("AI_NEWS_KEYWORDS_FILE", "assets/data/keywords.yaml")
            ),
            cache_dir=Path(os.getenv("AI_NEWS_CACHE_DIR", "cache")),
            update_interval_hours=int(
                os.getenv("AI_NEWS_UPDATE_INTERVAL", "24")
            ),
            max_articles_per_source=int(os.getenv("AI_NEWS_MAX_ARTICLES", "20")),
            request_timeout=int(os.getenv("AI_NEWS_TIMEOUT", "30")),
            output_format=os.getenv("AI_NEWS_OUTPUT_FORMAT", "json"),
            enable_cache=os.getenv("AI_NEWS_ENABLE_CACHE", "true").lower() == "true",
            enable_deduplication=os.getenv("AI_NEWS_ENABLE_DEDUP", "true").lower()
            == "true",
            verbose=os.getenv("AI_NEARS_VERBOSE", "false").lower() == "true",
        )

    def to_yaml(self, path: Path) -> None:
        """
        Save configuration to a YAML file.

        Args:
            path: Path to save the configuration
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        config_data = {
            "sources_file": str(self.sources_file.relative_to(path.parent.parent)),
            "keywords_file": str(self.keywords_file.relative_to(path.parent.parent)),
            "cache_dir": str(self.cache_dir.relative_to(path.parent.parent)),
            "update_interval_hours": self.update_interval_hours,
            "max_articles_per_source": self.max_articles_per_source,
            "request_timeout": self.request_timeout,
            "output_format": self.output_format,
            "enable_cache": self.enable_cache,
            "enable_deduplication": self.enable_deduplication,
        }

        if self.proxies:
            config_data["proxies"] = self.proxies

        if self.user_agent != "AI News Radar/1.0 (+https://github.com/yourname/ai-news-radar)":
            config_data["user_agent"] = self.user_agent

        if self.metadata:
            config_data["metadata"] = self.metadata

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, default_flow_style=False)

    def load_sources(self) -> List[Dict[str, Any]]:
        """
        Load news sources configuration.

        Returns:
            List of source configuration dictionaries
        """
        if not self.sources_file.exists():
            return []

        with open(self.sources_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return data.get("sources", [])

    def load_keywords(self) -> Dict[str, List[str]]:
        """
        Load AI keywords configuration.

        Returns:
            Dictionary with keyword categories
        """
        if not self.keywords_file.exists():
            return {"primary": [], "secondary": [], "aliases": []}

        with open(self.keywords_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return {
            "primary": data.get("primary", []),
            "secondary": data.get("secondary", []),
            "aliases": data.get("aliases", []),
        }

    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_request_headers(self) -> Dict[str, str]:
        """
        Get HTTP request headers.

        Returns:
            Dictionary of headers
        """
        return {"User-Agent": self.user_agent}

    def get_request_kwargs(self) -> Dict[str, Any]:
        """
        Get keyword arguments for requests library.

        Returns:
            Dictionary of request kwargs
        """
        kwargs = {
            "timeout": self.request_timeout,
            "headers": self.get_request_headers(),
        }

        if self.proxies:
            kwargs["proxies"] = self.proxies

        return kwargs


def load_default_config() -> RadarConfig:
    """
    Load default configuration from standard locations.

    Checks for config in the following order:
    1. ./config.yaml
    2. ./assets/data/config.yaml
    3. Environment variables
    4. Default hardcoded values

    Returns:
        RadarConfig instance
    """
    current_dir = Path(os.getcwd())

    # Try ./config.yaml
    config_path = current_dir / "config.yaml"
    if config_path.exists():
        return RadarConfig.from_yaml(config_path)

    # Try ./assets/data/config.yaml
    config_path = current_dir / "assets" / "data" / "config.yaml"
    if config_path.exists():
        return RadarConfig.from_yaml(config_path)

    # Use environment or defaults
    return RadarConfig.from_env()
