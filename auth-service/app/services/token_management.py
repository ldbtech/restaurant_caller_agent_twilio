import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from jose import jwt
from app.core.config import settings
from app.services.redis_handler import RedisHandler

logger = logging.getLogger(__name__)

class TokenManagement:
    """Token management service for handling JWT tokens."""
    
    def __init__(self):
        self.access_token_expiry = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        self.refresh_token_expiry = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        self.redis_handler = RedisHandler()

    def generate_access_token(self, user_data: Dict) -> str:
        """
        Generate an access token.
        
        Args:
            user_data (Dict): User data to include in token
            
        Returns:
            str: JWT access token
        """
        try:
            expire = datetime.utcnow() + self.access_token_expiry
            to_encode = {
                "sub": str(user_data.get("user_id", user_data.get("id"))),
                "exp": expire,
                "type": "access"
            }
            token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
            self.redis_handler.store_token(f"token:{to_encode['sub']}", token, self.access_token_expiry.seconds)
            return token
        except Exception as e:
            logger.error(f"Failed to generate access token: {str(e)}")
            raise

    def generate_refresh_token(self, user_data: Dict) -> str:
        """
        Generate a refresh token.
        
        Args:
            user_data (Dict): User data to include in token
            
        Returns:
            str: JWT refresh token
        """
        try:
            expire = datetime.utcnow() + self.refresh_token_expiry
            to_encode = {
                "sub": str(user_data.get("user_id", user_data.get("id"))),
                "exp": expire,
                "type": "refresh"
            }
            token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
            self.redis_handler.store_token(f"token:{to_encode['sub']}", token, self.refresh_token_expiry.seconds)
            return token
        except Exception as e:
            logger.error(f"Failed to generate refresh token: {str(e)}")
            raise

    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify a JWT token.
        
        Args:
            token (str): JWT token to verify
            
        Returns:
            Optional[Dict]: Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token (str): Refresh token to use
            
        Returns:
            Optional[str]: New access token if successful, None otherwise
        """
        try:
            payload = self.verify_token(refresh_token)
            if not payload or payload.get("type") != "refresh":
                return None
                
            return self.generate_access_token({"user_id": payload["sub"]})
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return None

    def revoke_token(self, token: str) -> bool:
        """
        Revoke a token by adding it to the blacklist.
        
        Args:
            token (str): Token to revoke
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            payload = self.verify_token(token)
            if not payload:
                return False
                
            return self.redis_handler.delete_token(f"token:{payload['sub']}")
        except Exception as e:
            logger.error(f"Token revocation failed: {str(e)}")
            return False

    def get_token_payload(self, token: str) -> Optional[Dict]:
        """
        Get the payload of a token without verification.
        
        Args:
            token (str): Token to decode
            
        Returns:
            Optional[Dict]: Token payload if valid, None otherwise
        """
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except Exception as e:
            logger.error(f"Failed to get token payload: {str(e)}")
            return None 