"""
HTML parser for AI News Radar.

This module provides parsing capabilities for HTML web pages using BeautifulSoup4.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from .base_parser import BaseParser, FetchError, ParseError

logger = logging.getLogger(__name__)


class HTMLParser(BaseParser):
    """
    Parser for HTML web pages.

    Uses CSS selectors to extract articles from web pages.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the HTML parser.

        Args:
            config: Configuration dictionary with optional keys:
                - timeout: Request timeout (default: 30)
                - user_agent: User agent string
                - proxies: Proxy configuration
                - selector: CSS selector for article elements
                - max_articles: Maximum articles to parse
        """
        super().__init__(config)
        self.timeout = self.config.get("timeout", 30)
        self.user_agent = self.config.get(
            "user_agent", "AI News Radar/1.0"
        )
        self.proxies = self.config.get("proxies")
        self.default_selector = self.config.get("selector", "article")
        self.max_articles = self.config.get("max_articles")

        # Selector configuration for article fields
        self.field_selectors = self.config.get("field_selectors", {})

    def fetch(self, url: str, **kwargs) -> str:
        """
        Fetch HTML content from URL.

        Args:
            url: Page URL
            **kwargs: Additional fetch arguments

        Returns:
            Raw HTML content as string

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
            raise FetchError(f"Failed to fetch page from {url}: {e}") from e

    def parse(self, content: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Parse HTML content to extract articles.

        Args:
            content: Raw HTML content
            **kwargs: Additional parsing arguments:
                - source_url: Base URL for resolving relative links
                - source_name: Override source name
                - selector: CSS selector for article elements
                - max_articles: Override max articles limit
                - field_selectors: Custom field selectors

        Returns:
            List of article dictionaries

        Raises:
            ParseError: If parsing fails
        """
        source_url = kwargs.get("source_url", "")
        source_name = kwargs.get("source_name", self.config.get("source_name", "HTML Source"))
        selector = kwargs.get("selector", self.default_selector)
        max_articles = kwargs.get("max_articles", self.max_articles)
        field_selectors = kwargs.get("field_selectors", self.field_selectors)

        try:
            soup = BeautifulSoup(content, "html.parser")

            # Find article elements
            article_elements = soup.select(selector)
            if not article_elements:
                logger.debug(f"No articles found with selector: {selector}")
                return []

            # Limit articles if specified
            if max_articles:
                article_elements = article_elements[:max_articles]

            # Parse each article
            articles = []
            for element in article_elements:
                article = self._parse_article_element(
                    element, source_url, source_name, field_selectors
                )
                if article:
                    articles.append(article)

            logger.info(f"Parsed {len(articles)} articles from {source_name}")
            return self.normalize(articles)

        except Exception as e:
            raise ParseError(f"Failed to parse HTML content: {e}") from e

    def _parse_article_element(
        self,
        element: Any,
        source_url: str,
        source_name: str,
        field_selectors: Dict[str, str],
    ) -> Optional[Dict[str, Any]]:
        """
        Parse a single article element.

        Args:
            element: BeautifulSoup element
            source_url: Base URL for resolving links
            source_name: Source name
            field_selectors: Custom selectors for fields

        Returns:
            Article dictionary or None if parsing fails
        """
        try:
            # Get selectors (use custom or default)
            title_selector = field_selectors.get("title", "h2, h3, .title, [class*='title']")
            link_selector = field_selectors.get("link", "a[href]")
            desc_selector = field_selectors.get("description", "p, .desc, .description, .summary")
            date_selector = field_selectors.get("date", ".date, time, [datetime], [class*='date']")
            author_selector = field_selectors.get("author", ".author, [class*='author']")
            tag_selector = field_selectors.get("tags", ".tag, .category, [class*='tag']")

            # Title
            title_elem = element.select_one(title_selector)
            title = title_elem.get_text(strip=True) if title_elem else ""
            if not title:
                return None

            # Link
            link_elem = element.select_one(link_selector)
            link = link_elem.get("href") if link_elem else ""
            if link:
                link = urljoin(source_url, link)
            if not link:
                return None

            # Description
            desc_elem = element.select_one(desc_selector)
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            # Date
            date = self._parse_date(element, date_selector)

            # Author
            author_elem = element.select_one(author_selector)
            author = author_elem.get_text(strip=True) if author_elem else ""

            # Tags
            tags = []
            tag_elems = element.select(tag_selector)
            for tag_elem in tag_elems:
                tag_text = tag_elem.get_text(strip=True)
                if tag_text:
                    tags.append(tag_text)

            # Image
            image_url = self._parse_image(element, source_url)

            return {
                "title": title,
                "url": link,
                "description": description,
                "date": date,
                "source": source_name,
                "author": author,
                "tags": tags,
                "image_url": image_url,
                "language": "en",  # Default, could be detected
            }

        except Exception as e:
            logger.warning(f"Failed to parse article element: {e}")
            return None

    def _parse_date(self, element: Any, selector: str) -> Optional[datetime]:
        """
        Parse date from article element.

        Args:
            element: BeautifulSoup element
            selector: CSS selector for date element

        Returns:
            datetime object or None
        """
        try:
            date_elem = element.select_one(selector)
            if not date_elem:
                return None

            # Try datetime attribute first
            date_str = date_elem.get("datetime") or date_elem.get("content")

            # Fall back to text content
            if not date_str:
                date_str = date_elem.get_text(strip=True)

            if not date_str:
                return None

            # Parse the date string
            return date_parser.parse(date_str)

        except (ValueError, AttributeError) as e:
            logger.debug(f"Could not parse date: {e}")
            return None

    def _parse_image(self, element: Any, base_url: str) -> Optional[str]:
        """
        Parse image URL from article element.

        Args:
            element: BeautifulSoup element
            base_url: Base URL for resolving relative URLs

        Returns:
            Image URL or None
        """
        try:
            # Try img element with src
            img_elem = element.select_one("img[src]")
            if img_elem:
                img_url = img_elem.get("src") or img_elem.get("data-src")
                if img_url:
                    return urljoin(base_url, img_url)

            # Try background image
            for elem in element.select("[style*='background-image']"):
                style = elem.get("style", "")
                if "url(" in style:
                    start = style.find("url(") + 4
                    end = style.find(")", start)
                    img_url = style[start:end].strip('"\'')
                    if img_url:
                        return urljoin(base_url, img_url)

            return None

        except Exception as e:
            logger.debug(f"Could not parse image: {e}")
            return None

    def fetch_and_parse(self, url: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch and parse a page in one call.

        Args:
            url: Page URL
            **kwargs: Additional arguments:
                - selector: CSS selector for articles
                - max_articles: Max articles limit
                - field_selectors: Custom field selectors

        Returns:
            List of parsed articles
        """
        try:
            kwargs.setdefault("source_url", url)
            content = self.fetch(url, **kwargs)
            return self.parse(content, **kwargs)
        except (FetchError, ParseError) as e:
            logger.error(f"Failed to fetch and parse {url}: {e}")
            return []
