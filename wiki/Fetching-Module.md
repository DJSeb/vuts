# Fetching Module

The fetching module handles collection of financial news articles from multiple sources.

## Overview

**Location**: `scratch/src/fetching/`

The fetching module provides asynchronous news collection with:
- Multi-source support (Google News RSS, Bing News, Finnhub, etc.)
- Parallel article fetching for speed
- Content extraction from full article pages
- Configurable filtering and prioritization
- Automatic deduplication

## Main Script

### `financial_news_collector_async.py`

The primary script for fetching financial news articles.

**Usage:**
```bash
cd scratch
python src/fetching/financial_news_collector_async.py <config_file> <output_dir>
```

**Example:**
```bash
python src/fetching/financial_news_collector_async.py \
    example_data/copilot-gpt5-cfg.json \
    output
```

## Configuration

Configuration is done via JSON files. Example (`example_data/copilot-gpt5-cfg.json`):

```json
{
  "topics": ["TSLA", "MSFT", "NVIDIA", "AMD"],
  "sources": ["googlenews_rss", "bingnews", "finnhub"],
  "max_age_days": 14,
  "fetch_full_content": true,
  "fetch_full_top_n": 5,
  "content_extractor": "readability",
  "max_content_chars": 6000
}
```

### Configuration Options

| Parameter | Type | Description |
|-----------|------|-------------|
| `topics` | array | Stock symbols or company names to search |
| `sources` | array | News sources to query |
| `max_age_days` | integer | Maximum age of articles to fetch |
| `fetch_full_content` | boolean | Whether to extract full article text |
| `fetch_full_top_n` | integer | Number of top articles to fully extract |
| `content_extractor` | string | Extraction method ("readability" or "simple") |
| `max_content_chars` | integer | Maximum characters per article |

## Supported Sources

### RSS/API Sources (Recommended)
- **googlenews_rss**: Google News RSS feed (no API key required)
- **bingnews**: Bing News Search API (requires `BING_NEWS_KEY`)
- **finnhub**: Finnhub Company News API (requires `FINNHUB_KEY`)

### Web Scraping Sources (Use Carefully)
- **yahoofinance**: Yahoo Finance news pages
- **googlenews**: Google News search results
- **marketwatch**: MarketWatch articles
- **reuters**: Reuters news

**Note**: Web scraping sources may be blocked or violate terms of service. Use RSS/API sources when possible.

## Output Structure

Articles are saved in this structure:

```
output/
├── googlenews_rss/
│   ├── TSLA/
│   │   ├── 001_2024-11-10.json
│   │   ├── 002_2024-11-10.json
│   │   └── ...
│   ├── MSFT/
│   └── ...
├── bingnews/
│   └── ...
└── finnhub/
    └── ...
```

### Article JSON Format

Each article is saved as:

```json
{
  "source": "googlenews_rss",
  "topic": "TSLA",
  "title": "Tesla Reports Strong Q4 Earnings",
  "url": "https://example.com/article",
  "published_at": "2024-11-10T12:00:00+00:00",
  "content": "Full article text here...",
  "score": 0.75
}
```

## Prioritization & Scoring

The module includes simple heuristics for prioritizing articles:

### Domain Bonuses
Higher-quality sources receive higher scores:
- Bloomberg, WSJ, Financial Times: +0.50
- Reuters: +0.40
- CNBC: +0.30
- MarketWatch, Seeking Alpha: +0.25

### Keyword Weights
Headlines are scored based on keywords:
- Positive: "beat", "surge", "record", "upgrade" (+0.5 to +0.8)
- Negative: "miss", "downgrade", "lawsuit", "bankruptcy" (-0.5 to -1.0)

## Advanced Features

### Async Processing

The module uses `asyncio` and `aiohttp` for concurrent requests:

```python
async def fetch_all_sources(topics, sources, max_age_days):
    tasks = []
    for topic in topics:
        for source in sources:
            tasks.append(fetch_source(session, source, topic, max_age_days))
    results = await asyncio.gather(*tasks)
```

### Content Extraction

Two extraction methods are supported:

1. **Readability** (recommended): Uses `readability-lxml` for clean extraction
2. **Simple**: Basic BeautifulSoup text extraction

### Rate Limiting

Built-in delays prevent API rate limits:
- 1-second delay between requests
- Configurable timeout (20 seconds default)
- Graceful error handling

## API Key Setup

```bash
# Bing News Search (Azure Cognitive Services)
export BING_NEWS_KEY="your-bing-key"

# Finnhub (Free tier available)
export FINNHUB_KEY="your-finnhub-key"

# NewsAPI (if using newsapi source)
export NEWSAPI_KEY="your-newsapi-key"
```

## Troubleshooting

**No articles found**
- Check your date range (`max_age_days`)
- Verify API keys are set
- Try different sources

**HTTP errors**
- Some sources may block automated requests
- Use RSS/API sources instead of web scraping
- Check your internet connection

**Content extraction fails**
- Install readability: `pip install readability-lxml`
- Some sites use JavaScript rendering (not supported)
- Paywalls will block content extraction

## Performance

Typical performance metrics:
- **Google News RSS**: ~2-5 seconds per topic
- **Bing News API**: ~1-2 seconds per topic
- **Finnhub API**: ~1-2 seconds per topic
- **Content extraction**: ~1-3 seconds per article

## See Also

- [LLM Module](LLM-Module) - For sentiment analysis
- [Utilities Module](Utilities-Module) - Shared datetime/file utilities
- [Architecture](Architecture) - System overview
