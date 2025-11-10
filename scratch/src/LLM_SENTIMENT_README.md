# LLM Sentiment Analyzer

This script analyzes financial news articles using Large Language Models (LLMs) to provide sentiment scores.

## Overview

The `llm_sentiment_analyzer.py` script reads articles collected by `financial_news_collector_async.py` and sends them to an LLM (OpenAI API) for sentiment analysis. The LLM returns a score between -10.00 and +10.00 indicating the sentiment impact on investor perception.

## Prerequisites

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Basic Usage

From the `scratch` directory:

```bash
python src/llm_sentiment_analyzer.py --data-dir .
```

### With Custom Configuration

```bash
python src/llm_sentiment_analyzer.py \
    --data-dir . \
    --max-age-days 1 \
    --max-articles 10 \
    --model gpt-4o-mini \
    --prompt-file src/llm_sentiment_prompt.txt
```

### Arguments

- `--data-dir`: Base directory containing fetched article data (default: current directory)
- `--prompt-file`: Path to the LLM prompt template file (default: llm_sentiment_prompt.txt)
- `--max-age-days`: Maximum age of articles to process in days (default: 1)
- `--max-articles`: Maximum number of articles to process (default: 10)
- `--model`: OpenAI model to use (default: gpt-4o-mini)
- `--api-key`: OpenAI API key (default: read from OPENAI_API_KEY env var)

## How It Works

1. **Article Discovery**: Scans the data directory for JSON article files
2. **Filtering**: Only processes articles up to `max-age-days` old
3. **Prompt Formation**: Fills in the prompt template with article data
4. **LLM Analysis**: Sends each article to the OpenAI API for sentiment analysis
5. **Score Validation**: Validates the returned score is between -10.00 and +10.00
6. **Storage**: Saves scores to `llm_scores/{topic}/{article}_score.json`

## Output Structure

Scores are saved in the following structure:
```
llm_scores/
├── TSLA/
│   ├── 001_2024-11-10_score.json
│   └── 002_2024-11-10_score.json
├── MSFT/
│   └── 001_2024-11-10_score.json
└── ...
```

Each score file contains:
```json
{
  "article_file": "path/to/original/article.json",
  "topic": "TSLA",
  "source": "googlenews_rss",
  "title": "Article Title",
  "url": "https://...",
  "published_at": "2024-11-10T12:00:00+00:00",
  "llm_score": -3.50,
  "llm_explanation": "Missed earnings guidance. Revenue below analyst expectations. Management cautious on Q4 outlook.",
  "model": "gpt-4o-mini",
  "scored_at": "2024-11-10T18:30:00+00:00"
}
```

The `llm_explanation` field provides a brief explanation (keywords or up to 5 sentences) of why the LLM assigned that particular score. This is useful for:
- Understanding the reasoning behind each score
- Creating reports and timelines
- Testing whether articles were parsed correctly
- Human-friendly result interpretation

## Scoring Scale

- **-10.00 to -7.00**: Extremely negative (bankruptcy, major fraud, catastrophic failure)
- **-6.99 to -4.00**: Very negative (missed earnings, downgrades, significant losses)
- **-3.99 to -2.00**: Moderately negative (concerns, warnings, minor setbacks)
- **-1.99 to -0.50**: Slightly negative (minor concerns, cautious outlook)
- **-0.49 to +0.49**: Neutral (balanced reporting, no clear direction)
- **+0.50 to +1.99**: Slightly positive (minor improvements, optimistic tone)
- **+2.00 to +3.99**: Moderately positive (good results, positive developments)
- **+4.00 to +6.99**: Very positive (beat earnings, upgrades, major wins)
- **+7.00 to +10.00**: Extremely positive (transformative success, major breakthroughs)

## Example Workflow

1. First, fetch articles using the news collector:
```bash
cd scratch
python src/fetching/financial_news_collector_async.py example_data/copilot-gpt5-cfg.json output
```

2. Then analyze them with LLM:
```bash
python src/llm_sentiment_analyzer.py --data-dir output --max-articles 10
```

3. View the results:
```bash
find output/llm_scores -name "*_score.json" -exec cat {} \;
```

## Notes

- The script uses `gpt-4o-mini` by default for cost efficiency
- A small delay (1 second) is added between API calls to avoid rate limiting
- Articles already scored are automatically skipped
- The prompt is designed to be consistent and minimize "LLM moods"
- Lower temperature (0.3) is used for more consistent scoring
