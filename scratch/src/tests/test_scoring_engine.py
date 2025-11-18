"""
Test Suite for Phase 4: Scoring & Recommendation Engine

This test suite validates all components of the recommendation engine:
- Temporal decay calculations
- Score aggregation with weights
- Trend analysis
- Recommendation generation
- Edge cases and error handling

No API keys or external services required.
"""

import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scoring.recommendation_engine import (
    calculate_temporal_weight,
    aggregate_scores,
    calculate_trend,
    generate_recommendation,
    process_topic_recommendation,
    SOURCE_WEIGHTS,
    RECOMMENDATION_THRESHOLDS,
    TEMPORAL_DECAY
)


def print_header(title):
    """Print a test section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def print_test(name, passed, details=""):
    """Print test result."""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"  {details}")


def test_temporal_weight():
    """Test temporal decay weight calculations."""
    print_header("TEST: Temporal Decay Calculations")
    
    now = datetime.now(timezone.utc)
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Same day article should have ~1.0 weight
    tests_total += 1
    same_day = now - timedelta(hours=6)
    weight = calculate_temporal_weight(same_day, now)
    if 0.95 <= weight <= 1.0:
        tests_passed += 1
        print_test("Same day article weight", True, f"weight={weight:.3f} (expected ~1.0)")
    else:
        print_test("Same day article weight", False, f"weight={weight:.3f} (expected ~1.0)")
    
    # Test 2: 7-day old article should have ~0.5 weight (half-life)
    tests_total += 1
    week_old = now - timedelta(days=7)
    weight = calculate_temporal_weight(week_old, now)
    if 0.45 <= weight <= 0.55:
        tests_passed += 1
        print_test("Week-old article weight", True, f"weight={weight:.3f} (expected ~0.5)")
    else:
        print_test("Week-old article weight", False, f"weight={weight:.3f} (expected ~0.5)")
    
    # Test 3: 14-day old article should have ~0.25 weight
    tests_total += 1
    two_weeks_old = now - timedelta(days=14)
    weight = calculate_temporal_weight(two_weeks_old, now)
    if 0.20 <= weight <= 0.30:
        tests_passed += 1
        print_test("Two-week-old article weight", True, f"weight={weight:.3f} (expected ~0.25)")
    else:
        print_test("Two-week-old article weight", False, f"weight={weight:.3f} (expected ~0.25)")
    
    # Test 4: 31-day old article should have ~0.0 weight (beyond max age)
    tests_total += 1
    month_old = now - timedelta(days=31)
    weight = calculate_temporal_weight(month_old, now)
    if weight == 0.0:
        tests_passed += 1
        print_test("Month-old article weight", True, f"weight={weight:.3f} (expected 0.0)")
    else:
        print_test("Month-old article weight", False, f"weight={weight:.3f} (expected 0.0)")
    
    print(f"\nTemporal decay: {tests_passed}/{tests_total} tests passed")
    return tests_passed == tests_total


def test_score_aggregation():
    """Test score aggregation with multiple articles."""
    print_header("TEST: Score Aggregation")
    
    # Create temporary directory for test files
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        now = datetime.now(timezone.utc)
        
        # Create test score files
        test_scores = [
            {
                'llm_score': 7.5,
                'source': 'finnhub',
                'published_at': (now - timedelta(days=1)).isoformat(),
                'title': 'Very positive recent news',
                'llm_explanation': 'Strong earnings beat'
            },
            {
                'llm_score': 5.0,
                'source': 'bingnews',
                'published_at': (now - timedelta(days=3)).isoformat(),
                'title': 'Positive news',
                'llm_explanation': 'Good performance'
            },
            {
                'llm_score': -2.0,
                'source': 'googlenews_rss',
                'published_at': (now - timedelta(days=5)).isoformat(),
                'title': 'Minor concerns',
                'llm_explanation': 'Some challenges'
            }
        ]
        
        score_files = []
        for i, score_data in enumerate(test_scores):
            file_path = temp_dir / f"article_{i}_score.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(score_data, f)
            score_files.append(file_path)
        
        # Test aggregation
        result = aggregate_scores(score_files, now)
        
        tests_passed = 0
        tests_total = 0
        
        # Test 1: Should process all articles
        tests_total += 1
        if result['article_count'] == 3:
            tests_passed += 1
            print_test("Article count", True, f"count={result['article_count']}")
        else:
            print_test("Article count", False, f"count={result['article_count']} (expected 3)")
        
        # Test 2: Aggregated score should be positive (more positive articles)
        tests_total += 1
        if result['aggregated_score'] > 0:
            tests_passed += 1
            print_test("Positive aggregated score", True, f"score={result['aggregated_score']:.2f}")
        else:
            print_test("Positive aggregated score", False, f"score={result['aggregated_score']:.2f}")
        
        # Test 3: Distribution should reflect article sentiments
        tests_total += 1
        dist = result['score_distribution']
        if dist['positive'] == 2 and dist['negative'] == 1:
            tests_passed += 1
            print_test("Score distribution", True, f"pos={dist['positive']}, neg={dist['negative']}")
        else:
            print_test("Score distribution", False, 
                      f"pos={dist['positive']}, neg={dist['negative']} (expected 2 pos, 1 neg)")
        
        # Test 4: Confidence should be reasonable
        tests_total += 1
        if 0.0 <= result['confidence'] <= 1.0:
            tests_passed += 1
            print_test("Confidence in range", True, f"confidence={result['confidence']:.2f}")
        else:
            print_test("Confidence in range", False, f"confidence={result['confidence']:.2f}")
        
        print(f"\nAggregation: {tests_passed}/{tests_total} tests passed")
        return tests_passed == tests_total
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def test_trend_analysis():
    """Test trend detection."""
    print_header("TEST: Trend Analysis")
    
    now = datetime.now(timezone.utc)
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Improving trend (recent more positive)
    tests_total += 1
    improving_articles = [
        {'score': 6.0, 'published_at': (now - timedelta(days=1)).isoformat()},
        {'score': 5.5, 'published_at': (now - timedelta(days=2)).isoformat()},
        {'score': 2.0, 'published_at': (now - timedelta(days=5)).isoformat()},
        {'score': 1.5, 'published_at': (now - timedelta(days=6)).isoformat()},
    ]
    trend = calculate_trend(improving_articles)
    if trend['trend'] == 'improving':
        tests_passed += 1
        print_test("Improving trend detected", True, 
                  f"trend={trend['trend']}, score={trend['trend_score']:.2f}")
    else:
        print_test("Improving trend detected", False, f"trend={trend['trend']}")
    
    # Test 2: Declining trend (recent more negative)
    tests_total += 1
    declining_articles = [
        {'score': -3.0, 'published_at': (now - timedelta(days=1)).isoformat()},
        {'score': -2.5, 'published_at': (now - timedelta(days=2)).isoformat()},
        {'score': 2.0, 'published_at': (now - timedelta(days=5)).isoformat()},
        {'score': 3.0, 'published_at': (now - timedelta(days=6)).isoformat()},
    ]
    trend = calculate_trend(declining_articles)
    if trend['trend'] == 'declining':
        tests_passed += 1
        print_test("Declining trend detected", True, 
                  f"trend={trend['trend']}, score={trend['trend_score']:.2f}")
    else:
        print_test("Declining trend detected", False, f"trend={trend['trend']}")
    
    # Test 3: Stable trend (consistent scores)
    tests_total += 1
    stable_articles = [
        {'score': 3.0, 'published_at': (now - timedelta(days=1)).isoformat()},
        {'score': 3.2, 'published_at': (now - timedelta(days=2)).isoformat()},
        {'score': 2.8, 'published_at': (now - timedelta(days=5)).isoformat()},
        {'score': 3.1, 'published_at': (now - timedelta(days=6)).isoformat()},
    ]
    trend = calculate_trend(stable_articles)
    if trend['trend'] == 'stable':
        tests_passed += 1
        print_test("Stable trend detected", True, 
                  f"trend={trend['trend']}, score={trend['trend_score']:.2f}")
    else:
        print_test("Stable trend detected", False, f"trend={trend['trend']}")
    
    # Test 4: Insufficient data
    tests_total += 1
    insufficient_articles = [
        {'score': 3.0, 'published_at': (now - timedelta(days=1)).isoformat()}
    ]
    trend = calculate_trend(insufficient_articles)
    if trend['trend'] == 'insufficient_data':
        tests_passed += 1
        print_test("Insufficient data handling", True, f"trend={trend['trend']}")
    else:
        print_test("Insufficient data handling", False, f"trend={trend['trend']}")
    
    print(f"\nTrend analysis: {tests_passed}/{tests_total} tests passed")
    return tests_passed == tests_total


def test_recommendation_generation():
    """Test recommendation generation logic."""
    print_header("TEST: Recommendation Generation")
    
    tests_passed = 0
    tests_total = 0
    
    trend_improving = {
        'trend': 'improving',
        'trend_score': 2.0,
        'recent_avg': 6.0,
        'older_avg': 4.0,
        'description': 'Sentiment is improving'
    }
    
    distribution_positive = {'positive': 7, 'negative': 1, 'neutral': 2}
    
    # Test 1: Strong Buy recommendation
    tests_total += 1
    rec = generate_recommendation(
        aggregated_score=7.5,
        confidence=0.85,
        trend=trend_improving,
        distribution=distribution_positive,
        article_count=10
    )
    if rec['recommendation'] == 'STRONG BUY':
        tests_passed += 1
        print_test("Strong Buy recommendation", True, 
                  f"rec={rec['recommendation']}, conf={rec['confidence_level']}")
    else:
        print_test("Strong Buy recommendation", False, f"rec={rec['recommendation']}")
    
    # Test 2: Buy recommendation
    tests_total += 1
    rec = generate_recommendation(
        aggregated_score=3.5,
        confidence=0.75,
        trend=trend_improving,
        distribution=distribution_positive,
        article_count=8
    )
    if rec['recommendation'] == 'BUY':
        tests_passed += 1
        print_test("Buy recommendation", True, 
                  f"rec={rec['recommendation']}, conf={rec['confidence_level']}")
    else:
        print_test("Buy recommendation", False, f"rec={rec['recommendation']}")
    
    # Test 3: Hold recommendation (neutral score)
    tests_total += 1
    rec = generate_recommendation(
        aggregated_score=0.5,
        confidence=0.70,
        trend={'trend': 'stable', 'trend_score': 0.0, 'description': 'Stable'},
        distribution={'positive': 3, 'negative': 3, 'neutral': 2},
        article_count=8
    )
    if rec['recommendation'] == 'HOLD':
        tests_passed += 1
        print_test("Hold recommendation (neutral)", True, 
                  f"rec={rec['recommendation']}, conf={rec['confidence_level']}")
    else:
        print_test("Hold recommendation (neutral)", False, f"rec={rec['recommendation']}")
    
    # Test 4: Hold recommendation (low confidence)
    tests_total += 1
    rec = generate_recommendation(
        aggregated_score=4.0,  # Would be BUY but low confidence
        confidence=0.45,       # Below threshold
        trend=trend_improving,
        distribution=distribution_positive,
        article_count=2
    )
    if rec['recommendation'] == 'HOLD':
        tests_passed += 1
        print_test("Hold recommendation (low confidence)", True, 
                  f"rec={rec['recommendation']}, conf={rec['confidence_level']}")
    else:
        print_test("Hold recommendation (low confidence)", False, f"rec={rec['recommendation']}")
    
    # Test 5: Sell recommendation
    tests_total += 1
    rec = generate_recommendation(
        aggregated_score=-3.5,
        confidence=0.80,
        trend={'trend': 'declining', 'trend_score': -2.0, 'description': 'Declining'},
        distribution={'positive': 1, 'negative': 7, 'neutral': 2},
        article_count=10
    )
    if rec['recommendation'] == 'SELL':
        tests_passed += 1
        print_test("Sell recommendation", True, 
                  f"rec={rec['recommendation']}, conf={rec['confidence_level']}")
    else:
        print_test("Sell recommendation", False, f"rec={rec['recommendation']}")
    
    # Test 6: Strong Sell recommendation
    tests_total += 1
    rec = generate_recommendation(
        aggregated_score=-7.5,
        confidence=0.90,
        trend={'trend': 'declining', 'trend_score': -3.0, 'description': 'Declining'},
        distribution={'positive': 0, 'negative': 10, 'neutral': 0},
        article_count=10
    )
    if rec['recommendation'] == 'STRONG SELL':
        tests_passed += 1
        print_test("Strong Sell recommendation", True, 
                  f"rec={rec['recommendation']}, conf={rec['confidence_level']}")
    else:
        print_test("Strong Sell recommendation", False, f"rec={rec['recommendation']}")
    
    # Test 7: Risk factors present
    tests_total += 1
    rec = generate_recommendation(
        aggregated_score=3.0,
        confidence=0.50,  # Low confidence
        trend=trend_improving,
        distribution={'positive': 2, 'negative': 0, 'neutral': 0},
        article_count=2  # At minimum threshold
    )
    # Should have at least 1 risk factor (low confidence)
    has_risk_factors = len(rec['risk_factors']) >= 1
    if has_risk_factors:
        tests_passed += 1
        print_test("Risk factors identified", True, 
                  f"factors={len(rec['risk_factors'])}")
    else:
        print_test("Risk factors identified", False, 
                  f"factors={len(rec['risk_factors'])}")
    
    print(f"\nRecommendation generation: {tests_passed}/{tests_total} tests passed")
    return tests_passed == tests_total


def test_end_to_end():
    """Test complete recommendation workflow."""
    print_header("TEST: End-to-End Workflow")
    
    # Create temporary directory structure
    temp_dir = Path(tempfile.mkdtemp())
    scores_dir = temp_dir / "llm_scores" / "DEMO"
    output_dir = temp_dir / "recommendations"
    scores_dir.mkdir(parents=True)
    
    try:
        now = datetime.now(timezone.utc)
        
        # Create test score files
        test_articles = [
            {
                'llm_score': 6.5,
                'source': 'finnhub',
                'published_at': (now - timedelta(days=1)).isoformat(),
                'title': 'Strong quarterly results',
                'llm_explanation': 'Beat earnings expectations'
            },
            {
                'llm_score': 5.0,
                'source': 'bingnews',
                'published_at': (now - timedelta(days=2)).isoformat(),
                'title': 'Positive analyst upgrade',
                'llm_explanation': 'Price target raised'
            },
            {
                'llm_score': 4.5,
                'source': 'googlenews_rss',
                'published_at': (now - timedelta(days=4)).isoformat(),
                'title': 'New product launch',
                'llm_explanation': 'Successful product debut'
            },
        ]
        
        score_files = []
        for i, article in enumerate(test_articles):
            file_path = scores_dir / f"article_{i:03d}_score.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(article, f)
            score_files.append(file_path)
        
        # Process recommendation
        result = process_topic_recommendation("DEMO", score_files, output_dir)
        
        tests_passed = 0
        tests_total = 0
        
        # Test 1: Recommendation generated
        tests_total += 1
        if result is not None:
            tests_passed += 1
            print_test("Recommendation generated", True, f"topic={result['topic']}")
        else:
            print_test("Recommendation generated", False, "No result returned")
            return False
        
        # Test 2: Output file created
        tests_total += 1
        output_file = output_dir / "DEMO_recommendation.json"
        if output_file.exists():
            tests_passed += 1
            print_test("Output file created", True, f"file={output_file.name}")
        else:
            print_test("Output file created", False, "File not found")
        
        # Test 3: Recommendation structure is valid
        tests_total += 1
        required_keys = ['topic', 'recommendation', 'aggregation', 'trend', 'articles']
        has_all_keys = all(key in result for key in required_keys)
        if has_all_keys:
            tests_passed += 1
            print_test("Valid structure", True, f"keys={list(result.keys())}")
        else:
            print_test("Valid structure", False, f"missing keys")
        
        # Test 4: Recommendation is BUY (all positive articles)
        tests_total += 1
        rec = result['recommendation']['recommendation']
        if rec in ['BUY', 'STRONG BUY']:
            tests_passed += 1
            print_test("Correct recommendation for positive sentiment", True, f"rec={rec}")
        else:
            print_test("Correct recommendation for positive sentiment", False, f"rec={rec}")
        
        # Test 5: Explainability present
        tests_total += 1
        has_reasoning = 'reasoning' in result['recommendation'] and len(result['recommendation']['reasoning']) > 0
        has_risk_factors = 'risk_factors' in result['recommendation'] and len(result['recommendation']['risk_factors']) > 0
        if has_reasoning and has_risk_factors:
            tests_passed += 1
            print_test("Explainability complete", True, "Has reasoning and risk factors")
        else:
            print_test("Explainability complete", False, "Missing explanations")
        
        print(f"\nEnd-to-end: {tests_passed}/{tests_total} tests passed")
        return tests_passed == tests_total
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def main():
    """Run all tests."""
    print("=" * 60)
    print("PHASE 4: SCORING & RECOMMENDATION ENGINE - TEST SUITE")
    print("=" * 60)
    
    results = {
        'Temporal Decay': test_temporal_weight(),
        'Score Aggregation': test_score_aggregation(),
        'Trend Analysis': test_trend_analysis(),
        'Recommendation Generation': test_recommendation_generation(),
        'End-to-End Workflow': test_end_to_end()
    }
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} test suites passed")
    
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Review output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
