# VUTS - Quick Start Guide

Complete guide to get started with the AI-powered stock sentiment analysis system, including all phases from news fetching to investment recommendations.

## What's Included

### Complete System (All Phases)
- **Phase 2: News Aggregation** - Multi-source news fetching with content extraction
- **Phase 3: Sentiment Analysis** - LLM-powered scoring from -10.00 to +10.00
- **Phase 4: Recommendation Engine** - Buy/Hold/Sell signals with confidence levels
- **Phase 5: Web UI** - Browser-based dashboard for viewing results
- **Phase 6: Notifications** - Real-time alerts for extreme sentiment changes

### Core Scripts
### Core Scripts
- **`scratch/src/fetching/financial_news_collector_async.py`** - Async news fetching from multiple sources (Phase 2)
- **`scratch/src/llm/sentiment_analyzer.py`** - Main script that analyzes articles using OpenAI API (Phase 3)
- **`scratch/src/scoring/recommendation_engine.py`** - Generates investment recommendations (Phase 4)
- **`scratch/src/ui/app.py`** - Flask web UI for viewing results (Phase 5)
- **`scratch/src/notifications/notification_manager.py`** - Alert system for sentiment changes (Phase 6)
- **`scratch/src/market/data_fetcher.py`** - Fetches historical stock data from Yahoo Finance
- **`scratch/src/llm/sentiment_prompt.txt`** - Reusable prompt template for consistent LLM scoring

### Testing & Demo
- **`scratch/src/tests/test_llm_analyzer.py`** - LLM analyzer test suite
- **`scratch/src/tests/test_scoring_engine.py`** - Recommendation engine tests (Phase 4)
- **`scratch/src/tests/test_notifications.py`** - Notification system tests (Phase 6)
- **`scratch/demos/demo_workflow.py`** - Mock workflow demo (no API keys required)
- **`scratch/demos/demo_openai_api.py`** - OpenAI API demo with real sentiment analysis
- **`scratch/demos/demo_recommendations.py`** - Recommendation engine demo (Phase 4)
- **`scratch/demos/demo_notifications.py`** - Notification system demo (Phase 6)

### Documentation
- **`docs/Workflow_Guide.md`** - Complete usage guide with all phases
- **`docs/Development_Outline.md`** - Project phases and architecture
- **`scratch/src/llm/README.md`** - LLM analyzer documentation (Phase 3)
- **`scratch/src/scoring/README.md`** - Recommendation engine documentation (Phase 4)
- **`scratch/src/ui/README.md`** - Web UI documentation (Phase 5)
- **`scratch/src/notifications/README.md`** - Notification system documentation (Phase 6)

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

**Using Web UI (Recommended - Phase 5):**
```bash
cd scratch
../vuts ui
# Then open http://localhost:5000 in your browser
```

The web UI provides:
- 📊 Reports dashboard with sentiment trends
- 📈 Detailed topics view at `/reports/topics`
- 🔔 Notifications for extreme sentiment changes
- ⚙️ Configuration management at `/config`

**Using Command Line:**
```bash
# View sentiment scores
find output/llm_scores -name "*_score.json" | head -3

# View a specific score
cat output/llm_scores/TSLA/001_article_score.json
```

### 4. Generate Investment Recommendations (Phase 4)

After sentiment analysis, generate actionable buy/hold/sell recommendations:

```bash
cd scratch

# Generate recommendations for all topics
python src/scoring/recommendation_engine.py \
    --data-dir output/llm_scores \
    --output-dir output/recommendations

# View recommendations
cat output/recommendations/TSLA_recommendation.json
```

This aggregates multiple article scores with:
- Source reliability weighting
- Temporal decay (recent news matters more)
- Trend analysis (improving/declining/stable)
- Confidence levels (HIGH/MEDIUM/LOW)
- Buy/Hold/Sell signals with detailed reasoning

### 5. Enable Notifications (Phase 6)

The notification system automatically alerts you to extreme sentiment changes:

```bash
cd scratch

# Run notification demo
python demos/demo_notifications.py

# Start UI to see notifications
../vuts ui
# Click the 🔔 bell icon to view alerts
```

Notifications are created automatically when:
- Sentiment score ≥ +7.0 (extremely positive)
- Sentiment score ≤ -7.0 (extremely negative)

## Key Features

✅ **LLM-Powered Analysis** - Uses OpenAI GPT models for sentiment scoring  
✅ **Score Range: -10.00 to +10.00** - Precise sentiment measurement  
✅ **Investment Recommendations** - Buy/Hold/Sell signals with confidence levels (Phase 4)  
✅ **Source Reliability Weighting** - Professional sources weighted higher in recommendations  
✅ **Temporal Decay** - Recent news matters more with exponential time-based decay  
✅ **Trend Analysis** - Detects improving/declining/stable sentiment patterns  
✅ **Market Context** - Includes historical price data for better analysis  
✅ **Web UI Dashboard** - Browser-based interface for viewing results (Phase 5)  
✅ **Notification System** - Real-time alerts for extreme sentiment changes (Phase 6)  
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

1. **Complete the Workflow** - Follow all phases from fetching to recommendations
2. **Read** `docs/Workflow_Guide.md` for detailed examples of all phases
3. **Try Demos**:
   - `demos/demo_workflow.py` - Mock workflow (no API keys)
   - `demos/demo_openai_api.py` - Real sentiment analysis
   - `demos/demo_recommendations.py` - Phase 4 recommendation engine
   - `demos/demo_notifications.py` - Phase 6 notification system
4. **Launch Web UI** - `../vuts ui` to browse results visually
5. **Test** with 1-2 real articles first
6. **Scale** up to larger batches once validated

## Support & Documentation

- **Complete Workflow**: `docs/Workflow_Guide.md` (includes all phases)
- **Development Roadmap**: `docs/Development_Outline.md` (phase details)
- **Module Documentation**:
  - LLM Module: `scratch/src/llm/README.md`
  - Scoring Module: `scratch/src/scoring/README.md` (Phase 4)
  - UI Module: `scratch/src/ui/README.md` (Phase 5)
  - Notifications: `scratch/src/notifications/README.md` (Phase 6)
- **Test Suite**: `cd scratch && python src/tests/test_llm_analyzer.py`
- **Architecture**: `docs/Architecture_Diagrams.md` (system visualizations)

---

**Created:** 2024-11-10  
**Purpose:** Testing LLM effectiveness for financial sentiment analysis  
**Note:** This is a research/testing tool, not production-ready investment advice
