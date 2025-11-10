# VUTS - AI Stock News Analyzer

An AI-powered platform for fetching financial news, analyzing sentiment with LLMs, and producing actionable insights on stock outlook.

## 🎯 Overview

VUTS (Value Understanding Through Sentiment) is a complete system that:
- **Fetches** financial news from multiple sources (Google News, Bing News, Finnhub)
- **Analyzes** article sentiment using Large Language Models (OpenAI GPT)
- **Enriches** analysis with historical market data context
- **Scores** news impact from -10.00 (extremely negative) to +10.00 (extremely positive)
- **Organizes** results for easy aggregation and trend analysis

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd scratch
pip install -r requirements.txt
```

### 2. Try the Demo (No API Keys Required)

```bash
cd scratch
python demo_workflow.py
```

This creates mock data and demonstrates the complete workflow without needing any API keys.

### 3. Set Up for Real Data

```bash
# Required for sentiment analysis
export OPENAI_API_KEY="your-openai-api-key"

# Optional for news fetching
export NEWSAPI_KEY="your-newsapi-key"
export BING_NEWS_KEY="your-bing-news-key"
export FINNHUB_KEY="your-finnhub-key"
```

### 4. Run the Complete Workflow

```bash
cd scratch

# Fetch news articles
python src/fetching/financial_news_collector_async.py \
    example_data/copilot-gpt5-cfg.json output

# Fetch market data (optional but recommended)
python src/market/data_fetcher.py TSLA MSFT NVIDIA AMD \
    --output-dir output/market_data

# Analyze sentiment with LLM
python src/llm/sentiment_analyzer.py \
    --data-dir output \
    --max-articles 10 \
    --market-data-dir output/market_data

# View results
find output/llm_scores -name "*_score.json" | head -5
```

## 📚 Documentation

- **[Quick Start Guide](docs/Quick_Start_Guide.md)** - Get up and running in 5 minutes
- **[Complete Workflow Guide](docs/Workflow_Guide.md)** - Detailed usage examples and advanced features
- **[Development Outline](docs/Development_Outline.md)** - Project architecture and future plans
- **[LLM Module](scratch/src/llm/README.md)** - Sentiment analyzer documentation
- **[AI Usage Notes](chats/ai_usage_notes.md)** - Development notes and AI tool usage

## 📁 Project Structure

```
vuts/
├── docs/                          # Main documentation
│   ├── Quick_Start_Guide.md
│   ├── Workflow_Guide.md
│   └── Development_Outline.md
├── scratch/                       # Main application code
│   ├── src/
│   │   ├── fetching/             # News collection module
│   │   │   └── financial_news_collector_async.py
│   │   ├── llm/                  # LLM sentiment analysis module
│   │   │   ├── sentiment_analyzer.py
│   │   │   ├── sentiment_prompt.txt
│   │   │   └── README.md
│   │   ├── market/               # Market data module
│   │   │   └── data_fetcher.py
│   │   ├── tests/                # Test suite
│   │   │   └── test_llm_analyzer.py
│   │   └── utils/                # Shared utilities
│   ├── example_data/             # Configuration examples
│   ├── demo_workflow.py          # Interactive demo
│   └── requirements.txt          # Python dependencies
└── chats/                        # Development notes and chat logs
```

## 🔑 Key Features

✅ **Multi-Source News Fetching** - Aggregates from Google News RSS, Bing News, Finnhub  
✅ **LLM-Powered Sentiment Analysis** - Uses OpenAI GPT models for accurate scoring  
✅ **Market Context Integration** - Includes historical price data for better analysis  
✅ **Precise Scoring** - Score range from -10.00 to +10.00 with explanations  
✅ **Cost Efficient** - Uses gpt-4o-mini by default (~$0.0006 per article)  
✅ **Smart Caching** - Avoids re-analyzing articles and re-fetching data  
✅ **Async Operations** - Fast parallel processing of multiple sources  
✅ **Test Suite** - Comprehensive tests with no API keys required  

## 📊 Understanding Scores

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

## 🧪 Running Tests

```bash
cd scratch
python src/tests/test_llm_analyzer.py
```

All tests run without requiring API keys and validate:
- Prompt template loading and formatting
- LLM response parsing
- Article discovery and filtering
- Score saving and validation

## 💰 Cost Estimation

Using gpt-4o-mini (recommended):
- Input: $0.150 per 1M tokens
- Output: $0.600 per 1M tokens
- **Cost per article: ~$0.0006** (less than 1/10th of a cent)
- **10 articles: ~$0.006** (about half a cent)

## 🛠️ Technology Stack

- **Language**: Python 3.8+
- **Async I/O**: aiohttp for parallel requests
- **LLM Integration**: OpenAI API (GPT-4o-mini, GPT-4, GPT-3.5-turbo)
- **Market Data**: yfinance (Yahoo Finance)
- **Content Extraction**: BeautifulSoup4, readability-lxml
- **Testing**: Built-in unittest-style tests

## 🔮 Roadmap

See [Development Outline](docs/Development_Outline.md) for detailed plans.

Current focus areas:
- **Phase 2**: News aggregation & storage ✅
- **Phase 3**: AI-powered sentiment analysis ✅
- **Phase 4**: Scoring & recommendation engine (in progress)
- **Phase 5**: User interface (planned)
- **Phase 6**: Notifications & alerts (planned)

## 📝 License

This project is currently a research/testing tool. See LICENSE file for details.

## 🤝 Contributing

This is currently a personal project. Feel free to fork and experiment!

## ⚠️ Disclaimer

This tool is for research and educational purposes only. The sentiment scores and analysis should **not** be considered as financial advice. Always do your own research and consult with financial professionals before making investment decisions.

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Note**: This is a Work In Progress (WIP). The system is functional but may undergo significant changes as development continues.
