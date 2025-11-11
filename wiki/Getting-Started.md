# Getting Started

This guide will help you get VUTS up and running in just a few minutes.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- OpenAI API key (for sentiment analysis)
- Optional: NewsAPI, Bing News, or Finnhub API keys (for news fetching)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/DJSeb/vuts.git
cd vuts/scratch
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `openai` - OpenAI API client
- `yfinance` - Yahoo Finance data
- `aiohttp` - Async HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML processing

### 3. Set Up API Keys

```bash
# Required for sentiment analysis
export OPENAI_API_KEY="your-openai-api-key"

# Optional for news fetching
export NEWSAPI_KEY="your-newsapi-key"
export BING_NEWS_KEY="your-bing-news-key"
export FINNHUB_KEY="your-finnhub-key"
```

## First Run - Try the Demo

The easiest way to verify your setup is to run the demo, which doesn't require any API keys:

```bash
cd scratch
python demo_workflow.py
```

This will:
- Create mock news articles
- Generate simulated market data
- Demonstrate the sentiment analysis workflow
- Show you example outputs

## Running with Real Data

### Step 1: Fetch News Articles

```bash
cd scratch
python src/fetching/financial_news_collector_async.py \
    example_data/copilot-gpt5-cfg.json \
    output
```

This fetches articles about TSLA, MSFT, NVIDIA, and AMD from multiple sources.

### Step 2: Fetch Market Data (Optional but Recommended)

```bash
python src/market/data_fetcher.py TSLA MSFT NVIDIA AMD \
    --output-dir output/market_data
```

This provides historical price context to improve sentiment analysis.

### Step 3: Analyze Sentiment

```bash
python src/llm/sentiment_analyzer.py \
    --data-dir output \
    --max-articles 10 \
    --market-data-dir output/market_data
```

### Step 4: View Results

**Using Web UI (Recommended):**
```bash
../vuts ui
# Then open http://localhost:5000 in your browser
```

**Using Command Line:**
```bash
# List all scores
find output/llm_scores -name "*_score.json"

# View a specific score with formatting
cat output/llm_scores/TSLA/001_*_score.json | python -m json.tool
```

## Understanding the Output

Each analyzed article produces a score file with:

```json
{
  "topic": "TSLA",
  "title": "Tesla Reports Strong Q4 Earnings",
  "llm_score": 6.75,
  "llm_explanation": "Strong earnings beat. Revenue up 25% YoY...",
  "model": "gpt-4o-mini",
  "scored_at": "2024-11-10T18:30:00+00:00"
}
```

### Score Interpretation

| Range | Meaning |
|-------|---------|
| +7 to +10 | Extremely Positive |
| +4 to +7 | Very Positive |
| +2 to +4 | Moderately Positive |
| +0.5 to +2 | Slightly Positive |
| -0.5 to +0.5 | Neutral |
| -2 to -0.5 | Slightly Negative |
| -4 to -2 | Moderately Negative |
| -7 to -4 | Very Negative |
| -10 to -7 | Extremely Negative |

## Next Steps

- Read the [Complete Workflow Guide](../docs/Workflow_Guide.md) for advanced features
- Explore the [Fetching Module](Fetching-Module) documentation
- Learn about [LLM Module](LLM-Module) configuration options
- Review the [Architecture](Architecture) to understand system design

## Troubleshooting

**"Module not found" errors**: Run `pip install -r requirements.txt`

**"API key not provided"**: Set the `OPENAI_API_KEY` environment variable

**"No articles found"**: Check the `max_age_days` parameter or run the demo first

**Rate limit errors**: Reduce `--max-articles` or increase delays in the code

## Cost Estimation

Using gpt-4o-mini (recommended):
- **Cost per article**: ~$0.0006 (less than 1/10th of a cent)
- **10 articles**: ~$0.006 (about half a cent)
- **100 articles**: ~$0.06 (six cents)

## Support

For questions or issues, please open an issue on GitHub.
