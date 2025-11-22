#!/usr/bin/env python3
"""
End-to-end logging demonstration for VUTS.

This script simulates a complete VUTS workflow and demonstrates
how operations are logged throughout the system.
"""

import sys
import tempfile
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from utils.logger import get_logger


def main():
    """Demonstrate logging in a simulated workflow."""
    print("=" * 70)
    print("VUTS LOGGING DEMONSTRATION")
    print("=" * 70)
    print()
    
    # Create a temporary directory for logs
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_logs = Path(temp_dir) / "logs"
        
        # Reset global logger for this demo
        import utils.logger as logger_module
        logger_module._global_logger = None
        
        # Initialize logger
        logger = get_logger(temp_logs)
        
        print(f"Logs will be stored in: {logger.current_log_file.name}")
        print()
        
        # Simulate a complete workflow
        print("Simulating VUTS workflow operations:")
        print()
        
        # Step 1: Fetch news
        print("1. Fetching news articles...")
        logger.log_fetch_request(
            sources=['googlenews_rss', 'bingnews', 'finnhub'],
            topics=['TSLA', 'MSFT', 'NVDA']
        )
        logger.log_search_execution('googlenews_rss', 'TSLA', 15)
        logger.log_search_execution('googlenews_rss', 'MSFT', 12)
        logger.log_search_execution('googlenews_rss', 'NVDA', 10)
        logger.log_search_execution('bingnews', 'TSLA', 8)
        logger.log_search_execution('bingnews', 'MSFT', 7)
        logger.log_search_execution('finnhub', 'NVDA', 5)
        print("   ✓ Logged fetch requests and search executions")
        print()
        
        # Step 2: Analyze sentiment
        print("2. Analyzing article sentiment...")
        logger.log_analysis_start('/tmp/output', 25, 'gpt-4o-mini')
        logger.log_article_processing(
            'TSLA', 
            'Tesla announces major breakthrough in battery technology',
            8.5
        )
        logger.log_article_processing(
            'TSLA',
            'Supply chain concerns impact Tesla production',
            -2.5
        )
        logger.log_article_processing(
            'MSFT',
            'Microsoft reports record quarterly earnings',
            7.8
        )
        logger.log_article_processing(
            'NVDA',
            'NVIDIA faces increased competition in AI chip market',
            -1.2
        )
        print("   ✓ Logged analysis start and article processing")
        print()
        
        # Step 3: Fetch market data
        print("3. Fetching market data...")
        logger.log_market_data_request(['TSLA', 'MSFT', 'NVDA'], 30)
        print("   ✓ Logged market data request")
        print()
        
        # Step 4: Generate recommendations
        print("4. Generating investment recommendations...")
        logger.log_recommendation_generation('TSLA', 'BUY', 5.8)
        logger.log_recommendation_generation('MSFT', 'STRONG BUY', 7.2)
        logger.log_recommendation_generation('NVDA', 'HOLD', 2.1)
        print("   ✓ Logged recommendation generation")
        print()
        
        # Step 5: UI and notifications
        print("5. Launching UI and creating notifications...")
        logger.log_ui_launch('127.0.0.1', 5000)
        logger.log_api_request('/api/execute', 'POST')
        logger.log_api_request('/api/notifications', 'GET')
        logger.log_notification_created(
            'High positive sentiment detected for TSLA',
            'warning'
        )
        logger.log_notification_created(
            'Strong buy signal generated for MSFT',
            'success'
        )
        print("   ✓ Logged UI launch, API requests, and notifications")
        print()
        
        # Display the log file
        print("=" * 70)
        print("LOG FILE CONTENTS")
        print("=" * 70)
        print()
        
        with open(logger.current_log_file, 'r') as f:
            log_content = f.read()
        
        log_lines = log_content.strip().split('\n')
        
        for i, line in enumerate(log_lines, 1):
            print(f"{i:2d}. {line}")
        
        print()
        print("=" * 70)
        print("LOGGING SUMMARY")
        print("=" * 70)
        print(f"Total log entries: {len(log_lines)}")
        print(f"Log file: {logger.current_log_file.name}")
        print()
        print("Key features demonstrated:")
        print("  ✓ Datetime prefixed log file names (log_YYYYMMDD_HHMMSS.log)")
        print("  ✓ Timestamped log entries")
        print("  ✓ Brief, descriptive messages (no emojis)")
        print("  ✓ Comprehensive operation tracking")
        print("  ✓ All major VUTS operations logged")
        print()
        print("In production, logs are stored in: scratch/logs/")
        print("=" * 70)


if __name__ == "__main__":
    main()
