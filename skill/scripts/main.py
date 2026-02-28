#!/usr/bin/env python3
"""
AI News Radar - CLI entry point.

This module provides the command-line interface for AI News Radar.
It uses the skill package which is self-contained.
"""

import logging
import sys
from pathlib import Path

import click

# Add project root to sys.path for imports
# When running from skill/scripts/, we need to add project root to sys.path
# to import from the skill package
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import from the skill package (self-contained)
from skill.config import RadarConfig, load_default_config
from skill.core.news_radar import NewsRadar, setup_logger


logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--output",
    "-o",
    default="news.json",
    help="Output file path",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Custom configuration file",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "csv"]),
    default="json",
    help="Output format",
)
@click.option(
    "--verbose",
    "-v",
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
    """
    AI News Radar - Aggregate AI/tech news from multiple sources.

    This is the CLI entry point for the AI News Radar skill.
    """

    # Setup logging
    setup_logger("ai_news_radar", level=logging.DEBUG if verbose else logging.INFO, verbose=verbose)

    # Load config
    if config:
        radar_config = RadarConfig.from_yaml(Path(config))
    else:
        script_dir = Path(__file__).resolve().parent.parent
        radar_config = load_default_config()
        # Override default paths to be relative to skill directory
        radar_config.sources_file = script_dir / "assets" / "data" / "sources.yaml"
        radar_config.keywords_file = script_dir / "assets" / "data" / "keywords.yaml"

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
    click.echo("\nSummary:")
    click.echo(f"  Total articles: {stats['total_fetched']}")
    click.echo(f"  After filtering: {stats['total_kept']}")
    click.echo(f"  Sources processed: {stats['sources_processed']}")
    click.echo(f"  Sources failed: {stats['sources_failed']}")
    click.echo(f"  Duration: {stats['duration']:.2f}s")
    click.echo(f"\nOutput saved to: {output}")


def main():
    """Main entry point for command-line usage."""
    cli()


if __name__ == "__main__":
    main()
