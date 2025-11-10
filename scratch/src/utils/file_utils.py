"""
File and directory utilities shared across modules.
"""
import json
from pathlib import Path
from typing import Any, Callable


def safe_json_load(file_path: Path, default: Any = None) -> Any:
    """
    Safely load JSON file with error handling.
    
    Args:
        file_path: Path to JSON file
        default: Value to return if loading fails
        
    Returns:
        Parsed JSON data or default value
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARNING] Could not load JSON from {file_path}: {e}")
        return default


def safe_json_save(file_path: Path, data: Any, json_handler: Callable = None) -> bool:
    """
    Safely save data to JSON file with error handling.
    
    Args:
        file_path: Path to save JSON file
        data: Data to serialize
        json_handler: Optional custom JSON serialization handler
        
    Returns:
        True if successful, False otherwise
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=json_handler)
        return True
    except Exception as e:
        print(f"[ERROR] Could not save JSON to {file_path}: {e}")
        return False


def ensure_directory(dir_path: Path) -> Path:
    """
    Ensure directory exists, create if necessary.
    
    Args:
        dir_path: Path to directory
        
    Returns:
        The directory path
    """
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path
