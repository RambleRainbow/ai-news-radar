"""
Configuration management for AI News Radar.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


@dataclass
class RadarConfig:
    """Configuration data class for AI News Radar."""

    # File paths
    sources_file: Path = field(
        default_factory=lambda: Path("skill/assets/data/sources.yaml")
    )
    keywords_file: Path = field(
        default_factory=lambda: Path("skill/assets/data/keywords.yaml")
    )

    # Core settings
    update_interval_hours: int = 24
    max_articles_per_source: int = 20
    output_format: str = "json"

    # Feature flags
    enable_cache: bool = True
    enable_deduplication: bool = True

    # Network settings
    request_timeout: int = 30
    user_agent: str = "AI News Radar/1.0"
    proxies: Optional[Dict[str, str]] = None

    # Cache settings
    cache_dir: Path = field(default_factory=lambda: Path(".cache"))
    cache_ttl_hours: int = 1

    # Output
    verbose: bool = False
    dry_run: bool = False

    def ensure_directories(self):
        """Ensure required directories exist."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.sources_file.parent.mkdir(parents=True, exist_ok=True)
        self.keywords_file.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_yaml(cls, path: Path) -> "RadarConfig":
        """
        Load configuration from YAML file.

        Args:
            path: Path to YAML configuration file

        Returns:
            RadarConfig instance
        """
        path = Path(path)
        if not path.exists():
            logger.warning(f"Config file not found: {path}, using defaults")
            return cls()

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            # Convert string paths to Path objects
            if "sources_file" in data:
                data["sources_file"] = Path(data["sources_file"])
            if "keywords_file" in data:
                data["keywords_file"] = Path(data["keywords_file"])
            if "cache_dir" in data:
                data["cache_dir"] = Path(data["cache_dir"])

            return cls(**data)
        except Exception as e:
            logger.error(f"Failed to load config from {path}: {e}")
            return cls()

    def load_sources(self) -> List[Dict[str, Any]]:
        """
        Load news sources from configuration file.

        Returns:
            List of source configuration dictionaries
        """
        try:
            with open(self.sources_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                return data.get("sources", [])
        except FileNotFoundError:
            logger.warning(f"Sources file not found: {self.sources_file}")
            return []
        except Exception as e:
            logger.error(f"Failed to load sources: {e}")
            return []

    def load_keywords(self) -> Dict[str, List[str]]:
        """
        Load AI keywords from configuration file.

        Returns:
            Dictionary of keyword lists
        """
        try:
            with open(self.keywords_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                return data.get("keywords", {})
        except FileNotFoundError:
            logger.warning(f"Keywords file not found: {self.keywords_file}")
            return {}
        except Exception as e:
            logger.error(f"Failed to load keywords: {e}")
            return {}


def load_default_config() -> RadarConfig:
    """
    Load default configuration.

    Returns:
        RadarConfig instance with defaults
    """
    return RadarConfig()
