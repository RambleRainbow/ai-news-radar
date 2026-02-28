"""
Caching utilities for AI News Radar.

This module provides simple file-based caching.
"""

import hashlib
import json
import logging
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Simple file-based cache manager.

    Supports TTL-based expiration and different serialization formats.
    """

    def __init__(self, cache_dir: Path, ttl_hours: int = 1):
        """
        Initialize the cache manager.

        Args:
            cache_dir: Directory for cache files
            ttl_hours: Default time-to-live in hours
        """
        self.cache_dir = Path(cache_dir)
        self.ttl_hours = ttl_hours
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, key: str) -> str:
        """
        Get cache filename from key.

        Args:
            key: Cache key

        Returns:
            Cache filename
        """
        # Hash the key for safe filename
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        """
        Get full cache file path.

        Args:
            key: Cache key

        Returns:
            Path to cache file
        """
        return self.cache_dir / self._get_cache_key(key)

    def _is_expired(self, cache_path: Path, ttl_hours: Optional[int] = None) -> bool:
        """
        Check if cache file is expired.

        Args:
            cache_path: Path to cache file
            ttl_hours: Time-to-live in hours (uses default if None)

        Returns:
            True if expired or doesn't exist
        """
        if not cache_path.exists():
            return True

        ttl = ttl_hours if ttl_hours is not None else self.ttl_hours
        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        cutoff = datetime.now() - timedelta(hours=ttl)

        return mtime < cutoff

    def get(
        self,
        key: str,
        format: str = "json",
        ttl_hours: Optional[int] = None,
    ) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key
            format: Serialization format ('json' or 'pickle')
            ttl_hours: Time-to-live override

        Returns:
            Cached value or None if not found/expired
        """
        cache_path = self._get_cache_path(key)

        if self._is_expired(cache_path, ttl_hours):
            logger.debug(f"Cache miss for key: {key}")
            return None

        try:
            with open(cache_path, "r" if format == "json" else "rb") as f:
                if format == "json":
                    return json.load(f)
                else:
                    return pickle.load(f)
        except (json.JSONDecodeError, pickle.PickleError, IOError) as e:
            logger.warning(f"Failed to load cache for key {key}: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        format: str = "json",
    ) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            format: Serialization format ('json' or 'pickle')
        """
        cache_path = self._get_cache_path(key)

        try:
            with open(cache_path, "w" if format == "json" else "wb") as f:
                if format == "json":
                    json.dump(value, f, indent=2)
                else:
                    pickle.dump(value, f)

            logger.debug(f"Cached value for key: {key}")
        except (TypeError, IOError) as e:
            logger.warning(f"Failed to cache value for key {key}: {e}")

    def get_or_fetch(
        self,
        key: str,
        fetch_func: Callable[[], Any],
        format: str = "json",
        ttl_hours: Optional[int] = None,
    ) -> Any:
        """
        Get from cache or fetch using provided function.

        Args:
            key: Cache key
            fetch_func: Function to fetch fresh data
            format: Serialization format
            ttl_hours: Time-to-live override

        Returns:
            Cached or fetched value
        """
        cached = self.get(key, format=format, ttl_hours=ttl_hours)
        if cached is not None:
            return cached

        # Fetch fresh data
        value = fetch_func()

        # Cache it
        self.set(key, value, format=format)

        return value

    def clear(self, key: Optional[str] = None) -> None:
        """
        Clear cache entry or all cache.

        Args:
            key: Specific key to clear (clears all if None)
        """
        if key:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
                logger.debug(f"Cleared cache for key: {key}")
        else:
            for cache_file in self.cache_dir.iterdir():
                cache_file.unlink()
            logger.debug("Cleared all cache")

    def cleanup_expired(self) -> int:
        """
        Remove expired cache files.

        Returns:
            Number of files removed
        """
        removed = 0

        for cache_file in self.cache_dir.iterdir():
            if self._is_expired(cache_file):
                cache_file.unlink()
                removed += 1

        logger.info(f"Cleaned up {removed} expired cache files")
        return removed
