# AI News Radar - Architecture Documentation

## System Overview

AI News Radar is a modular news aggregation system designed to fetch, filter, and present AI/technology news from multiple sources.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AI News Radar                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Config     │────│   Main       │────│   Storage    │       │
│  │  Management  │    │  Controller  │    │    Layer     │       │
│  └──────────────┘    └──────┬───────┘    └──────────────┘       │
│                             │                                    │
│                    ┌────────┴────────┐                         │
│                    │                 │                         │
│             ┌──────▼──────┐  ┌──────▼──────┐                   │
│             │   Parsers   │  │   Filters   │                   │
│             └─────────────┘  └─────────────┘                   │
│                    │                 │                         │
│             ┌──────▼──────┐  ┌──────▼──────┐                   │
│             │   RSS/OPML  │  │   AI Topic  │                   │
│             │   Parser    │  │   Filter    │                   │
│             └─────────────┘  └─────────────┘                   │
│             ┌─────────────┐  ┌─────────────┐                   │
│             │   HTML      │  │   Time      │                   │
│             │   Parser    │  │   Filter    │                   │
│             └─────────────┘  └─────────────┘                   │
│                              ┌─────────────┐                   │
│                              │  Duplicate  │                   │
│                              │   Filter    │                   │
│                              └─────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Module Breakdown

### 1. Core Modules (`scripts/`)

#### `config.py`
- **Purpose**: Configuration management
- **Classes**: `RadarConfig`
- **Responsibilities**:
  - Load configuration from YAML files
  - Load configuration from environment variables
  - Provide default configuration values
  - Validate configuration settings

#### `main.py`
- **Purpose**: Main controller and CLI interface
- **Classes**: `NewsRadar`
- **Responsibilities**:
  - Coordinate aggregation workflow
  - Manage parser instances
  - Apply filters in sequence
  - Handle output formatting
  - Provide CLI interface

### 2. Parser Modules (`scripts/parsers/`)

#### `base_parser.py`
- **Purpose**: Abstract base class for all parsers
- **Classes**: `BaseParser`
- **Key Methods**:
  - `fetch(url)`: Fetch raw content
  - `parse(content)`: Parse content into articles
  - `normalize(articles)`: Standardize article format

#### `rss_parser.py`
- **Purpose**: Parse RSS and Atom feeds
- **Classes**: `RSSParser`
- **Key Features**:
  - Support for RSS 0.9, 1.0, 2.0
  - Support for Atom feeds
  - OPML file parsing
  - Robust error handling

#### `html_parser.py`
- **Purpose**: Parse HTML web pages
- **Classes**: `HTMLParser`
- **Key Features**:
  - CSS selector-based extraction
  - Relative URL resolution
  - Date parsing
  - Image extraction

### 3. Filter Modules (`scripts/filters/`)

#### `ai_topic_filter.py`
- **Purpose**: Filter by AI-related topics
- **Classes**: `AITopicFilter`
- **Features**:
  - Keyword-based filtering
  - Relevance scoring
  - Configurable keyword lists
  - Primary/secondary keyword categories

#### `time_filter.py`
- **Purpose**: Filter by time window
- **Classes**: `TimeFilter`
- **Features**:
  - Configurable time window
  - Timezone-aware comparison
  - Date parsing from multiple formats

#### `duplicate_filter.py`
- **Purpose**: Remove duplicate articles
- **Classes**: `DuplicateFilter`
- **Features**:
  - URL-based deduplication
  - Title-based deduplication
  - Fuzzy matching
  - Content hash-based deduplication

### 4. Utility Modules (`scripts/utils/`)

#### `date_utils.py`
- Date parsing and formatting
- Time range calculations
- Time ago formatting

#### `text_utils.py`
- Text cleaning and normalization
- Keyword extraction
- Language detection
- URL extraction

#### `cache.py`
- File-based caching
- TTL-based expiration
- Multiple serialization formats

#### `logger.py`
- Logging configuration
- Console and file handlers
- Verbose mode support

### 5. Storage Modules (`scripts/storage/`)

#### `json_storage.py`
- JSON file storage
- Article serialization
- Append operations
- Source filtering

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         Data Flow                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Load Configuration                                          │
│     └── config.yaml / environment                               │
│                                                                  │
│  2. Initialize Components                                       │
│     └── Parsers, Filters, Storage                               │
│                                                                  │
│  3. For Each Source:                                            │
│     └── Fetch Content (HTTP)                                    │
│     └── Parse Content (RSS/HTML)                                │
│     └── Normalize Articles                                      │
│                                                                  │
│  4. Apply Filters (Sequential)                                  │
│     └── Time Filter (24h window)                                │
│     └── AI Topic Filter (keywords)                              │
│     └── Duplicate Filter (URL/title)                            │
│                                                                  │
│  5. Store Results                                               │
│     └── Save to JSON/CSV                                        │
│                                                                  │
│  6. Return Results & Statistics                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Article Data Model

```python
{
    "title": str,              # Article title
    "url": str,                # Article URL
    "description": str,        # Article summary
    "date": datetime,          # Publish date
    "source": str,             # Source name
    "author": str,             # Author (optional)
    "tags": List[str],         # Article tags (optional)
    "image_url": str,          # Featured image (optional)
    "language": str,           # Language code
    "_ai_score": float,        # AI relevance score (internal)
    "_cached": bool,           # Cached flag (internal)
}
```

## Extension Points

### Custom Parsers

To add a custom parser:

1. Extend `BaseParser`
2. Implement `fetch()` and `parse()` methods
3. Register with `NewsRadar.register_parser()`

Example:
```python
from scripts.parsers.base_parser import BaseParser

class CustomParser(BaseParser):
    def fetch(self, url: str, **kwargs) -> str:
        # Custom fetch logic
        pass

    def parse(self, content: str, **kwargs) -> List[Dict]:
        # Custom parse logic
        pass
```

### Custom Filters

To add a custom filter:

1. Create filter class with `filter(articles)` method
2. Apply filter in aggregation pipeline

Example:
```python
class CustomFilter:
    def filter(self, articles: List[Dict]) -> List[Dict]:
        # Custom filter logic
        return [a for a in articles if condition(a)]
```

### Custom Storage

To add custom storage:

1. Implement storage interface
2. Integrate with `NewsRadar`

## Performance Considerations

### Caching Strategy
- File-based cache with TTL
- Cache keys based on URL/content hash
- Automatic cleanup of expired entries

### Parallel Fetching
- Parsers can be extended for async operation
- Sources can be fetched concurrently

### Memory Management
- Streaming parsing for large feeds
- Periodic cache cleanup
- Configurable article limits

## Security Considerations

### Input Validation
- URL validation before fetching
- Content sanitization after parsing
- Safe file path handling

### Request Handling
- User-agent identification
- Timeout enforcement
- Rate limiting consideration

### Dependency Management
- Regular dependency updates
- Security vulnerability scanning
- Minimal external dependencies

## Error Handling Strategy

### Parser Errors
- Log and continue on parse failures
- Skip invalid articles
- Report failed sources

### Network Errors
- Retry with exponential backoff
- Graceful degradation
- Source blacklisting

### Configuration Errors
- Validate on load
- Provide helpful error messages
- Use sensible defaults

## Testing Strategy

### Unit Tests
- Parser modules
- Filter logic
- Utility functions

### Integration Tests
- End-to-end workflows
- Multi-source aggregation
- Filter combinations

### Performance Tests
- Large feed handling
- Concurrent operations
- Cache effectiveness

## Future Enhancements

### Planned Features
- Database storage backend
- Web UI
- Real-time updates
- Translation API integration
- Custom alerting

### API Design
- REST API for programmatic access
- Webhook support
- GraphQL query interface

### Deployment
- Docker containerization
- Kubernetes manifests
- Cloud-native deployment
