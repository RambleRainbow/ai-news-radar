"""
RSS and Atom feed parser for AI News Radar.

This module provides parsing capabilities for RSS and Atom feeds using feedparser.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import feedparser
import requests

from .base_parser import BaseParser, FetchError, ParseError

logger = logging.getLogger(__name__)


class RSSParser(BaseParser):
    """
    Parser for RSS and Atom feeds.

    Supports:
    - RSS 0.9, 1.0, 2.0
    - Atom 0.3, 1.0
    - OPML file parsing for feed lists
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the RSS parser.

        Args:
            config: Configuration dictionary with optional keys:
                - timeout: Request timeout (default: 30)
                - user_agent: User agent string
                - proxies: Proxy configuration
                - max_entries: Maximum entries to parse
        """
        super().__init__(config)
        self.timeout = self.config.get("timeout", 30)
        self.user_agent = self.config.get("user_agent", "AI News Radar/1.0")
        self.proxies = self.config.get("proxies")
        self.max_entries = self.config.get("max_entries")

    def fetch(self, url: str, **kwargs) -> str:
        """
        Fetch RSS/Atom feed content from URL.

        Args:
            url: Feed URL
            **kwargs: Additional fetch arguments

        Returns:
            Raw feed content as string

        Raises:
            FetchError: If fetch fails
        """
        timeout = kwargs.get("timeout", self.timeout)

        headers = kwargs.get("headers", {"User-Agent": self.user_agent})

        proxies = kwargs.get("proxies", self.proxies)

        try:
            response = requests.get(
                url,
                timeout=timeout,
                headers=headers,
                proxies=proxies,
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise FetchError(f"Failed to fetch feed from {url}: {e}") from e

    def parse(self, content: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Parse RSS/Atom feed content.

        Args:
            content: Raw feed content
            **kwargs: Additional parsing arguments:
                - source_name: Override source name
                - max_entries: Override max entries

        Returns:
            List of article dictionaries

        Raises:
            ParseError: If parsing fails
        """
        source_name = kwargs.get(
            "source_name", self.config.get("source_name", "RSS Feed")
        )
        max_entries = kwargs.get("max_entries", self.max_entries)

        try:
            feed = feedparser.parse(content)

            # Check for errors
            if feed.get("bozo"):
                logger.warning(f"Feed parsing warning: {feed.get('bozo_exception')}")

            if not feed.get("entries"):
                logger.debug("No entries found in feed")
                return []

            # Get feed metadata
            feed_title = feed.feed.get("title", source_name)
            feed_link = feed.feed.get("link", "")

            # Parse entries
            articles = []
            for entry in feed.entries[:max_entries] if max_entries else feed.entries:
                article = self._parse_entry(entry, feed_title, feed_link)
                if article:
                    articles.append(article)

            logger.info(f"Parsed {len(articles)} articles from {feed_title}")
            return self.normalize(articles)

        except Exception as e:
            raise ParseError(f"Failed to parse feed content: {e}") from e

    def _parse_entry(
        self, entry: Any, feed_title: str, feed_link: str
    ) -> Optional[Dict[str, Any]]:
        """
        Parse a single feed entry.

        Args:
            entry: Feedparser entry object
            feed_title: Title of the source feed
            feed_link: Link to the source feed

        Returns:
            Article dictionary or None if parsing fails
        """
        try:
            # Title
            title = entry.get("title", "")
            if not title:
                return None

            # Link/URL
            url = entry.get("link", "")
            if not url:
                return None

            # Description/summary
            description = entry.get("description") or entry.get("summary", "")

            # Date
            date = self._parse_date(
                entry.get("published_parsed") or entry.get("updated_parsed")
            )

            # Author
            author = entry.get("author", "")

            # Tags/categories
            tags = []
            if "tags" in entry:
                tags = [tag.get("term", "") for tag in entry.tags if tag.get("term")]

            # Media/thumbnail
            image_url = None
            if "media_thumbnail" in entry:
                image_url = entry.media_thumbnail[0].get("url")
            elif "enclosures" in entry:
                for enclosure in entry.enclosures:
                    if enclosure.get("type", "").startswith("image/"):
                        image_url = enclosure.get("href")
                        break

            return {
                "title": title,
                "url": url,
                "description": description,
                "date": date,
                "source": feed_title,
                "author": author,
                "tags": tags,
                "image_url": image_url,
                "language": "en",  # Default, could be detected
            }

        except Exception as e:
            logger.warning(f"Failed to parse entry: {e}")
            return None

    def _parse_date(self, date_tuple: Optional[tuple]) -> Optional[datetime]:
        """
        Parse date from feedparser time tuple.

        Args:
            date_tuple: Time tuple from feedparser

        Returns:
            datetime object or None
        """
        if not date_tuple:
            return None

        try:
            return datetime(*date_tuple[:6])
        except (TypeError, ValueError) as e:
            logger.debug(f"Could not parse date tuple: {e}")
            return None

    def fetch_and_parse(self, url: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch and parse a feed in one call.

        Args:
            url: Feed URL
            **kwargs: Additional arguments

        Returns:
            List of parsed articles
        """
        try:
            content = self.fetch(url, **kwargs)
            return self.parse(content, **kwargs)
        except (FetchError, ParseError) as e:
            logger.error(f"Failed to fetch and parse {url}: {e}")
            return []

    def parse_opml(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse an OPML file to extract RSS feed URLs.

        Args:
            file_path: Path to OPML file

        Returns:
            List of feed information dictionaries with keys:
                - title: Feed title
                - url: Feed URL
                - type: Feed type (usually 'rss')
        """
        try:
            url = (
                file_path
                if file_path.startswith(("http://", "https://"))
                else f"file://{file_path}"
            )
            content = self.fetch(url)
            feed = feedparser.parse(content)

            feeds = []
            for outline in feed.get("entries", []):
                if outline.get("type") == "rss" or "xmlUrl" in outline:
                    feeds.append(
                        {
                            "title": outline.get(
                                "title", outline.get("text", "Unknown")
                            ),
                            "url": outline.get("xmlUrl", ""),
                            "type": "rss",
                        }
                    )

            logger.info(f"Found {len(feeds)} RSS feeds in OPML file")
            return feeds

        except Exception as e:
            logger.error(f"Failed to parse OPML file {file_path}: {e}")
            return []
