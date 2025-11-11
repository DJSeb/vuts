#!/usr/bin/env python3
"""
Demonstration script showing the complete workflow without requiring API keys.

This creates mock data and demonstrates how all the components work together.
"""

import json
import datetime
from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm.sentiment_analyzer import (
    load_prompt_template,
    format_prompt,
    parse_llm_response,
    find_article_files,
    save_llm_score
)
from market.data_fetcher import format_market_context


def create_demo_data(base_dir: Path):
    """Create demonstration article and market data."""
    print("=" * 70)
    print("CREATING DEMO DATA")
    print("=" * 70)
    
    # Create test articles
    articles_dir = base_dir / "demo_source" / "TSLA"
    articles_dir.mkdir(parents=True, exist_ok=True)
    
    # Article 1: Positive news
    article1 = {
        "source": "demo_source",
        "topic": "TSLA",
        "title": "Tesla Reports Record Quarterly Deliveries, Exceeds Expectations",
        "url": "https://example.com/article1",
        "published_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "content": """
Tesla Inc. announced record vehicle deliveries for Q4 2024, significantly exceeding 
Wall Street expectations. The electric vehicle manufacturer delivered 485,000 vehicles 
during the quarter, up 35% year-over-year and above analyst estimates of 450,000.

CEO Elon Musk attributed the strong performance to improved production efficiency at 
the company's factories in Texas and Germany, along with robust demand in both North 
American and European markets. The Model Y continues to be the best-selling electric 
vehicle globally.

Financial analysts praised the results, with several raising their price targets. 
Morgan Stanley analyst Adam Jonas called the delivery numbers "impressive" and noted 
that Tesla's manufacturing scale advantages continue to widen relative to competitors.

The company also announced plans to expand its Supercharger network by 50% in 2025 
and confirmed that its next-generation vehicle platform remains on track for 
production in late 2025.
""".strip(),
        "score": 0.7
    }
    
    with open(articles_dir / "001_positive_news.json", "w") as f:
        json.dump(article1, f, indent=2)
    print(f"✓ Created positive article: {article1['title'][:60]}...")
    
    # Article 2: Negative news
    article2 = {
        "source": "demo_source",
        "topic": "TSLA",
        "title": "Tesla Recalls 500,000 Vehicles Over Safety Concerns",
        "url": "https://example.com/article2",
        "published_at": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=6)).isoformat(),
        "content": """
Tesla is recalling approximately 500,000 vehicles in the United States due to a 
software issue that could affect the rearview camera display. The National Highway 
Traffic Safety Administration (NHTSA) announced the recall today, affecting Model 3 
and Model Y vehicles manufactured between 2022 and 2024.

According to NHTSA documents, the rearview camera image may not display immediately 
when shifting into reverse, increasing the risk of a crash. This is the third major 
recall for Tesla this year, raising questions about the company's quality control 
processes.

Consumer advocacy groups have criticized Tesla's approach to vehicle safety, noting 
that while the issue can be fixed through an over-the-air software update, the 
frequency of recalls is concerning. "Tesla needs to prioritize safety over rapid 
feature deployment," said a spokesperson for the Center for Auto Safety.

Tesla stock declined 2.3% in after-hours trading following the announcement.
""".strip(),
        "score": -0.4
    }
    
    with open(articles_dir / "002_negative_news.json", "w") as f:
        json.dump(article2, f, indent=2)
    print(f"✓ Created negative article: {article2['title'][:60]}...")
    
    # Create market data
    market_data_dir = base_dir / "market_data"
    market_data_dir.mkdir(parents=True, exist_ok=True)
    
    market_data = {
        "symbol": "TSLA",
        "company_name": "Tesla, Inc.",
        "sector": "Consumer Cyclical",
        "market_cap": 850000000000,
        "period_days": 30,
        "start_date": (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat(),
        "end_date": datetime.datetime.now().isoformat(),
        "latest_price": 242.50,
        "first_price": 218.75,
        "price_change": 23.75,
        "price_change_percent": 10.86,
        "period_high": 248.30,
        "period_low": 215.20,
        "avg_volume": 125000000,
        "data_points": 21,
        "daily_prices": [
            {"date": "2024-11-04", "open": 218.75, "high": 225.30, "low": 217.50, "close": 223.80, "volume": 130000000},
            {"date": "2024-11-05", "open": 223.80, "high": 228.40, "low": 222.10, "close": 226.50, "volume": 142000000},
            {"date": "2024-11-06", "open": 226.50, "high": 232.80, "low": 225.90, "close": 231.20, "volume": 155000000},
            {"date": "2024-11-07", "open": 231.20, "high": 235.60, "low": 229.80, "close": 233.40, "volume": 128000000},
            {"date": "2024-11-08", "open": 233.40, "high": 238.90, "low": 232.50, "close": 237.10, "volume": 145000000},
            {"date": "2024-11-09", "open": 237.10, "high": 242.80, "low": 236.20, "close": 241.60, "volume": 138000000},
            {"date": "2024-11-10", "open": 241.60, "high": 248.30, "low": 240.50, "close": 242.50, "volume": 120000000},
        ],
        "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    with open(market_data_dir / "TSLA_market_data.json", "w") as f:
        json.dump(market_data, f, indent=2)
    print(f"✓ Created market data: TSLA (${market_data['latest_price']}, +{market_data['price_change_percent']:.2f}%)")
    
    return articles_dir, market_data_dir


def demonstrate_prompt_formatting(prompt_template: str, article: dict, market_data: dict):
    """Show how the prompt is formatted with article and market context."""
    print("\n" + "=" * 70)
    print("PROMPT FORMATTING DEMONSTRATION")
    print("=" * 70)
    
    # Format market context
    market_context = format_market_context(market_data)
    
    # Format full prompt
    full_prompt = format_prompt(prompt_template, article, market_context)
    
    print("\n--- MARKET CONTEXT (prepended to prompt) ---")
    print(market_context[:500] + "..." if len(market_context) > 500 else market_context)
    
    print("\n--- ARTICLE INFORMATION IN PROMPT ---")
    print(f"Title: {article['title']}")
    print(f"Topic: {article['topic']}")
    print(f"Content length: {len(article['content'])} characters")
    
    print("\n--- FULL PROMPT LENGTH ---")
    print(f"Total prompt size: {len(full_prompt)} characters")
    print("(This is what gets sent to the LLM)")


def demonstrate_scoring(articles_dir: Path):
    """Demonstrate the scoring process with mock scores."""
    print("\n" + "=" * 70)
    print("SENTIMENT SCORING DEMONSTRATION")
    print("=" * 70)
    
    # Find articles
    articles = list(articles_dir.glob("*.json"))
    
    print(f"\nFound {len(articles)} articles to score")
    
    # Mock responses (these would come from the LLM)
    mock_responses = {
        "001_positive_news.json": "SCORE: +6.75\nEXPLANATION: Record deliveries exceed expectations. Strong YoY growth of 35%. Improved production efficiency. Positive analyst response. Expansion plans announced.",
        "002_negative_news.json": "SCORE: -4.25\nEXPLANATION: Major recall of 500K vehicles. Third recall this year raises quality concerns. Consumer advocacy criticism. Stock declined in after-hours trading."
    }
    
    llm_scores_dir = articles_dir.parent.parent / "llm_scores"
    
    for article_file in articles:
        print(f"\n--- Processing: {article_file.name} ---")
        
        with open(article_file) as f:
            article = json.load(f)
        
        print(f"Title: {article['title'][:60]}...")
        
        # Get mock response
        mock_response = mock_responses.get(article_file.name, "SCORE: 0.00\nEXPLANATION: No information available.")
        print(f"LLM Response:\n{mock_response}")
        
        # Parse score and explanation
        score, explanation = parse_llm_response(mock_response)
        
        if score is not None:
            print(f"\nParsed Score: {score:+.2f}")
            print(f"Parsed Explanation: {explanation}")
            
            # Interpret the score
            if score >= 7.0:
                interpretation = "EXTREMELY POSITIVE"
            elif score >= 4.0:
                interpretation = "VERY POSITIVE"
            elif score >= 2.0:
                interpretation = "MODERATELY POSITIVE"
            elif score >= 0.5:
                interpretation = "SLIGHTLY POSITIVE"
            elif score > -0.5:
                interpretation = "NEUTRAL"
            elif score > -2.0:
                interpretation = "SLIGHTLY NEGATIVE"
            elif score > -4.0:
                interpretation = "MODERATELY NEGATIVE"
            elif score > -7.0:
                interpretation = "VERY NEGATIVE"
            else:
                interpretation = "EXTREMELY NEGATIVE"
            
            print(f"Interpretation: {interpretation}")
            
            # Save score and explanation
            save_llm_score(article_file, article, score, explanation, llm_scores_dir, "demo-model")
            
            # Show saved file content
            score_file = llm_scores_dir / article['topic'] / f"{article_file.stem}_score.json"
            with open(score_file) as f:
                saved_data = json.load(f)
            
            print(f"Saved to: {score_file}")
        else:
            print("✗ Invalid response")


def show_results(llm_scores_dir: Path):
    """Display the final results."""
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    
    score_files = list(llm_scores_dir.rglob("*_score.json"))
    
    print(f"\nTotal articles analyzed: {len(score_files)}")
    
    scores = []
    for score_file in sorted(score_files):
        with open(score_file) as f:
            data = json.load(f)
        scores.append(data)
    
    print("\n{:<15} {:<10} {:<60}".format("Topic", "Score", "Title"))
    print("-" * 85)
    
    for data in scores:
        title = data['title'][:57] + "..." if len(data['title']) > 60 else data['title']
        score_color = "↑" if data['llm_score'] > 0 else "↓" if data['llm_score'] < 0 else "→"
        print(f"{data['topic']:<15} {score_color} {data['llm_score']:+6.2f}   {title}")
        if 'llm_explanation' in data:
            explanation = data['llm_explanation'][:75] + "..." if len(data['llm_explanation']) > 75 else data['llm_explanation']
            print(f"{'':15}   └─ {explanation}")
    
    avg_score = sum(d['llm_score'] for d in scores) / len(scores) if scores else 0
    print("-" * 85)
    print(f"Average sentiment: {avg_score:+.2f}")


def main():
    """Run the complete demonstration."""
    print("\n" + "=" * 70)
    print("LLM SENTIMENT ANALYSIS - COMPLETE WORKFLOW DEMO")
    print("=" * 70)
    print("\nThis demonstration shows how all components work together")
    print("without requiring actual API keys or network access.\n")
    
    # Setup
    demo_dir = Path(__file__).parent / "demo_output"
    demo_dir.mkdir(exist_ok=True)
    
    # Load prompt template
    prompt_file = Path(__file__).parent.parent / "src" / "llm" / "sentiment_prompt.txt"
    prompt_template = load_prompt_template(prompt_file)
    
    # Create demo data
    articles_dir, market_data_dir = create_demo_data(demo_dir)
    
    # Load one article for demonstration
    article_file = articles_dir / "001_positive_news.json"
    with open(article_file) as f:
        article = json.load(f)
    
    market_file = market_data_dir / "TSLA_market_data.json"
    with open(market_file) as f:
        market_data = json.load(f)
    
    # Demonstrate prompt formatting
    demonstrate_prompt_formatting(prompt_template, article, market_data)
    
    # Demonstrate scoring
    demonstrate_scoring(articles_dir)
    
    # Show final results
    llm_scores_dir = demo_dir / "llm_scores"
    show_results(llm_scores_dir)
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print(f"\nDemo files saved to: {demo_dir}")
    print("\nTo run with real data, follow the instructions in WORKFLOW_GUIDE.md")
    print("\nKey files created:")
    print(f"  - Articles: {articles_dir}")
    print(f"  - Market data: {market_data_dir}")
    print(f"  - Sentiment scores: {llm_scores_dir}")
    
    return 0


if __name__ == "__main__":
    exit(main())
