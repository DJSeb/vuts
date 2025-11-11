# VUTS Demo Applications

This directory contains demonstration scripts that showcase the VUTS sentiment analysis workflow.

## Available Demos

### 1. demo_workflow.py - Mock Workflow Demo

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

### 2. demo_openai_api.py - OpenAI API Demo

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

## Output Directories

Both demos create output in separate directories to avoid conflicts:

- `demo_workflow.py` → `demos/demo_output/`
- `demo_openai_api.py` → `demos/demo_output_openai/`

These directories are in `.gitignore` and won't be committed to the repository.

## Cleaning Up

To remove demo output:

```bash
cd scratch
rm -rf demos/demo_output demos/demo_output_openai
```

## Next Steps

After running the demos:

1. **Understand the workflow**: Review the demo output to see how articles are structured and scored
2. **Read the documentation**: See `docs/Quick_Start_Guide.md` and `docs/Workflow_Guide.md`
3. **Try the Web UI**: Run `python run_ui.py` and view the demo results at http://localhost:5000
4. **Run production workflows**: Use the `vuts` CLI to fetch real news and analyze it

## Tips

- Run `demo_workflow.py` first to understand the system without any costs
- Use `demo_openai_api.py` when you want to verify the OpenAI integration works
- Check the generated articles to see examples of the expected data format
- The demo articles cover diverse scenarios (positive, negative, neutral) to test score ranges
