# AI News Radar

A production-grade AI/technology news aggregator that fetches from multiple sources, filters by AI topics, and supports automation.

## Features

- **Multi-Source Aggregation**: 10+ web sources and OPML RSS feeds
- **AI Topic Filtering**: Keyword-based relevance scoring
- **Incremental Updates**: 24-hour time window filtering
- **Bilingual Support**: Display titles in multiple languages
- **Automation Ready**: GitHub Actions workflows included
- **Extensible**: Modular design for custom parsers and filters

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourname/ai-news-radar.git
cd ai-news-radar

# Install dependencies
pip install -r requirements.txt

# Run the aggregator
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

# Only fetch articles from last 6 hours
python scripts/main.py --since 6
```

### Python API

```python
from scripts.main import NewsRadar

# Create radar instance
radar = NewsRadar()

# Aggregate news
articles = radar.aggregate()

# Get with statistics
result = radar.aggregate_with_stats()
print(f"Articles: {result['stats']['total_kept']}")

# Save to file
radar.save_to_json(articles, 'news.json')
```

## Configuration

### Sources Configuration

Edit `assets/data/sources.yaml` to configure news sources:

```yaml
sources:
  - name: TechCrunch
    url: https://techcrunch.com/feed/
    type: rss
    max_articles: 20

  - name: Custom HTML Source
    url: https://example.com/news
    type: html
    selector: article.news-item
    field_selectors:
      title: h2.title
      link: a.article-link
      description: p.summary
```

### Keywords Configuration

Edit `assets/data/keywords.yaml` to customize AI topic filtering:

```yaml
primary:
  - artificial intelligence
  - machine learning
  - deep learning

secondary:
  - chatgpt
  - openai
  - anthropic

aliases:
  - ai
  - ml
  - llm
```

## GitHub Actions

Add `.github/workflows/news-radar.yml` for automated aggregation:

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
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python scripts/main.py --output news.json
      - uses: actions/upload-artifact@v4
        with:
          name: news-data
          path: news.json
```

## Directory Structure

```
ai-news-radar/
├── SKILL.md                      # Agent Skills specification
├── scripts/                      # Python modules
│   ├── main.py                   # Main entry point
│   ├── config.py                 # Configuration
│   ├── parsers/                  # Parsers (RSS, HTML, etc.)
│   ├── filters/                  # Filters (AI, time, duplicate)
│   ├── utils/                    # Utilities (date, text, cache)
│   └── storage/                  # Storage (JSON, etc.)
├── references/                   # Documentation
│   ├── ARCHITECTURE.md           # System architecture
│   ├── DEPLOYMENT.md             # Deployment guide
│   ├── SOURCE_MAPPING.md         # Source configuration
│   └── FILTERING_RULES.md       # Filter rules
├── assets/                       # Static resources
│   ├── data/                     # Configuration files
│   │   ├── sources.yaml         # News sources
│   │   └── keywords.yaml        # AI keywords
│   └── templates/                # Output templates
├── tests/                        # Test suite
└── requirements.txt             # Python dependencies
```

## Agent Skills Integration

This package is designed as an [Agent Skill](https://agentskills.io) for use with Claude Code and compatible platforms.

### Installation as a Skill

For project-level skill installation:

```bash
.claude/skills/ai-news-radar/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

The skill will be automatically detected and loaded by supported platforms.

## Documentation

- **SKILL.md**: Complete skill documentation and usage guide
- **references/ARCHITECTURE.md**: System architecture and design
- **references/DEPLOYMENT.md**: Deployment and CI/CD setup
- **references/SOURCE_MAPPING.md**: News source configurations
- **references/FILTERING_RULES.md**: Filtering algorithm details

## Requirements

- Python 3.11 or higher
- Dependencies listed in `requirements.txt`

## License

This skill follows the Agent Skills specification. See [agentskills.io](https://agentskills.io) for more information.

## Contributing

Contributions are welcome! Please:

1. Add new parsers in `scripts/parsers/`
2. Add new filters in `scripts/filters/`
3. Update documentation in `references/`
4. Add tests in `tests/`
5. Update `SKILL.md` with new features

## Support

For issues and questions:
- Check the documentation in `references/`
- Review `SKILL.md` for usage examples
- Open an issue on GitHub
