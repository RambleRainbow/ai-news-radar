"""
Storage modules for AI News Radar.

This package contains storage implementations:
- json_storage: JSON file storage
- sqlite_storage: SQLite database storage (optional)
"""

from .json_storage import JSONStorage

__all__ = [
    "JSONStorage",
]
