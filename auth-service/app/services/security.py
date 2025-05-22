import logging
from typing import Dict, Optional
from datetime import datetime
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
            current = self.redis_handler.get(key)
            if current is None:
                self.redis_handler.setex(key, window, "1")
                return True
                
            current = int(current)
            if current >= limit:
                return False
                
            self.redis_handler.incr(key)
            return True
        except Exception as e:
            logger.error(f"Rate limit check failed: {str(e)}")
            return False

    def log_security_event(self, event_type: str, event_data: dict) -> None:
        """
        Log security events with proper sanitization.
        
        Args:
            event_type (str): Type of security event
            event_data (dict): Event data to log
        """
        try:
            sanitized_data = self._sanitize_log_data(event_data)
            logger.info(f"Security Event - {event_type}: {sanitized_data}")
            self.redis_handler.log_security_event(event_type, sanitized_data)
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")

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
            bool: True if IP is not blacklisted, False otherwise
        """
        try:
            return not self.redis_handler.sismember("blacklisted_ips", ip)
        except Exception as e:
            logger.error(f"IP blacklist check failed: {str(e)}")
            return True  # Allow request if check fails

    def add_to_ip_blacklist(self, ip: str, duration: int = 3600) -> None:
        """
        Add an IP to the blacklist.
        
        Args:
            ip (str): IP address to blacklist
            duration (int): Duration in seconds (default: 1 hour)
        """
        try:
            self.redis_handler.setex(f"blacklisted_ips:{ip}", duration, "1")
            self.log_security_event("ip_blacklisted", {"ip": ip, "duration": duration})
        except Exception as e:
            logger.error(f"Failed to blacklist IP: {str(e)}")

    def check_token_blacklist(self, token: str) -> bool:
        """
        Check if a token is blacklisted.
        
        Args:
            token (str): Token to check
            
        Returns:
            bool: True if token is not blacklisted, False otherwise
        """
        try:
            return not self.redis_handler.sismember("blacklisted_tokens", token)
        except Exception as e:
            logger.error(f"Token blacklist check failed: {str(e)}")
            return True  # Allow request if check fails

    def add_to_token_blacklist(self, token: str, duration: int = 86400) -> None:
        """
        Add a token to the blacklist.
        
        Args:
            token (str): Token to blacklist
            duration (int): Duration in seconds (default: 24 hours)
        """
        try:
            self.redis_handler.setex(f"blacklisted_tokens:{token}", duration, "1")
            self.log_security_event("token_blacklisted", {"token": token[:10] + "..."})
        except Exception as e:
            logger.error(f"Failed to blacklist token: {str(e)}") 