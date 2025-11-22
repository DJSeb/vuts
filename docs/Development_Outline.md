# Development Outline: AI-Powered Stock News Analyzer
## 1. Project Overview

Goal:
Develop an AI-powered platform that fetches financial news, analyzes sentiment, and produces actionable insights on stock outlooks — with real-time updates and notifications.

Core Components:
- Data pipeline: Fetch and store news and financial data.
- AI analysis: Use a public LLM to interpret text sentiment and relevance.
- Scoring engine: Generate and update dynamic sentiment-based scores per company.
- User interface: Display results, insights, and alerts.
- Notifications system: Send alerts for significant sentiment shifts.

## 2. Development Phases

### Phase 1: System Architecture & Setup ✅ COMPLETED
**Status**: Initial architecture established with modular design

**Implemented**:
- Defined overall architecture with clear module separation
- Established data flow: news fetching → sentiment analysis → scoring → UI → notifications
- Selected Python-based stack with Flask, OpenAI API, yfinance, aiohttp
- Created centralized CLI entrypoint (`vuts` command)
- Organized code into logical modules (fetching, llm, market, scoring, ui, notifications, utils)

**Key Decisions**:
- Python for all components (simpler deployment, strong AI/ML ecosystem)
- Flask for web UI (lightweight, easy to integrate)
- JSON file storage (simple, no database overhead for MVP)
- OpenAI GPT models for sentiment analysis (high quality, cost-effective)

### Phase 2: News Aggregation & Storage ✅ COMPLETED
**Status**: Multi-source news fetching with intelligent content extraction

**Implemented**:
- Automated fetching from multiple sources:
  - Google News RSS (free, broad coverage)
  - Bing News API (structured data)
  - Finnhub (professional financial API)
- Async/parallel fetching for speed
- Article deduplication by URL
- Full content extraction with fallback options
- Age-based filtering (configurable max_age_days)
- JSON-based storage with organized directory structure
- Smart caching to avoid re-fetching

**Key Files**:
- `src/fetching/financial_news_collector_async.py`
- Configuration: `example_data/copilot-gpt5-cfg.json`

### Phase 3: AI-Powered Sentiment & Relevance Analysis ✅ COMPLETED
**Status**: LLM-powered sentiment scoring with market context

**Implemented**:
- OpenAI API integration (GPT-4o-mini, GPT-4, GPT-3.5-turbo)
- Precise scoring: -10.00 (extremely negative) to +10.00 (extremely positive)
- Detailed explanations for every score
- Market context integration (price changes, volume, historical data)
- Comprehensive prompt engineering for consistent results
- Automatic score validation and error handling
- Smart article discovery from multiple sources
- Caching to avoid re-analyzing articles

**Features**:
- Sentiment categories: Highly Negative/Negative/Neutral/Positive/Highly Positive
- Context-aware scoring considers recent market performance
- Explanations make results interpretable and actionable
- Cost optimization with gpt-4o-mini (~$0.0006 per article)

**Key Files**:
- `src/llm/sentiment_analyzer.py`
- `src/llm/sentiment_prompt.txt`

### Phase 4: Scoring & Recommendation Engine ✅ COMPLETED
**Status**: Investment recommendations with full explainability

**Implemented**:
- **Sentiment Aggregation**: Combines multiple article scores into topic-level scores
- **Source Reliability Weighting**: 
  - Finnhub: 1.0 (professional financial data)
  - Bing News: 0.9 (mainstream news)
  - Google News RSS: 0.85 (RSS aggregation)
- **Temporal Decay**: Recent news matters more (7-day half-life, 30-day max age)
- **Trend Analysis**: Detects improving/declining/stable sentiment patterns
- **Recommendation Types**: STRONG BUY / BUY / HOLD / SELL / STRONG SELL
- **Confidence Levels**: HIGH/MEDIUM/LOW based on article count, recency, consistency
- **Full Explainability**: Every recommendation includes detailed reasoning
- **Risk Factors**: Automatically identified concerns and caveats

**Thresholds**:
- STRONG BUY: ≥ +5.0
- BUY: +2.5 to +5.0
- HOLD: -2.5 to +2.5
- SELL: -5.0 to -2.5
- STRONG SELL: ≤ -5.0

**Key Files**:
- `src/scoring/recommendation_engine.py`
- Demo: `demos/demo_recommendations.py`

### Phase 5: User Interface ✅ COMPLETED
**Status**: Web-based dashboard with comprehensive views

**Implemented**:
- **Flask Web Application**: Lightweight, responsive web interface
- **Reports Dashboard**: Overview of all topics with sentiment trends
- **Topics View**: Detailed article analysis organized by topic
- **Topic Detail Pages**: Deep dive into individual topic analysis
- **Configuration Manager**: View and edit system settings
- **Configuration Editor**: Visual form for creating new configurations
- **REST API**: JSON endpoints for programmatic access
- **Notification Integration**: Real-time alerts visible in UI

**Features**:
- Mobile-responsive design
- Color-coded sentiment indicators
- Article filtering and sorting
- Workflow command reference
- Data directory configuration
- No JavaScript framework dependencies (vanilla JS for notifications)

**Routes**:
- `/` - Home (redirects to reports)
- `/reports` - Dashboard overview
- `/reports/topics` - Detailed topics list
- `/reports/topics/<topic>` - Topic detail page
- `/config` - Configuration management
- `/config/editor` - Configuration editor
- `/api/topics` - JSON API for topics
- `/api/notifications` - Notification API

**Key Files**:
- `src/ui/app.py`
- `src/ui/templates/` - HTML templates
- `src/ui/static/css/style.css`

### Phase 6: Notifications & Alerts ✅ COMPLETED
**Status**: Comprehensive notification system with multiple delivery methods

**Implemented**:
- **In-App Notifications**: Display in web UI with badge indicators
- **Browser Alerts**: Audible notifications using Web Notification API
- **Phone Subscriptions**: SMS-ready subscription system (webhook integration)
- **Severity Levels**: info, success, warning, critical (color-coded)
- **Automatic Triggers**: Auto-notification for extreme scores (±7.0 threshold)
- **Persistent Storage**: JSON-based notification history
- **Read/Unread Tracking**: Mark notifications as read/unread
- **Topic Filtering**: Subscribe to specific topics only

**Notification Triggers**:
- Score ≥ +7.0: SUCCESS notification (extremely positive sentiment)
- Score ≤ -7.0: CRITICAL notification (extremely negative sentiment)
- Custom triggers can be added for specific use cases

**API Endpoints**:
- `GET /api/notifications` - All notifications
- `GET /api/notifications/unread` - Unread only
- `POST /api/notifications/<id>/mark-read` - Mark as read
- `POST /api/notifications/mark-all-read` - Mark all as read
- `POST /api/notifications/subscribe` - Subscribe phone
- `GET /api/notifications/subscriptions` - List subscriptions

**Integration Points**:
- Can integrate with Twilio (SMS)
- Can integrate with AWS SNS (push notifications)
- Can integrate with Zapier/IFTTT (webhooks)

**Key Files**:
- `src/notifications/notification_manager.py`
- Demo: `demos/demo_notifications.py`

### Phase 7: Testing, Optimization, & Deployment 🔄 IN PROGRESS
**Status**: Comprehensive testing, ready for deployment

**Implemented**:
- Unit tests for all core modules (no API keys required)
- Demo scripts for testing without external APIs
- Security scanning with CodeQL
- Cost optimization (gpt-4o-mini by default)
- Smart caching throughout

**Test Coverage**:
- LLM analyzer: prompt loading, formatting, parsing
- Scoring engine: temporal decay, aggregation, trend analysis, recommendations
- Notifications: creation, persistence, management
- UI: endpoint routing
- CLI: entrypoint and subcommand routing

**Optimization**:
- Async operations for parallel fetching
- Article deduplication
- Market data caching (24-hour cache)
- Score caching (avoid re-analysis)
- Rate limiting for API calls

**Ready for Deployment**:
- Can deploy with Gunicorn for production
- Docker-ready architecture
- Environment-based configuration
- No hardcoded credentials

**Key Files**:
- `src/tests/test_llm_analyzer.py`
- `src/tests/test_scoring_engine.py`
- `src/tests/test_notifications.py`
- `src/tests/test_vuts_entrypoint.py`

## 3. Future Enhancements

### High Priority
- **Backtesting Framework**: Compare sentiment trends to actual stock price movements
- **Performance Metrics**: Track recommendation accuracy over time
- **Custom Alert Rules**: User-defined thresholds and conditions
- **Email Notifications**: Direct email delivery for critical alerts
- **Portfolio Tracking**: Monitor multiple stocks as a portfolio

### Medium Priority
- **Historical Analysis**: Analyze past sentiment patterns
- **Correlation Studies**: Quantify sentiment-price relationships
- **Multi-timeframe Analysis**: Short-term vs long-term sentiment trends
- **Sector Analysis**: Compare sentiment across industry sectors
- **Volume Weighting**: Consider article volume in scoring

### Future Exploration
- **Multi-language Support**: Analyze global financial news in multiple languages
- **Chat Interface**: Natural language queries (e.g., "What's the latest on Tesla?")
- **Portfolio Simulation**: Paper trading based on sentiment signals
- **Advanced Visualizations**: Interactive charts and trend graphs
- **Machine Learning**: Learn optimal scoring weights from historical data
- **Real-time Streaming**: WebSocket-based live updates
- **Social Media Integration**: Include Twitter/Reddit sentiment

## 4. Current Tech Stack

| Layer                | Implemented Technology                              | Notes                                    |
|----------------------|-----------------------------------------------------|------------------------------------------|
| **Frontend**         | Flask Templates + Vanilla CSS                       | Simple, responsive, no build process     |
| **Backend API**      | Flask (Python)                                      | Lightweight REST API                     |
| **Storage**          | JSON files                                          | Simple, portable, no database needed     |
| **Data Fetching**    | Google News RSS, Bing News API, Finnhub API         | Multi-source aggregation                 |
| **AI Model**         | OpenAI GPT-4o-mini (default), GPT-4, GPT-3.5-turbo  | Cost-effective, high quality             |
| **Market Data**      | yfinance (Yahoo Finance)                            | Free historical price data               |
| **Notifications**    | Web UI + Browser Notification API                   | SMS-ready (Twilio integration possible)  |
| **CLI**              | argparse + custom entrypoint (`vuts`)               | Unified command interface                |
| **Testing**          | Python unittest                                     | No external dependencies for tests       |
| **Async**            | aiohttp                                             | Fast parallel news fetching              |
| **Content Extract**  | BeautifulSoup4 + readability-lxml                   | Robust content extraction                |

## 5. Project Structure

```
vuts/
├── README.md                          # Main project documentation
├── REORGANIZATION_SUMMARY.md          # History of major reorganization
├── docs/                              # Comprehensive documentation
│   ├── Development_Outline.md         # This file - project phases
│   ├── Workflow_Guide.md              # Complete usage guide (all phases)
│   ├── Quick_Start_Guide.md           # 5-minute getting started
│   └── Architecture_Diagrams.md       # Mermaid system diagrams
├── wiki/                              # GitHub wiki pages
│   ├── Home.md
│   ├── Getting-Started.md
│   ├── Architecture.md
│   ├── Fetching-Module.md
│   ├── LLM-Module.md
│   ├── Market-Module.md
│   └── Utilities-Module.md
├── scratch/                           # Main application code
│   ├── vuts                           # Centralized CLI entrypoint
│   ├── run_ui.py                      # Quick UI launcher
│   ├── requirements.txt               # Python dependencies
│   ├── src/
│   │   ├── fetching/                  # Phase 2: News collection
│   │   ├── llm/                       # Phase 3: Sentiment analysis
│   │   ├── market/                    # Market data fetching
│   │   ├── scoring/                   # Phase 4: Recommendations
│   │   ├── ui/                        # Phase 5: Web interface
│   │   ├── notifications/             # Phase 6: Alert system
│   │   ├── utils/                     # Shared utilities
│   │   └── tests/                     # Test suite
│   ├── demos/                         # Demo applications
│   │   ├── demo_workflow.py           # Mock workflow (no API keys)
│   │   ├── demo_openai_api.py         # OpenAI demo
│   │   ├── demo_recommendations.py    # Phase 4 demo
│   │   └── demo_notifications.py      # Phase 6 demo
│   └── example_data/                  # Configuration examples
└── chats/                             # Development notes
```

## 6. Key Metrics & Performance

### Current Capabilities
- **Processing Speed**: ~10 articles per minute (limited by LLM API)
- **Cost per Article**: ~$0.0006 (using gpt-4o-mini)
- **Sources**: 3 news sources (Google, Bing, Finnhub)
- **Score Precision**: 0.01 (-10.00 to +10.00 in 0.01 increments)
- **Confidence Levels**: HIGH/MEDIUM/LOW based on article count and consistency
- **Temporal Decay**: 7-day half-life for article weighting
- **Max Article Age**: 30 days (configurable)

### Scalability Considerations
- JSON storage works well up to ~1000 articles per topic
- For larger scale, consider migrating to SQLite or PostgreSQL
- Current async fetching handles 10+ sources efficiently
- LLM API rate limits are the main bottleneck (can be parallelized)

## 7. Success Metrics (Phase 7 - Future)

### Quantitative Goals
- [ ] Backtest accuracy: >55% directional prediction (better than random)
- [ ] Response time: <2 seconds for UI page loads
- [ ] Cost efficiency: <$1 per day for continuous monitoring of 10 stocks
- [ ] Uptime: >99% availability for production deployment

### Qualitative Goals
- [ ] User-friendly interface accessible to non-technical users
- [ ] Transparent reasoning for all recommendations
- [ ] Reliable notification delivery
- [ ] Clear documentation for all features