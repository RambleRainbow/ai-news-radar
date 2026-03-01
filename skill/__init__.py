"""
AI News Radar - Standalone skill package.

This package is a self-contained skill that can be used directly
without requiring installation from PyPI.
"""

from .config import RadarConfig, load_default_config
from .core.news_radar import NewsRadar, setup_logger
from .filters import AITopicFilter, DuplicateFilter, TimeFilter
from .parsers import BaseParser, HTMLParser, RSSParser
from .state import State
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
    # State
    "State",
    # Storage
    "JSONStorage",
]

__version__ = "1.0.0"
