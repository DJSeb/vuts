#!/usr/bin/env python3
"""
Test script for the VUTS logging system.

This script validates that the logger properly:
1. Creates log directory
2. Creates log files with datetime prefix
3. Writes log entries with timestamps
4. Provides all required logging functions
"""

import sys
import tempfile
import os
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import VutsLogger, get_logger


def test_logger_initialization():
    """Test that logger initializes correctly."""
    print("=" * 60)
    print("TEST: Logger Initialization")
    print("=" * 60)
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        logger = VutsLogger(logs_dir=temp_path)
        
        # Check that logs directory was created
        if not temp_path.exists():
            print("✗ Logs directory was not created")
            return False
        
        # Check that log file was created
        if not logger.current_log_file:
            print("✗ Log file was not initialized")
            return False
        
        # Check that log file has correct naming pattern
        log_filename = logger.current_log_file.name
        if not log_filename.startswith("log_") or not log_filename.endswith(".log"):
            print(f"✗ Log file has incorrect naming: {log_filename}")
            return False
        
        print(f"✓ Logger initialized with log file: {log_filename}")
        return True


def test_log_entry_format():
    """Test that log entries have correct format."""
    print("\n" + "=" * 60)
    print("TEST: Log Entry Format")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        logger = VutsLogger(logs_dir=temp_path)
        
        # Write a test log entry
        test_message = "Test log entry"
        logger.log_custom(test_message)
        
        # Read the log file
        if not logger.current_log_file.exists():
            print("✗ Log file was not created")
            return False
        
        with open(logger.current_log_file, 'r') as f:
            content = f.read()
        
        # Check that message was written
        if test_message not in content:
            print(f"✗ Log message not found in file")
            return False
        
        # Check that entry has timestamp
        if not content.strip().startswith('['):
            print("✗ Log entry does not have timestamp prefix")
            return False
        
        # Check for no emojis (basic check)
        emoji_chars = ['😀', '🎉', '✅', '❌', '⚠️', '🔔', '📊', '🚀']
        has_emoji = any(emoji in content for emoji in emoji_chars)
        if has_emoji:
            print("✗ Log entry contains emojis")
            return False
        
        print(f"✓ Log entry format is correct")
        print(f"  Content preview: {content.strip()[:80]}...")
        return True


def test_all_logging_functions():
    """Test that all logging functions work."""
    print("\n" + "=" * 60)
    print("TEST: All Logging Functions")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        logger = VutsLogger(logs_dir=temp_path)
        
        tests_passed = 0
        tests_total = 0
        
        # Test fetch request logging
        tests_total += 1
        try:
            logger.log_fetch_request(['googlenews', 'bing'], ['TSLA', 'MSFT'])
            tests_passed += 1
            print("✓ log_fetch_request works")
        except Exception as e:
            print(f"✗ log_fetch_request failed: {e}")
        
        # Test search execution logging
        tests_total += 1
        try:
            logger.log_search_execution('googlenews', 'TSLA', 5)
            tests_passed += 1
            print("✓ log_search_execution works")
        except Exception as e:
            print(f"✗ log_search_execution failed: {e}")
        
        # Test analysis start logging
        tests_total += 1
        try:
            logger.log_analysis_start('/path/to/data', 10, 'gpt-4o-mini')
            tests_passed += 1
            print("✓ log_analysis_start works")
        except Exception as e:
            print(f"✗ log_analysis_start failed: {e}")
        
        # Test article processing logging
        tests_total += 1
        try:
            logger.log_article_processing('TSLA', 'Test Article Title', 5.5)
            tests_passed += 1
            print("✓ log_article_processing works")
        except Exception as e:
            print(f"✗ log_article_processing failed: {e}")
        
        # Test market data request logging
        tests_total += 1
        try:
            logger.log_market_data_request(['TSLA', 'MSFT'], 30)
            tests_passed += 1
            print("✓ log_market_data_request works")
        except Exception as e:
            print(f"✗ log_market_data_request failed: {e}")
        
        # Test recommendation generation logging
        tests_total += 1
        try:
            logger.log_recommendation_generation('TSLA', 'BUY', 5.5)
            tests_passed += 1
            print("✓ log_recommendation_generation works")
        except Exception as e:
            print(f"✗ log_recommendation_generation failed: {e}")
        
        # Test UI launch logging
        tests_total += 1
        try:
            logger.log_ui_launch('127.0.0.1', 5000)
            tests_passed += 1
            print("✓ log_ui_launch works")
        except Exception as e:
            print(f"✗ log_ui_launch failed: {e}")
        
        # Test API request logging
        tests_total += 1
        try:
            logger.log_api_request('/api/execute', 'POST')
            tests_passed += 1
            print("✓ log_api_request works")
        except Exception as e:
            print(f"✗ log_api_request failed: {e}")
        
        # Test notification creation logging
        tests_total += 1
        try:
            logger.log_notification_created('Test notification', 'warning')
            tests_passed += 1
            print("✓ log_notification_created works")
        except Exception as e:
            print(f"✗ log_notification_created failed: {e}")
        
        # Verify all log entries were written
        with open(logger.current_log_file, 'r') as f:
            content = f.read()
        
        lines = content.strip().split('\n')
        expected_lines = tests_passed
        
        if len(lines) >= expected_lines:
            print(f"\n✓ All {tests_passed}/{tests_total} logging functions worked")
            print(f"  Total log entries: {len(lines)}")
            return tests_passed == tests_total
        else:
            print(f"\n✗ Expected at least {expected_lines} log entries, got {len(lines)}")
            return False


def test_log_message_format():
    """Test that log messages are brief and descriptive."""
    print("\n" + "=" * 60)
    print("TEST: Log Message Format")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        logger = VutsLogger(logs_dir=temp_path)
        
        # Write various log entries
        logger.log_fetch_request(['googlenews'], ['TSLA'])
        logger.log_search_execution('googlenews', 'TSLA', 5)
        logger.log_analysis_start('/data', 10, 'gpt-4o-mini')
        
        # Read the log file
        with open(logger.current_log_file, 'r') as f:
            content = f.read()
        
        lines = content.strip().split('\n')
        
        # Check that messages are not too long (no paragraphs)
        max_line_length = 300  # Reasonable limit for brief messages
        all_brief = True
        for line in lines:
            # Remove timestamp part for message length check
            if ']' in line:
                message = line.split(']', 1)[1].strip()
                if len(message) > max_line_length:
                    print(f"✗ Log message too long ({len(message)} chars): {message[:80]}...")
                    all_brief = False
        
        if all_brief:
            print("✓ All log messages are brief and descriptive")
            print(f"  Average message length: {sum(len(l.split(']', 1)[1]) if ']' in l else 0 for l in lines) // len(lines)} chars")
            return True
        else:
            return False


def test_global_logger():
    """Test that global logger instance works."""
    print("\n" + "=" * 60)
    print("TEST: Global Logger Instance")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Reset global logger for testing
        import utils.logger as logger_module
        logger_module._global_logger = None
        
        # Get logger instance
        logger1 = get_logger(temp_path)
        logger2 = get_logger()
        
        # Check that both return the same instance
        if logger1 is not logger2:
            print("✗ Global logger returns different instances")
            return False
        
        print("✓ Global logger instance works correctly")
        return True


def main():
    """Run all logger tests."""
    print("=" * 60)
    print("VUTS LOGGER TEST SUITE")
    print("=" * 60)
    print()
    
    results = {
        "Logger Initialization": test_logger_initialization(),
        "Log Entry Format": test_log_entry_format(),
        "All Logging Functions": test_all_logging_functions(),
        "Log Message Format": test_log_message_format(),
        "Global Logger Instance": test_global_logger()
    }
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
