# Complete Workflow Guide

This guide demonstrates the complete workflow from fetching news articles to analyzing sentiment with LLM and market context.

## Prerequisites

1. **Install Dependencies**
```bash
cd scratch
pip install -r requirements.txt
```

2. **Set Up API Keys**

You'll need the following API keys:
- OpenAI API key for LLM sentiment analysis
- Optional: NewsAPI, Bing News API, or Finnhub API keys for news fetching

Set environment variables:
```bash
export OPENAI_API_KEY="your-openai-key"
export NEWSAPI_KEY="your-newsapi-key"  # optional
export BING_NEWS_KEY="your-bing-key"   # optional
export FINNHUB_KEY="your-finnhub-key"  # optional
```

## Complete Workflow

### Step 1: Fetch News Articles

Use the financial news collector to fetch recent articles:

```bash
cd scratch
python src/fetching/financial_news_collector_async.py example_data/copilot-gpt5-cfg.json output
```

This will:
- Fetch articles for TSLA, MSFT, NVIDIA, AMD
- From sources: Google News RSS, Bing News, Finnhub
- Articles up to 14 days old
- Extract full content for top 5 articles per topic
- Save to `output/{source}/{topic}/` directories

**Configuration file** (`example_data/copilot-gpt5-cfg.json`):
```json
{
  "topics": [ "TSLA", "MSFT", "NVIDIA", "AMD" ],
  "sources": [ "googlenews_rss", "bingnews", "finnhub" ],
  "max_age_days": 14,
  "fetch_full_content": true,
  "fetch_full_top_n": 5,
  "content_extractor": "readability",
  "max_content_chars": 6000
}
```

### Step 2: Fetch Market Data (Optional but Recommended)

Fetch historical stock prices to provide context for sentiment analysis:

```bash
cd scratch
python src/market/data_fetcher.py TSLA MSFT NVIDIA AMD \
    --days 30 \
    --output-dir output/market_data \
    --show-context
```

This will:
- Fetch 30 days of historical price data from Yahoo Finance
- Calculate price changes, highs, lows, volume
- Save market data to `output/market_data/`
- Display formatted context that will be sent to LLM

### Step 3: Analyze Sentiment with LLM

Run the LLM sentiment analyzer on the fetched articles:

```bash
cd scratch
python src/llm/sentiment_analyzer.py \
    --data-dir output \
    --max-age-days 1 \
    --max-articles 10 \
    --model gpt-4o-mini \
    --market-data-dir output/market_data
```

This will:
- Find articles up to 1 day old in the output directory
- Process at most 10 articles (as requested)
- Include market context if available
- Send each article to OpenAI for sentiment scoring
- Save scores to `output/llm_scores/{topic}/`

**Without market context:**
```bash
python src/llm/sentiment_analyzer.py --data-dir output --max-age-days 1 --max-articles 10
```

### Step 4: View Results

Check the sentiment scores:

```bash
# List all score files
find output/llm_scores -name "*_score.json"

# View a specific score
cat output/llm_scores/TSLA/001_2024-11-10_score.json

# View all scores in a formatted way
find output/llm_scores -name "*_score.json" -exec echo "---" \; -exec jq '{topic, title, llm_score, llm_explanation}' {} \;
```

Example output structure:
```json
{
  "article_file": "output/googlenews_rss/TSLA/001_2024-11-10.json",
  "topic": "TSLA",
  "source": "googlenews_rss",
  "title": "Tesla Reports Strong Q4 Earnings",
  "url": "https://example.com/article",
  "published_at": "2024-11-10T12:00:00+00:00",
  "llm_score": 6.75,
  "llm_explanation": "Strong Q4 earnings beat. Revenue up 25% YoY. Raised guidance for next quarter. Analyst upgrades following announcement. Positive market reception.",
  "model": "gpt-4o-mini",
  "scored_at": "2024-11-10T18:30:00+00:00"
}
```

The `llm_explanation` field provides context for the score, making results more interpretable and useful for reports.

## Quick Test Run

For a quick test without needing API keys (except OpenAI):

```bash
cd scratch

# Create a test article manually
mkdir -p test_data/test_source/TSLA
cat > test_data/test_source/TSLA/001_test.json << 'EOF'
{
  "source": "test_source",
  "topic": "TSLA",
  "title": "Tesla Stock Surges on Strong Earnings Report",
  "url": "https://example.com/test",
  "published_at": "2024-11-10T12:00:00Z",
  "content": "Tesla Inc. reported better-than-expected earnings today, beating analyst estimates by a wide margin. The electric vehicle maker saw revenue increase 25% year-over-year, driven by strong Model 3 and Model Y sales. CEO Elon Musk expressed optimism about future growth.",
  "score": 0.5
}
EOF

# Analyze it
python src/llm/sentiment_analyzer.py \
    --data-dir test_data \
    --max-age-days 7 \
    --max-articles 1

# View result
cat test_data/llm_scores/TSLA/001_test_score.json
```

## Understanding the Scores

The LLM provides scores from **-10.00 to +10.00**:

- **Highly Negative (-10 to -7)**: Bankruptcy, fraud, catastrophic failure
- **Negative (-7 to -4)**: Missed earnings, downgrades, major losses
- **Moderately Negative (-4 to -2)**: Concerns, warnings, setbacks
- **Slightly Negative (-2 to -0.5)**: Minor concerns, cautious outlook
- **Neutral (-0.5 to +0.5)**: Balanced reporting, no clear direction
- **Slightly Positive (+0.5 to +2)**: Minor improvements, optimism
- **Moderately Positive (+2 to +4)**: Good results, positive developments
- **Positive (+4 to +7)**: Beat earnings, upgrades, major wins
- **Highly Positive (+7 to +10)**: Transformative success, breakthroughs

## Advanced Usage

### Batch Processing Multiple Configurations

Create different configuration files for different use cases:

```bash
# Tech stocks
python src/fetching/financial_news_collector_async.py example_data/tech-cfg.json output_tech

# Financial stocks
python src/fetching/financial_news_collector_async.py example_data/finance-cfg.json output_finance

# Analyze all
python src/llm/sentiment_analyzer.py --data-dir output_tech --max-articles 10
python src/llm/sentiment_analyzer.py --data-dir output_finance --max-articles 10
```

### Using Different LLM Models

For higher accuracy (higher cost):
```bash
python src/llm/sentiment_analyzer.py --data-dir output --model gpt-4o --max-articles 5
```

For faster/cheaper analysis:
```bash
python src/llm/sentiment_analyzer.py --data-dir output --model gpt-3.5-turbo --max-articles 20
```

### Scheduling Regular Updates

Set up a cron job to fetch and analyze news daily:

```bash
# Add to crontab (crontab -e)
0 9 * * * cd /path/to/vuts/scratch && ./daily_analysis.sh >> logs/analysis.log 2>&1
```

Create `daily_analysis.sh`:
```bash
#!/bin/bash
# Fetch news
python src/fetching/financial_news_collector_async.py example_data/copilot-gpt5-cfg.json output

# Fetch market data
python src/market/data_fetcher.py TSLA MSFT NVIDIA AMD --output-dir output/market_data --use-cache

# Analyze sentiment
python src/llm/sentiment_analyzer.py --data-dir output --max-age-days 1 --max-articles 10 --market-data-dir output/market_data
```

## Notes and Best Practices

1. **API Costs**: The LLM analyzer uses OpenAI API which costs money. Start with `gpt-4o-mini` (cheapest) and limit `--max-articles` to 10 for testing.

2. **Rate Limiting**: The scripts include 1-second delays between API calls to avoid rate limits. For large batches, increase the delay in the code.

3. **Caching**: The market data fetcher caches results for 24 hours. Use `--use-cache` to avoid unnecessary API calls.

4. **Data Privacy**: The scripts are designed to NOT train on your data. Chats are temporary and scores are stored locally.

5. **Content Quality**: The fetching script can extract full article content, but this doesn't work for all sources (paywalls, dynamic content). The LLM will work with whatever content is available.

6. **Prompt Engineering**: The prompt file (`llm_sentiment_prompt.txt`) is carefully designed to be consistent. Modify it if you need different scoring criteria.

7. **Testing First**: Always test with a small number of articles first to ensure everything works before processing larger batches.

## Troubleshooting

**"Module not found" errors**: Run `pip install -r requirements.txt`

**"API key not provided"**: Set the `OPENAI_API_KEY` environment variable

**"No articles found"**: Check the `max_age_days` parameter or manually create test data

**"Invalid score"**: The LLM occasionally returns text instead of a number. The script will skip these and continue.

**Rate limit errors**: Reduce the number of articles or increase the delay between API calls in the code

## What's Next?

After collecting sentiment scores, you can:

1. **Aggregate scores** by topic to see overall sentiment trends
2. **Correlate with price movements** to validate the sentiment analysis
3. **Set up alerts** for major sentiment shifts
4. **Build a dashboard** to visualize sentiment over time
5. **Compare sources** to see if certain sources are more bullish/bearish
