# Market Module

The market module fetches historical stock price data to provide context for sentiment analysis.

## Overview

**Location**: `scratch/src/market/`

The market module provides:
- Historical price data from Yahoo Finance
- Price change calculations
- Volume statistics
- Market context formatting for LLM
- Smart caching (24-hour validity)

## Main Script

### `data_fetcher.py`

Fetches historical market data for stock symbols.

**Usage:**
```bash
cd scratch
python src/market/data_fetcher.py <symbols> [options]
```

**Example:**
```bash
python src/market/data_fetcher.py TSLA MSFT NVIDIA AMD \
    --days 30 \
    --output-dir output/market_data \
    --show-context
```

## Command-Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `symbols` | (required) | Stock symbols to fetch (e.g., TSLA MSFT) |
| `--days` | 30 | Number of days of historical data |
| `--output-dir` | `.` | Directory to save market data files |
| `--use-cache` | False | Reuse data if < 24 hours old |
| `--show-context` | False | Display formatted context for LLM |

## Data Source

The module uses **yfinance** (Yahoo Finance API):
- Free, no API key required
- Reliable historical data
- Company information (name, sector, market cap)
- Daily OHLCV (Open, High, Low, Close, Volume)

## Output Structure

Market data is saved as:
```
output/
└── market_data/
    ├── TSLA_market_data.json
    ├── MSFT_market_data.json
    ├── NVIDIA_market_data.json
    └── AMD_market_data.json
```

### Market Data JSON Format

```json
{
  "symbol": "TSLA",
  "company_name": "Tesla, Inc.",
  "sector": "Consumer Cyclical",
  "market_cap": 850000000000,
  "period_days": 30,
  "start_date": "2024-10-11T00:00:00+00:00",
  "end_date": "2024-11-10T00:00:00+00:00",
  "latest_price": 242.50,
  "first_price": 218.75,
  "price_change": 23.75,
  "price_change_percent": 10.86,
  "period_high": 248.30,
  "period_low": 215.20,
  "avg_volume": 125000000,
  "data_points": 21,
  "daily_prices": [
    {
      "date": "2024-10-11",
      "open": 220.50,
      "close": 223.80,
      "high": 225.10,
      "low": 219.30,
      "volume": 120000000
    },
    ...
  ]
}
```

## Formatted Context

When used with the LLM module, market data is formatted as:

```
MARKET CONTEXT FOR TSLA (Tesla, Inc.):

Recent Performance (30 days):
- Current Price: $242.50
- Price Change: up 10.86%
- Period High: $248.30
- Period Low: $215.20
- Average Daily Volume: 125,000,000

Company Information:
- Sector: Consumer Cyclical
- Market Cap: $850.00B

Recent Daily Closes:
  2024-11-04: $223.80
  2024-11-05: $226.50
  2024-11-06: $231.20
  2024-11-07: $233.40
  2024-11-08: $237.10
  2024-11-09: $241.60
  2024-11-10: $242.50
```

This context helps the LLM:
- Evaluate news impact relative to recent performance
- Consider whether news is "priced in"
- Understand current momentum (up/down trends)
- Assess significance of price movements

## Caching

The `--use-cache` flag enables smart caching:
- Checks if existing file is < 24 hours old
- Reuses cached data to avoid unnecessary API calls
- Useful for batch processing or repeated runs
- Market data older than 24 hours is automatically refreshed

**Example:**
```bash
# First run - fetches fresh data
python src/market/data_fetcher.py TSLA --output-dir output/market_data

# Second run within 24 hours - uses cache
python src/market/data_fetcher.py TSLA --output-dir output/market_data --use-cache
```

## Statistics Calculated

The module automatically calculates:
- **Price Change**: Absolute change over period
- **Price Change %**: Percentage change
- **Period High**: Highest price in period
- **Period Low**: Lowest price in period
- **Average Volume**: Mean daily trading volume
- **Data Points**: Number of trading days

## Integration with LLM Module

To use market context with sentiment analysis:

```bash
# Step 1: Fetch market data
python src/market/data_fetcher.py TSLA MSFT NVIDIA AMD \
    --output-dir output/market_data

# Step 2: Analyze with market context
python src/llm/sentiment_analyzer.py \
    --data-dir output \
    --market-data-dir output/market_data
```

The LLM module automatically:
1. Looks for matching market data files
2. Formats the context
3. Prepends it to the sentiment prompt
4. Sends to LLM for analysis

## Error Handling

The module handles various errors gracefully:
- **Invalid symbol**: Logs warning, continues with other symbols
- **No data returned**: Logs warning, skips symbol
- **Network errors**: Logs error, continues processing
- **File write errors**: Logs error but doesn't crash

## Data Quality

Yahoo Finance data is generally reliable but may have:
- Occasional gaps (market holidays, trading halts)
- Delayed updates (usually ~15 minutes for free tier)
- Corporate actions (splits, dividends) already adjusted

## Performance

Typical fetch times:
- **Single symbol**: ~1-2 seconds
- **Multiple symbols**: ~1-2 seconds per symbol (sequential)
- **With cache**: Instant (no network request)

## Advanced Usage

### Custom Date Ranges

```bash
# Last 90 days
python src/market/data_fetcher.py TSLA --days 90

# Last 7 days (for short-term context)
python src/market/data_fetcher.py TSLA --days 7
```

### Viewing Context

```bash
# Show formatted context without saving
python src/market/data_fetcher.py TSLA --show-context
```

### Batch Processing

```bash
# Fetch for many symbols
python src/market/data_fetcher.py TSLA MSFT AAPL GOOGL AMZN META NFLX \
    --days 30 \
    --output-dir output/market_data
```

## Scheduling

For daily updates, use cron:

```bash
# Add to crontab (crontab -e)
0 9 * * * cd /path/to/vuts/scratch && python src/market/data_fetcher.py TSLA MSFT --output-dir output/market_data
```

## Troubleshooting

**"No data found for symbol"**
- Verify symbol is correct (e.g., TSLA not Tesla)
- Check if symbol is traded (not delisted)
- Try on Yahoo Finance website first

**"yfinance library not found"**
- Install: `pip install yfinance`

**Network errors**
- Check internet connection
- Yahoo Finance may be temporarily down
- Try again later

**Incorrect prices**
- Data includes corporate actions (splits, dividends)
- Historical prices are adjusted automatically
- This is normal and expected

## API Limitations

Yahoo Finance (via yfinance):
- Free tier, no API key required
- No explicit rate limits (reasonable use)
- Data delayed ~15 minutes for free tier
- Historical data includes adjustments

## See Also

- [LLM Module](LLM-Module) - Uses market context
- [Fetching Module](Fetching-Module) - Fetches news
- [Utilities Module](Utilities-Module) - Shared functions
- [Getting Started](Getting-Started) - Setup guide
