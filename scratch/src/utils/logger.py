"""
Logger utility for tracking user operations in the VUTS system.

This module provides centralized logging functionality for recording
user operations and system events. Logs are stored in the logs directory
with datetime-prefixed filenames.
"""
from pathlib import Path
from datetime import datetime
from typing import Optional


# Default logs directory relative to the scratch directory
DEFAULT_LOGS_DIR = Path(__file__).parent.parent.parent / "logs"


class VutsLogger:
    """Logger for tracking user operations and system events."""
    
    def __init__(self, logs_dir: Optional[Path] = None):
        """
        Initialize the logger.
        
        Args:
            logs_dir: Directory to store log files. If None, uses default.
        """
        self.logs_dir = logs_dir or DEFAULT_LOGS_DIR
        self.ensure_logs_directory()
        self.current_log_file = None
        self._initialize_log_file()
    
    def ensure_logs_directory(self):
        """Create logs directory if it doesn't exist."""
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def _initialize_log_file(self):
        """Create a new log file with datetime prefix."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"log_{timestamp}.log"
        self.current_log_file = self.logs_dir / log_filename
    
    def _write_log_entry(self, message: str):
        """
        Write a log entry to the current log file.
        
        Args:
            message: Log message to write
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        try:
            with open(self.current_log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"[WARNING] Failed to write log: {e}")
    
    def log_fetch_request(self, sources: list, topics: list):
        """
        Log a news fetch request.
        
        Args:
            sources: List of news sources
            topics: List of topics/symbols to fetch
        """
        sources_str = ", ".join(sources) if sources else "all sources"
        topics_str = ", ".join(topics) if topics else "no topics"
        message = f"User requested news fetch from {sources_str} for topics: {topics_str}"
        self._write_log_entry(message)
    
    def log_search_execution(self, source: str, topic: str, articles_found: int):
        """
        Log execution of a search operation.
        
        Args:
            source: News source being searched
            topic: Topic being searched
            articles_found: Number of articles found
        """
        message = f"Executing search for {topic} in {source}, found {articles_found} articles"
        self._write_log_entry(message)
    
    def log_analysis_start(self, data_dir: str, max_articles: int, model: str):
        """
        Log start of sentiment analysis.
        
        Args:
            data_dir: Directory containing articles
            max_articles: Maximum articles to process
            model: LLM model being used
        """
        message = f"Starting sentiment analysis from {data_dir}, max articles: {max_articles}, model: {model}"
        self._write_log_entry(message)
    
    def log_article_processing(self, topic: str, article_title: str, score: float):
        """
        Log processing of an individual article.
        
        Args:
            topic: Topic/symbol
            article_title: Article title
            score: Sentiment score assigned
        """
        # Truncate title if too long
        title_preview = article_title[:60] + "..." if len(article_title) > 60 else article_title
        message = f"Analyzed article for {topic}: '{title_preview}', score: {score}"
        self._write_log_entry(message)
    
    def log_market_data_request(self, symbols: list, days: int):
        """
        Log market data fetch request.
        
        Args:
            symbols: List of stock symbols
            days: Number of days of historical data
        """
        symbols_str = ", ".join(symbols) if symbols else "no symbols"
        message = f"Fetching market data for {symbols_str}, {days} days of history"
        self._write_log_entry(message)
    
    def log_recommendation_generation(self, topic: str, recommendation: str, score: float):
        """
        Log generation of investment recommendation.
        
        Args:
            topic: Topic/symbol
            recommendation: Recommendation type (BUY, HOLD, SELL, etc.)
            score: Aggregated sentiment score
        """
        message = f"Generated recommendation for {topic}: {recommendation} (score: {score:.2f})"
        self._write_log_entry(message)
    
    def log_ui_launch(self, host: str, port: int):
        """
        Log UI application launch.
        
        Args:
            host: Host address
            port: Port number
        """
        message = f"Web UI launched at {host}:{port}"
        self._write_log_entry(message)
    
    def log_api_request(self, endpoint: str, method: str):
        """
        Log API request to the web interface.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
        """
        message = f"API request: {method} {endpoint}"
        self._write_log_entry(message)
    
    def log_notification_created(self, title: str, severity: str):
        """
        Log creation of a notification.
        
        Args:
            title: Notification title
            severity: Severity level
        """
        message = f"Notification created: {title} (severity: {severity})"
        self._write_log_entry(message)
    
    def log_custom(self, message: str):
        """
        Log a custom message.
        
        Args:
            message: Custom log message
        """
        self._write_log_entry(message)


# Global logger instance
_global_logger: Optional[VutsLogger] = None


def get_logger(logs_dir: Optional[Path] = None) -> VutsLogger:
    """
    Get or create the global logger instance.
    
    Args:
        logs_dir: Optional logs directory. Only used on first call.
    
    Returns:
        VutsLogger instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = VutsLogger(logs_dir)
    return _global_logger


def log_fetch_request(sources: list, topics: list):
    """Convenience function to log fetch request."""
    get_logger().log_fetch_request(sources, topics)


def log_search_execution(source: str, topic: str, articles_found: int):
    """Convenience function to log search execution."""
    get_logger().log_search_execution(source, topic, articles_found)


def log_analysis_start(data_dir: str, max_articles: int, model: str):
    """Convenience function to log analysis start."""
    get_logger().log_analysis_start(data_dir, max_articles, model)


def log_article_processing(topic: str, article_title: str, score: float):
    """Convenience function to log article processing."""
    get_logger().log_article_processing(topic, article_title, score)


def log_market_data_request(symbols: list, days: int):
    """Convenience function to log market data request."""
    get_logger().log_market_data_request(symbols, days)


def log_recommendation_generation(topic: str, recommendation: str, score: float):
    """Convenience function to log recommendation generation."""
    get_logger().log_recommendation_generation(topic, recommendation, score)


def log_ui_launch(host: str, port: int):
    """Convenience function to log UI launch."""
    get_logger().log_ui_launch(host, port)


def log_api_request(endpoint: str, method: str):
    """Convenience function to log API request."""
    get_logger().log_api_request(endpoint, method)


def log_notification_created(title: str, severity: str):
    """Convenience function to log notification creation."""
    get_logger().log_notification_created(title, severity)


def log_custom(message: str):
    """Convenience function to log custom message."""
    get_logger().log_custom(message)
