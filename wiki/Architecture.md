# Architecture

System architecture and design overview for VUTS.

## System Overview

VUTS is a modular pipeline for financial news sentiment analysis:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Fetching  │────▶│   Market    │────▶│     LLM     │────▶│   Output    │
│   Module    │     │   Module    │     │   Module    │     │   Scores    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                    │                    │                    │
      │                    │                    │                    │
   Articles           Market Data          Sentiment             Results
   (JSON)              (JSON)              Analysis              (JSON)
```

## Data Flow

### 1. News Collection (Fetching Module)

```
Input: Configuration (topics, sources, date range)
  ↓
Async fetching from multiple sources
  ↓
Content extraction (optional)
  ↓
Prioritization & scoring
  ↓
Output: Article JSON files organized by source/topic
```

**Example Flow:**
```
Config: {topics: ["TSLA"], sources: ["googlenews_rss"]}
  ↓
Query Google News RSS for TSLA articles
  ↓
Extract full content from top 5 articles
  ↓
Save: output/googlenews_rss/TSLA/001_2024-11-10.json
```

### 2. Market Data Collection (Market Module)

```
Input: Stock symbols
  ↓
Fetch from Yahoo Finance
  ↓
Calculate statistics (price change, high/low, volume)
  ↓
Format context for LLM
  ↓
Output: Market data JSON files
```

**Example Flow:**
```
Symbols: ["TSLA"]
  ↓
Fetch 30 days of price history
  ↓
Calculate: +10.86% change, $248.30 high, $215.20 low
  ↓
Save: output/market_data/TSLA_market_data.json
```

### 3. Sentiment Analysis (LLM Module)

```
Input: Article JSON files + optional market data
  ↓
Load prompt template
  ↓
For each article:
  - Format prompt with article + market context
  - Send to OpenAI API
  - Parse score and explanation
  - Validate score range
  - Save result
  ↓
Output: Score JSON files organized by topic
```

**Example Flow:**
```
Article: output/googlenews_rss/TSLA/001_2024-11-10.json
Market: output/market_data/TSLA_market_data.json
  ↓
Format prompt with article content + market context
  ↓
Send to GPT-4o-mini (temperature 0.3)
  ↓
Receive: "SCORE: +6.75\nEXPLANATION: Strong earnings beat..."
  ↓
Validate: 6.75 is in [-10.00, +10.00] range
  ↓
Save: output/llm_scores/TSLA/001_2024-11-10_score.json
```

## Module Interactions

### Fetching → LLM

```python
# Articles saved by Fetching Module
output/googlenews_rss/TSLA/001_*.json

# Read by LLM Module
find_article_files(data_dir="output")
  → Discovers all article JSONs
  → Filters by age and required fields
  → Processes each through LLM
```

### Market → LLM

```python
# Market data saved by Market Module
output/market_data/TSLA_market_data.json

# Loaded by LLM Module
load_market_context(topic="TSLA", market_data_dir)
  → Reads market data file
  → Formats as context string
  → Prepends to article prompt
```

### Utilities → All Modules

```python
# Used by Fetching Module
ensure_datetime(article["published_at"])
json_datetime_handler(datetime.now())

# Used by LLM Module
ensure_datetime(article["published_at"])
safe_json_save(score_file, score_data)

# Used by Market Module
json_datetime_handler(datetime.now())
ensure_directory(output_dir)
```

## Directory Structure

```
vuts/
├── README.md                      # Main project README
├── docs/                          # Documentation
│   ├── Quick_Start_Guide.md
│   ├── Workflow_Guide.md
│   └── Development_Outline.md
├── wiki/                          # GitHub wiki pages
│   ├── Home.md
│   ├── Getting-Started.md
│   ├── Fetching-Module.md
│   ├── LLM-Module.md
│   ├── Market-Module.md
│   ├── Utilities-Module.md
│   └── Architecture.md (this file)
├── scratch/                       # Main application
│   ├── src/
│   │   ├── fetching/             # News collection
│   │   │   ├── __init__.py
│   │   │   └── financial_news_collector_async.py
│   │   ├── llm/                  # Sentiment analysis
│   │   │   ├── __init__.py
│   │   │   ├── sentiment_analyzer.py
│   │   │   ├── sentiment_prompt.txt
│   │   │   └── README.md
│   │   ├── market/               # Market data
│   │   │   ├── __init__.py
│   │   │   └── data_fetcher.py
│   │   ├── tests/                # Test suite
│   │   │   ├── __init__.py
│   │   │   └── test_llm_analyzer.py
│   │   └── utils/                # Shared utilities
│   │       ├── __init__.py
│   │       ├── datetime_utils.py
│   │       └── file_utils.py
│   ├── example_data/             # Configuration examples
│   │   ├── copilot-gpt5-cfg.json
│   │   └── fetch-cfg.json
│   ├── demo_workflow.py          # Interactive demo
│   └── requirements.txt          # Python dependencies
└── chats/                        # Development notes
```

## Data Formats

### Article JSON

```json
{
  "source": "googlenews_rss",
  "topic": "TSLA",
  "title": "Tesla Reports Strong Q4 Earnings",
  "url": "https://example.com/article",
  "published_at": "2024-11-10T12:00:00+00:00",
  "content": "Full article text...",
  "score": 0.75
}
```

### Market Data JSON

```json
{
  "symbol": "TSLA",
  "company_name": "Tesla, Inc.",
  "latest_price": 242.50,
  "price_change_percent": 10.86,
  "period_high": 248.30,
  "period_low": 215.20,
  "daily_prices": [...]
}
```

### Score JSON

```json
{
  "article_file": "output/googlenews_rss/TSLA/001.json",
  "topic": "TSLA",
  "title": "Tesla Reports Strong Q4 Earnings",
  "llm_score": 6.75,
  "llm_explanation": "Strong earnings beat...",
  "model": "gpt-4o-mini",
  "scored_at": "2024-11-10T18:30:00+00:00"
}
```

## Technology Stack

### Core Technologies
- **Python 3.8+**: Primary language
- **asyncio**: Async I/O for concurrent operations
- **aiohttp**: Async HTTP client

### External APIs
- **OpenAI API**: GPT models for sentiment analysis
- **Yahoo Finance**: Market data (via yfinance)
- **Bing News API**: News search (optional)
- **Finnhub API**: Company news (optional)

### Key Libraries
- **beautifulsoup4**: HTML parsing
- **readability-lxml**: Content extraction
- **pathlib**: Modern path handling
- **json**: Data serialization

## Design Principles

### Modularity
Each module is self-contained with:
- Clear input/output contracts
- Independent CLI interfaces
- Minimal cross-dependencies
- Reusable utilities

### Async Processing
- Concurrent article fetching
- Parallel API requests
- Non-blocking I/O operations
- Efficient resource usage

### Error Resilience
- Graceful error handling
- Continue on failure
- Detailed logging
- Sensible fallbacks

### Cost Efficiency
- Smart caching
- Batch processing
- Configurable limits
- Default to cheap models

### Extensibility
- Easy to add new sources
- Pluggable LLM models
- Customizable prompts
- Configurable pipelines

## Performance Characteristics

### Fetching Module
- **Throughput**: ~10-20 articles/second (RSS sources)
- **Latency**: 1-5 seconds per source
- **Bottleneck**: Network I/O, content extraction

### LLM Module
- **Throughput**: ~1-2 articles/second (gpt-4o-mini)
- **Latency**: 1-2 seconds per article
- **Bottleneck**: OpenAI API rate limits

### Market Module
- **Throughput**: ~1 symbol/second
- **Latency**: 1-2 seconds per symbol
- **Bottleneck**: Yahoo Finance API response time

## Scalability Considerations

### Current Limits
- **Articles**: Hundreds per run (API costs)
- **Symbols**: Dozens per run (rate limits)
- **Concurrency**: Limited by API quotas

### Scaling Strategies
1. **Batch Processing**: Process in configurable batches
2. **Caching**: Avoid re-fetching/re-analyzing
3. **Rate Limiting**: Respect API limits
4. **Parallel Processing**: Use async where possible

## Security Considerations

### API Keys
- Stored in environment variables
- Never committed to git
- Optional command-line override

### Data Privacy
- No data sent to OpenAI for training
- Temporary chat sessions only
- Local storage of results
- No persistent user data

### Input Validation
- URL validation in fetching
- Score range validation in LLM
- Date format validation throughout
- JSON schema validation

## Future Enhancements

See [Development Outline](../docs/Development_Outline.md) for detailed roadmap.

### Planned Features
1. **Scoring Engine**: Aggregate scores for recommendations
2. **User Interface**: Web dashboard for visualization
3. **Notifications**: Alerts for sentiment shifts
4. **Backtesting**: Correlate scores with price movements
5. **Multi-language**: Analyze global news

### Technical Improvements
1. **Database**: Persistent storage (PostgreSQL)
2. **API Layer**: FastAPI backend
3. **Caching**: Redis for performance
4. **Monitoring**: Metrics and logging
5. **Testing**: Expanded test coverage

## See Also

- [Getting Started](Getting-Started) - Setup instructions
- [Fetching Module](Fetching-Module) - News collection details
- [LLM Module](LLM-Module) - Sentiment analysis details
- [Market Module](Market-Module) - Market data details
- [Utilities Module](Utilities-Module) - Shared utilities
