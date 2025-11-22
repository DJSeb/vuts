# Scoring & Recommendation Engine (Phase 4)

## Overview

The Scoring & Recommendation Engine is **Phase 4** of the VUTS project. It aggregates individual article sentiment scores and generates actionable investment recommendations (Buy/Hold/Sell) with detailed explanations.

This module builds upon Phase 3 (AI-powered sentiment analysis) by combining multiple article scores into comprehensive topic-level recommendations.

## Key Features

### 🎯 Core Capabilities

1. **Sentiment Aggregation**: Combines multiple article scores into a single topic-level score
2. **Source Reliability Weighting**: Weights scores based on source credibility
3. **Temporal Decay**: Recent news has more influence than older articles
4. **Trend Analysis**: Detects if sentiment is improving, declining, or stable
5. **Recommendation Generation**: Produces Buy/Hold/Sell signals with confidence levels
6. **Full Explainability**: Every recommendation includes detailed reasoning

### 📊 Recommendation Types

| Recommendation | Score Range | Description |
|---------------|-------------|-------------|
| **STRONG BUY** | ≥ +5.0 | Very positive sentiment, high confidence |
| **BUY** | +2.5 to +5.0 | Positive sentiment, good opportunity |
| **HOLD** | -2.5 to +2.5 | Neutral sentiment or low confidence |
| **SELL** | -5.0 to -2.5 | Negative sentiment, consider reducing |
| **STRONG SELL** | ≤ -5.0 | Very negative sentiment, high risk |

## How It Works

### 1. Score Aggregation

The engine reads individual article scores from Phase 3 and combines them using weighted averaging:

```
aggregated_score = Σ(article_score × source_weight × temporal_weight) / Σ(weights)
```

**Source Weights:**
- Finnhub: 1.0 (professional financial API)
- Bing News: 0.9 (mainstream news aggregation)
- Google News RSS: 0.85 (RSS feed aggregation)
- Unknown sources: 0.8 (default weight)

**Temporal Decay:**
- Half-life: 7 days (articles lose 50% weight after a week)
- Max age: 30 days (older articles are excluded)

### 2. Trend Analysis

Compares recent articles vs older articles to detect sentiment shifts:

- **Improving**: Recent sentiment is more positive than older sentiment
- **Declining**: Recent sentiment is more negative than older sentiment
- **Stable**: Sentiment is consistent over time

### 3. Confidence Calculation

Confidence is based on:
- **Article count**: More articles = higher confidence (up to 10 articles)
- **Recency**: More recent articles = higher confidence
- **Consistency**: Lower score variance = higher confidence

Confidence levels:
- **HIGH**: ≥ 80%
- **MEDIUM**: 60-80%
- **LOW**: < 60%

### 4. Recommendation Generation

The final recommendation considers:
1. Aggregated sentiment score
2. Confidence level (low confidence → downgrade to HOLD)
3. Trend direction
4. Score distribution (positive/negative/neutral ratio)

## Usage

### Command Line Interface

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

### Python API

```python
from scoring.recommendation_engine import (
    process_topic_recommendation,
    aggregate_scores,
    calculate_trend,
    generate_recommendation
)
from pathlib import Path

# Process a topic
score_files = list(Path("output/llm_scores/TSLA").glob("*_score.json"))
result = process_topic_recommendation(
    topic="TSLA",
    score_files=score_files,
    output_dir=Path("output/recommendations")
)

# Access recommendation details
print(result['recommendation']['recommendation'])  # e.g., "BUY"
print(result['recommendation']['reasoning'])
print(result['aggregation']['score'])  # Aggregated score
```

## Output Format

### Recommendation JSON Structure

```json
{
  "topic": "TSLA",
  "recommendation": {
    "recommendation": "BUY",
    "confidence_level": "HIGH",
    "score": 5.75,
    "reasoning": "Aggregated sentiment is positive with a score of 5.75 based on 8 article(s). Score distribution: 6 positive, 1 negative, 1 neutral (75% positive, 12% negative). Sentiment is improving (recent: 6.50, older: 4.80). Recommendation confidence is HIGH (85%) based on article count, recency, and score consistency.",
    "risk_factors": [
      "Standard investment risks apply. This is sentiment analysis, not financial advice."
    ],
    "article_count": 8,
    "trend_indicator": "↗ Improving (trend: +1.70)",
    "generated_at": "2025-11-18T13:30:00.123456+00:00"
  },
  "aggregation": {
    "score": 5.75,
    "confidence": 0.85,
    "article_count": 8,
    "weighted_count": 7.2,
    "distribution": {
      "positive": 6,
      "negative": 1,
      "neutral": 1
    }
  },
  "trend": {
    "trend": "improving",
    "trend_score": 1.70,
    "recent_avg": 6.50,
    "older_avg": 4.80,
    "description": "Sentiment is improving (recent: 6.50, older: 4.80)"
  },
  "articles": [
    {
      "title": "Tesla Reports Record Deliveries",
      "score": 6.75,
      "source": "finnhub",
      "published_at": "2025-11-18T10:30:00+00:00",
      "source_weight": 1.0,
      "temporal_weight": 0.995,
      "combined_weight": 0.995,
      "explanation": "Record deliveries exceed expectations..."
    }
    // ... more articles
  ]
}
```

## Configuration

You can customize the recommendation engine by modifying constants in `recommendation_engine.py`:

### Source Weights
```python
SOURCE_WEIGHTS = {
    'finnhub': 1.0,
    'bingnews': 0.9,
    'googlenews_rss': 0.85,
    'default': 0.8
}
```

### Recommendation Thresholds
```python
RECOMMENDATION_THRESHOLDS = {
    'strong_buy': 5.0,
    'buy': 2.5,
    'sell': -2.5,
    'strong_sell': -5.0
}
```

### Temporal Decay
```python
TEMPORAL_DECAY = {
    'half_life_days': 7,    # News loses 50% weight after 7 days
    'max_age_days': 30      # News older than 30 days is ignored
}
```

### Minimum Requirements
```python
MIN_ARTICLES = 2             # Need at least 2 articles
CONFIDENCE_THRESHOLD = 0.6   # Minimum confidence (0.0 to 1.0)
```

## Integration with Other Modules

### Input: Phase 3 (LLM Sentiment Analysis)

The recommendation engine reads score files generated by `llm/sentiment_analyzer.py`:

```
output/
└── llm_scores/
    └── TSLA/
        ├── 001_article_score.json
        ├── 002_article_score.json
        └── 003_article_score.json
```

### Output: Phase 5 (User Interface)

Recommendations are saved for consumption by the web UI:

```
output/
└── recommendations/
    ├── TSLA_recommendation.json
    ├── MSFT_recommendation.json
    └── NVIDIA_recommendation.json
```

## Complete Workflow Example

```bash
cd scratch

# Step 1: Fetch news articles (Phase 2)
./vuts fetch --config example_data/copilot-gpt5-cfg.json --output-dir output

# Step 2: Fetch market data (optional but recommended)
./vuts market TSLA MSFT NVIDIA AMD --output-dir output/market_data

# Step 3: Analyze sentiment with LLM (Phase 3)
./vuts analyze --data-dir output --max-articles 10 --market-data-dir output/market_data

# Step 4: Generate recommendations (Phase 4) - NEW!
python src/scoring/recommendation_engine.py \
    --data-dir output/llm_scores \
    --output-dir output/recommendations

# Step 5: View results
cat output/recommendations/TSLA_recommendation.json
```

## Risk Factors

The engine automatically identifies and reports risk factors:

1. **Limited Data**: Fewer than minimum required articles
2. **Low Confidence**: Confidence below threshold (60%)
3. **Mixed Signals**: Equal positive and negative articles
4. **Contradictory Trends**: Trend doesn't match recommendation
5. **Standard Risks**: Always included as reminder

## Important Notes

### ⚠️ Disclaimer

**This is NOT financial advice.** The recommendation engine provides sentiment analysis based on news articles. It does NOT:
- Consider fundamental analysis
- Account for technical indicators
- Include your personal financial situation
- Replace professional financial advice

Always:
- Do your own research
- Consult with financial professionals
- Consider your risk tolerance
- Diversify your investments

### 🔬 Experimental Nature

Phase 4 is experimental. The recommendation weights, thresholds, and formulas are based on reasonable heuristics but have not been backtested extensively. Use recommendations as one input among many in your investment research.

### 📊 Data Quality

Recommendation quality depends on:
- Number and quality of articles
- Accuracy of LLM sentiment scoring
- Diversity of news sources
- Recency of information

## Testing

Run the tests to validate the scoring module:

```bash
cd scratch
python src/tests/test_scoring_engine.py
```

Tests cover:
- Temporal decay calculations
- Score aggregation logic
- Trend analysis
- Recommendation generation
- Edge cases and error handling

## Future Enhancements

Planned improvements for Phase 4:

1. **Backtesting**: Compare recommendations to actual stock performance
2. **Dynamic Thresholds**: Adjust thresholds based on market volatility
3. **Sector Analysis**: Consider sector-specific sentiment patterns
4. **Portfolio Optimization**: Generate portfolio-level recommendations
5. **Risk Scoring**: Quantify risk beyond confidence levels
6. **Real-time Updates**: Streaming recommendations as news arrives

## Architecture

### Module Structure

```
scratch/src/scoring/
├── __init__.py                    # Module exports
├── recommendation_engine.py       # Main recommendation logic
└── README.md                      # This file
```

### Data Flow

```
[Phase 3: LLM Scores] 
    ↓
[Score Aggregation]
    ↓
[Temporal Weighting + Source Reliability]
    ↓
[Trend Analysis]
    ↓
[Recommendation Generation]
    ↓
[JSON Output with Explainability]
    ↓
[Phase 5: User Interface Display]
```

## Dependencies

The scoring module uses:
- Standard library: `json`, `math`, `datetime`, `pathlib`, `collections`
- Project utilities: `utils.datetime_utils`, `utils.file_utils`

No additional external dependencies required.

## Contributing

When modifying the recommendation engine:

1. **Document changes**: Update this README
2. **Add comments**: Follow the detailed commenting style
3. **Test thoroughly**: Run tests and demos
4. **Consider edge cases**: Handle insufficient data gracefully
5. **Maintain explainability**: Every decision should be traceable

## Version History

- **v1.0.0** (2025-11-18): Initial Phase 4 implementation
  - Sentiment aggregation with source weights
  - Temporal decay for article recency
  - Trend analysis (improving/declining/stable)
  - Buy/Hold/Sell recommendations
  - Confidence scoring
  - Full explainability and risk factors

## Support

For questions or issues:
1. Check this README
2. Review the code comments in `recommendation_engine.py`
3. Run the demo: `python demos/demo_recommendations.py`
4. Open an issue on GitHub

---

**Phase 4 Implementation Complete** ✅
Next: Phase 5 - User Interface (displaying recommendations in the web UI)
