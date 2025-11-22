"""
Date and time utilities shared across modules.
"""
import datetime
from typing import Optional
from email.utils import parsedate_to_datetime


def ensure_datetime(dt_value: Optional[object]) -> datetime.datetime:
    """
    Convert various datetime representations to datetime object with timezone.
    
    Args:
        dt_value: Can be datetime object, ISO string, or email date string
        
    Returns:
        datetime object with UTC timezone
    """
    if isinstance(dt_value, datetime.datetime):
        if dt_value.tzinfo is None:
            return dt_value.replace(tzinfo=datetime.timezone.utc)
        return dt_value
        
    if isinstance(dt_value, str):
        # Try ISO format first
        try:
            dt = datetime.datetime.fromisoformat(dt_value.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            return dt
        except Exception:
            pass
            
        # Try email date format
        try:
            dt = parsedate_to_datetime(dt_value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            return dt
        except Exception:
            pass
    
    # Default to current time
    return datetime.datetime.now(datetime.timezone.utc)


def is_recent(date: datetime.datetime, max_age_days: int) -> bool:
    """
    Check if a date is within the specified age limit.
    
    Args:
        date: The datetime to check
        max_age_days: Maximum age in days
        
    Returns:
        True if date is recent enough, False otherwise
    """
    if date.tzinfo is None:
        date = date.replace(tzinfo=datetime.timezone.utc)
    now = datetime.datetime.now(datetime.timezone.utc)
    return (now - date).days <= max_age_days


def json_datetime_handler(obj):
    """
    JSON serialization handler for datetime objects.
    
    Args:
        obj: Object to serialize
        
    Returns:
        ISO format string for datetime, str() for others
    """
    if isinstance(obj, datetime.datetime):
        if obj.tzinfo is None:
            obj = obj.replace(tzinfo=datetime.timezone.utc)
        return obj.isoformat()
    return str(obj)
