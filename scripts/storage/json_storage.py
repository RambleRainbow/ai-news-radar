"""
JSON storage implementation for AI News Radar.

This module provides JSON file-based storage for articles.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class JSONStorage:
    """
    JSON file-based storage for articles.

    Supports saving, loading, and appending articles to JSON files.
    """

    def __init__(self, file_path: Path):
        """
        Initialize JSON storage.

        Args:
            file_path: Path to JSON storage file
        """
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, articles: List[Dict[str, Any]]) -> None:
        """
        Save articles to JSON file.

        Args:
            articles: List of article dictionaries
        """
        # Prepare data for JSON serialization
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

        # Save to file
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "generated_at": datetime.now().isoformat(),
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

    def append(self, articles: List[Dict[str, Any]]) -> None:
        """
        Append articles to existing JSON file.

        Args:
            articles: List of article dictionaries to append
        """
        existing = self.load()

        # Deduplicate by URL
        existing_urls = {a.get("url") for a in existing}

        new_articles = [a for a in articles if a.get("url") not in existing_urls]

        # Combine and save
        combined = existing + new_articles
        self.save(combined)

        logger.info(f"Appended {len(new_articles)} new articles (total: {len(combined)})")

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
