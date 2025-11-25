"""
Recommendation Engine - Scoring & Recommendation System

This module aggregates individual article sentiment scores and generates
actionable investment recommendations (Buy/Hold/Sell) with detailed explanations.

The engine considers:
1. Multiple article scores for each topic
2. Source reliability weights
3. Temporal decay for older news
4. Sentiment trends over time
5. Score distribution and consistency

Author: VUTS Team
Module: Scoring & Recommendation Engine
Created: 2025-11-18
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import sys

# Import shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.datetime_utils import ensure_datetime
from utils.file_utils import safe_json_save, ensure_directory
from utils.logger import log_recommendation_generation


# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# Source reliability weights (higher = more trustworthy)
# These weights reflect the credibility and accuracy of different news sources
SOURCE_WEIGHTS = {
    'finnhub': 1.0,          # Professional financial API
    'bingnews': 0.9,         # Aggregated mainstream news
    'googlenews_rss': 0.85,  # RSS feed aggregation
    'demo_source': 1.0,      # Demo/testing source
    'default': 0.8           # Unknown sources get lower weight
}

# Recommendation thresholds for Buy/Hold/Sell signals
# Based on aggregated sentiment score range: -10.0 to +10.0
RECOMMENDATION_THRESHOLDS = {
    'strong_buy': 5.0,       # Score >= 5.0
    'buy': 2.5,              # Score >= 2.5
    'hold_upper': 2.5,       # Score < 2.5 and > -2.5
    'hold_lower': -2.5,      # Score < 2.5 and > -2.5
    'sell': -2.5,            # Score <= -2.5
    'strong_sell': -5.0      # Score <= -5.0
}

# Temporal decay parameters
# Older news has less impact on current recommendations
TEMPORAL_DECAY = {
    'half_life_days': 7,     # News loses 50% weight after 7 days
    'max_age_days': 30       # News older than 30 days is ignored
}

# Minimum requirements for generating recommendations
MIN_ARTICLES = 2             # Need at least 2 articles for recommendation
CONFIDENCE_THRESHOLD = 0.6   # Minimum confidence score (0.0 to 1.0)


# ============================================================================
# TEMPORAL DECAY CALCULATION
# ============================================================================

def calculate_temporal_weight(article_date: datetime, reference_date: Optional[datetime] = None) -> float:
    """
    Calculate temporal decay weight for an article based on its age.
    
    Newer articles have more weight (closer to 1.0), older articles decay
    exponentially. This ensures recent news has more influence on recommendations.
    
    Args:
        article_date: Publication date of the article
        reference_date: Reference date (defaults to now)
    
    Returns:
        Float weight between 0.0 and 1.0
    
    Example:
        >>> from datetime import datetime, timedelta, timezone
        >>> now = datetime.now(timezone.utc)
        >>> recent = now - timedelta(days=1)
        >>> calculate_temporal_weight(recent, now)
        0.906...  # ~90% weight after 1 day
        >>> old = now - timedelta(days=14)
        >>> calculate_temporal_weight(old, now)
        0.25...  # ~25% weight after 2 weeks
    """
    if reference_date is None:
        reference_date = datetime.now(timezone.utc)
    
    # Ensure both dates are datetime objects
    article_date = ensure_datetime(article_date)
    reference_date = ensure_datetime(reference_date)
    
    # Calculate age in days
    age_days = (reference_date - article_date).total_seconds() / (24 * 3600)
    
    # Articles older than max age get zero weight
    if age_days > TEMPORAL_DECAY['max_age_days']:
        return 0.0
    
    # Exponential decay: weight = 0.5^(age / half_life)
    half_life = TEMPORAL_DECAY['half_life_days']
    weight = math.pow(0.5, age_days / half_life)
    
    return max(0.0, min(1.0, weight))


# ============================================================================
# SCORE AGGREGATION ENGINE
# ============================================================================

def aggregate_scores(
    score_files: List[Path],
    reference_date: Optional[datetime] = None
) -> Dict:
    """
    Aggregate multiple article scores into a single topic-level score.
    
    This core feature combines individual sentiment scores
    while considering:
    - Source reliability (some sources are more trustworthy)
    - Temporal decay (recent news matters more)
    - Score distribution (variance and consistency)
    
    Args:
        score_files: List of paths to individual score JSON files
        reference_date: Reference date for temporal calculations
    
    Returns:
        Dictionary containing:
        - aggregated_score: Weighted average score
        - article_count: Number of articles included
        - weighted_count: Effective number after weighting
        - score_distribution: Positive/negative/neutral breakdown
        - confidence: Confidence level (0.0 to 1.0)
        - articles: List of article details with weights
    
    Example:
        >>> files = [Path("article1_score.json"), Path("article2_score.json")]
        >>> result = aggregate_scores(files)
        >>> result['aggregated_score']
        4.5
        >>> result['confidence']
        0.85
    """
    if reference_date is None:
        reference_date = datetime.now(timezone.utc)
    
    articles_data = []
    total_weighted_score = 0.0
    total_weight = 0.0
    
    # Process each scored article
    for score_file in score_files:
        try:
            with open(score_file, 'r', encoding='utf-8') as f:
                score_data = json.load(f)
            
            # Extract article information
            llm_score = score_data.get('llm_score')
            source = score_data.get('source', 'default')
            published_at = score_data.get('published_at')
            
            if llm_score is None or published_at is None:
                continue
            
            # Calculate combined weight
            # Weight = source_reliability × temporal_decay
            source_weight = SOURCE_WEIGHTS.get(source, SOURCE_WEIGHTS['default'])
            pub_date = ensure_datetime(published_at)
            temporal_weight = calculate_temporal_weight(pub_date, reference_date)
            
            combined_weight = source_weight * temporal_weight
            
            # Skip if weight is too low (very old articles)
            if combined_weight < 0.01:
                continue
            
            # Accumulate weighted scores
            total_weighted_score += llm_score * combined_weight
            total_weight += combined_weight
            
            # Store article details for explainability
            articles_data.append({
                'title': score_data.get('title', 'Unknown'),
                'score': llm_score,
                'source': source,
                'published_at': published_at,
                'source_weight': round(source_weight, 3),
                'temporal_weight': round(temporal_weight, 3),
                'combined_weight': round(combined_weight, 3),
                'explanation': score_data.get('llm_explanation', '')
            })
            
        except Exception as e:
            print(f"[WARNING] Error processing {score_file}: {e}")
            continue
    
    # Calculate aggregated score
    if total_weight == 0 or len(articles_data) == 0:
        return {
            'aggregated_score': 0.0,
            'article_count': 0,
            'weighted_count': 0.0,
            'confidence': 0.0,
            'score_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
            'articles': []
        }
    
    aggregated_score = total_weighted_score / total_weight
    
    # Calculate score distribution
    distribution = {'positive': 0, 'negative': 0, 'neutral': 0}
    for article in articles_data:
        score = article['score']
        if score > 1.0:
            distribution['positive'] += 1
        elif score < -1.0:
            distribution['negative'] += 1
        else:
            distribution['neutral'] += 1
    
    # Calculate confidence score
    # Higher confidence when:
    # - More articles (up to a point)
    # - More recent articles (higher total_weight)
    # - More consistent scores (lower variance)
    article_count_factor = min(len(articles_data) / 10.0, 1.0)  # Cap at 10 articles
    weight_factor = min(total_weight / len(articles_data), 1.0)  # Avg weight per article
    
    # Calculate score variance for consistency
    scores = [a['score'] for a in articles_data]
    mean_score = sum(scores) / len(scores)
    variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
    consistency_factor = 1.0 / (1.0 + variance / 10.0)  # Lower variance = higher consistency
    
    confidence = (article_count_factor * 0.4 + weight_factor * 0.3 + consistency_factor * 0.3)
    
    return {
        'aggregated_score': round(aggregated_score, 2),
        'article_count': len(articles_data),
        'weighted_count': round(total_weight, 2),
        'confidence': round(confidence, 2),
        'score_distribution': distribution,
        'articles': sorted(articles_data, key=lambda x: x['published_at'], reverse=True)
    }


# ============================================================================
# TREND ANALYSIS
# ============================================================================

def calculate_trend(articles: List[Dict]) -> Dict:
    """
    Analyze sentiment trend over time.
    
    Detects if sentiment is improving, declining,
    or stable by comparing recent vs older articles.
    
    Args:
        articles: List of article dictionaries with scores and dates
    
    Returns:
        Dictionary with:
        - trend: 'improving', 'declining', 'stable', or 'insufficient_data'
        - trend_score: Numeric trend indicator (-1.0 to +1.0)
        - recent_avg: Average score of recent articles
        - older_avg: Average score of older articles
        - description: Human-readable trend description
    """
    if len(articles) < 2:
        return {
            'trend': 'insufficient_data',
            'trend_score': 0.0,
            'recent_avg': 0.0,
            'older_avg': 0.0,
            'description': 'Not enough articles to determine trend'
        }
    
    # Sort articles by date (newest first)
    sorted_articles = sorted(
        articles,
        key=lambda x: ensure_datetime(x['published_at']),
        reverse=True
    )
    
    # Split into recent (first half) and older (second half)
    split_point = len(sorted_articles) // 2
    recent_articles = sorted_articles[:split_point] if split_point > 0 else sorted_articles
    older_articles = sorted_articles[split_point:] if split_point < len(sorted_articles) else []
    
    # Calculate averages (defensive check for empty lists, though current logic prevents this)
    if not recent_articles:
        recent_avg = 0.0
    else:
        recent_avg = sum(a['score'] for a in recent_articles) / len(recent_articles)
    
    older_avg = sum(a['score'] for a in older_articles) / len(older_articles) if older_articles else recent_avg
    
    # Calculate trend score
    trend_score = recent_avg - older_avg
    
    # Determine trend category
    if abs(trend_score) < 1.0:
        trend = 'stable'
        description = f'Sentiment is stable (recent: {recent_avg:.2f}, older: {older_avg:.2f})'
    elif trend_score > 0:
        trend = 'improving'
        description = f'Sentiment is improving (recent: {recent_avg:.2f}, older: {older_avg:.2f})'
    else:
        trend = 'declining'
        description = f'Sentiment is declining (recent: {recent_avg:.2f}, older: {older_avg:.2f})'
    
    return {
        'trend': trend,
        'trend_score': round(trend_score, 2),
        'recent_avg': round(recent_avg, 2),
        'older_avg': round(older_avg, 2),
        'description': description
    }


# ============================================================================
# RECOMMENDATION GENERATION
# ============================================================================

def generate_recommendation(
    aggregated_score: float,
    confidence: float,
    trend: Dict,
    distribution: Dict,
    article_count: int
) -> Dict:
    """
    Generate Buy/Hold/Sell recommendation with detailed explanation.
    
    Produces actionable investment signals
    based on aggregated sentiment analysis.
    
    Args:
        aggregated_score: Weighted average sentiment score (-10.0 to +10.0)
        confidence: Confidence level (0.0 to 1.0)
        trend: Trend analysis dictionary from calculate_trend()
        distribution: Score distribution (positive/negative/neutral counts)
        article_count: Number of articles analyzed
    
    Returns:
        Dictionary containing:
        - recommendation: 'STRONG BUY', 'BUY', 'HOLD', 'SELL', 'STRONG SELL'
        - confidence_level: 'HIGH', 'MEDIUM', 'LOW'
        - score: The aggregated sentiment score
        - reasoning: Detailed explanation of the recommendation
        - risk_factors: List of considerations and risks
        - article_count: Number of articles used
        - trend_indicator: Trend direction and strength
    """
    # Determine base recommendation from score
    if aggregated_score >= RECOMMENDATION_THRESHOLDS['strong_buy']:
        base_rec = 'STRONG BUY'
        sentiment = 'very positive'
    elif aggregated_score >= RECOMMENDATION_THRESHOLDS['buy']:
        base_rec = 'BUY'
        sentiment = 'positive'
    elif aggregated_score > RECOMMENDATION_THRESHOLDS['sell']:
        base_rec = 'HOLD'
        sentiment = 'neutral'
    elif aggregated_score > RECOMMENDATION_THRESHOLDS['strong_sell']:
        base_rec = 'SELL'
        sentiment = 'negative'
    else:
        base_rec = 'STRONG SELL'
        sentiment = 'very negative'
    
    # Adjust for confidence level
    if confidence < CONFIDENCE_THRESHOLD:
        # Low confidence - downgrade to HOLD unless already there
        if base_rec != 'HOLD':
            base_rec = 'HOLD'
            sentiment = 'uncertain'
    
    # Determine confidence level description
    if confidence >= 0.8:
        conf_level = 'HIGH'
    elif confidence >= 0.6:
        conf_level = 'MEDIUM'
    else:
        conf_level = 'LOW'
    
    # Build reasoning explanation
    reasoning_parts = []
    
    # Sentiment explanation
    reasoning_parts.append(
        f"Aggregated sentiment is {sentiment} with a score of {aggregated_score:.2f} "
        f"based on {article_count} article(s)."
    )
    
    # Distribution explanation
    pos_pct = (distribution['positive'] / article_count * 100) if article_count > 0 else 0
    neg_pct = (distribution['negative'] / article_count * 100) if article_count > 0 else 0
    reasoning_parts.append(
        f"Score distribution: {distribution['positive']} positive, "
        f"{distribution['negative']} negative, {distribution['neutral']} neutral "
        f"({pos_pct:.0f}% positive, {neg_pct:.0f}% negative)."
    )
    
    # Trend explanation
    reasoning_parts.append(trend['description'])
    
    # Confidence explanation
    reasoning_parts.append(
        f"Recommendation confidence is {conf_level} ({confidence:.0%}) based on "
        f"article count, recency, and score consistency."
    )
    
    # Identify risk factors
    risk_factors = []
    
    if article_count < MIN_ARTICLES:
        risk_factors.append(
            f"Limited data: Only {article_count} article(s) available. "
            "More articles would improve recommendation reliability."
        )
    
    if confidence < CONFIDENCE_THRESHOLD:
        risk_factors.append(
            f"Low confidence ({confidence:.0%}): Recommendation may not be reliable. "
            "Consider waiting for more recent news or diverse sources."
        )
    
    if distribution['positive'] > 0 and distribution['negative'] > 0:
        # Mixed signals
        if distribution['positive'] == distribution['negative']:
            risk_factors.append(
                "Mixed signals: Equal number of positive and negative articles. "
                "Market sentiment may be uncertain or transitioning."
            )
    
    if trend['trend'] == 'declining' and base_rec in ['STRONG BUY', 'BUY']:
        risk_factors.append(
            "Declining trend: Recent articles are less positive than older ones. "
            "Sentiment may be shifting negatively."
        )
    
    if trend['trend'] == 'improving' and base_rec in ['STRONG SELL', 'SELL']:
        risk_factors.append(
            "Improving trend: Recent articles are less negative than older ones. "
            "Sentiment may be recovering."
        )
    
    if not risk_factors:
        risk_factors.append(
            "Standard investment risks apply. This is sentiment analysis, not financial advice."
        )
    
    # Determine trend indicator
    if trend['trend'] == 'improving':
        trend_indicator = f"↗ Improving (trend: +{trend['trend_score']:.2f})"
    elif trend['trend'] == 'declining':
        trend_indicator = f"↘ Declining (trend: {trend['trend_score']:.2f})"
    else:
        trend_indicator = f"→ Stable (trend: {trend['trend_score']:.2f})"
    
    return {
        'recommendation': base_rec,
        'confidence_level': conf_level,
        'score': aggregated_score,
        'reasoning': ' '.join(reasoning_parts),
        'risk_factors': risk_factors,
        'article_count': article_count,
        'trend_indicator': trend_indicator,
        'generated_at': datetime.now(timezone.utc).isoformat()
    }


# ============================================================================
# RECOMMENDATION ENGINE: MAIN PROCESSING FUNCTION
# ============================================================================

def process_topic_recommendation(
    topic: str,
    score_files: List[Path],
    output_dir: Path
) -> Optional[Dict]:
    """
    Process all scores for a topic and generate a recommendation.
    
    This is the main entry point for recommendation generation.
    It orchestrates all the scoring components:
    1. Aggregate individual article scores
    2. Analyze sentiment trends
    3. Generate recommendation
    4. Save results with full explainability
    
    Args:
        topic: Stock symbol/topic (e.g., 'TSLA')
        score_files: List of score JSON file paths
        output_dir: Directory to save recommendation
    
    Returns:
        Complete recommendation dictionary or None if insufficient data
    """
    if len(score_files) < MIN_ARTICLES:
        print(f"[WARNING] {topic}: Only {len(score_files)} article(s) found. "
              f"Need at least {MIN_ARTICLES} for recommendation.")
        return None
    
    # Step 1 - Aggregate scores
    print(f"\n[SCORING] Processing {topic}: Aggregating {len(score_files)} article(s)...")
    aggregation = aggregate_scores(score_files)
    
    if aggregation['article_count'] == 0:
        print(f"[WARNING] {topic}: No valid articles after filtering.")
        return None
    
    # Step 2 - Analyze trends
    trend = calculate_trend(aggregation['articles'])
    
    # Step 3 - Generate recommendation
    recommendation = generate_recommendation(
        aggregated_score=aggregation['aggregated_score'],
        confidence=aggregation['confidence'],
        trend=trend,
        distribution=aggregation['score_distribution'],
        article_count=aggregation['article_count']
    )
    
    # Combine all results
    result = {
        'topic': topic,
        'recommendation': recommendation,
        'aggregation': {
            'score': aggregation['aggregated_score'],
            'confidence': aggregation['confidence'],
            'article_count': aggregation['article_count'],
            'weighted_count': aggregation['weighted_count'],
            'distribution': aggregation['score_distribution']
        },
        'trend': trend,
        'articles': aggregation['articles'][:10]  # Include top 10 most recent
    }
    
    # Save recommendation
    ensure_directory(output_dir)
    output_file = output_dir / f"{topic}_recommendation.json"
    safe_json_save(result, output_file)
    
    # Log recommendation generation
    log_recommendation_generation(
        topic,
        recommendation['recommendation'],
        aggregation['aggregated_score']
    )
    
    print(f"[SCORING] {topic}: {recommendation['recommendation']} "
          f"(score: {aggregation['aggregated_score']:.2f}, "
          f"confidence: {recommendation['confidence_level']})")
    
    return result


# ============================================================================
# RECOMMENDATION ENGINE: CLI INTERFACE
# ============================================================================

def main():
    """
    Command-line interface for recommendation engine.
    
    Usage:
        python recommendation_engine.py --data-dir output/llm_scores --output-dir output/recommendations
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate investment recommendations from sentiment scores'
    )
    parser.add_argument(
        '--data-dir',
        type=Path,
        required=True,
        help='Directory containing llm_scores (e.g., output/llm_scores)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('output/recommendations'),
        help='Directory to save recommendations (default: output/recommendations)'
    )
    parser.add_argument(
        '--topic',
        type=str,
        help='Process only this specific topic (e.g., TSLA). If not provided, processes all topics.'
    )
    
    args = parser.parse_args()
    
    # Validate input directory
    if not args.data_dir.exists():
        print(f"[ERROR] Data directory not found: {args.data_dir}")
        print("Please run sentiment analysis first to generate scores.")
        return 1
    
    # Create output directory
    ensure_directory(args.output_dir)
    
    print("=" * 80)
    print("RECOMMENDATION ENGINE")
    print("=" * 80)
    print(f"Data directory: {args.data_dir}")
    print(f"Output directory: {args.output_dir}")
    print()
    
    # Find all topics
    topics_to_process = []
    if args.topic:
        topic_dir = args.data_dir / args.topic
        if topic_dir.exists() and topic_dir.is_dir():
            topics_to_process.append(args.topic)
        else:
            print(f"[ERROR] Topic directory not found: {topic_dir}")
            return 1
    else:
        # Find all topic directories
        for item in args.data_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                topics_to_process.append(item.name)
    
    if not topics_to_process:
        print("[ERROR] No topics found in data directory.")
        return 1
    
    print(f"Found {len(topics_to_process)} topic(s) to process: {', '.join(topics_to_process)}")
    print()
    
    # Process each topic
    recommendations = {}
    for topic in sorted(topics_to_process):
        topic_dir = args.data_dir / topic
        score_files = list(topic_dir.glob("*_score.json"))
        
        result = process_topic_recommendation(topic, score_files, args.output_dir)
        if result:
            recommendations[topic] = result
    
    # Print summary
    print()
    print("=" * 80)
    print("RECOMMENDATION SUMMARY")
    print("=" * 80)
    
    if not recommendations:
        print("No recommendations generated. Check warnings above.")
        return 0
    
    for topic, rec_data in sorted(recommendations.items()):
        rec = rec_data['recommendation']
        agg = rec_data['aggregation']
        print(f"\n{topic}:")
        print(f"  Recommendation: {rec['recommendation']} ({rec['confidence_level']} confidence)")
        print(f"  Score: {agg['score']:.2f} ({agg['article_count']} articles)")
        print(f"  Trend: {rec['trend_indicator']}")
        print(f"  File: {args.output_dir}/{topic}_recommendation.json")
    
    print()
    print(f"✓ Generated {len(recommendations)} recommendation(s)")
    print(f"✓ Results saved to: {args.output_dir}")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
