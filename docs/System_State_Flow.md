# VUTS System State Flow and Pipeline

This document provides a high-level, visual overview of how VUTS processes financial news from initial fetching through to investment recommendations and user notifications. It includes comprehensive state flow diagrams showing the complete data pipeline and detailed explanations of each component.

## 📋 Table of Contents

- [Complete System Pipeline](#complete-system-pipeline)
- [State Flow Diagram](#state-flow-diagram)
- [Module-by-Module Workflow](#module-by-module-workflow)
- [Data Transformation Flow](#data-transformation-flow)
- [Error Handling and Recovery](#error-handling-and-recovery)
- [Related Documentation](#related-documentation)

---

## Complete System Pipeline

The VUTS system follows a clear, linear pipeline from data collection through analysis to actionable recommendations:

```mermaid
graph TB
    subgraph "Stage 1: Data Collection"
        START([User Initiates Workflow]) --> CONFIG[Load Configuration]
        CONFIG --> FETCH[Fetch News Articles]
        CONFIG --> MARKET[Fetch Market Data]
    end
    
    subgraph "Stage 2: Analysis"
        FETCH --> FILTER[Filter & Validate Articles]
        MARKET --> CONTEXT[Format Market Context]
        FILTER --> LLM[LLM Sentiment Analysis]
        CONTEXT --> LLM
        LLM --> SCORES[Individual Article Scores]
    end
    
    subgraph "Stage 3: Aggregation"
        SCORES --> AGG[Aggregate Scores by Topic]
        AGG --> WEIGHT[Apply Source Weights]
        WEIGHT --> DECAY[Apply Temporal Decay]
        DECAY --> TREND[Analyze Trends]
        TREND --> REC[Generate Recommendations]
    end
    
    subgraph "Stage 4: Delivery"
        REC --> UI[Web UI Display]
        REC --> NOTIFY[Notification System]
        NOTIFY --> BROWSER[Browser Notifications]
        NOTIFY --> SMS[SMS/Phone Alerts]
        UI --> USER([User Reviews Results])
    end
    
    style START fill:#e1f5ff
    style CONFIG fill:#ffe1f5
    style FETCH fill:#ffe1f5
    style MARKET fill:#ffe1f5
    style FILTER fill:#fff3e1
    style CONTEXT fill:#fff3e1
    style LLM fill:#e1ffe1
    style SCORES fill:#e1ffe1
    style AGG fill:#f5e1ff
    style WEIGHT fill:#f5e1ff
    style DECAY fill:#f5e1ff
    style TREND fill:#f5e1ff
    style REC fill:#f5e1ff
    style UI fill:#ffe1e1
    style NOTIFY fill:#ffe1e1
    style BROWSER fill:#ffe1e1
    style SMS fill:#ffe1e1
    style USER fill:#e1f5ff
```

### Pipeline Component Descriptions

**Stage 1: Data Collection**
- **Load Configuration**: Reads user settings including target topics (e.g., TSLA, MSFT), news sources to query, and time ranges
- **Fetch News Articles**: Asynchronously queries multiple news APIs (Google News RSS, Bing News, Finnhub) for recent financial articles
- **Fetch Market Data**: Retrieves historical stock prices, volume, and trading statistics from Yahoo Finance for context

**Stage 2: Analysis**
- **Filter & Validate Articles**: Removes duplicates, validates required fields, and filters by age and relevance
- **Format Market Context**: Transforms raw market data into structured context (price changes, trends, volatility) for the LLM
- **LLM Sentiment Analysis**: Sends each article to OpenAI's GPT models with market context to generate sentiment scores (-10.00 to +10.00)
- **Individual Article Scores**: Stores scored articles with explanations for transparency

**Stage 3: Aggregation**
- **Aggregate Scores**: Combines multiple article scores for each stock symbol
- **Apply Source Weights**: Weights scores based on source reliability (e.g., Finnhub 1.0, Bing 0.9, Google RSS 0.85)
- **Apply Temporal Decay**: Recent articles receive higher weights (7-day half-life exponential decay)
- **Analyze Trends**: Detects if sentiment is improving, declining, or stable over time
- **Generate Recommendations**: Produces actionable Buy/Hold/Sell signals with confidence levels

**Stage 4: Delivery**
- **Web UI Display**: Shows interactive dashboard with sentiment trends, article details, and recommendations
- **Notification System**: Triggers alerts for significant sentiment shifts or extreme scores
- **Browser Notifications**: In-app alerts with audible notifications
- **SMS/Phone Alerts**: Sends notifications to subscribed phone numbers for critical events
- **User Reviews Results**: Users examine recommendations and make informed investment decisions

---

## State Flow Diagram

This diagram shows the complete state machine for processing a single article through the VUTS system:

```mermaid
stateDiagram-v2
    [*] --> Idle: System Ready
    
    Idle --> ConfigLoaded: User starts workflow
    ConfigLoaded --> FetchingNews: Begin data collection
    
    FetchingNews --> ArticleQueued: Article found
    FetchingNews --> FetchingNews: More sources
    FetchingNews --> MarketDataCheck: All articles fetched
    
    MarketDataCheck --> FetchingMarket: Market data needed
    MarketDataCheck --> ProcessingQueue: Skip market data
    FetchingMarket --> ProcessingQueue: Market data ready
    
    ProcessingQueue --> ValidatingArticle: Select next article
    ProcessingQueue --> AggregationPhase: Queue empty
    
    ValidatingArticle --> CheckingCache: Article valid
    ValidatingArticle --> ProcessingQueue: Invalid/duplicate
    
    CheckingCache --> ProcessingQueue: Already scored
    CheckingCache --> LoadingMarket: Not scored
    
    LoadingMarket --> FormattingPrompt: Market context loaded
    LoadingMarket --> FormattingPrompt: No market data available
    
    FormattingPrompt --> CallingLLM: Prompt ready
    
    CallingLLM --> ParsingResponse: LLM response received
    CallingLLM --> ErrorHandling: API error
    
    ParsingResponse --> ValidatingScore: Score extracted
    ParsingResponse --> ErrorHandling: Parse error
    
    ValidatingScore --> SavingScore: Score valid (-10 to +10)
    ValidatingScore --> ErrorHandling: Score invalid
    
    SavingScore --> ProcessingQueue: Score saved
    
    ErrorHandling --> ProcessingQueue: Log error, continue
    
    AggregationPhase --> LoadingScores: Begin aggregation
    LoadingScores --> ApplyingWeights: Scores loaded
    ApplyingWeights --> ApplyingDecay: Weights applied
    ApplyingDecay --> TrendAnalysis: Decay applied
    TrendAnalysis --> GeneratingRec: Trends calculated
    GeneratingRec --> SavingRec: Recommendation ready
    SavingRec --> NotificationCheck: Recommendation saved
    
    NotificationCheck --> TriggeringNotif: Extreme score (±7.0+)
    NotificationCheck --> Complete: Normal score
    TriggeringNotif --> Complete: Notification sent
    
    Complete --> Idle: Ready for next run
    Complete --> [*]: System shutdown
    
    note right of FetchingNews
        Parallel async operations:
        - Multiple topics
        - Multiple sources
        - Concurrent requests
    end note
    
    note right of CallingLLM
        Uses OpenAI API:
        - Model: gpt-4o-mini (default)
        - Temperature: 0.3
        - Cost: ~$0.0006/article
    end note
    
    note right of AggregationPhase
        Combines scores with:
        - Source reliability weights
        - Temporal decay (7-day half-life)
        - Trend analysis
    end note
```

### State Descriptions

**Idle**: System is ready to process new data. Waiting for user to initiate a workflow run.

**ConfigLoaded**: Configuration file has been read and validated. System knows which topics to analyze and which sources to query.

**FetchingNews**: Actively querying news APIs asynchronously. Multiple concurrent requests are made to different sources (Google News, Bing, Finnhub). Articles are deduplicated by URL to prevent processing the same content twice.

**ArticleQueued**: A valid article has been retrieved and queued for processing. The article includes title, URL, publication date, and optionally full content.

**MarketDataCheck**: System determines if market data should be fetched. This provides context like recent price changes and volatility that helps the LLM produce more informed sentiment scores.

**FetchingMarket**: Querying Yahoo Finance for historical stock data (typically 30 days). Calculates statistics like price change percentage, period high/low, and average volume.

**ProcessingQueue**: Iterating through queued articles sequentially. Each article goes through validation, caching checks, and sentiment analysis.

**ValidatingArticle**: Checking article has required fields (title, content, date, topic). Ensures content is not empty and publication date is recent enough.

**CheckingCache**: Looking for existing score file to avoid re-analyzing the same article. This saves API costs and processing time.

**LoadingMarket**: Loading previously fetched market data for the article's topic. Formats it into a context string that will be prepended to the LLM prompt.

**FormattingPrompt**: Constructing the complete prompt by combining the template, article content, and market context. The prompt instructs the LLM to provide a score (-10.00 to +10.00) and explanation.

**CallingLLM**: Sending the formatted prompt to OpenAI's API. Using temperature 0.3 for consistent, deterministic results. The gpt-4o-mini model provides excellent quality at low cost.

**ParsingResponse**: Extracting the score and explanation from the LLM's response. Looks for "SCORE: X.XX" pattern and captures the explanation text.

**ValidatingScore**: Ensuring the extracted score is a valid number within the -10.00 to +10.00 range. Invalid scores trigger error handling.

**SavingScore**: Writing the score, explanation, article metadata, and timestamp to a JSON file in the `llm_scores/` directory, organized by topic.

**ErrorHandling**: Logging errors (API failures, parse errors, invalid scores) and continuing to process remaining articles. The system is designed to be resilient to individual failures.

**AggregationPhase**: Beginning the recommendation generation phase. All individual article scores have been collected.

**LoadingScores**: Reading all score JSON files for each topic from the `llm_scores/` directory.

**ApplyingWeights**: Multiplying each score by its source's reliability weight. For example, Finnhub scores (weight 1.0) are trusted more than Google News RSS (weight 0.85).

**ApplyingDecay**: Applying exponential temporal decay to older articles. Articles lose 50% of their weight after 7 days. Articles older than 30 days are excluded entirely.

**TrendAnalysis**: Comparing recent scores (last 3 days) with older scores (4-7 days) to detect if sentiment is improving, declining, or stable.

**GeneratingRec**: Determining Buy/Hold/Sell recommendation based on the weighted average score. Thresholds: Strong Buy ≥5.0, Buy ≥2.5, Hold -2.5 to 2.5, Sell ≤-2.5, Strong Sell ≤-5.0.

**SavingRec**: Writing the recommendation with confidence level, aggregated score, trend analysis, article count, and detailed explanation to a JSON file.

**NotificationCheck**: Evaluating if the recommendation meets criteria for triggering user notifications (e.g., extreme scores ±7.0 or higher).

**TriggeringNotif**: Creating and sending notifications through available channels (in-app UI alerts, browser notifications, SMS to subscribed phones).

**Complete**: Processing cycle finished. Results are ready for viewing in the Web UI.

---

## Module-by-Module Workflow

### 1. Fetching Module Workflow

```mermaid
flowchart TD
    START([Start Fetching]) --> LOAD[Load Configuration File]
    LOAD --> PARSE[Parse Topics & Sources]
    PARSE --> TASKS[Create Async Tasks]
    
    TASKS --> T1[Topic 1 + Source 1]
    TASKS --> T2[Topic 1 + Source 2]
    TASKS --> T3[Topic 2 + Source 1]
    TASKS --> TMORE[...]
    
    T1 --> QUERY1[Query API]
    T2 --> QUERY2[Query API]
    T3 --> QUERY3[Query API]
    TMORE --> QUERYMORE[Query APIs]
    
    QUERY1 --> RESULTS1[Article Results]
    QUERY2 --> RESULTS2[Article Results]
    QUERY3 --> RESULTS3[Article Results]
    QUERYMORE --> RESULTSMORE[Article Results]
    
    RESULTS1 --> DEDUP[Deduplication by URL]
    RESULTS2 --> DEDUP
    RESULTS3 --> DEDUP
    RESULTSMORE --> DEDUP
    
    DEDUP --> EXTRACT[Extract Full Content?]
    EXTRACT -->|Yes| CONTENT[Fetch & Extract Content]
    EXTRACT -->|No| SAVE
    CONTENT --> SAVE[Save Articles to JSON]
    
    SAVE --> END([Fetching Complete])
    
    style START fill:#e1f5ff
    style END fill:#e1ffe1
```

**How it works:**
1. **Configuration Loading**: Reads JSON config specifying topics (stock symbols) and sources (news APIs)
2. **Task Creation**: Creates one async task for each topic-source combination (e.g., TSLA+GoogleNews, TSLA+Bing)
3. **Parallel Querying**: All tasks run concurrently, maximizing speed through async I/O
4. **Deduplication**: Removes duplicate articles based on URL to avoid processing the same content multiple times
5. **Content Extraction**: Optionally fetches full article text from URLs (top N articles per topic)
6. **Storage**: Saves articles as JSON files in structured directories: `output/{source}/{topic}/`

### 2. Market Module Workflow

```mermaid
flowchart LR
    START([Start Market Fetch]) --> SYMBOLS[Input Stock Symbols]
    SYMBOLS --> YAHOO[Query Yahoo Finance API]
    YAHOO --> HIST[Fetch Historical Prices]
    HIST --> CALC[Calculate Statistics]
    
    CALC --> STATS[Price Change %<br/>Period High/Low<br/>Average Volume<br/>Volatility]
    
    STATS --> FORMAT[Format Context String]
    FORMAT --> SAVE[Save Market Data JSON]
    SAVE --> END([Market Data Ready])
    
    style START fill:#e1f5ff
    style END fill:#e1ffe1
```

**How it works:**
1. **Symbol Input**: Receives list of stock symbols to fetch (e.g., TSLA, MSFT, NVIDIA)
2. **Historical Data**: Queries Yahoo Finance for daily OHLCV data (typically 30 days)
3. **Statistics Calculation**: Computes price change percentage, period high/low, average volume, and volatility
4. **Context Formatting**: Transforms statistics into human-readable text for the LLM (e.g., "TSLA is up 10.5% over the past 30 days")
5. **Storage**: Saves market data as JSON: `output/market_data/{SYMBOL}_market_data.json`

### 3. LLM Module Workflow

```mermaid
flowchart TD
    START([Start LLM Analysis]) --> DISCOVER[Discover Article Files]
    DISCOVER --> FILTER[Filter by Age & Required Fields]
    FILTER --> LOOP{More Articles?}
    
    LOOP -->|Yes| NEXT[Select Next Article]
    LOOP -->|No| DONE([Analysis Complete])
    
    NEXT --> CACHE{Already Scored?}
    CACHE -->|Yes| LOOP
    CACHE -->|No| MARKET{Market Data Available?}
    
    MARKET -->|Yes| LOADM[Load Market Context]
    MARKET -->|No| PROMPT
    LOADM --> PROMPT[Format Prompt]
    
    PROMPT --> API[Call OpenAI API]
    API --> PARSE[Parse Response]
    PARSE --> VALIDATE{Valid Score?}
    
    VALIDATE -->|Yes| SAVE[Save Score JSON]
    VALIDATE -->|No| ERROR[Log Error]
    
    SAVE --> LOOP
    ERROR --> LOOP
    
    style START fill:#e1f5ff
    style DONE fill:#e1ffe1
```

**How it works:**
1. **Article Discovery**: Recursively scans data directory for article JSON files
2. **Filtering**: Removes articles that are too old or missing required fields
3. **Cache Check**: Skips articles that have already been scored (saves API costs)
4. **Market Context**: If available, loads and prepends market data context to the prompt
5. **Prompt Formatting**: Combines template + article content + market context into final prompt
6. **LLM Call**: Sends prompt to OpenAI API (gpt-4o-mini by default) with temperature 0.3
7. **Response Parsing**: Extracts score (e.g., "SCORE: +6.75") and explanation text
8. **Validation**: Ensures score is numeric and within [-10.00, +10.00] range
9. **Storage**: Saves score, explanation, and metadata to `output/llm_scores/{topic}/`

### 4. Scoring Module Workflow

```mermaid
flowchart TD
    START([Start Recommendation Engine]) --> LOAD[Load All Score Files by Topic]
    LOAD --> CHECK{Enough Articles?}
    
    CHECK -->|No: <2 articles| INSUFFICIENT[Output: HOLD<br/>Reason: Insufficient Data]
    CHECK -->|Yes: ≥2 articles| PROCESS[Process Scores]
    
    PROCESS --> WEIGHT[Apply Source Weights]
    WEIGHT --> DECAY[Apply Temporal Decay]
    DECAY --> AGG[Calculate Weighted Average]
    
    AGG --> TREND[Analyze Trend]
    TREND --> RECENT[Recent Scores: Last 3 Days]
    RECENT --> OLD[Older Scores: 4-7 Days]
    OLD --> COMPARE{Trend Direction?}
    
    COMPARE -->|Improving| TRENDPOS[Trend: Improving]
    COMPARE -->|Declining| TRENDNEG[Trend: Declining]
    COMPARE -->|Stable| TRENDSTABLE[Trend: Stable]
    
    TRENDPOS --> RECOMMEND
    TRENDNEG --> RECOMMEND
    TRENDSTABLE --> RECOMMEND[Determine Recommendation]
    
    RECOMMEND --> R1{Score ≥ 5.0?}
    R1 -->|Yes| STRONGBUY[STRONG BUY]
    R1 -->|No| R2{Score ≥ 2.5?}
    R2 -->|Yes| BUY[BUY]
    R2 -->|No| R3{Score ≤ -5.0?}
    R3 -->|Yes| STRONGSELL[STRONG SELL]
    R3 -->|No| R4{Score ≤ -2.5?}
    R4 -->|Yes| SELL[SELL]
    R4 -->|No| HOLD[HOLD]
    
    STRONGBUY --> CONF
    BUY --> CONF
    HOLD --> CONF
    SELL --> CONF
    STRONGSELL --> CONF
    INSUFFICIENT --> SAVE
    
    CONF[Calculate Confidence] --> FACTORS[Consider:<br/>Article Count<br/>Recency<br/>Score Consistency]
    FACTORS --> SAVE[Save Recommendation JSON]
    SAVE --> END([Recommendation Complete])
    
    style START fill:#e1f5ff
    style END fill:#e1ffe1
    style STRONGBUY fill:#00ff00
    style BUY fill:#66ff66
    style HOLD fill:#ffff99
    style SELL fill:#ff9966
    style STRONGSELL fill:#ff0000
```

**How it works:**
1. **Load Scores**: Reads all score JSON files for a given topic from `llm_scores/` directory
2. **Minimum Check**: Requires at least 2 articles for a recommendation; otherwise outputs HOLD with "insufficient data" reason
3. **Source Weighting**: Multiplies each score by source reliability weight (Finnhub 1.0, Bing 0.9, Google RSS 0.85)
4. **Temporal Decay**: Applies exponential decay based on article age (7-day half-life, 30-day cutoff)
5. **Weighted Average**: Calculates final aggregated score considering both weights and decay
6. **Trend Analysis**: Compares recent scores (last 3 days) with older scores (4-7 days) to detect sentiment direction
7. **Recommendation Logic**: Maps score to recommendation:
   - Score ≥ 5.0 → STRONG BUY
   - Score ≥ 2.5 → BUY
   - -2.5 < Score < 2.5 → HOLD
   - Score ≤ -2.5 → SELL
   - Score ≤ -5.0 → STRONG SELL
8. **Confidence Calculation**: Determines HIGH/MEDIUM/LOW confidence based on article count, recency, and score consistency
9. **Risk Factors**: Identifies potential concerns (low article count, conflicting scores, extreme volatility)
10. **Storage**: Saves recommendation with full explainability to `output/recommendations/{TOPIC}_recommendation.json`

### 5. UI Module Workflow

```mermaid
flowchart LR
    START([User Opens Browser]) --> FLASK[Flask Web Server]
    FLASK --> ROUTE{Route?}
    
    ROUTE -->|/| DASHBOARD[Dashboard View]
    ROUTE -->|/reports/topics| TOPICS[Topics List]
    ROUTE -->|/reports/topic/TSLA| DETAIL[Topic Detail]
    ROUTE -->|/notifications| NOTIF[Notifications Page]
    ROUTE -->|/config| CONFIG[Configuration Editor]
    
    DASHBOARD --> SCAN1[Scan llm_scores/]
    TOPICS --> SCAN2[Scan llm_scores/]
    DETAIL --> SCAN3[Load Topic Scores]
    
    SCAN1 --> RENDER1[Render Dashboard Template]
    SCAN2 --> RENDER2[Render Topics Template]
    SCAN3 --> RENDER3[Render Detail Template]
    
    NOTIF --> DB[Load Notifications from SQLite]
    DB --> RENDER4[Render Notifications Template]
    
    CONFIG --> FORM[Configuration Form]
    FORM --> SAVE{Save?}
    SAVE -->|Yes| UPDATE[Update Config JSON]
    SAVE -->|No| FORM
    
    RENDER1 --> BROWSER[Display in Browser]
    RENDER2 --> BROWSER
    RENDER3 --> BROWSER
    RENDER4 --> BROWSER
    UPDATE --> BROWSER
    
    BROWSER --> INTERACT{User Action?}
    INTERACT -->|Click Link| ROUTE
    INTERACT -->|Mark Read| API[API Call]
    INTERACT -->|Close| END([Session End])
    
    API --> DB
    
    style START fill:#e1f5ff
    style END fill:#e1ffe1
```

**How it works:**
1. **Flask Server**: Web framework serves HTML pages and API endpoints
2. **Route Handling**: Different URLs map to different views (dashboard, topics, notifications)
3. **Data Loading**: Scans file system for score JSONs and loads recommendation data
4. **Template Rendering**: Uses Jinja2 templates to generate HTML with dynamic data
5. **Interactive Features**: JavaScript handles browser notifications, mark-as-read actions, and real-time updates
6. **Configuration Editor**: Allows editing workflow settings through web interface
7. **API Endpoints**: RESTful APIs for notifications management (`/api/notifications/*`)

### 6. Notification Module Workflow

```mermaid
flowchart TD
    START([Notification Trigger]) --> CHECK{Trigger Type?}
    
    CHECK -->|Extreme Score| EXTREME[Score ≥ ±7.0]
    CHECK -->|Manual| MANUAL[User Created]
    CHECK -->|System| SYSTEM[System Event]
    
    EXTREME --> CREATE
    MANUAL --> CREATE
    SYSTEM --> CREATE[Create Notification]
    
    CREATE --> PROPS[Set Properties:<br/>Topic, Message<br/>Severity, Timestamp]
    PROPS --> SAVE[Save to SQLite DB]
    SAVE --> DISPATCH{Dispatch to Channels}
    
    DISPATCH --> WEBAPP[Web App Badge Update]
    DISPATCH --> BROWSER[Browser Notification API]
    DISPATCH --> CHECK_SUB{Phone Subscriptions?}
    
    CHECK_SUB -->|Yes| SMS[Send SMS/Webhook]
    CHECK_SUB -->|No| SKIP
    
    WEBAPP --> COMPLETE
    BROWSER --> COMPLETE
    SMS --> COMPLETE([Notification Delivered])
    SKIP --> COMPLETE
    
    style START fill:#e1f5ff
    style COMPLETE fill:#e1ffe1
```

**How it works:**
1. **Trigger Detection**: Automatically triggers for extreme sentiment scores (±7.0 or higher)
2. **Notification Creation**: Generates notification with topic, message, severity (info/success/warning/critical), and timestamp
3. **Persistence**: Saves to SQLite database for history and unread tracking
4. **Multi-Channel Dispatch**:
   - **Web App**: Updates notification badge count in UI navigation
   - **Browser**: Uses browser Notification API for desktop/mobile alerts with sound
   - **SMS**: Sends to subscribed phone numbers if configured
5. **User Management**: Users can mark as read, dismiss, or manage phone subscriptions

---

## Data Transformation Flow

This section shows how data transforms as it moves through the system:

```mermaid
graph LR
    subgraph "Input"
        A[News Article URL]
        B[Stock Symbol]
    end
    
    subgraph "Fetching Output"
        C["Article JSON<br/>{title, url, content<br/>published_at, topic}"]
        D["Market Data JSON<br/>{symbol, price_change<br/>high, low, volume}"]
    end
    
    subgraph "LLM Output"
        E["Score JSON<br/>{llm_score: 6.75<br/>llm_explanation<br/>model, scored_at}"]
    end
    
    subgraph "Scoring Output"
        F["Recommendation JSON<br/>{recommendation: BUY<br/>aggregated_score: 5.2<br/>confidence: HIGH<br/>trend: improving}"]
    end
    
    subgraph "UI Presentation"
        G["HTML Dashboard<br/>Charts & Tables<br/>Interactive Views"]
    end
    
    A --> C
    B --> D
    C --> E
    D --> E
    E --> F
    F --> G
    
    style C fill:#ffe1f5
    style D fill:#ffe1f5
    style E fill:#e1ffe1
    style F fill:#f5e1ff
    style G fill:#ffe1e1
```

### Data Format Examples

**1. Article JSON** (`output/googlenews_rss/TSLA/001_2024-11-22.json`)
```json
{
  "source": "googlenews_rss",
  "topic": "TSLA",
  "title": "Tesla Reports Record Q4 Deliveries",
  "url": "https://example.com/article",
  "published_at": "2024-11-22T10:30:00+00:00",
  "content": "Full article text...",
  "score": 0.85
}
```

**2. Market Data JSON** (`output/market_data/TSLA_market_data.json`)
```json
{
  "symbol": "TSLA",
  "company_name": "Tesla, Inc.",
  "latest_price": 242.50,
  "price_change_percent": 10.86,
  "period_high": 248.30,
  "period_low": 215.20,
  "average_volume": 120000000,
  "data_period_days": 30,
  "fetched_at": "2024-11-22T12:00:00+00:00"
}
```

**3. Score JSON** (`output/llm_scores/TSLA/001_2024-11-22_score.json`)
```json
{
  "article_file": "output/googlenews_rss/TSLA/001_2024-11-22.json",
  "topic": "TSLA",
  "title": "Tesla Reports Record Q4 Deliveries",
  "llm_score": 6.75,
  "llm_explanation": "Extremely positive sentiment due to record deliveries exceeding expectations...",
  "model": "gpt-4o-mini",
  "scored_at": "2024-11-22T14:30:00+00:00",
  "market_context_used": true
}
```

**4. Recommendation JSON** (`output/recommendations/TSLA_recommendation.json`)
```json
{
  "topic": "TSLA",
  "recommendation": "BUY",
  "aggregated_score": 5.25,
  "confidence": "HIGH",
  "num_articles": 8,
  "trend": "improving",
  "reasoning": "Strong positive sentiment across 8 recent articles with improving trend...",
  "risk_factors": [],
  "generated_at": "2024-11-22T15:00:00+00:00"
}
```

---

## Error Handling and Recovery

VUTS is designed to be resilient to failures at any stage:

```mermaid
flowchart TD
    START([Normal Processing]) --> DETECT{Error Detected?}
    
    DETECT -->|No| CONTINUE[Continue Processing]
    DETECT -->|Yes| CLASSIFY{Error Type?}
    
    CLASSIFY -->|Network Error| RETRY[Retry with Backoff]
    CLASSIFY -->|API Rate Limit| WAIT[Wait & Retry]
    CLASSIFY -->|Invalid Data| SKIP[Skip Item & Log]
    CLASSIFY -->|Parse Error| SKIP
    CLASSIFY -->|Critical Error| ABORT[Abort & Report]
    
    RETRY --> SUCCESS{Success?}
    SUCCESS -->|Yes| CONTINUE
    SUCCESS -->|No: Max Retries| SKIP
    
    WAIT --> SUCCESS
    
    SKIP --> LOG[Log Error Details]
    LOG --> CONTINUE
    
    ABORT --> CLEANUP[Save Partial Results]
    CLEANUP --> END([End with Error Status])
    
    CONTINUE --> MORE{More Items?}
    MORE -->|Yes| PROCESS[Process Next Item]
    MORE -->|No| COMPLETE([Complete Successfully])
    
    PROCESS --> DETECT
    
    style START fill:#e1f5ff
    style COMPLETE fill:#00ff00
    style END fill:#ff0000
```

### Error Handling Strategies

**Network Errors**: Temporary network failures (timeouts, connection refused) trigger exponential backoff retry (3 attempts with 2x, 4x, 8x delays).

**API Rate Limits**: When hitting OpenAI or news API rate limits, the system waits for the specified retry-after period before continuing.

**Invalid Data**: Articles with missing required fields or scores outside the valid range are skipped and logged. Processing continues with remaining items.

**Parse Errors**: If LLM response cannot be parsed (malformed output), the article is skipped and an error is logged. The system does not halt.

**Critical Errors**: Fatal errors (configuration file not found, API key invalid) cause graceful shutdown with error reporting and saving of any partial results.

### Graceful Degradation

- **No Market Data**: If market data fetching fails, LLM analysis continues without market context
- **Partial Scores**: Recommendations can be generated even if some articles failed to score
- **Insufficient Data**: Topics with <2 articles receive "HOLD" recommendation with "insufficient data" explanation
- **API Unavailable**: System can operate in demo mode with mock data for testing

---

## Related Documentation

This document provides the high-level overview. For deeper dives into specific areas:

### Technical Documentation
- **[Architecture Diagrams](Architecture_Diagrams.md)** - Detailed Mermaid diagrams of system components
- **[Development Outline](Development_Outline.md)** - Complete project phases and feature roadmap
- **[Technical Setup Guide](Technical_Setup_Guide.md)** - Developer environment setup and configuration

### Usage Guides
- **[Quick Start Guide](Quick_Start_Guide.md)** - Get running in 5 minutes
- **[Workflow Guide](Workflow_Guide.md)** - Complete workflow with examples for all phases
- **[Hands-On Tutorial](Tutorial_Hands_On.md)** - Interactive tutorial for new users

### Module Documentation
- **[Fetching Module README](../scratch/src/fetching/README.md)** - News collection implementation details
- **[LLM Module README](../scratch/src/llm/README.md)** - Sentiment analysis and prompt engineering
- **[Scoring Module README](../scratch/src/scoring/README.md)** - Recommendation engine algorithms
- **[UI Module README](../scratch/src/ui/README.md)** - Web interface features and API
- **[Notifications Module README](../scratch/src/notifications/README.md)** - Alert system and subscriptions

### Wiki Pages
- **[Wiki Home](../wiki/Home.md)** - Wiki navigation and overview
- **[Getting Started](../wiki/Getting-Started.md)** - Setup instructions
- **[Architecture](../wiki/Architecture.md)** - System architecture overview

---

## Summary

VUTS processes financial news through six distinct stages:

1. **Data Collection** - Fetches news and market data from multiple sources
2. **Validation** - Filters, deduplicates, and validates data quality
3. **Analysis** - Uses LLM to score sentiment with market context
4. **Aggregation** - Combines scores with weighting and temporal decay
5. **Recommendation** - Generates actionable Buy/Hold/Sell signals
6. **Delivery** - Presents results through UI and sends notifications

The system is designed for reliability, cost-efficiency, and transparency. Every score includes an explanation, every recommendation includes reasoning, and the entire pipeline is observable through logs and the Web UI.

For hands-on experience, try the demos:
```bash
cd scratch

# Complete mock workflow (no API keys needed)
python demos/demo_workflow.py

# Real OpenAI API analysis
export OPENAI_API_KEY="your-key"
python demos/demo_openai_api.py

# Recommendation engine demo
python demos/demo_recommendations.py
```
