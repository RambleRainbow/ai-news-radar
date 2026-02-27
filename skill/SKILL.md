---
name: ai-news-radar
description: |
  A production-grade AI/tech news aggregator that fetches news from 10+ web sources and OPML RSS feeds,
  filters for AI-related topics with 24-hour incremental updates, displays bilingual titles, and can be
  automated via GitHub Actions. Use when you need to: aggregate multi-source AI news, filter by AI topics,
  get incremental updates within last 24 hours, display news with bilingual support, or set up automated
  news aggregation workflows.
version: 1.0.0
dependencies: python>=3.11,requests,beautifulsoup4,feedparser,python-dateutil
metadata:
  category: data-aggregation
  tags: [news, aggregator, ai, rss, python]
---

# AI News Radar

AI News Radar is a production-grade news aggregator focused on AI and technology news. It aggregates from multiple web sources and RSS feeds, applies AI topic filtering, provides 24-hour incremental updates, displays bilingual titles, and supports automation via GitHub Actions.

## Quick Start

### Installation

1. Ensure you have Python 3.11 or higher installed:
```bash
python --version
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the aggregator:
```bash
python scripts/main.py
```

### Basic Usage

```bash
# Default: aggregate from configured sources
python scripts/main.py

# Specify output file
python scripts/main.py --output news.json

# Use custom config
python scripts/main.py --config custom_config.yaml

# Enable verbose logging
python scripts/main.py --verbose
```

## Features

### Multi-Source Aggregation

- **10+ Web Sources**: Direct scraping from major tech news sites
- **OPML RSS Support**: Batch import RSS feeds from OPML files
- **Incremental Updates**: Only fetch articles from the last 24 hours
- **Deduplication**: Remove duplicate articles across sources

### AI Topic Filtering

- **Keyword-Based**: Filter by AI-related keywords
- **Configurable Rules**: Customize filtering criteria
- **Score-Based**: Prioritize articles by relevance

### Bilingual Display

- **Dual Titles**: Display both English and original language titles
- **Translation Support**: Optional translation via external APIs

### Automation

- **GitHub Actions**: Ready-to-use CI/CD workflows
- **Scheduled Runs**: Configure automated updates
- **Artifact Storage**: Store results as workflow artifacts

## Configuration

### Configuration Files

Located in `assets/data/` (inside the skill package):

#### `sources.yaml`

```yaml
# News sources configuration
sources:
  - name: TechCrunch
    url: https://techcrunch.com
    type: rss
    url_template: https://techcrunch.com/feed/
    max_articles: 20

  - name: Ars Technica
    url: https://arstechnica.com
    type: html
    selector: article.post-item
    max_articles: 15

  - name: AI News
    url: https://example.com/ai
    type: opml
    file_path: assets/data/sample_opml.opml
    max_articles: 30
```

#### `keywords.yaml`

```yaml
# AI-related keywords for filtering
keywords:
  primary:
    - artificial intelligence
    - machine learning
    - deep learning
    - neural network
    - natural language processing
    - computer vision

  secondary:
    - chatgpt
    - gpt
    - openai
    - anthropic
    - claude
    - hugging face

  aliases:
    - ai
    - ml
    - llm
    - generative ai
```

### Configuration API

Use `scripts/main.py` to run the aggregator. The configuration is managed internally with `assets/data/` files:

```yaml
# assets/data/sources.yaml - configure news sources
# assets/data/keywords.yaml - configure AI filtering keywords
```

## Usage Examples

### Example 1: Basic Aggregation

Run the default aggregator:

```bash
python scripts/main.py
```

This will aggregate news from all configured sources in `assets/data/sources.yaml` and save to `news.json`.

### Example 2: Custom Sources

Edit `assets/data/sources.yaml` to add custom news sources:

```yaml
sources:
  - name: My Custom Source
    url: https://example.com/news
    type: rss
    url_template: https://example.com/news/feed/
    max_articles: 10
```

### Example 3: OPML Import

Place your OPML file in `assets/data/` and reference it in `sources.yaml`:

```yaml
- name: My RSS Feeds
  type: opml
  file_path: assets/data/my_feeds.opml
  max_articles: 30
```

## API Reference

### Command Line Interface

```bash
python skill/scripts/main.py [OPTIONS]
```

**Options:**

- `--output, -o PATH`: Output file path (default: `news.json`)
- `--config, -c PATH`: Custom configuration file
- `--format, -f FORMAT`: Output format (json, csv, rss) (default: `json`)
- `--verbose, -v`: Enable verbose logging
- `--dry-run`: Show what would be done without executing
- `--since HOURS`: Only fetch articles from last N hours (default: 24)
- `--max-per-source N`: Maximum articles per source (default: 20)

### Python API

#### `NewsRadar` Class

```python
class NewsRadar:
    """Main aggregator class"""

    def __init__(self, config: RadarConfig = None):
        """Initialize with optional config"""

    def aggregate(self) -> List[Dict]:
        """Aggregate news from all sources"""

    def add_source(self, source: Dict):
        """Add a news source"""

    def register_parser(self, name: str, parser: BaseParser):
        """Register custom parser"""

    def save_to_json(self, articles: List[Dict], path: str):
        """Save articles to JSON file"""

    def save_to_csv(self, articles: List[Dict], path: str):
        """Save articles to CSV file"""
```

#### `RadarConfig` Class

```python
@dataclass
class RadarConfig:
    """Configuration data class"""

    sources_file: Path
    keywords_file: Path
    cache_dir: Path
    update_interval_hours: int = 24
    max_articles_per_source: int = 20
    output_format: str = 'json'
    enable_cache: bool = True
    enable_deduplication: bool = True
```

#### Parser Classes

**`RSSParser`**
```python
class RSSParser(BaseParser):
    def fetch_and_parse(self, url: str) -> List[Dict]:
        """Fetch and parse RSS feed"""

    def parse_opml(self, file_path: str) -> List[Dict]:
        """Parse OPML file for RSS feeds"""
```

**`HTMLParser`**
```python
class HTMLParser(BaseParser):
    def parse(self, content: str, selector: str) -> List[Dict]:
        """Parse HTML content with CSS selector"""
```

#### Filter Classes

**`AITopicFilter`**
```python
class AITopicFilter:
    def filter(self, articles: List[Dict]) -> List[Dict]:
        """Filter articles by AI keywords"""

    def score(self, article: Dict) -> float:
        """Score article by AI relevance"""
```

**`TimeFilter`**
```python
class TimeFilter:
    def __init__(self, hours: int = 24):
        """Filter by time window"""

    def filter(self, articles: List[Dict]) -> List[Dict]:
        """Filter articles by publish date"""
```

## Advanced Topics

### Custom Parser Development

Create a custom parser by extending `BaseParser`:

```python
from scripts.parsers.base_parser import BaseParser
from typing import List, Dict

class MyCustomParser(BaseParser):
    def fetch(self, url: str) -> str:
        """Implement custom fetch logic"""
        response = requests.get(url, headers={
            'User-Agent': 'AI News Radar/1.0'
        })
        return response.text

    def parse(self, content: str) -> List[Dict]:
        """Implement custom parse logic"""
        soup = BeautifulSoup(content, 'html.parser')
        articles = []

        # Your parsing logic here
        for item in soup.select('.news-item'):
            articles.append({
                'title': item.select_one('.title').text,
                'url': item.select_one('a')['href'],
                'date': self._parse_date(item.select_one('.date')),
                'description': item.select_one('.desc').text
            })

        return articles
```

### Custom Filter Rules

Extend filter functionality:

```python
from scripts.filters.ai_topic_filter import AITopicFilter

class CustomTopicFilter(AITopicFilter):
    def filter(self, articles: List[Dict]) -> List[Dict]:
        # Apply parent filter
        filtered = super().filter(articles)

        # Additional custom logic
        filtered = [
            a for a in filtered
            if len(a.get('title', '')) > 10  # Minimum title length
        ]

        return filtered
```

### Caching Strategy

Configure caching for performance:

```python
from scripts.utils.cache import CacheManager

cache = CacheManager(
    cache_dir='cache',
    ttl_hours=1  # Cache TTL
)

# Use cache
articles = cache.get_or_fetch('techcrunch', lambda: parser.fetch_and_parse(url))
```

### GitHub Actions Integration

Example workflow file:

```yaml
name: AI News Aggregation

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  aggregate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run aggregator
        run: |
          python scripts/main.py --output news.json --verbose

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: news-data-${{ github.run_number }}
          path: news.json
          retention-days: 7
```

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'feedparser'`

**Solution**: Install missing dependencies
```bash
pip install -r requirements.txt
```

---

**Issue**: `Connection timeout when fetching sources`

**Solution**: Increase timeout or use proxy. Edit `skill/scripts/main.py` or set environment variables.

---

**Issue**: `Zero articles found`

**Solution**: Check source configuration and filters
```bash
# Run with verbose logging
python skill/scripts/main.py --verbose
```

---

**Issue**: `Duplicate articles in output`

**Solution**: Verify deduplication is enabled
```python
config = RadarConfig(enable_deduplication=True)
```

### Debug Mode

Enable debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Or use command line
python skill/scripts/main.py --verbose
```

### Testing

For development, run tests from project root:

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_parsers.py

# Run with coverage
pytest --cov=src tests/
```

## Performance Tuning

### Optimization Tips

1. **Enable Caching**: Reduce redundant requests
   ```python
   config = RadarConfig(enable_cache=True)
   ```

2. **Limit Articles**: Reduce per-source limits
   ```python
   config = RadarConfig(max_articles_per_source=10)
   ```

3. **Parallel Fetching**: Use async for multiple sources
   ```python
   # scripts/parsers/async_parser.py
   import asyncio

   async def fetch_multiple(sources):
       tasks = [fetch_source(s) for s in sources]
       return await asyncio.gather(*tasks)
   ```

4. **Selective Sources**: Only fetch from high-priority sources
   ```yaml
   sources:
     - name: High Priority Source
       priority: 1
     - name: Low Priority Source
       priority: 10  # Skip if time-limited
   ```

### Monitoring

Track aggregation statistics:

```python
from scripts.main import NewsRadar

radar = NewsRadar()
stats = radar.aggregate_with_stats()

print(f"Total articles: {stats['total']}")
print(f"Filtered: {stats['filtered']}")
print(f"Sources: {stats['sources']}")
print(f"Time: {stats['duration']}s")
```

## References

For detailed documentation, see the project's `docs/` directory:
- **Architecture**: `docs/ARCHITECTURE.md` - System architecture and design
- **Deployment**: `docs/DEPLOYMENT.md` - Deployment and CI/CD setup
- **Source Mapping**: `docs/SOURCE_MAPPING.md` - News source configurations
- **Filtering Rules**: `docs/FILTERING_RULES.md` - Filtering algorithm details

## Contributing

To extend this skill:

1. Add new parsers in `src/parsers/`
2. Add new filters in `src/filters/`
3. Update documentation in `docs/`
4. Add tests in `tests/`
5. Update `SKILL.md` with new features

## License

This skill follows the Agent Skills specification. See [agentskills.io](https://agentskills.io) for more information.
