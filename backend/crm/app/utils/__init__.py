"""
Utility functions for CRM application
"""

from .auth import hash_password, verify_password, create_access_token, verify_token
from .logger import log_activity
from .json_serializer import json_safe
from .redis_client import redis_client

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "verify_token",
    "redis_client",
    "log_activity",
    "json_safe",
]
