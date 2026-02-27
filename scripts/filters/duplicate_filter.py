"""
Duplicate filter for AI News Radar.

This module removes duplicate articles based on URL, title similarity, or content hash.
"""

import logging
import hashlib
from typing import List, Dict, Set, Optional
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class DuplicateFilter:
    """
    Remove duplicate articles from aggregated results.

    Supports duplicate detection by:
    - URL (exact match)
    - Title (exact or fuzzy match)
    - Content hash (exact match)
    """

    def __init__(
        self,
        by_url: bool = True,
        by_title: bool = True,
        title_similarity_threshold: float = 0.85,
        by_content: bool = False,
    ):
        """
        Initialize the duplicate filter.

        Args:
            by_url: Enable URL-based duplicate detection
            by_title: Enable title-based duplicate detection
            title_similarity_threshold: Similarity threshold for title matching (0.0 to 1.0)
            by_content: Enable content hash-based duplicate detection
        """
        self.by_url = by_url
        self.by_title = by_title
        self.title_similarity_threshold = title_similarity_threshold
        self.by_content = by_content

        # Track seen values
        self.seen_urls: Set[str] = set()
        self.seen_titles: Set[str] = set()
        self.seen_hashes: Set[str] = set()

    def filter(self, articles: List[Dict]) -> List[Dict]:
        """
        Filter out duplicate articles.

        Args:
            articles: List of article dictionaries

        Returns:
            List of articles with duplicates removed
        """
        filtered = []
        duplicates_count = 0

        for article in articles:
            if self._is_duplicate(article):
                duplicates_count += 1
                continue

            # Track this article
            self._track_article(article)
            filtered.append(article)

        logger.info(
            f"Duplicate Filter: Removed {duplicates_count} duplicates, "
            f"kept {len(filtered)} unique articles"
        )
        return filtered

    def _is_duplicate(self, article: Dict) -> bool:
        """
        Check if article is a duplicate.

        Args:
            article: Article dictionary

        Returns:
            True if duplicate, False otherwise
        """
        # Check by URL
        if self.by_url:
            url = article.get("url", "").strip()
            if url in self.seen_urls:
                return True

        # Check by title (exact)
        if self.by_title:
            title = article.get("title", "").strip().lower()
            if title in self.seen_titles:
                return True

            # Check by title similarity
            for seen_title in self.seen_titles:
                similarity = SequenceMatcher(None, title, seen_title).ratio()
                if similarity >= self.title_similarity_threshold:
                    return True

        # Check by content hash
        if self.by_content:
            content_hash = self._compute_content_hash(article)
            if content_hash in self.seen_hashes:
                return True

        return False

    def _track_article(self, article: Dict) -> None:
        """
        Track article for duplicate detection.

        Args:
            article: Article dictionary
        """
        # Track URL
        if self.by_url:
            url = article.get("url", "").strip()
            if url:
                self.seen_urls.add(url)

        # Track title
        if self.by_title:
            title = article.get("title", "").strip().lower()
            if title:
                self.seen_titles.add(title)

        # Track content hash
        if self.by_content:
            content_hash = self._compute_content_hash(article)
            if content_hash:
                self.seen_hashes.add(content_hash)

    def _compute_content_hash(self, article: Dict) -> str:
        """
        Compute hash of article content for duplicate detection.

        Args:
            article: Article dictionary

        Returns:
            MD5 hash string
        """
        content_parts = [
            article.get("title", ""),
            article.get("description", ""),
            article.get("source", ""),
        ]
        content = "|".join(part for part in content_parts if part)

        return hashlib.md5(content.encode()).hexdigest()

    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL for comparison.

        Args:
            url: URL string

        Returns:
            Normalized URL
        """
        # Remove common tracking parameters
        url = url.lower()
        for param in ["utm_source", "utm_medium", "utm_campaign", "ref"]:
            url = re.sub(r"[?&]" + re.escape(param) + r"=[^&]*", "", url)

        return url

    def reset(self) -> None:
        """Reset all tracked values."""
        self.seen_urls.clear()
        self.seen_titles.clear()
        self.seen_hashes.clear()

    def merge_duplicates(
        self, articles: List[Dict], prefer: str = "newest"
    ) -> List[Dict]:
        """
        Merge duplicate articles instead of removing them.

        Args:
            articles: List of article dictionaries
            prefer: Which version to prefer ('newest', 'oldest', 'first')

        Returns:
            List of merged articles
        """
        # Group by normalized URL
        groups: Dict[str, List[Dict]] = {}

        for article in articles:
            url = self._normalize_url(article.get("url", ""))

            if url not in groups:
                groups[url] = []
            groups[url].append(article)

        # Merge groups
        merged = []

        for url, group in groups.items():
            if len(group) == 1:
                merged.append(group[0])
            else:
                # Sort based on preference
                if prefer == "newest":
                    group.sort(key=lambda a: a.get("date", ""), reverse=True)
                elif prefer == "oldest":
                    group.sort(key=lambda a: a.get("date", ""))
                # 'first' keeps original order

                # Use first article as base, merge others
                base = group[0].copy()

                for article in group[1:]:
                    # Merge fields
                    for key in ["description", "tags", "source"]:
                        if not base.get(key) and article.get(key):
                            base[key] = article[key]

                # Track sources
                sources = set(a.get("source", "") for a in group)
                if len(sources) > 1:
                    base["duplicate_sources"] = list(sources - {base.get("source", "")})

                merged.append(base)

        logger.info(
            f"Merged {len(articles)} articles into {len(merged)} unique articles "
            f"(removed {len(articles) - len(merged)} duplicates)"
        )
        return merged
