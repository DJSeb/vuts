# VUTS - AI Stock News Analyzer

An AI-powered platform for fetching financial news, analyzing sentiment with LLMs, and producing actionable insights on stock outlook.

## 🎯 Overview

VUTS (Value Understanding Through Sentiment) is a complete system that:
- **Fetches** financial news from multiple sources (Google News, Bing News, Finnhub)
- **Analyzes** article sentiment using Large Language Models (OpenAI GPT)
- **Enriches** analysis with historical market data context
- **Scores** news impact from -10.00 (extremely negative) to +10.00 (extremely positive)
- **Organizes** results for easy aggregation and trend analysis

### System Architecture

```mermaid
graph LR
    A[News Sources] -->|Articles| B[Fetching Module]
    C[Yahoo Finance] -->|Market Data| D[Market Module]
    B -->|Articles JSON| E[LLM Module]
    D -->|Context| E
    E -->|Scores -10 to +10| F[Output]
    
    style A fill:#e1f5ff
    style C fill:#e1f5ff
    style B fill:#ffe1f5
    style D fill:#ffe1f5
    style E fill:#ffe1f5
    style F fill:#f5ffe1
```

_See [System State Flow](docs/System_State_Flow.md) for complete pipeline visualization and [Architecture Diagrams](docs/Architecture_Diagrams.md) for detailed system diagrams._

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd scratch
pip install -r requirements.txt
```

### 2. Try the Demos

**Demo 1: Real World Large-Scale Demo (No API Keys Required)** ⭐ RECOMMENDED
```bash
cd scratch
python demos/demo_real_world.py
```

Comprehensive demonstration with 12 companies and 224 articles showcasing the system at scale. Includes diverse writing styles, sentiments, and complete workflow from articles through recommendations.

**Demo 2: Mock Workflow (No API Keys Required)**
```bash
cd scratch
python demos/demo_workflow.py
```

This creates mock data and demonstrates the complete workflow without needing any API keys.

**Demo 3: OpenAI API Demo (Requires OpenAI API Key)**
```bash
cd scratch
export OPENAI_API_KEY="your-openai-api-key"
python demos/demo_openai_api.py
```

This generates articles about AMD, Nvidia, and Broadcom, then analyzes them using the OpenAI API.
Estimated cost: ~$0.01 (less than 2 cents for all articles).

**Demo 4: Recommendation Engine Demo (No API Keys Required)**
```bash
cd scratch
python demos/demo_recommendations.py
```

Demonstrates recommendation generation with mock article scores. Shows aggregation, trend analysis, and Buy/Hold/Sell signal generation with full explainability.

See [demos/README.md](scratch/demos/README.md) for detailed information about all demos.

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

#### Using the Centralized `vuts` Command (Recommended)

```bash
cd scratch

# Fetch news articles
./vuts fetch --config example_data/copilot-gpt5-cfg.json --output-dir output

# Fetch market data (optional but recommended)
./vuts market TSLA MSFT NVIDIA AMD --output-dir output/market_data

# Analyze sentiment with LLM
./vuts analyze --data-dir output --max-articles 10 --market-data-dir output/market_data

# Generate investment recommendations
python src/scoring/recommendation_engine.py \
    --data-dir output/llm_scores \
    --output-dir output/recommendations

# View results
find output/llm_scores -name "*_score.json" | head -5
cat output/recommendations/TSLA_recommendation.json
```

#### Alternative: Direct Script Calls

```bash
cd scratch

# Fetch news articles
python src/fetching/financial_news_collector_async.py \
    --config example_data/copilot-gpt5-cfg.json --output_dir output

# Fetch market data (optional but recommended)
python src/market/data_fetcher.py TSLA MSFT NVIDIA AMD \
    --output-dir output/market_data

# Analyze sentiment with LLM
python src/llm/sentiment_analyzer.py \
    --data-dir output \
    --max-articles 10 \
    --market-data-dir output/market_data

# Generate investment recommendations
python src/scoring/recommendation_engine.py \
    --data-dir output/llm_scores \
    --output-dir output/recommendations

# View results
find output/llm_scores -name "*_score.json" | head -5
cat output/recommendations/TSLA_recommendation.json
```

### 5. Launch the Web UI (Recommended)

```bash
cd scratch

# Launch using vuts command (recommended)
./vuts ui

# Or with custom options
./vuts ui --host 0.0.0.0 --port 8080 --debug

# Alternative: Quick launch script
python run_ui.py

# Alternative: Direct script call
python src/ui/app.py --host 0.0.0.0 --port 5000

# Then open your browser to http://localhost:5000
```

The Web UI provides:
- 📊 **Reports Dashboard** - Overview of all topics and sentiment trends
- 📈 **Topics View** - Detailed article analysis at `/reports/topics`
- 🔔 **Notifications** - Real-time alerts with browser notifications and audible alerts
- ⚙️ **Configuration Page** - Manage settings and view workflow commands

## 📚 Documentation

### Getting Started
- **[Hands-On Tutorial](docs/Tutorial_Hands_On.md)** - 🎓 Interactive tutorial for non-tech users (learn by doing)
- **[Quick Start Guide](docs/Quick_Start_Guide.md)** - Get up and running in 5 minutes
- **[Complete Workflow Guide](docs/Workflow_Guide.md)** - Detailed usage examples and advanced features

### Technical Documentation
- **[System State Flow](docs/System_State_Flow.md)** - 📊 Visual state flow diagrams and complete pipeline overview
- **[Technical Setup Guide](docs/Technical_Setup_Guide.md)** - 🔧 Comprehensive guide for developers and power users
- **[Architecture Diagrams](docs/Architecture_Diagrams.md)** - Visual system diagrams and flow charts
- **[Development Outline](docs/Development_Outline.md)** - Project architecture and future plans

### Module Documentation
- **[LLM Module](scratch/src/llm/README.md)** - Sentiment analyzer documentation
- **[Scoring Module](scratch/src/scoring/README.md)** - Recommendation engine documentation
- **[Web UI Module](scratch/src/ui/README.md)** - Web interface documentation
- **[Notifications Module](scratch/src/notifications/README.md)** - Alert system documentation
- **[Wiki Pages](wiki/)** - Comprehensive module documentation (ready for GitHub Wiki)

## 📁 Project Structure

```
vuts/
├── docs/                          # Main documentation
│   ├── Quick_Start_Guide.md       # 5-minute getting started
│   ├── Workflow_Guide.md          # Complete workflow (all phases)
│   ├── Development_Outline.md     # Project phases and architecture
│   └── Architecture_Diagrams.md   # System visualizations
├── scratch/                       # Main application code
│   ├── vuts                       # Centralized CLI entrypoint
│   ├── src/
│   │   ├── fetching/             # Phase 2: News collection module
│   │   │   └── financial_news_collector_async.py
│   │   ├── llm/                  # Phase 3: LLM sentiment analysis
│   │   │   ├── sentiment_analyzer.py
│   │   │   ├── sentiment_prompt.txt
│   │   │   └── README.md
│   │   ├── scoring/              # Phase 4: Recommendation engine
│   │   │   ├── recommendation_engine.py
│   │   │   └── README.md
│   │   ├── ui/                   # Phase 5: Web UI module
│   │   │   ├── app.py            # Flask application
│   │   │   ├── templates/        # HTML templates
│   │   │   ├── static/           # CSS and assets
│   │   │   └── README.md
│   │   ├── notifications/        # Phase 6: Alert system
│   │   │   ├── notification_manager.py
│   │   │   └── README.md
│   │   ├── market/               # Market data module
│   │   │   └── data_fetcher.py
│   │   ├── tests/                # Test suite
│   │   │   ├── test_llm_analyzer.py
│   │   │   ├── test_scoring_engine.py
│   │   │   ├── test_notifications.py
│   │   │   └── test_vuts_entrypoint.py
│   │   └── utils/                # Shared utilities
│   ├── demos/                     # Demo applications
│   │   ├── demo_workflow.py           # Mock workflow demo (no API keys)
│   │   ├── demo_openai_api.py         # OpenAI API demo (requires key)
│   │   ├── demo_recommendations.py    # Phase 4: Recommendation demo
│   │   └── demo_notifications.py      # Phase 6: Notification demo
│   ├── example_data/             # Configuration examples
│   ├── run_ui.py                 # Web UI launcher
│   └── requirements.txt          # Python dependencies
└── chats/                        # Development notes and chat logs
```

## 💻 CLI Usage

The `vuts` command provides a unified interface to all functionality:

```bash
# Get help
./vuts --help
# or
python vuts --help

# Fetch news articles
./vuts fetch --config <config.json> --output-dir <output>

# Analyze sentiment
./vuts analyze --data-dir <data> --max-articles <n> [--market-data-dir <market>]

# Fetch market data
./vuts market <SYMBOL1> <SYMBOL2> ... [--days <n>] [--output-dir <dir>]

# Launch web UI
./vuts ui [--host <host>] [--port <port>] [--debug] [--data-dir <dir>]
```

**Command Details:**

- **fetch**: Collects news articles from multiple sources (Google News, Bing, Finnhub, etc.)
- **analyze**: Performs LLM-powered sentiment analysis on collected articles
- **market**: Fetches historical market data from Yahoo Finance for context
- **ui**: Launches the web interface for viewing sentiment analysis reports

For detailed options, use `./vuts <command> --help`

## 🔑 Key Features

✅ **Centralized CLI** - Single `vuts` command for all operations  
✅ **Multi-Source News Fetching** - Aggregates from Google News RSS, Bing News, Finnhub  
✅ **LLM-Powered Sentiment Analysis** - Uses OpenAI GPT models for accurate scoring  
✅ **Market Context Integration** - Includes historical price data for better analysis  
✅ **Precise Scoring** - Score range from -10.00 to +10.00 with explanations  
✅ **Investment Recommendations** - Buy/Hold/Sell signals with confidence levels  
✅ **Source Reliability Weighting** - Weights scores based on news source credibility  
✅ **Temporal Decay** - Recent news matters more with exponential time-based decay  
✅ **Trend Analysis** - Detects improving/declining/stable sentiment patterns  
✅ **Full Explainability** - Detailed reasoning and risk factors for recommendations  
✅ **Cost Efficient** - Uses gpt-4o-mini by default (~$0.0006 per article)  
✅ **Web UI** - Browse reports, view sentiment trends, and manage configurations via browser  
✅ **Notification System** - Real-time alerts in UI, browser notifications, and phone subscriptions  
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

## 💼 Investment Recommendations (Phase 4)

The recommendation engine aggregates multiple article scores into actionable Buy/Hold/Sell signals:

| Recommendation | Aggregated Score | Confidence | Meaning |
|---------------|-----------------|------------|---------|
| **STRONG BUY** | ≥ +5.0 | HIGH | Very positive sentiment, strong opportunity |
| **BUY** | +2.5 to +5.0 | MEDIUM-HIGH | Positive sentiment, good entry point |
| **HOLD** | -2.5 to +2.5 | ANY | Neutral sentiment or insufficient data |
| **SELL** | -5.0 to -2.5 | MEDIUM-HIGH | Negative sentiment, consider reducing |
| **STRONG SELL** | ≤ -5.0 | HIGH | Very negative sentiment, high risk |

**Key Factors:**
- **Source Weighting**: Professional APIs (Finnhub) weighted higher than news aggregators
- **Temporal Decay**: Recent articles have more influence (7-day half-life)
- **Trend Analysis**: Improving/declining/stable sentiment detection
- **Confidence Levels**: Based on article count, recency, and consistency
- **Risk Factors**: Automatically identified concerns and caveats

**⚠️ Disclaimer**: Recommendations are based on sentiment analysis, NOT financial advice. Always do your own research and consult financial professionals.

See [Scoring Module Documentation](scratch/src/scoring/README.md) for details.

## 🧪 Running Tests

```bash
cd scratch

# Test LLM analyzer functionality
python src/tests/test_llm_analyzer.py

# Test scoring & recommendation engine
python src/tests/test_scoring_engine.py

# Test vuts CLI entrypoint
python src/tests/test_vuts_entrypoint.py

# Test notification system
python src/tests/test_notifications.py
```

All tests run without requiring API keys and validate:
- Prompt template loading and formatting
- LLM response parsing
- Temporal decay calculations
- Score aggregation with weighting
- Trend analysis and recommendation generation
- Article discovery and filtering
- Score saving and validation
- CLI entrypoint and subcommand routing
- Notification creation, persistence, and management

## 🔔 Notification System

VUTS includes a comprehensive notification system to alert you about important sentiment changes:

### Features

- **In-App Notifications** - View notifications in the web UI with a notification bell badge
- **Browser Alerts** - Receive audible browser notifications for critical events
- **Phone Subscriptions** - Subscribe phone numbers for SMS/webhook notifications
- **Severity Levels** - info, success, warning, critical with color-coding
- **Auto-Notifications** - Automatic alerts for extreme sentiment scores (±7.0 threshold)

### Quick Start

```bash
cd scratch

# Run the notification demo
python demos/demo_notifications.py

# Start the web UI to see notifications
./vuts ui

# Click the 🔔 bell icon in the navigation bar
```

### API Endpoints

- `GET /api/notifications` - Get all notifications
- `GET /api/notifications/unread` - Get unread notifications
- `POST /api/notifications/<id>/mark-read` - Mark as read
- `POST /api/notifications/mark-all-read` - Mark all as read
- `POST /api/notifications/subscribe` - Subscribe phone number
- `GET /api/notifications/subscriptions` - Get subscriptions

### Phone Subscriptions

```python
# Subscribe to notifications
curl -X POST http://localhost:5000/api/notifications/subscribe \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890", "topics": ["TSLA", "MSFT"], "min_severity": "warning"}'
```

See [Notification Module README](scratch/src/notifications/README.md) for detailed documentation.

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

All core phases complete:
- ✅ News aggregation & storage
- ✅ AI-powered sentiment analysis
- ✅ Scoring & recommendation engine
- ✅ User interface
- ✅ Notifications & alerts

Future enhancements:
- Backtesting and performance correlation
- Real-time streaming updates
- Multi-language support
- Advanced portfolio optimization

## 📝 License

This project is currently a research/testing tool. See LICENSE file for details.

## 🤝 Contributing

This is currently a personal project. Feel free to fork and experiment!

## ⚠️ Disclaimer

This tool is for research and educational purposes only. The sentiment scores and analysis should **not** be considered as financial advice. Always do your own research and consult with financial professionals before making investment decisions.

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Note**: The system is fully functional with all core features implemented. Additional enhancements and optimizations are ongoing.
