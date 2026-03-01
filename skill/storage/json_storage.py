"""
JSON storage implementation for AI News Radar.

This module provides JSON file-based storage for articles with version management
and query capabilities.
"""

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class JSONStorage:
    """
    JSON file-based storage for articles.

    Supports saving, loading, version management, and querying articles.
    """

    # Storage versions
    VERSION_LATEST = "latest"
    VERSION_ARCHIVE = "archive"
    VERSION_BACKUP = "backup"

    def __init__(self, file_path: Path):
        """
        Initialize JSON storage.

        Args:
            file_path: Path to JSON storage file
        """
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, articles: List[Dict[str, Any]], backup: bool = True,
             overwrite: bool = True) -> None:
        """
        Save articles to JSON file with optional backup.

        Args:
            articles: List of article dictionaries
            backup: Create backup before overwriting existing file
            overwrite: Overwrite existing file or merge
        """
        # Create backup before overwriting
        if backup and self.file_path.exists() and overwrite:
            backup_path = self._get_backup_path()
            shutil.copy2(self.file_path, backup_path)
            logger.debug(f"Created backup at {backup_path}")

        # Prepare data for JSON serialization
        serializable_data = self._serialize_articles(articles)

        # Save to file
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "version": "1.0",
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "count": len(serializable_data),
                        "articles": serializable_data,
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            logger.info(f"Saved {len(serializable_data)} articles to {self.file_path}")

        except (IOError, TypeError) as e:
            logger.error(f"Failed to save to {self.file_path}: {e}")
            raise

    def _get_backup_path(self) -> Path:
        """Generate backup file path with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.file_path.parent / f"{self.file_path.stem}.backup_{timestamp}.json"

    def _serialize_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Serialize articles for JSON storage."""
        serializable_data = []

        for article in articles:
            serializable = {}
            for key, value in article.items():
                # Skip internal keys starting with underscore
                if key.startswith("_"):
                    continue

                # Convert datetime to ISO string
                if isinstance(value, datetime):
                    serializable[key] = value.isoformat()
                # Convert lists
                elif isinstance(value, list):
                    serializable[key] = list(value)
                # Other serializable types
                elif isinstance(value, (str, int, float, bool)):
                    serializable[key] = value
                else:
                    serializable[key] = str(value)

            serializable_data.append(serializable)

        return serializable_data

    def load(self) -> List[Dict[str, Any]]:
        """
        Load articles from JSON file.

        Returns:
            List of article dictionaries
        """
        if not self.file_path.exists():
            logger.debug(f"No existing file at {self.file_path}")
            return []

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            articles = data.get("articles", [])
            logger.info(f"Loaded {len(articles)} articles from {self.file_path}")
            return articles

        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load from {self.file_path}: {e}")
            return []

    def load_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Load metadata from storage file.

        Returns:
            Dictionary containing version, generated_at, and count
        """
        if not self.file_path.exists():
            return None

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return {
                "version": data.get("version", "unknown"),
                "generated_at": data.get("generated_at"),
                "count": data.get("count", 0),
            }

        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load metadata from {self.file_path}: {e}")
            return None

    def append(self, articles: List[Dict[str, Any]], deduplicate: bool = True) -> None:
        """
        Append articles to existing JSON file.

        Args:
            articles: List of article dictionaries to append
            deduplicate: Deduplicate by URL before appending
        """
        existing = self.load()

        # Deduplicate by URL if enabled
        if deduplicate:
            existing_urls = {a.get("url") for a in existing}
            new_articles = [a for a in articles if a.get("url") not in existing_urls]
        else:
            new_articles = articles

        # Combine and save
        combined = existing + new_articles
        self.save(combined)

        logger.info(
            f"Appended {len(new_articles)} new articles (total: {len(combined)})"
        )

    def get_by_source(self, source: str) -> List[Dict[str, Any]]:
        """
        Get articles filtered by source.

        Args:
            source: Source name to filter by

        Returns:
            Filtered list of articles
        """
        articles = self.load()
        return [a for a in articles if a.get("source") == source]

    def get_by_time_range(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        field: str = "date"
    ) -> List[Dict[str, Any]]:
        """
        Get articles filtered by time range.

        Args:
            start: Start datetime (inclusive)
            end: End datetime (inclusive)
            field: Field name containing the datetime value

        Returns:
            Filtered list of articles
        """
        articles = self.load()
        filtered = []

        for article in articles:
            article_date_str = article.get(field)
            if not article_date_str:
                continue

            try:
                # Parse ISO format datetime
                if isinstance(article_date_str, str):
                    article_date = datetime.fromisoformat(article_date_str.replace("Z", "+00:00"))
                elif isinstance(article_date_str, datetime):
                    article_date = article_date_str
                else:
                    continue

                # Check if within range
                if start and article_date < start:
                    continue
                if end and article_date > end:
                    continue

                filtered.append(article)

            except (ValueError, TypeError):
                logger.debug(f"Failed to parse date for article: {article.get('url')}")
                continue

        return filtered

    def get_by_keywords(
        self,
        keywords: List[str],
        fields: Optional[List[str]] = None,
        case_sensitive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get articles filtered by keywords.

        Args:
            keywords: List of keywords to search for
            fields: List of fields to search (default: title, description)
            case_sensitive: Whether search should be case sensitive

        Returns:
            Filtered list of articles
        """
        if fields is None:
            fields = ["title", "description", "summary"]

        articles = self.load()
        filtered = []

        for article in articles:
            for keyword in keywords:
                if self._article_contains_keyword(article, keyword, fields, case_sensitive):
                    filtered.append(article)
                    break

        return filtered

    def _article_contains_keyword(
        self,
        article: Dict[str, Any],
        keyword: str,
        fields: List[str],
        case_sensitive: bool
    ) -> bool:
        """Check if article contains keyword in any of the specified fields."""
        search_keyword = keyword if case_sensitive else keyword.lower()

        for field in fields:
            field_value = article.get(field, "")
            if not isinstance(field_value, str):
                continue

            search_value = field_value if case_sensitive else field_value.lower()
            if search_keyword in search_value:
                return True

        return False

    def get_count(self) -> int:
        """
        Get total article count.

        Returns:
            Number of articles in storage
        """
        articles = self.load()
        return len(articles)

    def clear(self) -> None:
        """Clear all articles from storage."""
        self.save([])
        logger.info(f"Cleared all articles from {self.file_path}")

    def get_sources(self) -> List[str]:
        """
        Get list of all unique sources in storage.

        Returns:
            List of unique source names
        """
        articles = self.load()
        return sorted(set(a.get("source") for a in articles if a.get("source")))

    def get_latest_articles(self, limit: int = 10, field: str = "date") -> List[Dict[str, Any]]:
        """
        Get the latest articles sorted by date.

        Args:
            limit: Maximum number of articles to return
            field: Field name containing the datetime value

        Returns:
            List of latest articles
        """
        articles = self.load()

        # Filter articles with valid dates
        valid_articles = []
        for article in articles:
            article_date_str = article.get(field)
            if not article_date_str:
                continue

            try:
                if isinstance(article_date_str, str):
                    article_date = datetime.fromisoformat(article_date_str.replace("Z", "+00:00"))
                elif isinstance(article_date_str, datetime):
                    article_date = article_date_str
                else:
                    continue

                valid_articles.append((article_date, article))
            except (ValueError, TypeError):
                continue

        # Sort by date (newest first) and return top N
        valid_articles.sort(key=lambda x: x[0], reverse=True)
        return [article for _, article in valid_articles[:limit]]
