"""
AI News Radar - A production-grade AI/tech news aggregator.

This package provides tools for aggregating news from multiple sources,
filtering by AI topics, and managing incremental updates.
"""

__version__ = "1.0.0"
__author__ = "AI News Radar Team"

from .main import NewsRadar
from .config import RadarConfig

__all__ = [
    "NewsRadar",
    "RadarConfig",
]
