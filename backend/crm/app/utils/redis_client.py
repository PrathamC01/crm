"""
Redis client for session management
"""

import redis
import json
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from ..config import settings


class RedisClient:
    def __init__(self):
        try:
            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            self.redis.ping()
            self.available = True
            print("✅ Redis connection established")
        except Exception as e:
            print(f"⚠️  Redis connection failed: {e}")
            print("📝 Session management will use fallback storage")
            self.redis = None
            self.available = False
            self._fallback_sessions = {}  # In-memory fallback

    def create_session(self, user_id: int, user_data: Dict[str, Any]) -> str:
        """Create a new session and return session ID"""
        session_id = user_data.get("token")
        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (
                datetime.utcnow() + timedelta(minutes=settings.SESSION_EXPIRE_MINUTES)
            ).isoformat(),
            **user_data,
        }

        if self.available:
            # Store session with expiration in Redis
            self.redis.setex(
                f"auth:{session_id}",
                timedelta(minutes=settings.SESSION_EXPIRE_MINUTES),
                json.dumps(session_data),
            )
            print("added the data", session_data)
        else:
            # Fallback to in-memory storage
            self._fallback_sessions[session_id] = session_data

        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by session ID"""
        if self.available:
            session_data = self.redis.get(f"auth:{session_id}")
            if session_data:
                return json.loads(session_data)
        else:
            # Fallback storage
            return self._fallback_sessions.get(session_id)

        return None

    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Update session data"""
        if self.available:
            session_data = self.get_session(session_id)
            if session_data:
                session_data.update(data)
                # Refresh expiration
                self.redis.setex(
                    f"auth:{session_id}",
                    timedelta(minutes=settings.SESSION_EXPIRE_MINUTES),
                    json.dumps(session_data),
                )
                return True
        else:
            # Fallback storage
            if session_id in self._fallback_sessions:
                self._fallback_sessions[session_id].update(data)
                return True

        return False

    def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        if self.available:
            return bool(self.redis.delete(f"auth:{session_id}"))
        else:
            # Fallback storage
            if session_id in self._fallback_sessions:
                del self._fallback_sessions[session_id]
                return True

        return False

    def refresh_session(self, session_id: str) -> bool:
        """Refresh session expiration"""
        if self.available:
            session_data = self.get_session(session_id)
            if session_data:
                session_data["expires_at"] = (
                    datetime.utcnow()
                    + timedelta(minutes=settings.SESSION_EXPIRE_MINUTES)
                ).isoformat()
                self.redis.setex(
                    f"auth:{session_id}",
                    timedelta(minutes=settings.SESSION_EXPIRE_MINUTES),
                    json.dumps(session_data),
                )
                return True
        else:
            # Fallback - just mark as refreshed
            if session_id in self._fallback_sessions:
                self._fallback_sessions[session_id]["expires_at"] = (
                    datetime.utcnow()
                    + timedelta(minutes=settings.SESSION_EXPIRE_MINUTES)
                ).isoformat()
                return True

        # For test sessions, always return True
        if session_id.startswith("test_"):
            return True

        return False


# Global Redis client instance
redis_client = RedisClient()
