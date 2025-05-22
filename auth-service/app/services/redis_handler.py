from datetime import datetime, timedelta
import redis
import logging
from functools import wraps
from app.core.config import settings
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Check if redis client is initialized properly.
def check_redist_initialized(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.client is None:
            logging.error("Redis client not initialized")
            raise Exception("Redis client not initialized")
        return func(self, *args, **kwargs)
    return wrapper

class RedisErrorCode(Enum):
    REDIS_TOKEN_NOT_FOUND = 1001

class RedisHandler:
    """
    Redis handler for managing Redis operations.
    """
    def __init__(self):
        """Initialize Redis client based on environment."""
        try:
            if settings.REDIS_MODE == "production":
                # Production mode - Redis Cloud
                if not all([settings.REDIS_CLOUD_URL, settings.REDIS_CLOUD_USERNAME, settings.REDIS_CLOUD_PASSWORD]):
                    raise ValueError("Redis Cloud credentials are required in production mode")
                
                self.client = redis.Redis.from_url(
                    settings.REDIS_CLOUD_URL,
                    username=settings.REDIS_CLOUD_USERNAME,
                    password=settings.REDIS_CLOUD_PASSWORD,
                    decode_responses=True,
                    ssl=True
                )
                logger.info("Connected to Redis Cloud in production mode")
            else:
                # Local development mode
                self.client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD,
                    decode_responses=True
                )
                logger.info("Connected to local Redis in development mode")
            
            # Test connection
            self.client.ping()
            
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error initializing Redis: {str(e)}")
            raise

    def get(self, key: str) -> str:
        """Get a value from Redis."""
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Failed to get value: {str(e)}")
            return None

    def setex(self, key: str, expiry: int, value: str) -> bool:
        """Set a value in Redis with expiry."""
        try:
            return self.client.setex(key, expiry, value)
        except Exception as e:
            logger.error(f"Failed to set value: {str(e)}")
            return False

    def incr(self, key: str) -> int:
        """Increment a value in Redis."""
        try:
            return self.client.incr(key)
        except Exception as e:
            logger.error(f"Failed to increment value: {str(e)}")
            return 0

    def lpush(self, key: str, value: str) -> int:
        """Push a value to the left of a list."""
        try:
            return self.client.lpush(key, value)
        except Exception as e:
            logger.error(f"Failed to push value: {str(e)}")
            return 0

    def ltrim(self, key: str, start: int, end: int) -> bool:
        """Trim a list to the specified range."""
        try:
            return self.client.ltrim(key, start, end)
        except Exception as e:
            logger.error(f"Failed to trim list: {str(e)}")
            return False

    def sismember(self, key: str, value: str) -> bool:
        """Check if a value is a member of a set."""
        try:
            return self.client.sismember(key, value)
        except Exception as e:
            logger.error(f"Failed to check set membership: {str(e)}")
            return False

    def sadd(self, key: str, value: str) -> int:
        """Add a value to a set."""
        try:
            return self.client.sadd(key, value)
        except Exception as e:
            logger.error(f"Failed to add to set: {str(e)}")
            return 0

    def delete(self, key: str) -> int:
        """Delete a key from Redis."""
        try:
            return self.client.delete(key)
        except Exception as e:
            logger.error(f"Failed to delete key: {str(e)}")
            return 0

    def log_security_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Log a security event to Redis."""
        try:
            # Redact sensitive information
            redacted_data = self._redact_sensitive_data(event_data)
            
            # Create event log entry
            log_entry = {
                "type": event_type,
                "timestamp": str(datetime.now()),
                "data": redacted_data
            }
            
            # Store in Redis list
            self.client.lpush("security_events", json.dumps(log_entry))
            # Keep only last 1000 events
            self.client.ltrim("security_events", 0, 999)
            return True
        except Exception as e:
            logger.error(f"Error logging security event: {str(e)}")
            return False

    def store_token(self, key: str, token: str, expiry: int) -> bool:
        """Store a token in Redis."""
        try:
            return self.client.setex(key, expiry, token)
        except Exception as e:
            logger.error(f"Error storing token: {str(e)}")
            return False

    def get_token(self, key: str) -> Optional[str]:
        """Get a token from Redis."""
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Error getting token: {str(e)}")
            return None

    def delete_token(self, key: str) -> bool:
        """Delete a token from Redis."""
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting token: {str(e)}")
            return False

    def store_refresh_token(self, user_id: str, refresh_token_id: str) -> bool:
        """Store a refresh token in Redis."""
        try:
            key = f"refresh_tokens:{user_id}"
            data = {
                "token_id": refresh_token_id,
                "created_at": str(datetime.now()),
                "expires_at": str(datetime.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
            }
            return self.client.hset(key, mapping=data)
        except Exception as e:
            logger.error(f"Error storing refresh token: {str(e)}")
            return False

    def get_refresh_token(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a refresh token from Redis."""
        try:
            key = f"refresh_tokens:{user_id}"
            data = self.client.hgetall(key)
            return data if data else None
        except Exception as e:
            logger.error(f"Error getting refresh token: {str(e)}")
            return None

    def delete_refresh_token(self, user_id: str) -> bool:
        """Delete a refresh token from Redis."""
        try:
            key = f"refresh_tokens:{user_id}"
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting refresh token: {str(e)}")
            return False

    def _redact_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive information from event data."""
        sensitive_fields = {'password', 'token', 'secret', 'key'}
        redacted = data.copy()
        
        for key in redacted:
            if key.lower() in sensitive_fields:
                redacted[key] = '[REDACTED]'
        
        return redacted
