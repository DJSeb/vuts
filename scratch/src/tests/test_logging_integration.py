#!/usr/bin/env python3
"""
Integration test for VUTS logging system.

This test validates that logging works in the context of actual module usage.
"""

import sys
import tempfile
import json
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import get_logger


def test_logging_integration():
    """Test that logging works in an integrated workflow."""
    print("=" * 60)
    print("LOGGING INTEGRATION TEST")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Reset global logger
        import utils.logger as logger_module
        logger_module._global_logger = None
        
        # Initialize logger
        logger = get_logger(temp_path)
        
        print("\nSimulating workflow operations...")
        
        # Simulate fetch operation
        print("  1. Fetching news...")
        logger.log_fetch_request(['googlenews', 'bingnews'], ['TSLA', 'MSFT', 'NVDA'])
        logger.log_search_execution('googlenews', 'TSLA', 12)
        logger.log_search_execution('googlenews', 'MSFT', 8)
        logger.log_search_execution('bingnews', 'TSLA', 5)
        
        # Simulate analysis operation
        print("  2. Analyzing sentiment...")
        logger.log_analysis_start('/tmp/output', 20, 'gpt-4o-mini')
        logger.log_article_processing('TSLA', 'Tesla announces new battery technology', 7.5)
        logger.log_article_processing('TSLA', 'Tesla faces supply chain challenges', -2.3)
        logger.log_article_processing('MSFT', 'Microsoft beats earnings expectations', 6.8)
        
        # Simulate market data fetch
        print("  3. Fetching market data...")
        logger.log_market_data_request(['TSLA', 'MSFT', 'NVDA'], 30)
        
        # Simulate recommendation generation
        print("  4. Generating recommendations...")
        logger.log_recommendation_generation('TSLA', 'BUY', 5.2)
        logger.log_recommendation_generation('MSFT', 'STRONG BUY', 6.8)
        
        # Simulate UI launch
        print("  5. Launching UI...")
        logger.log_ui_launch('127.0.0.1', 5000)
        logger.log_api_request('/api/execute', 'POST')
        logger.log_api_request('/api/notifications', 'GET')
        
        # Simulate notifications
        print("  6. Creating notifications...")
        logger.log_notification_created('High sentiment score detected for TSLA', 'warning')
        
        # Verify log file exists and has content
        log_file = logger.current_log_file
        
        if not log_file.exists():
            print("\n✗ Log file was not created")
            return False
        
        # Read and analyze log content
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        log_lines = log_content.strip().split('\n')
        
        print(f"\n✓ Log file created: {log_file.name}")
        print(f"✓ Total log entries: {len(log_lines)}")
        
        # Check for expected keywords in logs
        expected_keywords = [
            'requested news fetch',
            'Executing search',
            'Starting sentiment analysis',
            'Analyzed article',
            'Fetching market data',
            'Generated recommendation',
            'Web UI launched',
            'API request',
            'Notification created'
        ]
        
        found_keywords = 0
        for keyword in expected_keywords:
            if any(keyword in line for line in log_lines):
                found_keywords += 1
        
        print(f"✓ Found {found_keywords}/{len(expected_keywords)} expected log types")
        
        # Display sample log entries
        print("\nSample log entries:")
        print("-" * 60)
        for i, line in enumerate(log_lines[:5], 1):
            print(f"  {i}. {line}")
        if len(log_lines) > 5:
            print(f"  ... and {len(log_lines) - 5} more entries")
        
        # Check log entry format
        all_formatted = True
        for line in log_lines:
            if not line.strip().startswith('['):
                all_formatted = False
                break
            if '] ' not in line:
                all_formatted = False
                break
        
        if all_formatted:
            print("\n✓ All log entries have correct format")
        else:
            print("\n✗ Some log entries have incorrect format")
            return False
        
        # Check that no emojis are present
        emoji_chars = ['😀', '🎉', '✅', '❌', '⚠️', '🔔', '📊', '🚀']
        has_emoji = any(emoji in log_content for emoji in emoji_chars)
        
        if not has_emoji:
            print("✓ No emojis in log entries")
        else:
            print("✗ Found emojis in log entries")
            return False
        
        # Check that messages are brief (not paragraphs)
        max_length = 300
        all_brief = True
        for line in log_lines:
            if ']' in line:
                message = line.split(']', 1)[1].strip()
                if len(message) > max_length:
                    all_brief = False
                    break
        
        if all_brief:
            print("✓ All log messages are brief and descriptive")
        else:
            print("✗ Some log messages are too long")
            return False
        
        return True


def main():
    """Run the integration test."""
    print("\n")
    result = test_logging_integration()
    
    print("\n" + "=" * 60)
    if result:
        print("✓ INTEGRATION TEST PASSED")
        print("=" * 60)
        print("\nThe logging system is working correctly!")
        print("Logs will be stored in the 'logs' directory with datetime prefixes.")
        return 0
    else:
        print("✗ INTEGRATION TEST FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    exit(main())
