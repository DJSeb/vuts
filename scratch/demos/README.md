# VUTS Demo Applications

This directory contains demonstration scripts that showcase the VUTS sentiment analysis workflow.

## Available Demos

### 1. demo_real_world.py - Large-Scale "Real World" Demo ⭐ NEW

**No API keys required** (but optional for real analysis) - Comprehensive demonstration at scale.

```bash
cd scratch
python demos/demo_real_world.py

# Optional: Use real OpenAI analysis
export OPENAI_API_KEY="your-api-key-here"
python demos/demo_real_world.py
```

**What it does:**
- Generates **12 companies** across multiple sectors (Tech, Finance, Entertainment, Aerospace, etc.)
- Creates **15-23 articles per company** (224 total articles with variance)
- Uses **diverse writing styles and lengths** for realistic variety
- Includes **multiple sentiment types** (positive, negative, neutral) with realistic scenarios
- Generates **complete workflow output**: articles → scores → recommendations
- Creates **investment recommendations** with Buy/Hold/Sell signals

**Companies included:**
- **Technology:** TSLA, AAPL, AMZN, GOOGL, MSFT, META, NVDA, AMD, NFLX
- **Finance:** JPM (JPMorgan Chase)
- **Entertainment:** DIS (Disney)
- **Aerospace:** BA (Boeing)

**Article types generated:**
- Earnings reports (beats and misses)
- Product announcements (successful and unsuccessful)
- Strategic partnerships (positive and problematic)
- Regulatory developments (approvals and investigations)
- Leadership changes (appointments and departures)
- Market analysis (upgrades and downgrades)

**Output:**
- Articles saved to `demo_output_real_world/demo_real_world/{SYMBOL}/`
- Sentiment scores saved to `demo_output_real_world/llm_scores/{SYMBOL}/`
- Recommendations saved to `demo_output_real_world/recommendations/`
- Configuration file: `demo_output_real_world/demo_real_world_config.json`

**Use case:** 
- Showcasing the system at scale with realistic, diverse data
- Demonstrating how VUTS handles large volumes of articles
- Testing the complete workflow including recommendations
- Seeing sentiment analysis across multiple companies and sectors

**Cost (if using OpenAI):** ~$0.13 for ~224 articles with gpt-4o-mini

---

### 2. demo_workflow.py - Mock Workflow Demo

**No API keys required** - Perfect for testing and understanding the system.

```bash
cd scratch
python demos/demo_workflow.py
```

**What it does:**
- Creates 2 mock articles about Tesla (TSLA)
- Creates mock market data
- Demonstrates prompt formatting
- Shows mock sentiment scoring (without calling OpenAI API)
- Displays final results

**Output:**
- Articles saved to `demos/demo_output/demo_source/TSLA/`
- Market data saved to `demos/demo_output/market_data/`
- Sentiment scores saved to `demos/demo_output/llm_scores/TSLA/`

**Use case:** Understanding how the system works without API costs.

---

### 3. demo_openai_api.py - OpenAI API Demo

**Requires OpenAI API key** - Demonstrates real sentiment analysis.

```bash
cd scratch
export OPENAI_API_KEY="your-api-key-here"
python demos/demo_openai_api.py
```

**What it does:**
- Generates 14 articles about AMD, Nvidia, and Broadcom:
  - 4 articles about AMD (Advanced Micro Devices)
  - 5 articles about Nvidia
  - 5 articles about Broadcom (ticker: AVGO)
- Calls the OpenAI API to analyze each article
- Uses the same sentiment analysis workflow as the production system
- Displays results grouped by topic

**Articles generated:**
Each article includes realistic financial news content covering various scenarios:
- Earnings reports (beats and misses)
- Product announcements
- Strategic partnerships
- Regulatory issues
- Customer concerns
- Market reactions

**Metadata included:**
- `source`: "demo_openai_api"
- `topic`: Stock symbol (AMD, NVIDIA, AVGO)
- `title`: Article headline
- `url`: Example URL
- `published_at`: ISO 8601 timestamp
- `content`: Full article text (200-400 words)
- `author`: Author name
- `sentiment_context`: Type of news (e.g., "earnings_beat", "product_announcement")

**Output:**
- Articles saved to `demos/demo_output_openai/demo_openai_api/{TOPIC}/`
- Sentiment scores saved to `demos/demo_output_openai/llm_scores/{TOPIC}/`

**Cost:** Approximately $0.01 (less than 2 cents) for all 14 articles using gpt-4o-mini.

**Use case:** Testing the real OpenAI integration before running production workflows.

---

### 4. demo_recommendations.py - Recommendation Engine Demo

**No API keys required** - Shows the Phase 4 recommendation engine.

```bash
cd scratch
python demos/demo_recommendations.py
```

**What it does:**
- Creates mock article scores for a demo stock
- Demonstrates score aggregation with source and temporal weighting
- Generates investment recommendations (Buy/Hold/Sell)
- Shows trend analysis and confidence scoring
- Provides detailed explainability for recommendations

**Use case:** Understanding how recommendations are generated from sentiment scores.

---

### 5. demo_notifications.py - Notification System Demo

**No API keys required** - Demonstrates the alert system.

```bash
cd scratch
python demos/demo_notifications.py
```

**What it does:**
- Creates sample notifications with different severity levels
- Shows notification persistence and management
- Demonstrates browser notifications and alerts
- Illustrates phone subscription functionality

**Use case:** Testing the notification and alert features.

---

## Output Directories

All demos create output in separate directories to avoid conflicts:

- `demo_real_world.py` → `demo_output_real_world/`
- `demo_workflow.py` → `demos/demo_output/`
- `demo_openai_api.py` → `demos/demo_output_openai/`

These directories are in `.gitignore` and won't be committed to the repository.

## Cleaning Up

To remove demo output:

```bash
cd scratch
rm -rf demos/demo_output demos/demo_output_openai demo_output_real_world
```

## Next Steps

After running the demos:

1. **Start with the real world demo**: Run `python demos/demo_real_world.py` to see the system at scale
2. **Understand the workflow**: Review the demo output to see how articles are structured and scored
3. **Read the documentation**: See `docs/Quick_Start_Guide.md` and `docs/Workflow_Guide.md`
4. **Try the Web UI**: Run `python run_ui.py` and view the demo results at http://localhost:5000
5. **Run production workflows**: Use the `vuts` CLI to fetch real news and analyze it

## Tips

- **Start with `demo_real_world.py`** to see a comprehensive demonstration with 12 companies and 224 articles
- Run `demo_workflow.py` first if you want to understand the system basics without any costs
- Use `demo_openai_api.py` when you want to verify the OpenAI integration works  
- Check the generated articles to see examples of the expected data format
- The demo articles cover diverse scenarios (positive, negative, neutral) to test score ranges
- **Recommendation:** The real world demo showcases the system's ability to handle realistic volumes
