# AI News Radar - Source Mapping

This document provides information about supported news sources and their configuration.

## Supported Source Types

### RSS/Atom Feeds
- Standard RSS 0.9, 1.0, 2.0
- Atom 0.3, 1.0
- MediaRSS extensions

### HTML Web Pages
- Static HTML pages
- CSS selector-based extraction
- JavaScript rendering (not supported - use RSS if needed)

### OPML Files
- RSS feed lists
- Feed categories
- Multi-feed import

## Default Sources

### TechCrunch
```yaml
- name: TechCrunch
  url: https://techcrunch.com/feed/
  type: rss
  max_articles: 20
```

### Ars Technica
```yaml
- name: Ars Technica
  url: https://feeds.arstechnica.com/arstechnica/index
  type: rss
  max_articles: 15
```

### VentureBeat
```yaml
- name: VentureBeat
  url: https://venturebeat.com/feed/
  type: rss
  max_articles: 20
```

### The Verge
```yaml
- name: The Verge
  url: https://www.theverge.com/rss/index.xml
  type: rss
  max_articles: 15
```

### Hacker News
```yaml
- name: Hacker News
  url: https://hnrss.org/frontpage
  type: rss
  max_articles: 30
```

### MIT Technology Review
```yaml
- name: MIT Technology Review
  url: https://www.technologyreview.com/feed/
  type: rss
  max_articles: 15
```

### Wired
```yaml
- name: Wired
  url: https://www.wired.com/feed/rss
  type: rss
  max_articles: 20
```

### AI News
```yaml
- name: AI News
  url: https://artificialintelligence-news.com/feed/
  type: rss
  max_articles: 15
```

### OpenAI Blog
```yaml
- name: OpenAI Blog
  url: https://openai.com/blog/rss.xml
  type: rss
  max_articles: 10
```

### Google AI Blog
```yaml
- name: Google AI Blog
  url: https://ai.googleblog.com/feeds/posts/default
  type: rss
  max_articles: 10
```

## HTML Source Configuration

For HTML sources, provide CSS selectors:

```yaml
- name: Example HTML Source
  url: https://example.com/tech-news
  type: html
  selector: article.news-item
  max_articles: 20
  field_selectors:
    title: h2.title, .headline
    link: a.article-link
    description: p.summary, .excerpt
    date: .publish-date, time[datetime]
    author: .author-name
    tags: .tag, .category
```

## OPML Configuration

```yaml
- name: Custom OPML
  type: opml
  file_path: assets/data/my_feeds.opml
  max_feeds: 10
  max_articles_per_feed: 5
```

## Source Priority

Sources can be prioritized:

```yaml
- name: High Priority Source
  url: https://example.com/feed.xml
  type: rss
  priority: 1
  max_articles: 20

- name: Low Priority Source
  url: https://example.com/feed.xml
  type: rss
  priority: 10
  max_articles: 10
```

Lower priority numbers are processed first.

## Regional Sources

### Asia Pacific
- Nikkei Asia
- South China Morning Post (Tech)

### Europe
- BBC Technology
- The Register

### Other
- Tech in Asia
- YourStory (India)

## Adding Custom Sources

### RSS Source

1. Find RSS feed URL on target site
2. Test with feedparser:
```python
import feedparser
feed = feedparser.parse('https://example.com/feed.xml')
print(feed.feed.title)
print(len(feed.entries))
```

3. Add to `assets/data/sources.yaml`

### HTML Source

1. Inspect target page structure
2. Identify article container and fields
3. Test with BeautifulSoup:
```python
from bs4 import BeautifulSoup
import requests

response = requests.get('https://example.com')
soup = BeautifulSoup(response.text, 'html.parser')
articles = soup.select('article.news-item')
print(len(articles))
```

4. Add to `assets/data/sources.yaml` with selectors

## Source-Specific Notes

### Hacker News
- High article volume, use conservative `max_articles`
- Comments often included, may want to filter out

### TechCrunch
- Includes startup funding news, may want broader keywords

### Ars Technica
- Long-form content, descriptions are often substantial

### The Verge
- Media-rich, includes many image URLs

## Rate Limiting

Be mindful of source rate limits:

| Source | Recommended Interval | Notes |
|--------|---------------------|-------|
| Hacker News | 5 minutes | High volume |
| TechCrunch | 15 minutes | Moderate |
| Ars Technica | 30 minutes | Low volume |
| Custom | Varies | Check robots.txt |

## Troubleshooting Sources

### Zero Articles from Source

1. Verify feed URL is accessible
2. Check feed format with feedparser directly
3. Review logs for parsing errors

### Incorrect Titles/Links

1. Inspect page/feed structure
2. Update CSS selectors for HTML sources
3. Check for feed format changes

### Timeouts

1. Increase `request_timeout` in config
2. Check network connectivity
3. Verify source server status

## Source Maintenance

Regularly verify:
- Feed URLs haven't changed
- Source still provides AI-relevant content
- Article structure hasn't changed
- Rate limits are respected
