# AI News Radar - Deployment Guide

## Prerequisites

### System Requirements

- Python 3.11 or higher
- 100MB minimum disk space
- Network connectivity for fetching news sources
- (Optional) Docker for containerized deployment

### Python Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

Core dependencies:
- requests >= 2.31.0
- beautifulsoup4 >= 4.12.0
- feedparser >= 6.0.10
- python-dateutil >= 2.8.2
- lxml >= 4.9.0
- pyyaml >= 6.0

## Local Installation

### Option 1: Direct Clone

```bash
# Clone the repository
git clone https://github.com/yourname/ai-news-radar.git
cd ai-news-radar

# Install dependencies
pip install -r requirements.txt

# Run aggregator
python scripts/main.py
```

### Option 2: Project-Level Skill Installation

For use with Claude Code or compatible platforms:

```bash
# Ensure project structure exists
.claude/skills/ai-news-radar/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

The skill will be automatically detected and loaded.

## GitHub Actions Deployment

### Basic Workflow

Create `.github/workflows/news-radar.yml`:

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
        run: pip install -r requirements.txt

      - name: Run aggregator
        run: python scripts/main.py --output news.json --verbose

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: news-data-${{ github.run_number }}
          path: news.json
          retention-days: 7
```

### Advanced Workflow with Notifications

```yaml
name: AI News Aggregation

on:
  schedule:
    - cron: '0 */6 * * *'
  workflow_dispatch:

jobs:
  aggregate:
    runs-on: ubuntu-latest
    outputs:
      article_count: ${{ steps.aggregate.outputs.count }}
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run aggregator
        id: aggregate
        run: |
          result=$(python scripts/main.py --output news.json)
          count=$(echo "$result" | grep "After filtering" | awk '{print $3}')
          echo "count=$count" >> $GITHUB_OUTPUT

      - name: Send notification
        if: steps.aggregate.outputs.count != '0'
        uses: actions/github-script@v7
        with:
          script: |
            const count = '${{ steps.aggregate.outputs.count }}';
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `AI News aggregation complete: ${count} new articles`
            })

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: news-data-${{ github.run_number }}
          path: news.json
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create output directory
RUN mkdir -p output

# Run
CMD ["python", "scripts/main.py", "--output", "output/news.json"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  news-radar:
    build: .
    volumes:
      - ./config:/app/config
      - ./output:/app/output
    environment:
      - AI_NEWS_UPDATE_INTERVAL=6
      - AI_NEARS_VERBOSE=true
```

### Running with Docker

```bash
# Build image
docker build -t ai-news-radar .

# Run container
docker run -v $(pwd)/output:/app/output ai-news-radar

# Run with custom config
docker run \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/output:/app/output \
  ai-news-radar \
  --config /app/config/custom.yaml \
  --output /app/output/news.json
```

## Cloud Deployment

### AWS Lambda

```python
# lambda_function.py
from scripts.main import NewsRadar
from scripts.config import RadarConfig

def lambda_handler(event, context):
    config = RadarConfig.from_env()
    radar = NewsRadar(config)
    articles = radar.aggregate()

    return {
        'statusCode': 200,
        'body': {
            'count': len(articles),
            'articles': articles
        }
    }
```

### Google Cloud Functions

```python
# main.py
from scripts.main import NewsRadar
from scripts.config import RadarConfig

def aggregate_news(request):
    config = RadarConfig.from_env()
    radar = NewsRadar(config)
    articles = radar.aggregate()

    return {
        'count': len(articles),
        'articles': articles
    }
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AI_NEWS_SOURCES_FILE` | Path to sources YAML | assets/data/sources.yaml |
| `AI_NEWS_KEYWORDS_FILE` | Path to keywords YAML | assets/data/keywords.yaml |
| `AI_NEWS_CACHE_DIR` | Cache directory | cache |
| `AI_NEWS_UPDATE_INTERVAL` | Update window (hours) | 24 |
| `AI_NEWS_MAX_ARTICLES` | Max articles per source | 20 |
| `AI_NEWS_TIMEOUT` | Request timeout (seconds) | 30 |
| `AI_NEWS_OUTPUT_FORMAT` | Output format | json |
| `AI_NEWS_ENABLE_CACHE` | Enable caching | true |
| `AI_NEWS_ENABLE_DEDUP` | Enable deduplication | true |
| `AI_NEARS_VERBOSE` | Verbose logging | false |

### Configuration File

Create `config.yaml`:

```yaml
sources_file: assets/data/sources.yaml
keywords_file: assets/data/keywords.yaml
cache_dir: cache
update_interval_hours: 24
max_articles_per_source: 20
request_timeout: 30
output_format: json
enable_cache: true
enable_deduplication: true

metadata:
  environment: production
  timezone: UTC
```

## Monitoring

### Logging

Enable verbose logging:

```bash
python scripts/main.py --verbose
```

Or in code:

```python
from scripts.utils.logger import setup_logger

logger = setup_logger(verbose=True)
```

### Statistics

Retrieve aggregation statistics:

```python
from scripts.main import NewsRadar

radar = NewsRadar()
result = radar.aggregate_with_stats()

print(f"Total: {result['stats']['total_fetched']}")
print(f"Kept: {result['stats']['total_kept']}")
print(f"Duration: {result['stats']['duration']}s")
```

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError`

**Solution**:
```bash
pip install -r requirements.txt
```

**Issue**: Connection timeout

**Solution**:
```yaml
# config.yaml
request_timeout: 60  # Increase timeout
proxies:
  http: http://proxy:port
```

**Issue**: Zero articles found

**Solution**:
```bash
# Run with verbose output
python scripts/main.py --verbose

# Check source configuration
cat assets/data/sources.yaml

# Verify keywords
cat assets/data/keywords.yaml
```

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python scripts/main.py --verbose
```

## Security Considerations

### Secrets Management

Never commit sensitive data:

```bash
# .gitignore
config.local.yaml
.env
cache/
*.log
```

Use environment variables for sensitive configuration:

```bash
# .env (not committed)
PROXY_URL=http://user:pass@proxy:port
API_KEY=your_api_key
```

### Rate Limiting

Respect rate limits of news sources:

```yaml
# config.yaml
request_timeout: 30
max_articles_per_source: 20
```

## Maintenance

### Cache Cleanup

Periodically clean cache:

```python
from scripts.utils.cache import CacheManager

cache = CacheManager("cache")
removed = cache.cleanup_expired()
print(f"Removed {removed} expired cache files")
```

### Dependency Updates

Update dependencies regularly:

```bash
pip list --outdated
pip install --upgrade package_name
```

## Backup and Recovery

### Backup Configuration

```bash
# Backup config files
tar -czf config-backup.tar.gz assets/data/ config.yaml
```

### Backup Data

```bash
# Backup generated news files
tar -czf news-backup.tar.gz news*.json
```

## Support

For issues and questions:
- Check `ARCHITECTURE.md` for design details
- Review `SKILL.md` for usage examples
- Check logs for error details
- Open an issue on GitHub
