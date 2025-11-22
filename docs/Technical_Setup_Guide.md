# VUTS Technical Setup Guide

Comprehensive technical documentation for developers and power users who want to understand the system architecture, advanced configuration, and implementation details.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Installation & Dependencies](#installation--dependencies)
3. [Module Documentation](#module-documentation)
4. [Configuration Reference](#configuration-reference)
5. [API Integration](#api-integration)
6. [Data Flow & Processing](#data-flow--processing)
7. [Advanced Usage](#advanced-usage)
8. [Performance & Optimization](#performance--optimization)
9. [Testing & Validation](#testing--validation)
10. [Troubleshooting](#troubleshooting)

---

## System Architecture

### High-Level Overview

VUTS is a modular Python-based system following a pipeline architecture:

```
News Sources → Fetching Module → Storage → LLM Analysis → Scoring Engine → UI/Notifications
     ↓              (Phase 2)       ↓        (Phase 3)      (Phase 4)     (Phases 5-6)
Market Data ────────────────────────┴──────────────┘
```

### Technology Stack

- **Language**: Python 3.8+
- **Async I/O**: `aiohttp`, `asyncio` for concurrent operations
- **LLM Integration**: OpenAI API (GPT-4o-mini, GPT-4, GPT-3.5-turbo)
- **Market Data**: `yfinance` (Yahoo Finance API wrapper)
- **Content Extraction**: `beautifulsoup4`, `readability-lxml`
- **Web Framework**: Flask (for UI)
- **Data Format**: JSON for all storage and interchange

### Module Breakdown

**Phase 2: Fetching Module** (`src/fetching/`)
- Async news collection from multiple sources
- Content extraction and cleaning
- Deduplication and filtering
- Output: Raw article JSON files

**Phase 3: LLM Module** (`src/llm/`)
- Sentiment analysis using OpenAI API
- Prompt engineering and response parsing
- Market context integration
- Output: Scored article JSON files

**Phase 4: Scoring Module** (`src/scoring/`)
- Multi-article aggregation
- Source weighting and temporal decay
- Trend analysis
- Recommendation generation
- Output: Buy/Hold/Sell recommendations

**Phase 5: UI Module** (`src/ui/`)
- Flask-based web interface
- Real-time data visualization
- Configuration management
- Output: Interactive dashboard

**Phase 6: Notifications Module** (`src/notifications/`)
- Alert generation and management
- Browser notifications
- Subscription management
- Output: User alerts

---

## Installation & Dependencies

### System Requirements

- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended for large batches)
- Internet connection for API calls
- ~100MB disk space for application
- Additional space for article storage (varies by usage)

### Full Installation

```bash
# Clone repository
git clone https://github.com/DJSeb/vuts.git
cd vuts/scratch

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import aiohttp, openai, flask, yfinance; print('All dependencies installed')"
```

### Dependency Details

Key dependencies from `requirements.txt`:

```
openai>=1.0.0           # OpenAI API client
aiohttp>=3.8.0          # Async HTTP requests
beautifulsoup4>=4.11.0  # HTML parsing
readability-lxml>=0.8.1 # Content extraction
yfinance>=0.2.0         # Market data
flask>=2.3.0            # Web framework
requests>=2.28.0        # HTTP requests
feedparser>=6.0.0       # RSS parsing
python-dateutil>=2.8.0  # Date handling
```

### Environment Configuration

Create a `.env` file or set environment variables:

```bash
# Required for sentiment analysis
export OPENAI_API_KEY="sk-..."

# Optional: News sources (at least one recommended)
export NEWSAPI_KEY="..."
export BING_NEWS_KEY="..."
export FINNHUB_KEY="..."

# Optional: Configuration
export VUTS_DATA_DIR="/path/to/data"
export VUTS_LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
```

---

## Module Documentation

### Fetching Module (`src/fetching/financial_news_collector_async.py`)

**Purpose**: Asynchronously fetch and process news articles from multiple sources.

#### Core Functions

```python
async def fetch_from_googlenews_rss(topic: str, max_age_days: int) -> List[Dict]
```
- Fetches articles from Google News RSS feed
- Returns: List of article dictionaries with metadata
- Rate limit: No official limit, recommended 10 req/sec

```python
async def fetch_from_bingnews(topic: str, api_key: str, max_age_days: int) -> List[Dict]
```
- Fetches articles from Bing News API
- Requires: `BING_NEWS_KEY` environment variable
- Rate limit: Depends on subscription tier
- Returns: Structured article data with content snippets

```python
async def fetch_from_finnhub(topic: str, api_key: str, max_age_days: int) -> List[Dict]
```
- Fetches company news from Finnhub API
- Requires: `FINNHUB_KEY` environment variable
- Returns: Professional-grade financial news
- Note: Highest reliability weight in scoring

```python
async def extract_content(url: str, extractor: str = "readability") -> str
```
- Extracts main content from article URLs
- Supported extractors: `readability`, `beautifulsoup`
- Returns: Cleaned article text
- Handles: Paywalls, JavaScript-rendered content

#### Configuration Schema

```json
{
  "topics": ["TSLA", "AAPL"],        // Stock symbols or search terms
  "sources": ["googlenews_rss"],      // News sources to use
  "max_age_days": 14,                 // Article age filter
  "fetch_full_content": true,         // Extract full article text
  "fetch_full_top_n": 5,              // How many articles to fully extract
  "content_extractor": "readability", // Extraction method
  "max_content_chars": 6000           // Content length limit
}
```

#### Output Format

Articles saved to: `output/{source}/{topic}/{sequence}_{date}.json`

```json
{
  "source": "googlenews_rss",
  "topic": "TSLA",
  "title": "Article Title",
  "url": "https://...",
  "published_at": "2024-11-10T12:00:00+00:00",
  "content": "Full article text...",
  "author": "Jane Doe",
  "score": 0.85  // Optional: source-provided relevance score
}
```

#### Error Handling

- **Network failures**: Automatic retry with exponential backoff
- **Content extraction failures**: Falls back to snippet/summary
- **Rate limiting**: Respects API limits with delay mechanisms
- **Invalid JSON**: Logs error and continues with next article

### LLM Module (`src/llm/sentiment_analyzer.py`)

**Purpose**: Analyze article sentiment using Large Language Models with market context.

#### Core Functions

```python
def load_prompt_template(filepath: str) -> str
```
- Loads the LLM prompt template
- Template file: `src/llm/sentiment_prompt.txt`
- Returns: Prompt string with placeholders

```python
def format_prompt(template: str, article: Dict, market_context: str = "") -> str
```
- Fills prompt template with article and context data
- Parameters:
  - `template`: Loaded prompt string
  - `article`: Article dictionary from fetching module
  - `market_context`: Optional market data context
- Returns: Complete prompt ready for LLM

```python
async def call_openai_api(prompt: str, model: str = "gpt-4o-mini", 
                          api_key: str = None) -> str
```
- Sends prompt to OpenAI API
- Supported models:
  - `gpt-4o-mini`: Fast, cheap, recommended ($0.15/$0.60 per 1M tokens)
  - `gpt-4o`: More capable, 4x cost
  - `gpt-3.5-turbo`: Older, less accurate for sentiment
- Returns: Raw LLM response text
- Handles: Rate limits, token limits, API errors

```python
def parse_llm_response(response: str) -> Tuple[float, str]
```
- Extracts score and explanation from LLM response
- Expected format: "Score: X.XX\nExplanation: ..."
- Returns: (score, explanation) tuple
- Validation: Ensures score is between -10.00 and +10.00

```python
def find_article_files(data_dir: str, max_age_days: int = 1) -> List[Path]
```
- Discovers article JSON files in directory tree
- Filters: Only returns articles within age limit
- Skips: Already-analyzed articles (checks `llm_scores/` dir)
- Returns: List of article file paths

```python
def save_llm_score(article_data: Dict, score: float, explanation: str, 
                   output_dir: str, model: str)
```
- Saves sentiment analysis results
- Output: `llm_scores/{topic}/{filename}_score.json`
- Includes: Original article metadata + score + explanation

#### Prompt Engineering

The prompt template (`sentiment_prompt.txt`) is carefully designed to:
- Provide clear scoring guidelines with examples
- Reduce "LLM mood" variations
- Include market context when available
- Request structured output for parsing
- Emphasize objectivity and consistency

**Prompt Structure:**
1. Role definition (financial sentiment analyzer)
2. Scoring scale with detailed ranges (-10 to +10)
3. Guidelines for accuracy and consistency
4. Market context section (if available)
5. Article to analyze
6. Output format specification

#### Market Context Integration

Market context from `market/data_fetcher.py` provides:
- 30-day price history
- Price change percentages
- High/low prices
- Volume trends
- YTD performance

Format sent to LLM:
```
Market Context for TSLA:
- Current Price: $242.50
- 1-day change: +3.2% ($7.50)
- 7-day change: -2.1% ($5.20)
- 30-day change: +15.4% ($32.35)
- YTD change: +42.8%
- 52-week high: $299.29 (0.81x current)
- 52-week low: $101.81 (2.38x current)
```

#### Output Format

Score files saved to: `llm_scores/{topic}/{sequence}_score.json`

```json
{
  "article_file": "output/googlenews_rss/TSLA/001.json",
  "topic": "TSLA",
  "source": "googlenews_rss",
  "title": "Article Title",
  "url": "https://...",
  "published_at": "2024-11-10T12:00:00+00:00",
  "llm_score": 6.75,
  "llm_explanation": "Strong Q4 earnings beat. Revenue up 25% YoY.",
  "model": "gpt-4o-mini",
  "scored_at": "2024-11-10T18:30:00+00:00"
}
```

#### Performance Characteristics

- **Latency**: 1-3 seconds per article (model-dependent)
- **Throughput**: ~20-30 articles/minute (with rate limiting)
- **Token usage**: ~4,000 input, ~50 output tokens per article
- **Cost**: ~$0.0006 per article (gpt-4o-mini)
- **Accuracy**: ~85-90% agreement with human annotators (estimated)

### Scoring Module (`src/scoring/recommendation_engine.py`)

**Purpose**: Aggregate individual article scores into actionable investment recommendations.

#### Core Functions

```python
def calculate_temporal_weight(age_days: float, half_life_days: float = 7.0) -> float
```
- Calculates exponential decay weight based on article age
- Formula: `weight = 2^(-age_days / half_life_days)`
- Default half-life: 7 days (50% weight after one week)
- Returns: Weight between 0.0 and 1.0

```python
def calculate_source_weight(source: str) -> float
```
- Returns reliability weight for news source
- Weights:
  - `finnhub`: 1.0 (professional financial API)
  - `bingnews`: 0.9 (mainstream aggregation)
  - `googlenews_rss`: 0.85 (RSS feed)
  - `default`: 0.8 (unknown sources)

```python
def aggregate_scores(articles: List[Dict]) -> Dict
```
- Combines multiple article scores with weighting
- Applies: Source weights × temporal weights
- Returns: Weighted average score + metadata
- Includes: Score distribution, article count, age stats

```python
def analyze_trend(articles: List[Dict], recent_days: int = 3) -> Dict
```
- Compares recent vs older article sentiment
- Classification: "improving", "declining", "stable"
- Threshold: ±1.0 score difference for trend detection
- Returns: Trend type + recent/older average scores

```python
def calculate_confidence(articles: List[Dict], score_variance: float) -> Tuple[str, float]
```
- Determines confidence level based on:
  - Article count (more is better, up to 10)
  - Recency (newer is better)
  - Consistency (lower variance is better)
- Returns: (level, percentage) where level is "HIGH", "MEDIUM", or "LOW"
- Thresholds: HIGH ≥ 80%, MEDIUM ≥ 60%, LOW < 60%

```python
def generate_recommendation(aggregated_score: float, confidence: str, 
                           trend: Dict, articles: List[Dict]) -> Dict
```
- Generates final buy/hold/sell recommendation
- Logic:
  - Score ≥ +5.0: STRONG BUY
  - Score +2.5 to +5.0: BUY
  - Score -2.5 to +2.5: HOLD
  - Score -5.0 to -2.5: SELL
  - Score ≤ -5.0: STRONG SELL
  - Low confidence → downgrade to HOLD
- Returns: Complete recommendation with reasoning

#### Recommendation Schema

```json
{
  "topic": "TSLA",
  "recommendation": "BUY",
  "confidence": "HIGH",
  "confidence_percentage": 85,
  "aggregated_score": 4.35,
  "article_count": 6,
  "date_range": {
    "oldest": "2024-11-05T10:00:00+00:00",
    "newest": "2024-11-10T16:30:00+00:00"
  },
  "trend": {
    "direction": "improving",
    "recent_avg": 5.2,
    "older_avg": 3.5
  },
  "score_distribution": {
    "positive": 5,
    "neutral": 0,
    "negative": 1
  },
  "reasoning": "Predominantly positive sentiment with improving trend...",
  "risk_factors": ["One article mentions supply chain concerns"],
  "generated_at": "2024-11-10T18:00:00+00:00"
}
```

#### Algorithm Parameters

Configurable via function parameters:

- `half_life_days`: Temporal decay rate (default: 7.0)
- `recent_days`: Window for trend analysis (default: 3)
- `max_age_days`: Maximum article age to consider (default: 30)
- `min_articles`: Minimum articles for high confidence (default: 5)

### Market Module (`src/market/data_fetcher.py`)

**Purpose**: Fetch and format historical market data for LLM context.

#### Core Functions

```python
def fetch_market_data(symbol: str, days: int = 30) -> pd.DataFrame
```
- Fetches historical price data from Yahoo Finance
- Parameters:
  - `symbol`: Stock ticker (e.g., "TSLA", "AAPL")
  - `days`: Historical period (default: 30)
- Returns: Pandas DataFrame with OHLCV data
- Caching: Results cached for 24 hours if `--use-cache`

```python
def format_market_context(symbol: str, data: pd.DataFrame) -> str
```
- Formats market data for LLM consumption
- Calculates: Price changes, highs, lows, volume
- Returns: Human-readable string for prompt
- Format: See "Market Context Integration" section above

#### Command-Line Interface

```bash
python src/market/data_fetcher.py <SYMBOLS...> [OPTIONS]

Options:
  --days N              Historical period (default: 30)
  --output-dir DIR      Save location (default: market_data/)
  --use-cache           Reuse data < 24h old
  --show-context        Print formatted context
```

#### Output Format

Saved to: `market_data/{symbol}_market_data.json`

```json
{
  "symbol": "TSLA",
  "fetched_at": "2024-11-10T18:00:00+00:00",
  "period_days": 30,
  "data": {
    "dates": ["2024-10-11", "2024-10-12", ...],
    "open": [240.50, 242.30, ...],
    "high": [245.20, 246.80, ...],
    "low": [239.10, 240.50, ...],
    "close": [244.50, 245.90, ...],
    "volume": [125000000, 98000000, ...]
  },
  "summary": {
    "current_price": 245.90,
    "1d_change": 1.40,
    "1d_change_pct": 0.57,
    "7d_change": -5.20,
    "30d_change": 32.35,
    "ytd_change_pct": 42.8,
    "52w_high": 299.29,
    "52w_low": 101.81
  }
}
```

---

## Configuration Reference

### Fetching Configuration

Comprehensive configuration example:

```json
{
  "topics": [
    "TSLA",    // Stock ticker or company name
    "AAPL",
    "Tech Industry"  // Can use freeform search terms
  ],
  "sources": [
    "googlenews_rss",  // Free, no API key
    "bingnews",        // Requires BING_NEWS_KEY
    "finnhub"          // Requires FINNHUB_KEY
  ],
  "max_age_days": 14,           // Article age filter
  "fetch_full_content": true,    // Extract full text vs snippets
  "fetch_full_top_n": 5,        // How many to fully extract (ordered by relevance)
  "content_extractor": "readability",  // Options: readability, beautifulsoup
  "max_content_chars": 6000,    // Truncate long articles
  "deduplicate": true,          // Remove duplicate URLs
  "min_content_length": 200     // Skip very short articles
}
```

### LLM Configuration

Command-line options for `sentiment_analyzer.py`:

```bash
--data-dir DIR             # Base directory with article files
--prompt-file FILE         # Custom prompt template (default: sentiment_prompt.txt)
--max-age-days N           # Only analyze articles N days old or newer (default: 1)
--max-articles N           # Process at most N articles (default: 10)
--model MODEL              # OpenAI model (default: gpt-4o-mini)
--api-key KEY              # OpenAI API key (default: from OPENAI_API_KEY env)
--market-data-dir DIR      # Directory with market data (optional)
--temperature FLOAT        # LLM temperature 0.0-2.0 (default: 0.0 for consistency)
--max-tokens N             # Maximum response tokens (default: 150)
```

### Scoring Configuration

Command-line options for `recommendation_engine.py`:

```bash
--data-dir DIR             # Directory with llm_scores/ data
--output-dir DIR           # Where to save recommendations
--topic SYMBOL             # Process specific topic only (default: all)
--half-life-days N         # Temporal decay rate (default: 7)
--max-age-days N           # Maximum article age (default: 30)
--min-articles N           # Minimum for high confidence (default: 5)
```

### UI Configuration

Command-line options for web interface:

```bash
--host HOST                # Bind address (default: 127.0.0.1)
--port PORT                # Port number (default: 5000)
--debug                    # Enable Flask debug mode
--data-dir DIR             # Root data directory
--reload                   # Auto-reload on file changes
```

---

## API Integration

### OpenAI API

**Authentication:**
```python
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
```

**Models and Pricing (as of Nov 2024):**

| Model | Input Cost | Output Cost | Speed | Quality |
|-------|-----------|-------------|-------|---------|
| gpt-4o-mini | $0.150/1M | $0.600/1M | Fast | Good |
| gpt-4o | $0.600/1M | $1.800/1M | Medium | Best |
| gpt-3.5-turbo | $0.150/1M | $0.600/1M | Fastest | Lower |

**Typical Usage Per Article:**
- Input tokens: ~4,000
- Output tokens: ~50
- Cost (gpt-4o-mini): $0.0006 per article

**Rate Limits:**
- Free tier: 3 requests/minute, 200 requests/day
- Tier 1: 500 requests/minute
- Tier 2: 5,000 requests/minute
- Enterprise: Custom limits

**Error Handling:**
```python
try:
    response = await openai.ChatCompletion.create(...)
except openai.error.RateLimitError:
    # Wait and retry
except openai.error.APIError:
    # Server error, retry
except openai.error.InvalidRequestError:
    # Bad request, log and skip
```

### News APIs

**Google News RSS:**
- No API key required
- Free, unlimited
- URL: `https://news.google.com/rss/search?q={topic}`
- Returns: RSS feed with headlines and links
- Limitations: No full content, must extract from URLs

**Bing News API:**
- Requires: Azure subscription + API key
- Pricing: Tiered by requests/month
- Endpoint: `https://api.bing.microsoft.com/v7.0/news/search`
- Returns: Structured JSON with snippets
- Rate limit: Subscription-dependent

**Finnhub API:**
- Requires: Free or paid API key
- Free tier: 60 API calls/minute
- Endpoint: `https://finnhub.io/api/v1/company-news`
- Returns: Professional financial news
- Best quality, highest reliability weight

---

## Data Flow & Processing

### Complete Pipeline

```
1. Configuration → Fetching Module
   - Read topics and sources from config
   - Validate API keys
   
2. Fetching Module → Raw Articles
   - Async fetch from multiple sources
   - Content extraction
   - Save to output/{source}/{topic}/*.json
   
3. Raw Articles + Market Data → LLM Module
   - Discover articles in data directory
   - Load market context if available
   - Format prompts with templates
   - Call OpenAI API
   - Parse and validate responses
   - Save to llm_scores/{topic}/*_score.json
   
4. LLM Scores → Scoring Module
   - Load all scores for each topic
   - Apply source and temporal weighting
   - Aggregate scores
   - Analyze trends
   - Generate recommendations
   - Save to recommendations/{topic}_recommendation.json
   
5. Recommendations → UI/Notifications
   - Web UI displays results
   - Notification system generates alerts
   - User views dashboard
```

### File Organization

```
project_root/
├── scratch/
│   ├── output/                      # Fetched articles
│   │   ├── googlenews_rss/
│   │   │   ├── TSLA/
│   │   │   │   ├── 001_2024-11-10.json
│   │   │   │   └── 002_2024-11-10.json
│   │   │   └── AAPL/
│   │   ├── bingnews/
│   │   └── finnhub/
│   ├── llm_scores/                  # Sentiment analysis results
│   │   ├── TSLA/
│   │   │   ├── 001_score.json
│   │   │   └── 002_score.json
│   │   └── AAPL/
│   ├── recommendations/             # Investment recommendations
│   │   ├── TSLA_recommendation.json
│   │   └── AAPL_recommendation.json
│   └── market_data/                 # Historical price data
│       ├── TSLA_market_data.json
│       └── AAPL_market_data.json
```

### Data Persistence

- **Format**: JSON for human readability and easy parsing
- **Atomicity**: Files written atomically (temp file + rename)
- **Caching**: Smart skipping of already-processed articles
- **Retention**: No automatic cleanup (user-managed)

---

## Advanced Usage

### Batch Processing

Process large numbers of articles efficiently:

```bash
# Fetch articles for many topics
./vuts fetch --config large_config.json --output-dir batch_output

# Process in chunks to manage API costs
for i in {0..100..10}; do
  ./vuts analyze --data-dir batch_output \
    --max-articles 10 \
    --skip $i
  sleep 60  # Rate limiting
done
```

### Custom Prompts

Modify `src/llm/sentiment_prompt.txt` for different analysis styles:

```text
You are a [CUSTOM ROLE].

Analyze this article and rate it on a scale of [CUSTOM SCALE].

Consider:
- [CUSTOM CRITERIA 1]
- [CUSTOM CRITERIA 2]

Article:
{article_text}

Provide your rating as: Rating: X
Explanation: [YOUR REASONING]
```

### Programmatic Usage

Use VUTS as a Python library:

```python
from pathlib import Path
from src.llm.sentiment_analyzer import (
    load_prompt_template,
    format_prompt,
    call_openai_api,
    parse_llm_response
)

# Load template
template = load_prompt_template("src/llm/sentiment_prompt.txt")

# Prepare article
article = {
    "title": "Company Reports Earnings",
    "content": "Full article text..."
}

# Format and analyze
prompt = format_prompt(template, article)
response = await call_openai_api(prompt, model="gpt-4o-mini")
score, explanation = parse_llm_response(response)

print(f"Score: {score}, Explanation: {explanation}")
```

### Integration with Other Tools

Export data for external analysis:

```bash
# Export to CSV
python -c "
import json, csv
from pathlib import Path

scores = []
for f in Path('llm_scores').rglob('*_score.json'):
    with open(f) as fh:
        scores.append(json.load(fh))

with open('scores.csv', 'w') as fh:
    writer = csv.DictWriter(fh, fieldnames=scores[0].keys())
    writer.writeheader()
    writer.writerows(scores)
"

# Import to database
# Use your preferred ORM or database client
```

---

## Performance & Optimization

### Latency Optimization

**Fetching Module:**
- Uses `asyncio` for concurrent requests
- Typical: 50-100 articles fetched in 10-15 seconds
- Bottleneck: Content extraction from slow websites

**LLM Module:**
- Main bottleneck: OpenAI API latency (1-3s per article)
- Optimization: Process in parallel batches
- Trade-off: Cost vs speed (more concurrency = faster but same cost)

**Scoring Module:**
- Fast: Processes 1000s of scores in seconds
- No API calls, pure computation
- Memory usage: ~1MB per 1000 articles

### Cost Optimization

**Reduce API Calls:**
```bash
# Only analyze recent articles
--max-age-days 1

# Limit total articles
--max-articles 10

# Skip already-analyzed articles (default behavior)
```

**Use Cheaper Models:**
```bash
# Use gpt-3.5-turbo (same cost as gpt-4o-mini)
--model gpt-3.5-turbo

# Trade-off: Lower accuracy, less consistent scoring
```

**Batch Operations:**
- Process multiple articles in single session
- Reuse market data across articles
- Share HTTP connections

### Caching Strategies

**Article Caching:**
- Fetching module saves articles locally
- Re-analysis uses cached articles (no re-fetch)
- Expires: Never (user-managed cleanup)

**Market Data Caching:**
- `--use-cache` flag reuses data < 24h old
- Reduces Yahoo Finance API calls
- Trade-off: Freshness vs speed

**LLM Score Caching:**
- Automatically skips already-scored articles
- Check: Looks for existing `*_score.json` files
- Override: Delete score files to re-analyze

---

## Testing & Validation

### Running Tests

```bash
cd scratch

# Test LLM analyzer (no API key required)
python src/tests/test_llm_analyzer.py

# Test scoring engine
python src/tests/test_scoring_engine.py

# Test notifications system
python src/tests/test_notifications.py

# Test vuts CLI entrypoint
python src/tests/test_vuts_entrypoint.py

# Run all tests
for test in src/tests/test_*.py; do
  python "$test" || exit 1
done
```

### Test Coverage

**LLM Analyzer Tests:**
- Prompt template loading and formatting
- LLM response parsing (valid and invalid)
- Score validation (-10 to +10 range)
- Article file discovery and filtering
- Market context integration

**Scoring Engine Tests:**
- Temporal decay calculations
- Source weight assignments
- Score aggregation with weighting
- Trend analysis (improving/declining/stable)
- Recommendation generation logic
- Confidence calculation

**Notification Tests:**
- Notification creation and persistence
- Severity level filtering
- Subscription management
- Read/unread state tracking

### Manual Testing

**End-to-End Test:**
```bash
# 1. Fetch demo data
python demos/demo_workflow.py

# 2. Verify articles created
ls -lh demo_output/demo_source/TSLA/

# 3. Analyze sentiment
cd scratch
python src/llm/sentiment_analyzer.py \
  --data-dir ../demo_output \
  --max-articles 2 \
  --model gpt-4o-mini

# 4. Verify scores
cat demo_output/llm_scores/TSLA/*_score.json

# 5. Generate recommendations
python src/scoring/recommendation_engine.py \
  --data-dir ../demo_output/llm_scores \
  --output-dir ../demo_output/recommendations

# 6. Verify recommendations
cat demo_output/recommendations/TSLA_recommendation.json
```

---

## Troubleshooting

### Common Issues

**"No articles found to analyze"**

Causes:
- Articles are too old (exceed `--max-age-days`)
- Articles lack `content` field
- Articles already analyzed (scores exist)

Solutions:
```bash
# Increase age filter
--max-age-days 7

# Check article structure
cat output/googlenews_rss/TSLA/001.json | jq '.content'

# Force re-analysis (delete existing scores)
rm -rf llm_scores/
```

**"OpenAI API error: Rate limit exceeded"**

Causes:
- Free tier limits (3 req/min, 200/day)
- Burst of requests

Solutions:
```bash
# Reduce parallelism
--max-articles 5

# Add delays between batches
for i in {0..20..5}; do
  ./vuts analyze --max-articles 5 --skip $i
  sleep 30
done

# Upgrade OpenAI tier
```

**"Invalid score returned by LLM"**

Causes:
- LLM returned text instead of numeric score
- Prompt template modified incorrectly
- Model hallucination

Solutions:
```bash
# Use default prompt template
--prompt-file src/llm/sentiment_prompt.txt

# Try different model
--model gpt-4o  # More reliable but pricier

# Check logs for LLM response
# Script automatically skips invalid scores
```

**"Market data fetch failed"**

Causes:
- Invalid ticker symbol
- Yahoo Finance API unavailable
- Network issues

Solutions:
```bash
# Verify symbol
python -c "import yfinance as yf; print(yf.Ticker('TSLA').info)"

# Skip market context
# Omit --market-data-dir flag

# Use cached data
--use-cache
```

**"Web UI shows no data"**

Causes:
- Data directory not specified
- Scores not generated yet
- Incorrect path

Solutions:
```bash
# Specify data directory
./vuts ui --data-dir /full/path/to/output

# Verify scores exist
ls -R llm_scores/

# Check terminal for Flask errors
```

### Debug Mode

Enable verbose logging:

```bash
# Set log level
export VUTS_LOG_LEVEL=DEBUG

# Run with Python warnings
python -W all src/llm/sentiment_analyzer.py ...

# Flask debug mode
./vuts ui --debug
```

### Performance Issues

**Slow fetching:**
- Check network speed
- Reduce `fetch_full_top_n`
- Disable content extraction: `"fetch_full_content": false`

**High API costs:**
- Reduce `--max-articles`
- Use cheaper model: `--model gpt-3.5-turbo`
- Increase `--max-age-days` to avoid re-analyzing same articles

**Memory usage:**
- Large batches (>1000 articles) may use significant RAM
- Process in chunks
- Clean up old data periodically

---

## Architecture Decisions

### Why JSON?

- Human-readable for debugging
- Universal format, easy integration
- No database dependencies
- Simple file-based storage
- Easy version control (if needed)

### Why Async for Fetching?

- Network I/O is the bottleneck
- Fetch 10 sources in parallel vs sequential (10x speedup)
- Python `asyncio` is mature and well-supported
- Minimal complexity overhead

### Why Not Async for LLM Analysis?

- OpenAI SDK handles connection pooling
- Rate limits are the bottleneck, not I/O
- Sequential processing easier to debug
- Cost tracking is simpler

### Why Separate Modules?

- **Separation of concerns**: Each phase can be developed independently
- **Reusability**: Use fetching without LLM, or LLM without fetching
- **Testing**: Easier to unit test isolated modules
- **Flexibility**: Replace components (e.g., different LLM provider)

### Why OpenAI API?

- Best-in-class accuracy for sentiment analysis
- Well-documented, reliable API
- Flexible model selection (cost vs quality)
- Future-proof (continuous improvements)

---

## Extending VUTS

### Adding New News Sources

Create a new fetcher function in `src/fetching/financial_news_collector_async.py`:

```python
async def fetch_from_newsource(topic: str, api_key: str, max_age_days: int) -> List[Dict]:
    """Fetch articles from NewSource API."""
    url = f"https://newsource.com/api/search?q={topic}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            
    articles = []
    for item in data["results"]:
        articles.append({
            "source": "newsource",
            "topic": topic,
            "title": item["headline"],
            "url": item["link"],
            "published_at": item["date"],
            "content": item.get("body", "")
        })
    
    return articles
```

Register in main fetch function:
```python
if "newsource" in sources:
    articles.extend(await fetch_from_newsource(topic, api_key, max_age_days))
```

### Custom Scoring Logic

Modify `src/scoring/recommendation_engine.py`:

```python
def calculate_custom_weight(article: Dict) -> float:
    """Custom weighting based on article characteristics."""
    weight = 1.0
    
    # Boost professional sources
    if article["source"] == "wsj":
        weight *= 1.5
    
    # Downweight short articles
    if len(article.get("content", "")) < 500:
        weight *= 0.8
    
    # Boost articles with high engagement
    if article.get("views", 0) > 10000:
        weight *= 1.2
    
    return weight
```

### Alternative LLM Providers

Replace OpenAI with another provider:

```python
async def call_anthropic_api(prompt: str, model: str = "claude-3-sonnet") -> str:
    """Call Anthropic Claude API."""
    import anthropic
    
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    message = client.messages.create(
        model=model,
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text
```

---

## Security Considerations

### API Key Management

**DO:**
- Store keys in environment variables
- Use `.env` files (not committed to git)
- Rotate keys regularly
- Use key restrictions where possible (e.g., IP whitelisting)

**DON'T:**
- Hard-code keys in source code
- Commit keys to version control
- Share keys via insecure channels
- Use production keys for testing

### Data Privacy

- Article content is sent to OpenAI API
- OpenAI policy: Data not used for training (as of 2024)
- Use temporary chats only
- Consider: Privacy implications of sending proprietary news

### Input Validation

- Validate all user inputs (file paths, URLs, config values)
- Sanitize article content before LLM submission
- Check response formats before parsing
- Handle malicious content gracefully

---

## Further Resources

### Official Documentation

- OpenAI API: https://platform.openai.com/docs
- Yahoo Finance: https://github.com/ranaroussi/yfinance
- Flask: https://flask.palletsprojects.com/
- aiohttp: https://docs.aiohttp.org/

### Related Reading

- Prompt Engineering Guide: https://www.promptingguide.ai/
- Sentiment Analysis Best Practices
- Financial NLP Research Papers
- Rate Limiting Strategies

### Community & Support

- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share use cases
- Wiki: Community-contributed documentation

---

## Appendix: Complete CLI Reference

### vuts Command

```bash
./vuts <subcommand> [options]
```

**Subcommands:**
- `fetch`: Collect news articles
- `analyze`: Perform sentiment analysis
- `market`: Fetch market data
- `ui`: Launch web interface

### fetch Subcommand

```bash
./vuts fetch --config CONFIG.json --output-dir DIR
```

**Options:**
- `--config PATH`: Configuration file (required)
- `--output-dir PATH`: Output directory (required)

### analyze Subcommand

```bash
./vuts analyze --data-dir DIR [OPTIONS]
```

**Options:**
- `--data-dir PATH`: Article directory (required)
- `--max-articles N`: Limit processing (default: 10)
- `--max-age-days N`: Article age filter (default: 1)
- `--model NAME`: OpenAI model (default: gpt-4o-mini)
- `--market-data-dir PATH`: Market context directory (optional)
- `--prompt-file PATH`: Custom prompt template (optional)

### market Subcommand

```bash
./vuts market <SYMBOLS...> [OPTIONS]
```

**Options:**
- `SYMBOLS`: Space-separated ticker symbols (required)
- `--days N`: Historical period (default: 30)
- `--output-dir PATH`: Output directory (default: market_data/)
- `--use-cache`: Reuse cached data < 24h
- `--show-context`: Display formatted context

### ui Subcommand

```bash
./vuts ui [OPTIONS]
```

**Options:**
- `--host HOST`: Bind address (default: 127.0.0.1)
- `--port PORT`: Port number (default: 5000)
- `--debug`: Enable debug mode
- `--data-dir PATH`: Data directory (default: current)

---

**Document Version:** 1.0
**Last Updated:** November 2024
**Maintainer:** VUTS Development Team
