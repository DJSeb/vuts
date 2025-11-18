"""
Demo: Phase 4 Recommendation Engine

This demonstration shows how the Phase 4 recommendation engine works
without requiring actual API keys or network access.

It creates mock article scores and generates investment recommendations.
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scoring.recommendation_engine import process_topic_recommendation


def create_demo_scores(output_dir: Path, topic: str):
    """Create demo article scores for testing."""
    scores_dir = output_dir / "llm_scores" / topic
    scores_dir.mkdir(parents=True, exist_ok=True)
    
    now = datetime.now(timezone.utc)
    
    # Create a mix of positive and slightly negative articles
    # to show realistic scenario
    articles = [
        {
            'llm_score': 7.5,
            'source': 'finnhub',
            'published_at': (now - timedelta(days=1)).isoformat(),
            'title': 'Strong Quarterly Results Exceed Expectations',
            'llm_explanation': 'Revenue up 25% YoY, beat analyst estimates by 15%'
        },
        {
            'llm_score': 6.0,
            'source': 'bingnews',
            'published_at': (now - timedelta(days=2)).isoformat(),
            'title': 'Analyst Upgrades to Buy Rating',
            'llm_explanation': 'Price target raised to $350, citing strong fundamentals'
        },
        {
            'llm_score': 5.5,
            'source': 'googlenews_rss',
            'published_at': (now - timedelta(days=3)).isoformat(),
            'title': 'New Product Launch Receives Positive Reviews',
            'llm_explanation': 'Industry experts praise innovative features and design'
        },
        {
            'llm_score': 4.0,
            'source': 'bingnews',
            'published_at': (now - timedelta(days=5)).isoformat(),
            'title': 'Expansion Plans Announced for European Market',
            'llm_explanation': 'Company opens 50 new locations, hiring 2,000 employees'
        },
        {
            'llm_score': -1.5,
            'source': 'googlenews_rss',
            'published_at': (now - timedelta(days=6)).isoformat(),
            'title': 'Minor Supply Chain Disruption Reported',
            'llm_explanation': 'Temporary delays in one manufacturing facility'
        },
        {
            'llm_score': 3.5,
            'source': 'finnhub',
            'published_at': (now - timedelta(days=8)).isoformat(),
            'title': 'Partnership with Major Tech Company',
            'llm_explanation': 'Strategic alliance to improve product offerings'
        }
    ]
    
    score_files = []
    for i, article in enumerate(articles):
        file_path = scores_dir / f"{i+1:03d}_article_score.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(article, f, indent=2)
        score_files.append(file_path)
    
    return score_files


def print_header(title, char='='):
    """Print a formatted header."""
    print()
    print(char * 80)
    print(title)
    print(char * 80)


def print_recommendation_details(rec_data):
    """Print detailed recommendation information."""
    rec = rec_data['recommendation']
    agg = rec_data['aggregation']
    trend = rec_data['trend']
    
    print(f"\n{'=' * 80}")
    print(f"RECOMMENDATION FOR: {rec_data['topic']}")
    print(f"{'=' * 80}")
    
    # Main recommendation
    print(f"\n🎯 RECOMMENDATION: {rec['recommendation']}")
    print(f"   Confidence: {rec['confidence_level']} ({agg['confidence']:.0%})")
    print(f"   Score: {agg['score']:.2f} / 10.00")
    print(f"   Trend: {rec['trend_indicator']}")
    
    # Score breakdown
    print(f"\n📊 SCORE BREAKDOWN:")
    print(f"   Articles Analyzed: {agg['article_count']}")
    print(f"   Weighted Count: {agg['weighted_count']:.2f}")
    dist = agg['distribution']
    print(f"   Distribution:")
    print(f"     • Positive: {dist['positive']} articles")
    print(f"     • Negative: {dist['negative']} articles")
    print(f"     • Neutral: {dist['neutral']} articles")
    
    # Trend analysis
    print(f"\n📈 TREND ANALYSIS:")
    print(f"   {trend['description']}")
    print(f"   Recent average: {trend['recent_avg']:.2f}")
    print(f"   Older average: {trend['older_avg']:.2f}")
    print(f"   Trend score: {trend['trend_score']:.2f}")
    
    # Reasoning
    print(f"\n💡 REASONING:")
    # Split reasoning into sentences for better readability
    sentences = rec['reasoning'].split('. ')
    for sentence in sentences:
        if sentence:
            print(f"   • {sentence.strip()}{'.' if not sentence.endswith('.') else ''}")
    
    # Risk factors
    print(f"\n⚠️  RISK FACTORS:")
    for i, risk in enumerate(rec['risk_factors'], 1):
        print(f"   {i}. {risk}")
    
    # Recent articles
    print(f"\n📰 RECENT ARTICLES (Top 3):")
    for i, article in enumerate(rec_data['articles'][:3], 1):
        print(f"\n   {i}. {article['title']}")
        print(f"      Score: {article['score']:+.2f}")
        print(f"      Source: {article['source']} (weight: {article['source_weight']:.2f})")
        print(f"      Published: {article['published_at'][:10]}")
        print(f"      Temporal weight: {article['temporal_weight']:.3f}")
        print(f"      Explanation: {article['explanation'][:80]}...")


def main():
    """Run the recommendation engine demo."""
    print_header("PHASE 4: RECOMMENDATION ENGINE - DEMO", '=')
    print("\nThis demo shows how the Phase 4 recommendation engine generates")
    print("actionable investment recommendations from article sentiment scores.")
    print("\nNo API keys or network access required!")
    
    # Create demo output directory
    demo_dir = Path(__file__).parent / "demo_output_recommendations"
    if demo_dir.exists():
        shutil.rmtree(demo_dir)
    demo_dir.mkdir(parents=True)
    
    print_header("STEP 1: Creating Mock Article Scores", '-')
    print("\nGenerating 6 articles with sentiment scores...")
    
    topic = "DEMO_STOCK"
    score_files = create_demo_scores(demo_dir, topic)
    
    print(f"✓ Created {len(score_files)} article score files")
    print(f"  Location: {demo_dir / 'llm_scores' / topic}")
    
    # Show sample scores
    print("\nSample scores:")
    with open(score_files[0], 'r') as f:
        article = json.load(f)
        print(f"  • {article['title']}")
        print(f"    Score: {article['llm_score']:+.2f}, Source: {article['source']}")
    with open(score_files[4], 'r') as f:
        article = json.load(f)
        print(f"  • {article['title']}")
        print(f"    Score: {article['llm_score']:+.2f}, Source: {article['source']}")
    
    print_header("STEP 2: Running Recommendation Engine", '-')
    print("\nProcessing scores through Phase 4 engine...")
    print("  1. Aggregating scores with source and temporal weights")
    print("  2. Analyzing sentiment trends")
    print("  3. Generating recommendation with explainability")
    
    # Generate recommendation
    rec_output_dir = demo_dir / "recommendations"
    result = process_topic_recommendation(topic, score_files, rec_output_dir)
    
    if not result:
        print("\n❌ Failed to generate recommendation")
        return 1
    
    print(f"\n✓ Recommendation generated successfully")
    print(f"  Output file: {rec_output_dir / f'{topic}_recommendation.json'}")
    
    print_header("STEP 3: Recommendation Results", '-')
    print_recommendation_details(result)
    
    print_header("STEP 4: Understanding the Results", '-')
    print("\n📚 Key Concepts:")
    print("\n1. SOURCE WEIGHTING:")
    print("   Different news sources have different reliability weights.")
    print("   Finnhub (1.0) > Bing News (0.9) > Google News (0.85)")
    print("\n2. TEMPORAL DECAY:")
    print("   Recent articles matter more than older ones.")
    print("   Articles lose 50% weight every 7 days (half-life).")
    print("\n3. CONFIDENCE SCORING:")
    print("   Based on article count, recency, and score consistency.")
    print("   LOW (<60%) → recommendation downgraded to HOLD")
    print("\n4. TREND ANALYSIS:")
    print("   Compares recent vs older articles to detect sentiment shifts.")
    print("   • Improving: Recent sentiment more positive")
    print("   • Declining: Recent sentiment more negative")
    print("   • Stable: Consistent sentiment over time")
    print("\n5. RECOMMENDATION THRESHOLDS:")
    print("   STRONG BUY: score ≥ +5.0")
    print("   BUY: score ≥ +2.5")
    print("   HOLD: -2.5 < score < +2.5 (or low confidence)")
    print("   SELL: score ≤ -2.5")
    print("   STRONG SELL: score ≤ -5.0")
    
    print_header("NEXT STEPS", '-')
    print("\n1. VIEW THE OUTPUT:")
    print(f"   cat {rec_output_dir / f'{topic}_recommendation.json'}")
    print("\n2. RUN WITH REAL DATA:")
    print("   # Step 1: Fetch news")
    print("   ./vuts fetch --config example_data/copilot-gpt5-cfg.json --output-dir output")
    print("\n   # Step 2: Analyze sentiment")
    print("   ./vuts analyze --data-dir output --max-articles 10")
    print("\n   # Step 3: Generate recommendations")
    print("   python src/scoring/recommendation_engine.py \\")
    print("       --data-dir output/llm_scores \\")
    print("       --output-dir output/recommendations")
    print("\n3. INTEGRATE WITH UI:")
    print("   The web UI (Phase 5) will display these recommendations")
    print("   in a user-friendly dashboard.")
    
    print_header("DEMO COMPLETE", '=')
    print(f"\n✓ Generated recommendation: {result['recommendation']['recommendation']}")
    print(f"✓ Output saved to: {rec_output_dir}")
    print("\n⚠️  DISCLAIMER: This is for educational purposes only.")
    print("   Not financial advice. Always do your own research.")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
