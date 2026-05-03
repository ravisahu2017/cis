"""
JSON utility functions for safe serialization
"""

import json
from datetime import datetime
from typing import Any


def safe_json_serialize(obj: Any) -> Any:
    """
    Safely serialize object to JSON, handling datetime objects and complex types
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON-serializable version of the object
    """
    if hasattr(obj, 'dict'):
        return safe_json_serialize(obj.dict())
    elif isinstance(obj, dict):
        return {k: safe_json_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [safe_json_serialize(item) for item in obj]
    elif isinstance(obj, tuple):
        return [safe_json_serialize(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        # Handle objects with __dict__ but no .dict() method
        return safe_json_serialize(obj.__dict__)
    else:
        return obj


def safe_json_dumps(obj: Any, indent: int = None) -> str:
    """
    Convert object to JSON string with safe serialization
    
    Args:
        obj: Object to convert to JSON
        indent: JSON indentation (optional)
        
    Returns:
        JSON string
    """
    return json.dumps(safe_json_serialize(obj), indent=indent, default=str)


def safe_json_loads(json_str: str) -> Any:
    """
    Load JSON string with error handling
    
    Args:
        json_str: JSON string to load
        
    Returns:
        Parsed JSON object or None if failed
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None


def safe_parse_json_field(json_str: str, default: Any = None) -> Any:
    """
    Safely parse JSON field with fallback
    
    Args:
        json_str: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed object or default value
    """
    if not json_str:
        return default or []
    
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        # Try to handle common Python list format
        if json_str.startswith('[') and json_str.endswith(']'):
            try:
                # Replace Python-style quotes with JSON quotes
                cleaned = json_str.replace("'", '"')
                return json.loads(cleaned)
            except json.JSONDecodeError:
                pass
        
        return default or []
