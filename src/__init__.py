"""
AI News Radar - Core implementation.

This package contains the core implementation of the AI News Radar skill.
It provides a production-grade AI/tech news aggregator with support for
multiple sources, RSS/HTML parsing, AI topic filtering, and deduplication.
"""

from .config import RadarConfig, load_default_config
from .core import NewsRadar, setup_logger
from .filters import AITopicFilter, DuplicateFilter, TimeFilter
from .parsers import BaseParser, HTMLParser, RSSParser
from .storage import JSONStorage

__all__ = [
    # Main class
    "NewsRadar",
    # Configuration
    "RadarConfig",
    "load_default_config",
    # Utilities
    "setup_logger",
    # Parsers
    "BaseParser",
    "RSSParser",
    "HTMLParser",
    # Filters
    "AITopicFilter",
    "TimeFilter",
    "DuplicateFilter",
    # Storage
    "JSONStorage",
]

__version__ = "1.0.0"
