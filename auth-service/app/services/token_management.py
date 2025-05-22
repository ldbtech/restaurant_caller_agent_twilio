import logging
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings
from app.services.redis_handler import RedisHandler

logger = logging.getLogger(__name__)

class TokenManagement:
    def __init__(self):
        self.redis_handler = RedisHandler()

    def generate_token(self, user_id: str, expiry: int = settings.TOKEN_EXPIRY) -> str:
        try:
            token = jwt.encode(
                {"user_id": user_id, "exp": datetime.utcnow() + timedelta(seconds=expiry)},
                settings.SECRET_KEY,
                algorithm="HS256"
            )
            self.redis_handler.store_token(f"token:{user_id}", token, expiry)
            return token
        except Exception as e:
            logger.error(f"Failed to generate token: {str(e)}")
            return None

    def verify_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            if not user_id:
                return None
            return user_id
        except Exception as e:
            logger.error(f"Failed to verify token: {str(e)}")
            return None

    def revoke_token(self, user_id: str) -> None:
        try:
            self.redis_handler.delete_token(f"token:{user_id}")
        except Exception as e:
            logger.error(f"Failed to revoke token: {str(e)}") 