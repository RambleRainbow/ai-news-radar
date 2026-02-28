"""
Base parser class for AI News Radar.

This module defines the abstract base class that all parsers must implement.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """
    Abstract base class for all news parsers.

    All parsers must implement the fetch() and parse() methods.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the parser.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.name = self.__class__.__name__

    @abstractmethod
    def fetch(self, url: str, **kwargs) -> str:
        """
        Fetch raw content from a URL.

        Args:
            url: The URL to fetch from
            **kwargs: Additional fetch arguments

        Returns:
            Raw content as string

        Raises:
            RequestException: If fetch fails
        """
        pass

    @abstractmethod
    def parse(self, content: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Parse fetched content into article dictionaries.

        Args:
            content: The raw content to parse
            **kwargs: Additional parsing arguments

        Returns:
            List of article dictionaries with keys:
                - title: Article title
                - url: Article URL
                - date: Publish date (datetime or ISO string)
                - description: Article description/summary
                - source: Source name
                - language: Language code (optional)
        """
        pass

    def fetch_and_parse(self, url: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Convenience method to fetch and parse in one call.

        Args:
            url: The URL to fetch from
            **kwargs: Additional arguments passed to fetch and parse

        Returns:
            List of parsed articles
        """
        content = self.fetch(url, **kwargs)
        return self.parse(content, **kwargs)

    def normalize(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize article dictionaries to ensure consistent format.

        Args:
            articles: List of article dictionaries

        Returns:
            Normalized articles
        """
        normalized = []

        for article in articles:
            norm = {
                "title": article.get("title", "").strip(),
                "url": article.get("url", "").strip(),
                "description": article.get("description", "").strip(),
                "source": article.get("source", self.name),
                "language": article.get("language", "en"),
            }

            # Normalize date
            date = article.get("date")
            if date:
                if isinstance(date, datetime):
                    norm["date"] = date
                elif isinstance(date, str):
                    try:
                        norm["date"] = datetime.fromisoformat(
                            date.replace("Z", "+00:00")
                        )
                    except (ValueError, AttributeError):
                        logger.warning(f"Could not parse date: {date}")
                        norm["date"] = None
                else:
                    norm["date"] = None
            else:
                norm["date"] = None

            # Add optional fields if present
            for key in ["author", "tags", "image_url", "language", "bilingual_title"]:
                if key in article and article[key]:
                    norm[key] = article[key]

            # Only include if has required fields
            if norm["title"] and norm["url"]:
                normalized.append(norm)
            else:
                logger.warning(f"Skipping article missing required fields: {article}")

        return normalized

    def validate_article(self, article: Dict[str, Any]) -> bool:
        """
        Validate that an article has all required fields.

        Args:
            article: Article dictionary

        Returns:
            True if valid, False otherwise
        """
        required = ["title", "url"]

        for field in required:
            if field not in article or not article[field]:
                logger.debug(f"Article missing required field '{field}': {article}")
                return False

        return True


class ParserError(Exception):
    """Base exception for parser errors."""

    pass


class FetchError(ParserError):
    """Exception raised when fetching content fails."""

    pass


class ParseError(ParserError):
    """Exception raised when parsing content fails."""

    pass
