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

## Complete Workflow (All Phases)

### Step 1: Fetch News Articles (Phase 2)

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

### Step 3: Analyze Sentiment with LLM (Phase 3)

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

### Step 4: Generate Investment Recommendations (Phase 4)

After sentiment analysis, generate actionable investment recommendations:

```bash
cd scratch

# Generate recommendations for all topics
python src/scoring/recommendation_engine.py \
    --data-dir output/llm_scores \
    --output-dir output/recommendations

# Process a specific topic only
python src/scoring/recommendation_engine.py \
    --data-dir output/llm_scores \
    --output-dir output/recommendations \
    --topic TSLA
```

This will:
- Aggregate multiple article scores for each topic
- Apply source reliability weighting (Finnhub: 1.0, Bing: 0.9, Google RSS: 0.85)
- Apply temporal decay (7-day half-life, recent news matters more)
- Detect sentiment trends (improving/declining/stable)
- Generate Buy/Hold/Sell recommendations with confidence levels
- Provide detailed reasoning and risk factors
- Save results to `output/recommendations/{topic}_recommendation.json`

**Recommendation Thresholds:**
- **STRONG BUY**: Aggregated score ≥ +5.0 (very positive sentiment)
- **BUY**: Score +2.5 to +5.0 (positive sentiment)
- **HOLD**: Score -2.5 to +2.5 (neutral or low confidence)
- **SELL**: Score -5.0 to -2.5 (negative sentiment)
- **STRONG SELL**: Score ≤ -5.0 (very negative sentiment)

View recommendation results:
```bash
# View a specific recommendation
cat output/recommendations/TSLA_recommendation.json

# View all recommendations
find output/recommendations -name "*_recommendation.json" -exec echo "---" \; -exec jq '{topic, recommendation: .recommendation.recommendation, score: .recommendation.score, confidence: .recommendation.confidence_level}' {} \;
```

### Step 5: View Results

#### Option 1: Using the Web UI (Recommended - Phase 5)

Launch the web interface to view and explore sentiment analysis results:

```bash
cd scratch

# Using vuts command
../vuts ui

# With custom port
../vuts ui --port 8080

# With debug mode (auto-reload on changes)
../vuts ui --debug

# With custom data directory
../vuts ui --data-dir /path/to/data

# Allow external connections
../vuts ui --host 0.0.0.0 --port 5000
```

Then open your browser to `http://localhost:5000` (or your specified port) to:
- View all topics and sentiment trends on the reports dashboard
- Browse detailed article analysis at `/reports/topics`
- View notifications for extreme sentiment changes at the notification bell icon
- Manage configurations and workflow commands at `/config`
- Access JSON API endpoints at `/api/topics`

#### Option 2: Using Command Line

Check the sentiment scores and recommendations directly:

```bash
# List all score files
find output/llm_scores -name "*_score.json"

# View a specific score
cat output/llm_scores/TSLA/001_2024-11-10_score.json

# View all scores in a formatted way
find output/llm_scores -name "*_score.json" -exec echo "---" \; -exec jq '{topic, title, llm_score, llm_explanation}' {} \;

# View recommendations
cat output/recommendations/TSLA_recommendation.json | jq '{topic, recommendation: .recommendation.recommendation, score: .recommendation.score, reasoning: .recommendation.reasoning}'
```

Example score output structure:
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

Example recommendation output structure:
```json
{
  "topic": "TSLA",
  "recommendation": {
    "recommendation": "BUY",
    "confidence_level": "HIGH",
    "score": 5.75,
    "reasoning": "Aggregated sentiment is positive with a score of 5.75 based on 8 article(s)...",
    "trend_indicator": "↗ Improving (trend: +1.70)"
  }
}
```

### Step 6: Set Up Notifications (Phase 6)

Configure the notification system to receive alerts for significant sentiment changes:

```bash
cd scratch

# Run the notification demo to see how it works
python demos/demo_notifications.py

# Notifications are automatically created when sentiment scores exceed thresholds:
# - Scores ≥ +7.0: SUCCESS notification (positive sentiment)
# - Scores ≤ -7.0: CRITICAL notification (negative sentiment)
```

**Using Notifications in the Web UI:**

1. Launch the web UI: `../vuts ui`
2. Open http://localhost:5000
3. Click the 🔔 bell icon in the navigation bar to view notifications
4. Browser notifications with sound alerts are enabled automatically
5. Mark notifications as read or subscribe phone numbers for SMS alerts

**API Endpoints for Notifications:**
```bash
# Get all notifications
curl http://localhost:5000/api/notifications

# Get unread notifications
curl http://localhost:5000/api/notifications/unread

# Mark a notification as read
curl -X POST http://localhost:5000/api/notifications/<id>/mark-read

# Subscribe phone number for SMS alerts
curl -X POST http://localhost:5000/api/notifications/subscribe \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890", "topics": ["TSLA", "MSFT"], "min_severity": "warning"}'

# Get subscriptions
curl http://localhost:5000/api/notifications/subscriptions
```

**Notification Severity Levels:**
- **info**: General updates (blue)
- **success**: Positive events like extremely positive sentiment (green)
- **warning**: Concerning events or negative trends (orange)
- **critical**: Urgent issues like extremely negative sentiment (red)

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
# Complete daily analysis workflow including all phases

# Phase 2: Fetch news
python src/fetching/financial_news_collector_async.py example_data/copilot-gpt5-cfg.json output

# Fetch market data
python src/market/data_fetcher.py TSLA MSFT NVIDIA AMD --output-dir output/market_data --use-cache

# Phase 3: Analyze sentiment
python src/llm/sentiment_analyzer.py --data-dir output --max-age-days 1 --max-articles 10 --market-data-dir output/market_data

# Phase 4: Generate recommendations
python src/scoring/recommendation_engine.py --data-dir output/llm_scores --output-dir output/recommendations

# Display summary
echo "=== Analysis Complete ==="
echo "Sentiment scores: $(find output/llm_scores -name "*_score.json" | wc -l) articles"
echo "Recommendations: $(find output/recommendations -name "*_recommendation.json" | wc -l) topics"
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

## Current System Capabilities

The system now includes all major phases:

1. **Phase 2 - News Aggregation** ✅: Multi-source news fetching with content extraction
2. **Phase 3 - AI Analysis** ✅: LLM-powered sentiment scoring with market context
3. **Phase 4 - Scoring & Recommendations** ✅: Investment recommendations with explainability
4. **Phase 5 - User Interface** ✅: Web-based dashboard for viewing results
5. **Phase 6 - Notifications** ✅: Real-time alerts for significant sentiment changes

## What's Next?

After setting up the complete workflow, you can:

1. **Monitor Sentiment Trends**: Use the web UI to track sentiment changes over time
2. **Validate with Price Movements**: Compare recommendations with actual stock performance
3. **Customize Thresholds**: Adjust scoring and notification thresholds in the code
4. **Expand Coverage**: Add more topics and news sources to your configuration
5. **Automate Analysis**: Set up scheduled jobs for continuous monitoring
6. **Integrate Notifications**: Connect phone subscriptions to SMS/webhook services
7. **Export Reports**: Use API endpoints to generate custom reports
8. **Backtest Recommendations**: Analyze historical accuracy of sentiment-based signals
