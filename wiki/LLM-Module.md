# LLM Module

The LLM module analyzes financial news sentiment using Large Language Models.

## Overview

**Location**: `scratch/src/llm/`

The LLM module provides:
- Sentiment scoring from -10.00 to +10.00
- Detailed explanations for each score
- Optional market context integration
- Cost-efficient processing
- Automatic caching to avoid re-analysis

## Main Script

### `sentiment_analyzer.py`

Analyzes articles using OpenAI's GPT models.

**Usage:**
```bash
cd scratch
python src/llm/sentiment_analyzer.py --data-dir <directory> [options]
```

**Example:**
```bash
python src/llm/sentiment_analyzer.py \
    --data-dir output \
    --max-articles 10 \
    --max-age-days 1 \
    --market-data-dir output/market_data
```

## Command-Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--data-dir` | `.` | Directory containing article JSON files |
| `--prompt-file` | `sentiment_prompt.txt` | Path to prompt template |
| `--max-age-days` | 1 | Only process articles this recent |
| `--max-articles` | 10 | Maximum number to analyze |
| `--model` | `gpt-4o-mini` | OpenAI model to use |
| `--market-data-dir` | None | Directory with market data for context |
| `--api-key` | env var | OpenAI API key |

## Models

### Recommended: gpt-4o-mini
- **Cost**: $0.150 per 1M input tokens, $0.600 per 1M output
- **Speed**: Fast (~1-2 seconds per article)
- **Quality**: Good for sentiment analysis
- **Cost per article**: ~$0.0006

### Alternative: gpt-4o
- **Cost**: $2.50 per 1M input tokens, $10.00 per 1M output
- **Speed**: Moderate (~2-4 seconds per article)
- **Quality**: Excellent, most accurate
- **Cost per article**: ~$0.01

### Alternative: gpt-3.5-turbo
- **Cost**: $0.50 per 1M input tokens, $1.50 per 1M output
- **Speed**: Very fast (<1 second per article)
- **Quality**: Acceptable for basic analysis
- **Cost per article**: ~$0.002

## Sentiment Prompt

The module uses a carefully designed prompt (`sentiment_prompt.txt`) that:
- Provides clear scoring guidelines
- Reduces "LLM mood" variance
- Requests specific explanations
- Uses consistent temperature (0.3)

### Prompt Template Structure

```
You are a financial sentiment analysis expert...

ARTICLE INFORMATION:
Title: {title}
Topic: {topic}
Content: {content}

SCORING GUIDELINES:
- Score between -10.00 and +10.00
- Negative = bearish, Positive = bullish
...

OUTPUT FORMAT:
SCORE: [number]
EXPLANATION: [brief explanation]
```

## Scoring Scale

| Range | Meaning | Example |
|-------|---------|---------|
| +7 to +10 | Extremely Positive | Major breakthrough, transformative success |
| +4 to +7 | Very Positive | Beat earnings, analyst upgrades |
| +2 to +4 | Moderately Positive | Good results, positive developments |
| +0.5 to +2 | Slightly Positive | Minor improvements, optimistic tone |
| -0.5 to +0.5 | Neutral | Balanced reporting |
| -2 to -0.5 | Slightly Negative | Minor concerns, caution |
| -4 to -2 | Moderately Negative | Concerns, warnings, setbacks |
| -7 to -4 | Very Negative | Missed earnings, downgrades |
| -10 to -7 | Extremely Negative | Bankruptcy, fraud, catastrophic failure |

## Market Context

When `--market-data-dir` is provided, the analyzer includes:
- Recent price performance
- Price change percentage
- Period high/low
- Trading volume
- Daily price history

This context helps the LLM better evaluate news impact.

**Example context:**
```
MARKET CONTEXT FOR TSLA (Tesla, Inc.):

Recent Performance (30 days):
- Current Price: $242.50
- Price Change: up 10.86%
- Period High: $248.30
- Period Low: $215.20

Recent Daily Closes:
  2024-11-04: $223.80
  2024-11-05: $226.50
  ...
```

## Output Structure

Scores are saved in:
```
output/
└── llm_scores/
    ├── TSLA/
    │   ├── 001_2024-11-10_score.json
    │   ├── 002_2024-11-10_score.json
    │   └── ...
    ├── MSFT/
    └── ...
```

### Score File Format

```json
{
  "article_file": "output/googlenews_rss/TSLA/001_2024-11-10.json",
  "topic": "TSLA",
  "source": "googlenews_rss",
  "title": "Tesla Reports Strong Q4 Earnings",
  "url": "https://example.com/article",
  "published_at": "2024-11-10T12:00:00+00:00",
  "llm_score": 6.75,
  "llm_explanation": "Strong Q4 earnings beat. Revenue up 25% YoY. Raised guidance. Positive analyst response.",
  "model": "gpt-4o-mini",
  "scored_at": "2024-11-10T18:30:00+00:00"
}
```

## Key Features

### Caching
The analyzer automatically skips articles that already have scores, saving API costs.

### Explanation Field
Each score includes a brief explanation (keywords or up to 5 sentences) explaining the reasoning.

### Error Handling
- Invalid scores (out of range) are rejected
- Failed API calls are logged and skipped
- Rate limiting respected with 1-second delays

### Validation
Scores are validated to be:
- Numeric (not text)
- Within range [-10.00, +10.00]
- Formatted with 2 decimal places

## API Configuration

### Setting API Key

```bash
export OPENAI_API_KEY="sk-..."
```

Or pass directly:
```bash
python src/llm/sentiment_analyzer.py --api-key "sk-..." ...
```

### API Settings

The analyzer uses:
- Temperature: 0.3 (for consistency)
- Max tokens: ~100 (for score + explanation)
- Response format: Text (parsed for SCORE and EXPLANATION)

## Cost Management

### Tips for Reducing Costs

1. **Use gpt-4o-mini** (default): Cheapest option with good quality
2. **Limit articles**: Use `--max-articles` to process batches
3. **Filter by age**: Use `--max-age-days 1` for recent articles only
4. **Cache results**: Already-scored articles are skipped automatically
5. **Test first**: Run demo or process 1-2 articles before large batches

### Cost Calculator

For gpt-4o-mini:
- 10 articles: ~$0.006 (half a cent)
- 100 articles: ~$0.06 (six cents)
- 1000 articles: ~$0.60 (sixty cents)

## Workflow Integration

Typical workflow:
1. Fetch articles with [Fetching Module](Fetching-Module)
2. Optionally fetch market data with [Market Module](Market-Module)
3. Run sentiment analysis (this module)
4. Aggregate/visualize results

## Testing

Run the test suite:
```bash
cd scratch
python src/tests/test_llm_analyzer.py
```

Tests verify:
- Prompt loading and formatting
- Response parsing
- Article discovery
- Score validation
- File saving

## Troubleshooting

**"API key not provided"**
- Set `OPENAI_API_KEY` environment variable
- Or use `--api-key` option

**"Invalid score"**
- LLM occasionally returns text instead of number
- Script automatically skips these
- Try adjusting prompt if frequent

**Rate limit errors**
- Reduce `--max-articles`
- Increase delay in code (currently 1 second)
- Check OpenAI account limits

**"No articles found"**
- Check `--max-age-days` parameter
- Verify articles have `content` field
- Run demo to test setup

## See Also

- [Fetching Module](Fetching-Module) - For article collection
- [Market Module](Market-Module) - For market context
- [Utilities Module](Utilities-Module) - Shared functions
- [Getting Started](Getting-Started) - Setup guide
