# AI News Radar - Filtering Rules

This document explains the filtering mechanisms and rules used by AI News Radar.

## Filter Pipeline

Articles pass through filters in sequence:

```
Raw Articles
    ↓
[Time Filter] ──→ Within 24h articles
    ↓
[AI Topic Filter] ──→ AI-related articles
    ↓
[Duplicate Filter] ──→ Unique articles
    ↓
Final Results
```

## Time Filter

### Purpose
Filter articles by publication time to ensure relevance.

### Configuration

```python
# Default: 24 hours
TimeFilter(hours=24)
```

### Time Window
- Articles published within the specified hours are kept
- Articles outside the window are removed
- Timezone-aware comparison (UTC)

### Date Parsing
Supported formats:
- ISO 8601 strings
- RFC 2822 strings
- Common human-readable formats
- Unix timestamps

### Edge Cases
- Missing dates: Article filtered out
- Invalid dates: Article filtered out
- Future dates: Article kept (data may be incorrect)

## AI Topic Filter

### Purpose
Filter articles by AI/technology relevance using keyword matching.

### Keyword Categories

#### Primary Keywords (Score: 1.0)
Required terms that indicate strong AI relevance:
- artificial intelligence
- machine learning
- deep learning
- neural network
- natural language processing
- computer vision
- generative ai
- large language model
- llm

#### Secondary Keywords (Score: 0.7)
Terms that suggest AI context:
- chatgpt
- gpt
- openai
- anthropic
- claude
- hugging face
- transformer
- bert
- stable diffusion
- midjourney

#### Aliases (Score: 0.5)
Short forms and abbreviations:
- ai
- ml
- ai/ml
- nlp
- cv

### Scoring

An article's AI relevance score is determined by:
1. Match any primary keyword: Score = 1.0
2. Match any secondary keyword: Score = 0.7
3. Match any alias: Score = 0.5
4. No matches: Score = 0.0

### Minimum Score Threshold

Default threshold: 0.5

```python
# Filter with custom threshold
ai_filter = AITopicFilter(keywords_file="keywords.yaml")
articles = ai_filter.filter(articles, min_score=0.7)
```

### Search Scope

Keywords are searched in:
- Article title
- Description/summary
- Tags/categories

### Case Sensitivity
Matching is case-insensitive for all keywords.

### Word Boundaries
Keywords must match whole words (e.g., "ai" won't match "brain").

### Adding Custom Keywords

Edit `assets/data/keywords.yaml`:

```yaml
primary:
  - artificial intelligence
  - machine learning
  # Add more...

secondary:
  - chatgpt
  - gpt
  # Add more...

aliases:
  - ai
  - ml
  # Add more...
```

### Negative Filtering

To exclude specific topics, create a custom filter:

```python
class ExclusionFilter:
    def __init__(self, exclude_keywords):
        self.exclude_keywords = exclude_keywords

    def filter(self, articles):
        return [
            a for a in articles
            if not any(kw in a.get('title', '').lower()
                      for kw in self.exclude_keywords)
        ]
```

## Duplicate Filter

### Purpose
Remove duplicate articles across sources.

### Detection Methods

#### URL Matching
Exact URL comparison (case-sensitive, normalized).

#### Title Matching
- Exact match: Identical titles (lowercase comparison)
- Fuzzy match: Similar titles above threshold (default: 0.85)

#### Content Hash
MD5 hash of title + description + source.

### Configuration

```python
DuplicateFilter(
    by_url=True,           # Enable URL matching
    by_title=True,         # Enable title matching
    title_similarity_threshold=0.85,  # Fuzzy match threshold
    by_content=False,      # Enable content hash matching
)
```

### Duplicate Handling

**Remove Mode** (default):
- First article kept
- Duplicates removed

**Merge Mode**:
```python
duplicates.merge_duplicates(articles, prefer='newest')
```

Options:
- `prefer='newest'`: Keep most recent
- `prefer='oldest'`: Keep oldest
- `prefer='first'`: Keep first seen

### Normalization

URLs are normalized by:
- Lowercasing
- Removing tracking parameters (utm_*, ref)
- Removing trailing slashes

### Edge Cases

- Short titles (< 5 chars): Skipped for fuzzy matching
- Missing URLs: Skipped for URL matching
- Empty articles: Skipped

## Performance Impact

| Filter | Time Complexity | Memory Impact |
|--------|-----------------|---------------|
| Time | O(n) | Low |
| AI Topic | O(n*m) where m = keywords | Medium |
| Duplicate | O(n²) worst case | High (stores seen items) |

### Optimization Tips

1. **Time Filter First**: Cheapest filter, apply first
2. **Limit Keywords**: Fewer keywords = faster matching
3. **Disable Unnecessary Methods**: Only enable needed duplicate detection
4. **Use Cache**: Cache filtered results

## Custom Filters

### Creating a Custom Filter

```python
from typing import List, Dict

class CustomFilter:
    def __init__(self, config: Dict):
        self.config = config

    def filter(self, articles: List[Dict]) -> List[Dict]:
        # Your filtering logic
        filtered = [
            article for article in articles
            if self._should_keep(article)
        ]
        return filtered

    def _should_keep(self, article: Dict) -> bool:
        # Your condition logic
        return True
```

### Registering Custom Filter

```python
from scripts.main import NewsRadar

radar = NewsRadar()
radar.custom_filters = [
    CustomFilter({"min_length": 100})
]

# In aggregation pipeline
for custom_filter in radar.custom_filters:
    articles = custom_filter.filter(articles)
```

## Filter Statistics

Track filter effectiveness:

```python
from scripts.main import NewsRadar

radar = NewsRadar()
result = radar.aggregate_with_stats()

print(f"Total fetched: {result['stats']['total_fetched']}")
print(f"Filtered out: {result['stats']['total_filtered']}")
print(f"Kept: {result['stats']['total_kept']}")
```

## Troubleshooting

### Too Many Articles

Increase filter strictness:
```python
ai_filter.filter(articles, min_score=0.7)  # Higher threshold
```

### Too Few Articles

Decrease filter strictness:
```python
ai_filter.filter(articles, min_score=0.3)  # Lower threshold
```

### Wrong Articles Filtered

Add or adjust keywords in `keywords.yaml`.

### Duplicates Not Removed

Enable more detection methods:
```python
DuplicateFilter(
    by_url=True,
    by_title=True,
    by_content=True  # Enable content hash
)
```

## Best Practices

1. **Start Broad, Narrow Down**: Use lower thresholds initially
2. **Monitor Results**: Regularly review filtered articles
3. **Update Keywords**: Keep keywords current with AI trends
4. **Test Changes**: Validate filter changes before deployment
5. **Log Decisions**: Enable verbose logging for debugging

## Examples

### Example 1: Filter for LLM News Only

```python
keywords = {
    "primary": ["large language model", "llm", "gpt", "claude"],
    "secondary": [],
    "aliases": []
}
filter = AITopicFilter(keywords=keywords)
```

### Example 2: Recent High-Relevance Articles

```python
articles = radar.aggregate()
articles = time_filter.filter(articles)  # Last 24h
articles = ai_filter.filter(articles, min_score=0.7)  # High relevance
```

### Example 3: Strict Deduplication

```python
dupe_filter = DuplicateFilter(
    by_url=True,
    by_title=True,
    title_similarity_threshold=0.95,  # Very strict
    by_content=True
)
```

### Example 4: Multiple Filters Combined

```python
# Apply filters in sequence
articles = raw_articles
articles = time_filter.filter(articles)
articles = ai_filter.filter(articles, min_score=0.6)
articles = dupe_filter.filter(articles)
```
