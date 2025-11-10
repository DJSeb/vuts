# Utilities Module

Shared utility functions used across multiple modules.

## Overview

**Location**: `scratch/src/utils/`

The utilities module provides common functionality:
- Date/time handling and timezone management
- JSON serialization with datetime support
- File operations with error handling
- Directory management

## Modules

### datetime_utils.py

Utilities for date and time operations.

#### `ensure_datetime(dt_value)`

Convert various datetime representations to timezone-aware datetime objects.

**Parameters:**
- `dt_value`: Can be datetime object, ISO string, or email date string

**Returns:**
- datetime object with UTC timezone

**Example:**
```python
from utils.datetime_utils import ensure_datetime

# From ISO string
dt = ensure_datetime("2024-11-10T12:00:00Z")

# From datetime object
dt = ensure_datetime(datetime.datetime.now())

# Handles missing timezone
dt = ensure_datetime("2024-11-10T12:00:00")  # Assumes UTC
```

#### `is_recent(date, max_age_days)`

Check if a date is within the specified age limit.

**Parameters:**
- `date`: datetime object to check
- `max_age_days`: Maximum age in days

**Returns:**
- True if date is recent enough, False otherwise

**Example:**
```python
from utils.datetime_utils import is_recent
import datetime

now = datetime.datetime.now(datetime.timezone.utc)
yesterday = now - datetime.timedelta(days=1)
week_ago = now - datetime.timedelta(days=7)

is_recent(yesterday, max_age_days=3)  # True
is_recent(week_ago, max_age_days=3)   # False
```

#### `json_datetime_handler(obj)`

JSON serialization handler for datetime objects.

**Parameters:**
- `obj`: Object to serialize

**Returns:**
- ISO format string for datetime, str() for others

**Example:**
```python
import json
from utils.datetime_utils import json_datetime_handler
import datetime

data = {
    "timestamp": datetime.datetime.now(datetime.timezone.utc),
    "value": 42
}

json_str = json.dumps(data, default=json_datetime_handler)
```

### file_utils.py

Utilities for file and directory operations.

#### `safe_json_load(file_path, default=None)`

Safely load JSON file with error handling.

**Parameters:**
- `file_path`: Path to JSON file
- `default`: Value to return if loading fails (default: None)

**Returns:**
- Parsed JSON data or default value

**Example:**
```python
from utils.file_utils import safe_json_load
from pathlib import Path

# Load with fallback
config = safe_json_load(Path("config.json"), default={})

# Load required file
data = safe_json_load(Path("data.json"))
if data is None:
    print("Failed to load data")
```

#### `safe_json_save(file_path, data, json_handler=None)`

Safely save data to JSON file with error handling.

**Parameters:**
- `file_path`: Path to save JSON file
- `data`: Data to serialize
- `json_handler`: Optional custom JSON serialization handler

**Returns:**
- True if successful, False otherwise

**Example:**
```python
from utils.file_utils import safe_json_save
from utils.datetime_utils import json_datetime_handler
from pathlib import Path
import datetime

data = {
    "created": datetime.datetime.now(datetime.timezone.utc),
    "value": 42
}

success = safe_json_save(
    Path("output/data.json"),
    data,
    json_handler=json_datetime_handler
)
```

#### `ensure_directory(dir_path)`

Ensure directory exists, create if necessary.

**Parameters:**
- `dir_path`: Path to directory

**Returns:**
- The directory path

**Example:**
```python
from utils.file_utils import ensure_directory
from pathlib import Path

# Create directory if it doesn't exist
output_dir = ensure_directory(Path("output/scores"))

# Works with nested directories
nested = ensure_directory(Path("output/data/2024/11"))
```

## Usage Patterns

### Loading Configuration

```python
from utils.file_utils import safe_json_load
from pathlib import Path

config = safe_json_load(
    Path("config.json"),
    default={"max_articles": 10, "model": "gpt-4o-mini"}
)

max_articles = config.get("max_articles", 10)
```

### Saving Results with Timestamps

```python
from utils.file_utils import safe_json_save, ensure_directory
from utils.datetime_utils import json_datetime_handler
from pathlib import Path
import datetime

# Prepare data
result = {
    "timestamp": datetime.datetime.now(datetime.timezone.utc),
    "score": 5.5,
    "status": "success"
}

# Ensure directory exists
output_dir = ensure_directory(Path("output/results"))

# Save with datetime handling
safe_json_save(
    output_dir / "result.json",
    result,
    json_handler=json_datetime_handler
)
```

### Filtering Recent Articles

```python
from utils.datetime_utils import ensure_datetime, is_recent
import datetime

articles = load_articles()  # Your article loading function

# Filter to last 7 days
cutoff_days = 7
recent_articles = []

for article in articles:
    pub_date = ensure_datetime(article["published_at"])
    if is_recent(pub_date, cutoff_days):
        recent_articles.append(article)
```

## Design Principles

### Error Handling

All utilities use graceful error handling:
- Print warnings for non-critical errors
- Return sensible defaults (None, empty dict, current time)
- Don't crash the entire application

### Timezone Awareness

All datetime utilities ensure timezone awareness:
- Assume UTC if no timezone specified
- Always return timezone-aware datetimes
- Handle various input formats consistently

### Path Flexibility

File utilities work with both strings and Path objects:
- Convert strings to Path internally
- Return Path objects for consistency
- Support nested directory creation

## Integration

These utilities are used throughout the codebase:

**Fetching Module:**
- `ensure_datetime` for parsing article dates
- `is_recent` for filtering articles
- `json_datetime_handler` for saving articles

**LLM Module:**
- `ensure_datetime` for date parsing
- `ensure_directory` for creating score directories
- `safe_json_save` for saving scores

**Market Module:**
- `json_datetime_handler` for saving market data
- `ensure_directory` for organizing output

## Testing

The utilities are indirectly tested through:
- Fetching module tests
- LLM module tests
- Demo workflow validation

Example usage in tests:

```python
from utils.datetime_utils import ensure_datetime, is_recent
import datetime

# Test ensure_datetime
dt1 = ensure_datetime("2024-11-10T12:00:00Z")
assert dt1.tzinfo is not None

dt2 = ensure_datetime(datetime.datetime.now())
assert dt2.tzinfo is not None

# Test is_recent
now = datetime.datetime.now(datetime.timezone.utc)
assert is_recent(now, 1) == True

old = now - datetime.timedelta(days=10)
assert is_recent(old, 1) == False
```

## Performance

Utilities are designed for efficiency:
- `ensure_datetime`: Fast conversion with fallbacks
- `is_recent`: Simple date arithmetic
- `safe_json_load/save`: Standard json library + error handling
- `ensure_directory`: Uses built-in mkdir with exist_ok=True

## Best Practices

1. **Always use ensure_datetime** for user input dates
2. **Use safe_json_save** instead of open() + json.dump()
3. **Create directories with ensure_directory** instead of mkdir
4. **Pass json_datetime_handler** when saving data with timestamps
5. **Check is_recent return value** for date filtering

## See Also

- [Fetching Module](Fetching-Module) - Uses datetime utilities
- [LLM Module](LLM-Module) - Uses file utilities
- [Market Module](Market-Module) - Uses both datetime and file utilities
- [Architecture](Architecture) - System design overview
