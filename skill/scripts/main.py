#!/usr/bin/env python3
"""
AI News Radar - Main entry point.

This module provides the main API for aggregating AI news from multiple sources.
"""

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add src to path for imports
script_dir = Path(__file__).resolve().parent.parent.parent
src_path = script_dir / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from config import RadarConfig, load_default_config
from parsers.rss_parser import RSSParser
from parsers.html_parser import HTMLParser
from filters.ai_topic_filter import AITopicFilter
from filters.time_filter import TimeFilter
from filters.duplicate_filter import DuplicateFilter
from storage.json_storage import JSONStorage

logger = logging.getLogger(__name__)


class NewsRadar:
    """
    Main AI news aggregator class.

    Coordinates fetching, parsing, filtering, and storing of AI news articles.
    """

    def __init__(self, config: Optional[RadarConfig] = None):
        """
        Initialize the news radar.

        Args:
            config: Configuration object (uses default if None)
        """
        self.config = config or load_default_config()
        self.config.ensure_directories()

        # Initialize parsers
        self.rss_parser = RSSParser({
            "timeout": self.config.request_timeout,
            "user_agent": self.config.user_agent,
            "proxies": self.config.proxies,
        })

        self.html_parser = HTMLParser({
            "timeout": self.config.request_timeout,
            "user_agent": self.config.user_agent,
            "proxies": self.config.proxies,
        })

        # Initialize filters
        self.ai_filter = AITopicFilter(
            keywords_file=self.config.keywords_file
        )
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
            f"Aggregation complete: {self.stats['total_kept']}/{self.stats['total_fetched']} articles kept"
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

    def _process_source(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process a single news source.

        Args:
            source: Source configuration dictionary

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
                    "max_entries": source.get("max_articles", self.config.max_articles_per_source),
                }
            elif source_type == "html":
                parser = self.html_parser
                kwargs = {
                    "selector": source.get("selector"),
                    "max_articles": source.get("max_articles", self.config.max_articles_per_source),
                    "field_selectors": source.get("field_selectors", {}),
                }
            elif source_type == "opml":
                # OPML file - parse feeds from it
                feeds = self.rss_parser.parse_opml(source.get("file_path", url))
                articles = []
                for feed in feeds[:source.get("max_feeds", 10)]:
                    feed_articles = self.rss_parser.fetch_and_parse(
                        feed["url"],
                        source_name=feed.get("title"),
                        max_entries=source.get("max_articles_per_feed", 10),
                    )
                    articles.extend(feed_articles)
                self.stats["sources_processed"] += 1
                return articles
            else:
                logger.warning(f"Unknown source type: {source_type}")
                self.stats["sources_failed"] += 1
                return []

            articles = parser.fetch_and_parse(url, **kwargs)
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


def main():
    """Main entry point for command-line usage."""
    import click

    @click.command()
    @click.option(
        "--output", "-o",
        default="news.json",
        help="Output file path",
    )
    @click.option(
        "--config", "-c",
        type=click.Path(exists=True),
        help="Custom configuration file",
    )
    @click.option(
        "--format", "-f",
        type=click.Choice(["json", "csv"]),
        default="json",
        help="Output format",
    )
    @click.option(
        "--verbose", "-v",
        is_flag=True,
        help="Enable verbose logging",
    )
    @click.option(
        "--dry-run",
        is_flag=True,
        help="Show what would be done without executing",
    )
    @click.option(
        "--since",
        type=int,
        default=24,
        help="Only fetch articles from last N hours",
    )
    @click.option(
        "--max-per-source",
        type=int,
        help="Maximum articles per source",
    )
    def cli(output, config, format, verbose, dry_run, since, max_per_source):
        """AI News Radar - Aggregate AI/tech news from multiple sources."""

        # Setup logging
        setup_logger(verbose=verbose)

        # Load config
        if config:
            radar_config = RadarConfig.from_yaml(Path(config))
        else:
            radar_config = load_default_config()

        # Override settings
        radar_config.update_interval_hours = since
        if max_per_source:
            radar_config.max_articles_per_source = max_per_source
        radar_config.verbose = verbose
        radar_config.dry_run = dry_run

        # Create radar
        radar = NewsRadar(radar_config)

        if dry_run:
            click.echo("Dry run mode - would process the following:")
            sources = radar_config.load_sources()
            for source in sources:
                click.echo(f"  - {source.get('name')}: {source.get('url')}")
            return

        # Aggregate
        click.echo("Aggregating news...")
        result = radar.aggregate_with_stats()

        articles = result["articles"]
        stats = result["stats"]

        # Save output
        if format == "json":
            radar.save_to_json(articles, output)
        elif format == "csv":
            radar.save_to_csv(articles, output)

        # Print summary
        click.echo(f"\nSummary:")
        click.echo(f"  Total articles: {stats['total_fetched']}")
        click.echo(f"  After filtering: {stats['total_kept']}")
        click.echo(f"  Sources processed: {stats['sources_processed']}")
        click.echo(f"  Sources failed: {stats['sources_failed']}")
        click.echo(f"  Duration: {stats['duration']:.2f}s")
        click.echo(f"\nOutput saved to: {output}")

    cli()


def setup_logger(verbose: bool = False):
    """Setup logging."""
    from utils.logger import setup_logger as _setup_logger

    return _setup_logger(
        "ai_news_radar",
        level=logging.DEBUG if verbose else logging.INFO,
        verbose=verbose,
    )


if __name__ == "__main__":
    main()
