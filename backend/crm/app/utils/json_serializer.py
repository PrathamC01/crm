"""
JSON serialization utilities for the CRM application.
Provides safe serialization functions for complex objects.
"""

import json
from typing import Any
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from enum import Enum


def json_safe(obj: Any) -> Any:
    """
    Convert objects to JSON-serializable format.
    Handles datetime, date, Decimal, UUID, Enum, and other common types.
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, UUID):
        return str(obj)
    elif isinstance(obj, Enum):
        return obj.value
    elif hasattr(obj, '__dict__'):
        # Handle SQLAlchemy models and similar objects
        return {key: json_safe(value) for key, value in obj.__dict__.items() 
                if not key.startswith('_')}
    elif isinstance(obj, (list, tuple)):
        return [json_safe(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: json_safe(value) for key, value in obj.items()}
    else:
        return obj


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """
    Safely serialize objects to JSON string.
    Uses json_safe to handle complex objects.
    """
    return json.dumps(json_safe(obj), **kwargs)