# VUTS Hands-On Tutorial: Understanding Stock Sentiment

**Welcome!** This guide will walk you through using VUTS to analyze stock news sentiment. No technical background needed - just follow along and try the examples.

## What You'll Learn

By the end of this tutorial, you'll know how to:
- Run the system to analyze news about stocks
- Understand sentiment scores and what they mean
- Generate buy/hold/sell recommendations
- View results in an easy-to-read format

## What is VUTS?

VUTS reads financial news articles about companies and uses AI to determine if the news is positive or negative. Think of it like asking an expert: "Is this news good or bad for investors?"

The system gives each article a score from **-10** (very bad news) to **+10** (very good news).

## Tutorial Overview

We'll go through 3 examples:
1. **Quick Test** - Try the system with fake data (2 minutes)
2. **Real Analysis** - Analyze actual news articles (5 minutes)
3. **View Results** - See everything in a web dashboard (2 minutes)

---

## Example 1: Quick Test (No Setup Required)

This example uses pre-made fake articles so you can see how the system works immediately.

### Step 1: Open Your Terminal

On **Mac**: Open "Terminal" from Applications
On **Windows**: Open "Command Prompt" or "PowerShell"
On **Linux**: Open your preferred terminal

### Step 2: Navigate to the Project

```bash
cd /path/to/vuts/scratch
```

*Replace `/path/to/vuts` with where you downloaded VUTS*

### Step 3: Run the Demo

```bash
python demos/demo_workflow.py
```

### What You'll See

The demo creates 2 fake articles:
- **Positive News**: "Tesla Reports Record Quarterly Deliveries"
- **Negative News**: "Tesla Recalls 500,000 Vehicles"

You'll see output like this:

```
=====================================
ARTICLE 1: Tesla Reports Record...
Score: +6.50
Reason: Strong delivery numbers, exceeded expectations, positive analyst response
=====================================
```

**Understanding the Score:**
- **+6.50** means very positive news for investors
- The reason explains why the AI gave this score
- Scores range from -10 (terrible) to +10 (excellent)

### Try It Yourself

After the demo finishes:
1. Look in the `demo_output` folder
2. Open any file ending in `_score.json`
3. See the detailed analysis for each article

---

## Example 2: Analyzing Real News

Now let's analyze actual news articles using AI. This requires an OpenAI account (costs about 1 cent for 10 articles).

### What You Need

An OpenAI API key (get one at https://platform.openai.com/api-keys)

### Step 1: Set Your API Key

**On Mac/Linux:**
```bash
export OPENAI_API_KEY="your-key-here"
```

**On Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your-key-here"
```

### Step 2: Run the Demo

```bash
python demos/demo_openai_api.py
```

This demo:
1. Creates articles about AMD, Nvidia, and Broadcom
2. Sends them to AI for analysis
3. Shows you the sentiment scores

### What You'll See

```
Analyzing: AMD Unveils Next-Gen EPYC Processors...
✓ Score: +5.75
✓ Explanation: New product launch, positive analyst response, stock up 4.2%

Analyzing: Broadcom Supply Chain Issues...
✓ Score: -3.25
✓ Explanation: Supply constraints, delayed shipments, concerns about Q3 targets
```

### Understanding Your Results

Each article gets:
- A **score** showing how positive/negative the news is
- An **explanation** of why the AI assigned that score
- Results saved to `demo_output/llm_scores/`

**Score Guide:**
- **+7 to +10**: Extremely positive (major breakthrough, huge success)
- **+4 to +7**: Very positive (beat earnings, big wins)
- **+2 to +4**: Moderately positive (good news)
- **0 to +2**: Slightly positive
- **0**: Neutral
- **-2 to 0**: Slightly negative
- **-4 to -2**: Moderately negative (concerns, warnings)
- **-7 to -4**: Very negative (missed targets, losses)
- **-10 to -7**: Extremely negative (crisis, scandal)

---

## Example 3: Getting Investment Recommendations

The system can combine multiple articles to give you a recommendation: Should you buy, hold, or sell?

### Step 1: Run the Recommendation Demo

```bash
python demos/demo_recommendations.py
```

This demo:
1. Uses pre-analyzed articles (no API key needed)
2. Combines scores from multiple articles
3. Generates a buy/hold/sell recommendation

### What You'll See

```
Topic: DEMO_STOCK
Average Score: +4.35
Recommendation: BUY
Confidence: HIGH (85%)

Reasoning:
- 5 out of 6 articles are positive
- Recent news is more positive than older news (improving trend)
- Strong earnings beat and product announcements
- Only minor concern about supply chain

Risk Factors:
- One article mentions supply chain concerns
- Market volatility could affect results
```

### Understanding Recommendations

The system gives 5 possible recommendations:

1. **STRONG BUY** (Score: +5.0 or higher)
   - Very positive news overall
   - High confidence the stock will do well
   
2. **BUY** (Score: +2.5 to +5.0)
   - Positive news overall
   - Good opportunity to invest
   
3. **HOLD** (Score: -2.5 to +2.5)
   - Neutral or mixed news
   - Wait and see what happens
   
4. **SELL** (Score: -5.0 to -2.5)
   - Negative news overall
   - Consider reducing your position
   
5. **STRONG SELL** (Score: -5.0 or lower)
   - Very negative news
   - High risk, consider selling

**Confidence Levels:**
- **HIGH**: Lots of recent articles, all agree
- **MEDIUM**: Some articles, generally consistent
- **LOW**: Few articles or conflicting signals

---

## Example 4: Using the Web Interface

The easiest way to view results is through the web dashboard.

### Step 1: Start the Web Server

```bash
./vuts ui
```

Or:
```bash
python run_ui.py
```

### Step 2: Open Your Browser

Go to: **http://localhost:5000**

### What You'll See

The dashboard shows:
- **Overview**: All stocks and their average sentiment
- **Individual Stocks**: Click any stock to see all its articles
- **Charts**: Visual representation of sentiment over time
- **Notifications**: Alerts for extreme news (very positive or negative)

### Navigate the Interface

- **Home**: Dashboard with all topics
- **Topics**: Detailed view of each stock
- **Notifications** (bell icon): Important alerts
- **Config**: Settings and commands

---

## Working with Your Own Stocks

Now that you've tried the demos, here's how to analyze stocks you care about.

### Step 1: Create a Configuration File

Create a file called `my_stocks.json`:

```json
{
  "topics": [ "AAPL", "GOOGL", "MSFT" ],
  "sources": [ "googlenews_rss" ],
  "max_age_days": 7,
  "fetch_full_content": true,
  "fetch_full_top_n": 5
}
```

**What this means:**
- `topics`: Stock symbols you want to track
- `sources`: Where to get news from
- `max_age_days`: How far back to look for news (7 days)
- `fetch_full_content`: Download complete articles (not just headlines)

### Step 2: Get the News

```bash
./vuts fetch --config my_stocks.json --output-dir my_results
```

This downloads recent news articles about your stocks.

### Step 3: Analyze the Sentiment

```bash
./vuts analyze --data-dir my_results --max-articles 10
```

This sends articles to AI for scoring. Remember to set your `OPENAI_API_KEY` first!

### Step 4: Generate Recommendations

```bash
python src/scoring/recommendation_engine.py \
    --data-dir my_results/llm_scores \
    --output-dir my_results/recommendations
```

### Step 5: View Your Results

Option A - Web Interface:
```bash
./vuts ui --data-dir my_results
```

Option B - Command Line:
```bash
cat my_results/recommendations/AAPL_recommendation.json
```

---

## Understanding Costs

Using the AI analysis costs money, but it's very cheap:

- **Cost per article**: About $0.0006 (less than 1/10th of a penny)
- **10 articles**: About $0.006 (half a penny)
- **100 articles**: About $0.06 (6 cents)

**Example:**
Analyzing 5 stocks with 10 articles each = 50 articles = **3 cents total**

---

## Common Questions

### Q: Do I need to pay for anything?

Yes, you need an OpenAI API key to analyze articles. They charge based on usage (see costs above). The news collection is free.

### Q: How accurate is the sentiment analysis?

The AI is pretty good at understanding news, but it's not perfect. Always read the articles yourself before making investment decisions. **This is not financial advice!**

### Q: Can I analyze more than stock news?

Yes! You can analyze news about any topic. Just change the `topics` in your configuration file.

### Q: What if I get an error?

Common issues:
- **"No articles found"**: Articles might be too old. Increase `max_age_days`
- **"API key invalid"**: Check your OpenAI API key is correct
- **"No module named..."**: Run `pip install -r requirements.txt`

### Q: How often should I run this?

It depends on your needs:
- **Daily traders**: Run once or twice per day
- **Long-term investors**: Run once per week
- **Casual monitoring**: Run whenever you're curious

---

## Next Steps

Now that you've completed the tutorial:

1. **Experiment**: Try different stocks and see their sentiment
2. **Compare**: Look at how sentiment changes over time
3. **Learn**: Read the articles to understand why scores are high or low
4. **Customize**: Adjust settings to match your needs

### Want More Details?

- **Quick Reference**: See `Quick_Start_Guide.md` for command examples
- **All Features**: See `Workflow_Guide.md` for advanced usage
- **Technical Details**: See `Technical_Setup_Guide.md` for developers

---

## Important Disclaimer

⚠️ **This tool is for information and education only.**

- Do NOT make investment decisions based solely on these scores
- Always do your own research
- Consult with a financial advisor
- Past performance doesn't predict future results
- The AI can make mistakes

Think of VUTS as a helpful assistant that summarizes news sentiment, not as financial advice.

---

## Summary: What You Learned

✅ How to run the system with demo data
✅ How to analyze real news articles with AI
✅ How to interpret sentiment scores (-10 to +10)
✅ How to get buy/hold/sell recommendations
✅ How to use the web interface
✅ How to analyze your own stocks
✅ What the costs are (about 1/10th penny per article)

**Remember**: Start small, experiment with demos, and understand the results before using it for real investment research.

Happy analyzing! 📊
