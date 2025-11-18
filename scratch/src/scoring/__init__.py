"""
Scoring and Recommendation Engine Module (Phase 4)

This module provides advanced scoring capabilities that aggregate individual
article sentiment scores into actionable investment recommendations.

Key Components:
- Sentiment Aggregation: Combines multiple article scores per topic
- Source Reliability: Weights scores based on source credibility
- Temporal Relevance: Applies time-based decay to older news
- Recommendation Engine: Generates Buy/Hold/Sell signals
- Trend Analysis: Tracks sentiment changes over time
"""

from .recommendation_engine import (
    generate_recommendation,
    aggregate_scores,
    calculate_trend,
    SOURCE_WEIGHTS,
    RECOMMENDATION_THRESHOLDS
)

__all__ = [
    'generate_recommendation',
    'aggregate_scores',
    'calculate_trend',
    'SOURCE_WEIGHTS',
    'RECOMMENDATION_THRESHOLDS'
]
