"""
Tests for cache utilities.
"""

from datetime import datetime, timedelta

from src.utils.cache import CacheManager


class TestCacheManager:
    """Test cache manager functionality."""

    def test_init(self, temp_dir):
        """Test cache manager initialization."""
        cache_dir = temp_dir / "cache"
        cache = CacheManager(cache_dir)
        assert cache.cache_dir == cache_dir
        assert cache_dir.exists()

    def test_init_with_ttl(self, temp_dir):
        """Test initialization with custom TTL."""
        cache = CacheManager(temp_dir / "cache", ttl_hours=24)
        assert cache.ttl_hours == 24

    def test_set_and_get_json(self, temp_dir):
        """Test setting and getting JSON cache."""
        cache = CacheManager(temp_dir / "cache")
        cache.set("test_key", {"data": "value"}, format="json")
        result = cache.get("test_key", format="json")
        assert result == {"data": "value"}

    def test_set_and_get_pickle(self, temp_dir):
        """Test setting and getting pickle cache."""
        cache = CacheManager(temp_dir / "cache")
        test_data = ["list", "of", "items"]
        cache.set("test_key", test_data, format="pickle")
        result = cache.get("test_key", format="pickle")
        assert result == test_data

    def test_get_miss(self, temp_dir):
        """Test cache miss returns None."""
        cache = CacheManager(temp_dir / "cache")
        result = cache.get("nonexistent_key")
        assert result is None

    def test_get_expired(self, temp_dir):
        """Test that expired cache returns None."""
        cache = CacheManager(temp_dir / "cache", ttl_hours=1)
        cache.set("test_key", "value")

        # Manually modify file mtime to simulate expiration
        cache_path = cache._get_cache_path("test_key")
        old_time = datetime.now() - timedelta(hours=2)
        import os

        os.utime(cache_path, (old_time.timestamp(), old_time.timestamp()))

        result = cache.get("test_key")
        assert result is None

    def test_get_or_fetch_cached(self, temp_dir):
        """Test get_or_fetch with cached value."""
        cache = CacheManager(temp_dir / "cache")
        cache.set("test_key", "cached_value")
        result = cache.get_or_fetch("test_key", lambda: "fetched_value")
        assert result == "cached_value"

    def test_get_or_fetch_miss(self, temp_dir):
        """Test get_or_fetch with cache miss."""
        cache = CacheManager(temp_dir / "cache")
        result = cache.get_or_fetch("test_key", lambda: "fetched_value")
        assert result == "fetched_value"
        # Should have cached the fetched value
        cached = cache.get("test_key")
        assert cached == "fetched_value"

    def test_clear_key(self, temp_dir):
        """Test clearing specific cache key."""
        cache = CacheManager(temp_dir / "cache")
        cache.set("test_key", "value")
        cache.clear("test_key")
        result = cache.get("test_key")
        assert result is None

    def test_clear_all(self, temp_dir):
        """Test clearing all cache."""
        cache = CacheManager(temp_dir / "cache")
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cleanup_expired(self, temp_dir):
        """Test cleaning up expired cache files."""
        cache = CacheManager(temp_dir / "cache", ttl_hours=1)
        cache.set("expired_key", "value")

        # Manually make file old
        cache_path = cache._get_cache_path("expired_key")
        old_time = datetime.now() - timedelta(hours=2)
        import os

        os.utime(cache_path, (old_time.timestamp(), old_time.timestamp()))

        # Add a fresh cache entry
        cache.set("fresh_key", "value")

        removed = cache.cleanup_expired()
        assert removed == 1
        assert cache.get("expired_key") is None
        assert cache.get("fresh_key") is not None

    def test_get_cache_key(self, temp_dir):
        """Test cache key generation."""
        cache = CacheManager(temp_dir / "cache")
        key1 = cache._get_cache_key("test")
        key2 = cache._get_cache_key("test")
        assert key1 == key2
        assert len(key1) == 32  # MD5 hash length

    def test_get_cache_path(self, temp_dir):
        """Test getting cache file path."""
        cache = CacheManager(temp_dir / "cache")
        path = cache._get_cache_path("test_key")
        assert str(path).startswith(str(cache.cache_dir))
        assert path.name == cache._get_cache_key("test_key")

    def test_is_expired_nonexistent(self, temp_dir):
        """Test is_expired for nonexistent file."""
        cache = CacheManager(temp_dir / "cache")
        cache_path = cache._get_cache_path("nonexistent")
        assert cache._is_expired(cache_path) is True

    def test_custom_ttl_in_get(self, temp_dir):
        """Test custom TTL in get method."""
        cache = CacheManager(temp_dir / "cache", ttl_hours=1)
        cache.set("test_key", "value")

        # Use custom TTL longer than default
        result = cache.get("test_key", ttl_hours=24)
        # Should still be within custom TTL
        assert result is not None
