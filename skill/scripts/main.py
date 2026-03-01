#!/usr/bin/env python3
"""
AI News Radar - CLI entry point.

This module provides the command-line interface for AI News Radar.
It uses the skill package which is self-contained.
"""

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

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
from skill.storage import JSONStorage


logger = logging.getLogger(__name__)


@click.group()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Custom configuration file",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
@click.pass_context
def cli(ctx: click.Context, config: Optional[str], verbose: bool):
    """
    AI News Radar - Aggregate AI/tech news from multiple sources.

    This is the CLI entry point for the AI News Radar skill.
    """
    # Setup logging
    setup_logger("ai_news_radar", level=logging.DEBUG if verbose else logging.INFO, verbose=verbose)

    # Load config and pass to subcommands via context
    if config:
        radar_config = RadarConfig.from_yaml(Path(config))
    else:
        script_dir = Path(__file__).resolve().parent.parent
        radar_config = load_default_config()
        # Override default paths to be relative to skill directory
        radar_config.sources_file = script_dir / "assets" / "data" / "sources.yaml"
        radar_config.keywords_file = script_dir / "assets" / "data" / "keywords.yaml"

    # Store config and radar in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["config"] = radar_config
    ctx.obj["verbose"] = verbose


@cli.command()
@click.argument("output", default="news.json")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "csv"]),
    default="json",
    help="Output format",
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
@click.option(
    "--incremental",
    "-i",
    is_flag=True,
    help="Fetch only new articles since last run (uses state file)",
)
@click.option(
    "--state-file",
    type=click.Path(),
    help="Custom state file for tracking incremental updates",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without executing",
)
@click.pass_context
def fetch(ctx: click.Context, output: str, format: str, since: int,
          max_per_source: Optional[int], incremental: bool, state_file: Optional[str],
          dry_run: bool):
    """
    Fetch and aggregate news from configured sources.

    \b
    Examples:
        radar fetch                      # Fetch and save to news.json
        radar fetch -o news.csv -f csv  # Save as CSV
        radar fetch --since 12           # Fetch articles from last 12 hours
        radar fetch --incremental         # Fetch only new articles since last run
        radar fetch -i -o news.json     # Same as above with short flag
    """
    config = ctx.obj["config"]

    # Override settings
    config.update_interval_hours = since
    if max_per_source:
        config.max_articles_per_source = max_per_source
    config.dry_run = dry_run

    # Set state file for incremental mode
    if incremental:
        if state_file:
            state_path = Path(state_file)
        else:
            # Use default state file in cache directory
            state_path = config.cache_dir / "radar_state.json"
            config.state_file = state_path

    # Create radar
    if incremental:
        radar = NewsRadar(config, state_file=state_path)
    else:
        radar = NewsRadar(config)

    if dry_run:
        click.echo("Dry run mode - would process the following:")
        sources = config.load_sources()
        for source in sources:
            click.echo(f"  - {source.get('name')}: {source.get('url')}")
        return

    output_path = Path(output)

    # Aggregate
    if incremental:
        if not output_path.exists():
            click.echo(f"Note: Output file '{output}' doesn't exist, fetching all articles...")
            result = radar.aggregate_with_stats()
        else:
            click.echo("Aggregating news incrementally...")
            result = radar.aggregate_incremental_with_stats(output_path)
    else:
        click.echo("Aggregating news...")
        result = radar.aggregate_with_stats()

    articles = result["articles"]
    stats = result["stats"]

    # Save output
    if format == "json":
        radar.save_to_json(articles, output_path)
    elif format == "csv":
        radar.save_to_csv(articles, output_path)

    # Print summary
    click.echo("\nSummary:")
    click.echo(f"  Total articles: {stats['total_fetched']}")
    if "new_articles" in stats:
        click.echo(f"  New articles: {stats['new_articles']}")
    click.echo(f"  After filtering: {stats['total_kept']}")
    click.echo(f"  Sources processed: {stats['sources_processed']}")
    click.echo(f"  Sources failed: {stats['sources_failed']}")
    click.echo(f"  Duration: {stats['duration']:.2f}s")
    click.echo(f"\nOutput saved to: {output}")
    if format == "json":
        radar.save_to_json(articles, output_path)
    elif format == "csv":
        radar.save_to_csv(articles, output_path)

    # Print summary
    click.echo("\nSummary:")
    click.echo(f"  Total articles: {stats['total_fetched']}")
    click.echo(f"  After filtering: {stats['total_kept']}")
    click.echo(f"  Sources processed: {stats['sources_processed']}")
    click.echo(f"  Sources failed: {stats['sources_failed']}")
    click.echo(f"  Duration: {stats['duration']:.2f}s")
    click.echo(f"\nOutput saved to: {output}")


@cli.command()
@click.argument("data_file", default="news.json")
@click.option(
    "--source",
    "-s",
    help="Filter by source name",
)
@click.option(
    "--limit",
    "-n",
    type=int,
    default=10,
    help="Maximum number of articles to display (default: 10, 0 for all)",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["short", "full", "count"]),
    default="short",
    help="Output format",
)
@click.option(
    "--keywords",
    "-k",
    help="Filter by keywords (comma-separated)",
)
@click.pass_context
def list_cmd(ctx: click.Context, data_file: str, source: Optional[str],
            limit: int, format: str, keywords: Optional[str]):
    """
    List saved articles from the data file.

    \b
    Examples:
        radar list                  # List last 10 articles
        radar list -n 20           # List last 20 articles
        radar list -n 0            # List all articles
        radar list -s TechNews      # List articles from TechNews source
        radar list --format full     # Show full article details
        radar list -k "AI,ML"      # List articles containing AI or ML
    """
    data_path = Path(data_file)
    if not data_path.exists():
        click.echo(f"Error: Data file '{data_file}' does not exist.", err=True)
        sys.exit(1)

    storage = JSONStorage(data_path)
    articles = storage.load()

    # Filter by source
    if source:
        articles = storage.get_by_source(source)

    # Filter by keywords
    if keywords:
        keyword_list = [k.strip() for k in keywords.split(",")]
        articles = storage.get_by_keywords(keyword_list)

    # Apply limit
    if limit > 0:
        articles = articles[:limit]

    # Count format
    if format == "count":
        click.echo(f"Total articles: {len(articles)}")
        return

    # Format output
    if format == "short":
        for i, article in enumerate(articles, 1):
            date = article.get("date", "N/A")
            title = article.get("title", "No title")
            src = article.get("source", "Unknown")
            url = article.get("url", "")
            click.echo(f"{i}. [{date}] {src} - {title}")
            if url:
                click.echo(f"   {url}")
    elif format == "full":
        for i, article in enumerate(articles, 1):
            click.echo(f"\n{'='*60}")
            click.echo(f"Article {i}")
            click.echo(f"{'='*60}")
            for key, value in article.items():
                click.echo(f"{key}: {value}")


@cli.command()
@click.argument("data_file", default="news.json")
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def clear(ctx: click.Context, data_file: str, confirm: bool):
    """
    Clear all articles from the data file.

    \b
    Examples:
        radar clear             # Clear with confirmation prompt
        radar clear --confirm   # Clear without confirmation
    """
    data_path = Path(data_file)
    if not data_path.exists():
        click.echo(f"Error: Data file '{data_file}' does not exist.", err=True)
        sys.exit(1)

    storage = JSONStorage(data_path)
    count = storage.get_count()

    if count == 0:
        click.echo("No articles to clear.")
        return

    if not confirm:
        click.echo(f"About to delete {count} articles from '{data_file}'")
        if not click.confirm("Do you want to continue?"):
            click.echo("Operation cancelled.")
            return

    storage.clear()
    click.echo(f"Cleared {count} articles from '{data_file}'")


@cli.command()
@click.argument("data_file", default="news.json")
@click.option(
    "--output",
    "-o",
    help="Custom backup file path (default: auto-generated with timestamp)",
)
@click.pass_context
def backup(ctx: click.Context, data_file: str, output: Optional[str]):
    """
    Create a backup of the data file.

    \b
    Examples:
        radar backup                    # Auto-generate backup filename
        radar backup -o backup.json    # Specify backup filename
    """
    data_path = Path(data_file)
    if not data_path.exists():
        click.echo(f"Error: Data file '{data_file}' does not exist.", err=True)
        sys.exit(1)

    storage = JSONStorage(data_path)
    articles = storage.load()
    metadata = storage.load_metadata()

    if output:
        backup_path = Path(output)
    else:
        # Auto-generate backup filename with timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_path = data_path.parent / f"{data_path.stem}.backup_{timestamp}.json"

    # Create backup storage and save
    backup_storage = JSONStorage(backup_path)
    backup_storage.save(articles, backup=False)

    count = len(articles)
    click.echo(f"Created backup: {backup_path}")
    click.echo(f"  Articles: {count}")
    if metadata and metadata.get("generated_at"):
        click.echo(f"  Original created: {metadata['generated_at']}")


@cli.command()
@click.argument("data_file", default="news.json")
@click.pass_context
def info(ctx: click.Context, data_file: str):
    """
    Show information about the data file.

    \b
    Examples:
        radar info    # Show info about default data file
        radar info data.json    # Show info about specific file
    """
    data_path = Path(data_file)
    if not data_path.exists():
        click.echo(f"Error: Data file '{data_file}' does not exist.", err=True)
        sys.exit(1)

    storage = JSONStorage(data_path)
    metadata = storage.load_metadata()
    articles = storage.load()

    if metadata:
        click.echo(f"File: {data_file}")
        click.echo(f"Version: {metadata.get('version', 'unknown')}")
        click.echo(f"Created: {metadata.get('generated_at', 'unknown')}")
    else:
        click.echo(f"File: {data_file}")

    click.echo(f"Total articles: {len(articles)}")

    # Get unique sources
    sources = storage.get_sources()
    click.echo(f"Sources ({len(sources)}):")
    for src in sources:
        count = len(storage.get_by_source(src))
        click.echo(f"  - {src}: {count} articles")


def main():
    """Main entry point for command-line usage."""
    cli()


if __name__ == "__main__":
    main()
