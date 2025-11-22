# VUTS Logging System

This document describes the logging system implemented in VUTS to track user operations and system events.

## Overview

The logging system provides centralized tracking of all major operations in the VUTS application. Logs are stored in the `logs` directory with datetime-prefixed filenames.

## Features

- **Automatic Log Creation**: Log files are created automatically with datetime prefix (e.g., `log_20251122_143012.log`)
- **Timestamped Entries**: Each log entry includes a timestamp in the format `[YYYY-MM-DD HH:MM:SS]`
- **Brief, Descriptive Messages**: Log messages are concise and clear, without emojis
- **Comprehensive Coverage**: Logs track all major operations across the application

## Log File Location

Logs are stored in: `scratch/logs/`

Each log file follows the naming pattern: `log_YYYYMMDD_HHMMSS.log`

## Logged Operations

The logging system tracks the following operations:

### 1. News Fetching
- User fetch requests with sources and topics
- Search execution results for each source/topic combination

Example:
```
[2025-11-22 14:30:12] User requested news fetch from googlenews, bingnews for topics: TSLA, MSFT
[2025-11-22 14:30:15] Executing search for TSLA in googlenews, found 15 articles
```

### 2. Sentiment Analysis
- Analysis initialization with parameters
- Individual article processing with scores

Example:
```
[2025-11-22 14:31:20] Starting sentiment analysis from /output, max articles: 10, model: gpt-4o-mini
[2025-11-22 14:31:25] Analyzed article for TSLA: 'Tesla announces breakthrough', score: 7.5
```

### 3. Market Data
- Market data fetch requests for symbols

Example:
```
[2025-11-22 14:32:10] Fetching market data for TSLA, MSFT, NVDA, 30 days of history
```

### 4. Recommendations
- Investment recommendation generation

Example:
```
[2025-11-22 14:33:45] Generated recommendation for TSLA: BUY (score: 5.80)
```

### 5. Web UI
- UI application launches
- API endpoint requests

Example:
```
[2025-11-22 14:35:00] Web UI launched at 127.0.0.1:5000
[2025-11-22 14:35:10] API request: POST /api/execute
```

### 6. Notifications
- Notification creation events

Example:
```
[2025-11-22 14:36:20] Notification created: High sentiment score detected (severity: warning)
```

## Usage

The logging system is automatically initialized when any VUTS module is used. No additional configuration is required.

### Using the Logger in Code

If you need to add custom logging in your code:

```python
from utils.logger import get_logger

logger = get_logger()
logger.log_custom("Your custom message here")
```

Or use the convenience functions:

```python
from utils.logger import log_custom

log_custom("Your custom message here")
```

## Testing

Run the logging tests to verify functionality:

```bash
cd scratch

# Test the logger utility
python src/tests/test_logger.py

# Test logging integration
python src/tests/test_logging_integration.py

# Run the logging demonstration
python demos/demo_logging.py
```

## Log File Management

- Log files are automatically created in the `logs` directory
- Each run creates a new log file with a unique timestamp
- Old log files are not automatically deleted (manual cleanup may be needed)
- The `logs` directory is excluded from version control (via `.gitignore`)

## Implementation Details

### Logger Module

The logger is implemented in `src/utils/logger.py` and provides:

- `VutsLogger` class: Main logger implementation
- `get_logger()`: Get or create the global logger instance
- Convenience functions for each operation type

### Integration Points

The logging system is integrated into:

- `src/fetching/financial_news_collector_async.py`
- `src/llm/sentiment_analyzer.py`
- `src/market/data_fetcher.py`
- `src/scoring/recommendation_engine.py`
- `src/ui/app.py`
- `src/notifications/notification_manager.py`

## Design Principles

1. **Minimal Overhead**: Logging adds minimal performance impact
2. **Non-Intrusive**: Logging failures don't affect normal operation
3. **Brief Messages**: Log entries are concise (typically < 300 characters)
4. **No Emojis**: Professional log format without decorative characters
5. **Timestamp Everything**: Every entry has a timestamp for tracking

## Example Log File

```
[2025-11-22 14:30:12] User requested news fetch from googlenews for topics: TSLA, MSFT
[2025-11-22 14:30:15] Executing search for TSLA in googlenews, found 15 articles
[2025-11-22 14:30:17] Executing search for MSFT in googlenews, found 12 articles
[2025-11-22 14:31:20] Starting sentiment analysis from /output, max articles: 20, model: gpt-4o-mini
[2025-11-22 14:31:25] Analyzed article for TSLA: 'Tesla announces breakthrough', score: 7.5
[2025-11-22 14:31:28] Analyzed article for MSFT: 'Microsoft beats earnings', score: 6.8
[2025-11-22 14:32:10] Fetching market data for TSLA, MSFT, 30 days of history
[2025-11-22 14:33:45] Generated recommendation for TSLA: BUY (score: 5.80)
[2025-11-22 14:33:47] Generated recommendation for MSFT: STRONG BUY (score: 7.20)
[2025-11-22 14:35:00] Web UI launched at 127.0.0.1:5000
```

## Future Enhancements

Possible future improvements:

- Log rotation/archival
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- Structured logging (JSON format)
- Log aggregation and analysis tools
- Remote logging support
