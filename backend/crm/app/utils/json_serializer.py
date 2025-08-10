from datetime import date, datetime
from decimal import Decimal


def json_safe(value):
    """Recursively convert Pydantic/complex objects to JSON-safe primitives."""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    if isinstance(value, dict):
        return {k: json_safe(v) for k, v in value.items()}
    return value
