# LLM Sentiment Analysis System - Quick Start

This system analyzes financial news articles using Large Language Models (LLMs).

## What's Included

### Core Scripts
- **`scratch/src/llm/sentiment_analyzer.py`** (14KB) - Main script that analyzes articles using OpenAI API
- **`scratch/src/market/data_fetcher.py`** (9.7KB) - Fetches historical stock data from Yahoo Finance
- **`scratch/src/llm/sentiment_prompt.txt`** (2.2KB) - Reusable prompt template for consistent LLM scoring

### Testing & Demo
- **`scratch/src/tests/test_llm_analyzer.py`** (8.7KB) - Test suite for validation
- **`scratch/demos/demo_workflow.py`** (12KB) - Mock workflow demo (no API keys required)
- **`scratch/demos/demo_openai_api.py`** (31KB) - OpenAI API demo with AMD/Nvidia/Broadcom articles

### Documentation
- **`docs/Workflow_Guide.md`** (8.4KB) - Complete usage guide with examples
- **`scratch/src/llm/README.md`** (3.9KB) - LLM analyzer documentation

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
cd scratch
pip install -r requirements.txt
```

### 2. Try the Demos

**Demo 1: Mock Workflow (No API Keys Needed)**
```bash
cd scratch
python demos/demo_workflow.py
```

This creates mock articles and demonstrates the complete workflow.

**Demo 2: OpenAI API (Requires API Key)**
```bash
cd scratch
export OPENAI_API_KEY="your-key-here"
python demos/demo_openai_api.py
```

This generates and analyzes articles about AMD, Nvidia, and Broadcom using the real OpenAI API.
Estimated cost: ~$0.01 (less than 2 cents).

### 3. Run with Real Data

#### Set API Key
```bash
export OPENAI_API_KEY="your-key-here"
```

#### Fetch News Articles
```bash
cd scratch
python src/fetching/financial_news_collector_async.py \
    example_data/copilot-gpt5-cfg.json \
    output
```

#### Fetch Market Data (Optional)
```bash
cd scratch
python src/market/data_fetcher.py TSLA MSFT NVIDIA AMD \
    --output-dir output/market_data
```

#### Analyze Sentiment
```bash
cd scratch
python src/llm/sentiment_analyzer.py \
    --data-dir output \
    --max-articles 10 \
    --max-age-days 1 \
    --market-data-dir output/market_data
```

#### View Results

**Using Web UI (Recommended):**
```bash
cd scratch
../vuts ui
# Then open http://localhost:5000 in your browser
```

**Using Command Line:**
```bash
find output/llm_scores -name "*_score.json" | head -3
```

## Key Features

✅ **LLM-Powered Analysis** - Uses OpenAI GPT models for sentiment scoring  
✅ **Score Range: -10.00 to +10.00** - Precise sentiment measurement  
✅ **Market Context** - Includes historical price data for better analysis  
✅ **Consistent Scoring** - Carefully designed prompt reduces "LLM moods"  
✅ **Cost Efficient** - Uses gpt-4o-mini by default (~$0.15 per 1M tokens)  
✅ **Privacy Focused** - No training on your data, temporary chats only  
✅ **Organized Output** - Results stored in `llm_scores/{topic}/` directories  
✅ **Smart Caching** - Skips already-analyzed articles  

## Understanding the Scores

| Score Range | Meaning | Example |
|------------|---------|---------|
| +7 to +10 | Extremely Positive | Major breakthrough, transformative success |
| +4 to +7 | Very Positive | Beat earnings, upgrades, major wins |
| +2 to +4 | Moderately Positive | Good results, positive developments |
| +0.5 to +2 | Slightly Positive | Minor improvements, optimistic tone |
| -0.5 to +0.5 | Neutral | Balanced reporting, no clear direction |
| -2 to -0.5 | Slightly Negative | Minor concerns, cautious outlook |
| -4 to -2 | Moderately Negative | Concerns, warnings, setbacks |
| -7 to -4 | Very Negative | Missed earnings, downgrades, major losses |
| -10 to -7 | Extremely Negative | Bankruptcy, fraud, catastrophic failure |

## Example Output

```json
{
  "article_file": "output/googlenews_rss/TSLA/001_2024-11-10.json",
  "topic": "TSLA",
  "source": "googlenews_rss",
  "title": "Tesla Reports Strong Q4 Earnings",
  "url": "https://example.com/article",
  "published_at": "2024-11-10T12:00:00+00:00",
  "llm_score": 6.75,
  "llm_explanation": "Strong Q4 earnings beat. Revenue up 25% YoY. Raised guidance for next quarter. Analyst upgrades following announcement.",
  "model": "gpt-4o-mini",
  "scored_at": "2024-11-10T18:30:00+00:00"
}
```

**Note**: Each score now includes an `llm_explanation` field with a brief explanation (keywords or up to 5 sentences) of why the LLM assigned that score. This makes results more interpretable and useful for creating reports and timelines.

## Configuration Options

### LLM Analyzer
- `--max-articles` - Limit number of articles (default: 10)
- `--max-age-days` - Article age filter (default: 1 day)
- `--model` - OpenAI model (default: gpt-4o-mini)
- `--market-data-dir` - Include market context (optional)

### Market Data Fetcher
- `--days` - Historical period (default: 30 days)
- `--use-cache` - Reuse data < 24h old
- `--show-context` - Display formatted context

## Cost Estimation

Using gpt-4o-mini (recommended):
- Input: $0.150 per 1M tokens
- Output: $0.600 per 1M tokens
- Typical article analysis: ~4,000 input tokens, ~10 output tokens
- **Cost per article: ~$0.0006 (less than 1 cent)**
- **10 articles: ~$0.006 (half a cent)**

## Troubleshooting

**No articles found?**
- Check `--max-age-days` parameter
- Verify articles have `content` field
- Run demo to test: `python demos/demo_workflow.py`

**API errors?**
- Verify `OPENAI_API_KEY` is set
- Check API rate limits
- Try reducing `--max-articles`

**Invalid scores?**
- LLM occasionally returns text instead of numbers
- Script automatically skips these and continues
- Check prompt file hasn't been modified

## Next Steps

1. **Read** `docs/Workflow_Guide.md` for detailed examples
2. **Run** `cd scratch && python demos/demo_workflow.py` to see it in action
3. **Test** with 1-2 real articles first
4. **Scale** up to larger batches once validated

## Support & Documentation

- Main Guide: `docs/Workflow_Guide.md`
- LLM Details: `scratch/src/llm/README.md`
- Test Suite: `cd scratch && python src/tests/test_llm_analyzer.py`
- Demos: `cd scratch && python demos/demo_workflow.py` or `python demos/demo_openai_api.py`

---

**Created:** 2024-11-10  
**Purpose:** Testing LLM effectiveness for financial sentiment analysis  
**Note:** This is a research/testing tool, not production-ready investment advice
