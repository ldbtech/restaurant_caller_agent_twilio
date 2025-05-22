from datetime import datetime, timedelta
import redis
import logging
from functools import wraps
from enum import Enum
from app.core.config import settings
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Check if redis client is initialized properly.
def check_redist_initialized(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.redis is None:
            logging.error("Redis client not initialized")
            raise Exception("Redis client not initialized")
        return func(self, *args, **kwargs)
    return wrapper

class RedisErrorCode(Enum):
    REDIS_TOKEN_NOT_FOUND = 1001

class RedisHandler:
    """Redis handler for managing tokens and security events."""
    
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )

    def get(self, key: str) -> str:
        """Get a value from Redis."""
        try:
            return self.redis.get(key)
        except Exception as e:
            logger.error(f"Failed to get value: {str(e)}")
            return None

    def setex(self, key: str, expiry: int, value: str) -> bool:
        """Set a value in Redis with expiry."""
        try:
            self.redis.setex(key, expiry, value)
            return True
        except Exception as e:
            logger.error(f"Failed to set value: {str(e)}")
            return False

    def incr(self, key: str) -> int:
        """Increment a value in Redis."""
        try:
            return self.redis.incr(key)
        except Exception as e:
            logger.error(f"Failed to increment value: {str(e)}")
            return 0

    def lpush(self, key: str, value: str) -> int:
        """Push a value to the left of a list."""
        try:
            return self.redis.lpush(key, value)
        except Exception as e:
            logger.error(f"Failed to push value: {str(e)}")
            return 0

    def ltrim(self, key: str, start: int, end: int) -> bool:
        """Trim a list to the specified range."""
        try:
            self.redis.ltrim(key, start, end)
            return True
        except Exception as e:
            logger.error(f"Failed to trim list: {str(e)}")
            return False

    def sismember(self, key: str, value: str) -> bool:
        """Check if a value is a member of a set."""
        try:
            return self.redis.sismember(key, value)
        except Exception as e:
            logger.error(f"Failed to check set membership: {str(e)}")
            return False

    def sadd(self, key: str, value: str) -> int:
        """Add a value to a set."""
        try:
            return self.redis.sadd(key, value)
        except Exception as e:
            logger.error(f"Failed to add to set: {str(e)}")
            return 0

    def delete(self, key: str) -> int:
        """Delete a key from Redis."""
        try:
            return self.redis.delete(key)
        except Exception as e:
            logger.error(f"Failed to delete key: {str(e)}")
            return 0

    def log_security_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Log a security event to Redis.
        
        Args:
            event_type (str): Type of event
            event_data (Dict[str, Any]): Event data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            event = {
                "type": event_type,
                "data": self._redact_sensitive_data(event_data),
                "timestamp": datetime.utcnow().isoformat()
            }
            return bool(self.redis.lpush("security_events", json.dumps(event)))
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")
            return False

    def store_token(self, key: str, token: str, expiry: int) -> bool:
        """
        Store a token in Redis.
        
        Args:
            key (str): Key to store token under
            token (str): Token to store
            expiry (int): Expiry time in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return self.redis.setex(key, expiry, token)
        except Exception as e:
            logger.error(f"Failed to store token: {str(e)}")
            return False

    def get_token(self, key: str) -> Optional[str]:
        """
        Get a token from Redis.
        
        Args:
            key (str): Key to get token for
            
        Returns:
            Optional[str]: Token if found, None otherwise
        """
        try:
            return self.redis.get(key)
        except Exception as e:
            logger.error(f"Failed to get token: {str(e)}")
            return None

    def delete_token(self, key: str) -> bool:
        """
        Delete a token from Redis.
        
        Args:
            key (str): Key to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"Failed to delete token: {str(e)}")
            return False

    def store_refresh_token(self, user_id: str, token_id: str) -> bool:
        """
        Store a refresh token in Redis.
        
        Args:
            user_id (str): User ID
            token_id (str): Token ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            key = f"refresh_tokens:{user_id}"
            data = {
                "token_id": token_id,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
            }
            return bool(self.redis.hset(key, mapping=data))
        except Exception as e:
            logger.error(f"Failed to store refresh token: {str(e)}")
            return False

    def get_refresh_token(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a refresh token from Redis.
        
        Args:
            user_id (str): User ID
            
        Returns:
            Optional[Dict[str, Any]]: Token data if found, None otherwise
        """
        try:
            key = f"refresh_tokens:{user_id}"
            data = self.redis.hgetall(key)
            return data if data else None
        except Exception as e:
            logger.error(f"Failed to get refresh token: {str(e)}")
            return None

    def delete_refresh_token(self, user_id: str) -> bool:
        """
        Delete a refresh token from Redis.
        
        Args:
            user_id (str): User ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            key = f"refresh_tokens:{user_id}"
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"Failed to delete refresh token: {str(e)}")
            return False

    def _redact_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive information from event data."""
        sensitive_fields = {'password', 'token', 'secret', 'key'}
        redacted = data.copy()
        
        for key in redacted:
            if key.lower() in sensitive_fields:
                redacted[key] = '[REDACTED]'
        
        return redacted
