"""
Logging utilities
"""
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import Request

async def log_activity(mongo_db, user_id: int, action: str, details: Optional[Dict[str, Any]] = None, request: Optional[Request] = None):
    """Log user activity to MongoDB"""
    try:
        if mongo_db is not None:
            log_entry = {
                "user_id": user_id,
                "action": action,
                "details": details or {},
                "timestamp": datetime.utcnow(),
                "ip_address": request.client.host if request else None,
                "user_agent": request.headers.get("user-agent") if request else None
            }
            mongo_db.activity_logs.insert_one(log_entry)
    except Exception as e:
        print(f"Failed to log activity: {e}")

async def log_request(mongo_db, method: str, url: str, status_code: int, 
                     process_time: float, ip_address: str, user_agent: str):
    """Log HTTP request to MongoDB""" 
    try:
        if mongo_db is not None: 
            log_entry = {
                "method": method,
                "url": url,
                "status_code": status_code,
                "process_time": process_time,
                "timestamp": datetime.utcnow(),
                "ip_address": ip_address,
                "user_agent": user_agent
            }
            mongo_db.request_logs.insert_one(log_entry)
    except Exception as e:
        print(f"Failed to log request: {e}")

async def log_error(mongo_db, error_id: int, url: str, method: str, error_details: Dict[str, Any]):
    """Log error to MongoDB"""
    try:
        if mongo_db is not None:
            mongo_db.error_logs.insert_one({
                "error_id": error_id,
                "url": url,
                "method": method,
                "error_details": error_details,
                "timestamp": datetime.utcnow()
            })
    except Exception as e:
        print(f"Failed to log error: {e}")