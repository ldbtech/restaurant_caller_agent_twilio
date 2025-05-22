import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from jose import jwt
from app.services.redis_handler import RedisHandler
from app.core.config import settings

logger = logging.getLogger(__name__)

class Security:
    """
    Security service that handles all security-related functionality.
    
    This class is the single source of truth for:
    - Rate limiting
    - Security event logging
    - Input validation
    - Security checks
    """
    
    def __init__(self):
        self.redis_handler = RedisHandler()

    def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """
        Check if a request is within rate limits.
        
        Args:
            key (str): Rate limit key
            limit (int): Maximum number of requests allowed
            window (int): Time window in seconds
            
        Returns:
            bool: True if within limits, False otherwise
        """
        try:
            current = self.redis_handler.redis.get(key)
            if current is None:
                self.redis_handler.redis.setex(key, window, "1")
                return True
                
            count = int(current)
            if count >= limit:
                return False
                
            self.redis_handler.redis.incr(key)
            return True
        except Exception as e:
            logger.error(f"Rate limit check failed: {str(e)}")
            return False

    def log_security_event(self, event_type: str, event_data: Dict) -> bool:
        """
        Log a security event.
        
        Args:
            event_type (str): Type of event
            event_data (Dict): Event data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return self.redis_handler.log_security_event(event_type, event_data)
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")
            return False

    def _sanitize_log_data(self, data: Dict) -> Dict:
        """
        Sanitize log data to remove sensitive information.
        
        Args:
            data (Dict): Data to sanitize
            
        Returns:
            Dict: Sanitized data
        """
        sanitized = data.copy()
        
        # Remove sensitive fields
        sensitive_fields = ['password', 'token', 'secret', 'key']
        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = '[REDACTED]'
                
        return sanitized

    def validate_password(self, password: str) -> bool:
        """
        Validate password strength.
        
        Args:
            password (str): Password to validate
            
        Returns:
            bool: True if password is valid, False otherwise
        """
        if len(password) < 8:
            return False
        return True

    def validate_email(self, email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email (str): Email to validate
            
        Returns:
            bool: True if email is valid, False otherwise
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def check_ip_blacklist(self, ip: str) -> bool:
        """
        Check if an IP is blacklisted.
        
        Args:
            ip (str): IP address to check
            
        Returns:
            bool: True if not blacklisted, False otherwise
        """
        try:
            return not self.redis_handler.redis.exists(f"blacklisted_ips:{ip}")
        except Exception as e:
            logger.error(f"IP blacklist check failed: {str(e)}")
            return False

    def add_to_ip_blacklist(self, ip: str, duration: int) -> bool:
        """
        Add an IP to the blacklist.
        
        Args:
            ip (str): IP address to blacklist
            duration (int): Blacklist duration in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return self.redis_handler.redis.setex(f"blacklisted_ips:{ip}", duration, "1")
        except Exception as e:
            logger.error(f"Failed to add IP to blacklist: {str(e)}")
            return False

    def check_token_blacklist(self, token: str) -> bool:
        """
        Check if a token is blacklisted.
        
        Args:
            token (str): Token to check
            
        Returns:
            bool: True if not blacklisted, False otherwise
        """
        try:
            return not self.redis_handler.redis.exists(f"blacklisted_tokens:{token}")
        except Exception as e:
            logger.error(f"Token blacklist check failed: {str(e)}")
            return False

    def add_to_token_blacklist(self, token: str, duration: int) -> bool:
        """
        Add a token to the blacklist.
        
        Args:
            token (str): Token to blacklist
            duration (int): Blacklist duration in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return self.redis_handler.redis.setex(f"blacklisted_tokens:{token}", duration, "1")
        except Exception as e:
            logger.error(f"Failed to add token to blacklist: {str(e)}")
            return False

    def create_access_token(self, user_id: str) -> str:
        """
        Create an access token.
        
        Args:
            user_id (str): User ID
            
        Returns:
            str: JWT access token
        """
        try:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            to_encode = {
                "sub": str(user_id),
                "exp": expire,
                "type": "access"
            }
            return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        except Exception as e:
            logger.error(f"Failed to create access token: {str(e)}")
            raise

    def create_refresh_token(self, user_id: str) -> str:
        """
        Create a refresh token.
        
        Args:
            user_id (str): User ID
            
        Returns:
            str: JWT refresh token
        """
        try:
            expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            to_encode = {
                "sub": str(user_id),
                "exp": expire,
                "type": "refresh"
            }
            return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        except Exception as e:
            logger.error(f"Failed to create refresh token: {str(e)}")
            raise 