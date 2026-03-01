"""
AI News Radar - Core aggregator class.

This module provides the main NewsRadar class for aggregating AI news
from multiple sources with filtering and deduplication.
"""

import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from skill.config import RadarConfig, load_default_config
from skill.filters import AITopicFilter, DuplicateFilter, TimeFilter
from skill.parsers import HTMLParser, RSSParser
from skill.state import State
from skill.storage import JSONStorage

logger = logging.getLogger(__name__)


class NewsRadar:
    """
    Main AI news aggregator class.

    Coordinates fetching, parsing, filtering, and storing of AI news articles.
    """

    def __init__(self, config: Optional[RadarConfig] = None, state_file: Optional[Path] = None):
        """
        Initialize the news radar.

        Args:
            config: Configuration object (uses default if None)
            state_file: Path to state file for incremental updates
        """
        self.config = config or load_default_config()
        self.config.ensure_directories()

        # Initialize state manager for incremental updates
        if state_file:
            self.state = State(state_file)
        elif hasattr(self.config, "state_file"):
            self.state = State(self.config.state_file)
        else:
            self.state = None

        # Initialize parsers
        self.rss_parser = RSSParser(
            {
                "timeout": self.config.request_timeout,
                "user_agent": self.config.user_agent,
                "proxies": self.config.proxies,
            }
        )

        self.html_parser = HTMLParser(
            {
                "timeout": self.config.request_timeout,
                "user_agent": self.config.user_agent,
                "proxies": self.config.proxies,
            }
        )

        # Initialize filters
        self.ai_filter = AITopicFilter(keywords_file=self.config.keywords_file)
        self.time_filter = TimeFilter(hours=self.config.update_interval_hours)
        self.duplicate_filter = DuplicateFilter(
            by_url=self.config.enable_deduplication,
        )

        # Statistics
        self.stats = {
            "total_fetched": 0,
            "total_filtered": 0,
            "total_kept": 0,
            "sources_processed": 0,
            "sources_failed": 0,
            "new_articles": 0,  # Number of new articles in incremental mode
        }

    def aggregate(self) -> List[Dict[str, Any]]:
        """
        Aggregate news from all configured sources.

        Returns:
            List of filtered article dictionaries
        """
        logger.info("Starting news aggregation...")

        all_articles = []
        sources = self.config.load_sources()

        if not sources:
            logger.warning("No sources configured, returning empty list")
            return []

        for source in sources:
            articles = self._process_source(source)
            all_articles.extend(articles)

        self.stats["total_fetched"] = len(all_articles)

        # Apply filters
        filtered = self._apply_filters(all_articles)
        self.stats["total_kept"] = len(filtered)

        logger.info(
            f"Aggregation complete: {self.stats['total_kept']}/"
            f"{self.stats['total_fetched']} articles kept"
        )

        return filtered

    def aggregate_incremental(self, storage_file: Path) -> List[Dict[str, Any]]:
        """
        Aggregate news incrementally, only fetching new articles since last run.

        Args:
            storage_file: Path to existing storage file for deduplication

        Returns:
            List of new filtered article dictionaries
        """
        if not self.state:
            logger.warning("No state file configured, falling back to normal aggregation")
            return self.aggregate()

        logger.info("Starting incremental news aggregation...")

        # Get last fetch time from state
        last_fetch = self.state.get_last_fetch_time()
        if last_fetch:
            logger.info(f"Last fetch was: {last_fetch.isoformat()}")
        else:
            logger.info("No previous fetch found, fetching all articles")
            last_fetch = None

        all_articles = []
        sources = self.config.load_sources()

        if not sources:
            logger.warning("No sources configured, returning empty list")
            return []

        # Load existing articles for deduplication
        storage = JSONStorage(storage_file)
        existing_articles = storage.load()
        existing_urls = {a.get("url") for a in existing_articles}
        logger.info(f"Loaded {len(existing_urls)} existing articles for deduplication")

        for source in sources:
            articles = self._process_source(source, last_fetch=last_fetch)
            # Filter out already existing articles by URL
            new_articles = [a for a in articles if a.get("url") not in existing_urls]
            all_articles.extend(new_articles)

            # Update source stats
            if self.state:
                self.state.update_source_stats(
                    source.get("name", "unknown"),
                    len(new_articles)
                )

        self.stats["total_fetched"] = len(all_articles)
        self.stats["new_articles"] = len(all_articles)

        # Apply filters
        filtered = self._apply_filters(all_articles)
        self.stats["total_kept"] = len(filtered)

        # Update last fetch time
        if self.state:
            self.state.set_last_fetch_time(datetime.now(timezone.utc))

        logger.info(
            f"Incremental aggregation complete: {self.stats['total_kept']}/"
            f"{self.stats['total_fetched']} new articles kept"
        )

        return filtered

    def aggregate_with_stats(self) -> Dict[str, Any]:
        """
        Aggregate news and return detailed statistics.

        Returns:
            Dictionary containing articles and statistics
        """
        start_time = datetime.now(timezone.utc)

        articles = self.aggregate()

        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        return {
            "articles": articles,
            "stats": {
                **self.stats,
                "duration": duration,
                "generated_at": end_time.isoformat(),
            },
        }

    def aggregate_incremental_with_stats(self, storage_file: Path) -> Dict[str, Any]:
        """
        Aggregate news incrementally and return detailed statistics.

        Args:
            storage_file: Path to existing storage file for deduplication

        Returns:
            Dictionary containing articles and statistics
        """
        start_time = datetime.now(timezone.utc)

        articles = self.aggregate_incremental(storage_file)

        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        return {
            "articles": articles,
            "stats": {
                **self.stats,
                "duration": duration,
                "generated_at": end_time.isoformat(),
            },
        }

    def _process_source(self, source: Dict[str, Any], last_fetch: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Process a single news source.

        Args:
            source: Source configuration dictionary
            last_fetch: Only fetch articles after this timestamp (for incremental mode)

        Returns:
            List of parsed articles
        """
        name = source.get("name", "Unknown")
        url = source.get("url", "")
        source_type = source.get("type", "rss")

        logger.info(f"Processing source: {name} ({source_type})")

        try:
            if source_type == "rss":
                parser = self.rss_parser
                kwargs = {
                    "max_entries": source.get(
                        "max_articles", self.config.max_articles_per_source
                    ),
                }
            elif source_type == "html":
                parser = self.html_parser
                kwargs = {
                    "selector": source.get("selector"),
                    "max_articles": source.get(
                        "max_articles", self.config.max_articles_per_source
                    ),
                    "field_selectors": source.get("field_selectors", {}),
                }
            elif source_type == "opml":
                # OPML file - parse feeds from it
                feeds = self.rss_parser.parse_opml(source.get("file_path", url))
                articles = []
                for feed in feeds[: source.get("max_feeds", 10)]:
                    feed_articles = self.rss_parser.fetch_and_parse(
                        feed["url"],
                        source_name=feed.get("title"),
                        max_entries=source.get("max_articles_per_feed", 10),
                    )
                    articles.extend(feed_articles)
                self.stats["sources_processed"] += 1

                # Filter by last_fetch if provided
                if last_fetch:
                    articles = self._filter_by_time(articles, last_fetch)

                return articles
            else:
                logger.warning(f"Unknown source type: {source_type}")
                self.stats["sources_failed"] += 1
                return []

            articles = parser.fetch_and_parse(url, **kwargs)

            # Filter by last_fetch if provided (incremental mode)
            if last_fetch:
                articles = self._filter_by_time(articles, last_fetch)

            self.stats["sources_processed"] += 1

            # Add source name to articles if not set
            for article in articles:
                if not article.get("source"):
                    article["source"] = name

            logger.info(f"Fetched {len(articles)} articles from {name}")
            return articles

        except Exception as e:
            logger.error(f"Failed to process source {name}: {e}")
            self.stats["sources_failed"] += 1
            return []

    def _filter_by_time(self, articles: List[Dict[str, Any]], since: datetime) -> List[Dict[str, Any]]:
        """
        Filter articles to only include those after a given timestamp.

        Args:
            articles: List of article dictionaries
            since: Only keep articles published after this time

        Returns:
            Filtered list of articles
        """
        filtered = []
        for article in articles:
            date_str = article.get("date") or article.get("published")
            if not date_str:
                # If no date, include the article (conservative approach)
                filtered.append(article)
                continue

            try:
                if isinstance(date_str, datetime):
                    article_date = date_str
                else:
                    # Parse ISO format string
                    article_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))

                # Check if article is newer than since time
                if article_date > since:
                    filtered.append(article)
            except (ValueError, TypeError):
                # If date parsing fails, include the article
                filtered.append(article)

        return filtered

    def _apply_filters(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply all configured filters to articles.

        Args:
            articles: List of article dictionaries

        Returns:
            Filtered list of articles
        """
        filtered = articles

        # Time filter
        filtered = self.time_filter.filter(filtered)

        # AI topic filter
        filtered = self.ai_filter.filter(filtered)

        # Duplicate filter
        if self.config.enable_deduplication:
            filtered = self.duplicate_filter.filter(filtered)

        self.stats["total_filtered"] = len(articles) - len(filtered)

        return filtered

    def add_source(self, source: Dict[str, Any]) -> None:
        """
        Add a new source configuration.

        Args:
            source: Source configuration dictionary
        """
        sources = self.config.load_sources()
        sources.append(source)

        # Note: In a full implementation, this would save back to the sources file
        logger.info(f"Added source: {source.get('name')}")

    def save_to_json(self, articles: List[Dict[str, Any]], path: str) -> None:
        """
        Save articles to JSON file.

        Args:
            articles: List of article dictionaries
            path: Output file path
        """
        storage = JSONStorage(Path(path))
        storage.save(articles)

    def save_to_csv(self, articles: List[Dict[str, Any]], path: str) -> None:
        """
        Save articles to CSV file.

        Args:
            articles: List of article dictionaries
            path: Output file path
        """
        import csv

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if not articles:
            logger.warning("No articles to save")
            return

        # Get all unique keys
        fieldnames = set()
        for article in articles:
            for key in article.keys():
                if not key.startswith("_"):
                    fieldnames.add(key)

        # Sort fieldnames for consistent output
        fieldnames = sorted(fieldnames)

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for article in articles:
                # Prepare row
                row = {}
                for key in fieldnames:
                    value = article.get(key, "")
                    if isinstance(value, (list, dict)):
                        value = str(value)
                    elif isinstance(value, datetime):
                        value = value.isoformat()
                    row[key] = value

                writer.writerow(row)

        logger.info(f"Saved {len(articles)} articles to {path}")


def setup_logger(name: str, level: int = logging.INFO, verbose: bool = False):
    """
    Setup logging with standard format.

    Args:
        name: Logger name
        level: Logging level
        verbose: Enable verbose output

    Returns:
        Configured logger
    """
    from skill.utils.logger import setup_logger as _setup_logger

    return _setup_logger(name, level=level, verbose=verbose)
