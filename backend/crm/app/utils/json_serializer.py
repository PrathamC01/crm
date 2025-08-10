"""
JSON serialization utilities for the CRM application.
Provides safe serialization functions for complex objects.
"""

import json
from typing import Any
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID


def json_safe(value: Any) -> Any:
    """Recursively convert to JSON-safe values."""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    if isinstance(value, dict):
        return {k: json_safe(v) for k, v in value.items()}
    return value


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """
    Safely serialize objects to JSON string.
    Uses json_safe to handle complex objects.
    """
    return json.dumps(json_safe(obj), **kwargs)
