from datetime import datetime, timedelta
import redis
import logging
from functools import wraps
logging.basicConfig(
    filename='redis_handler.log', 
    level=logging.ERROR, 
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

# Check if redis client is initialized properly.
def check_redist_initialized(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.redis_client is None:
            logging.error("Redis client not initialized")
            raise Exception("Redis client not initialized")
        return func(self, *args, **kwargs)
    return wrapper

class RedisErrorCode(Enum):
    REDIS_TOKEN_NOT_FOUND = 1001

class RedisHandler:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        try:
            self.redis_client = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True) # Added decode_responses
            self.redis_client.ping()
            logging.info("Redis client initialized successfully")
            print("Redis client initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing Redis client: {e}")
            print(f"Error initializing Redis client: {e}")
            self.redis_client = None
            raise e

    @check_redist_initialized
    def store_refresh_token(self, user_id: str, refresh_token_id: str):
        try:
            self.redis_client.hset(f"refresh_tokens:{user_id}", mapping={
                "token_id": refresh_token_id,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=30)).isoformat() # 30 days refresh token
            })
            return True
        except Exception as e:
            logging.error(f"Error storing refresh token: {e}")
            raise e

    @check_redist_initialized
    def get_refresh_token(self, user_id: str): # refresh_token_id is not used here based on the current logic
        try:
            result = self.redis_client.hgetall(f"refresh_tokens:{user_id}") # Get all fields for the user
            if not result:
                logging.warning(f"No refresh token found for user {user_id}")
                return self._handle_missing_refresh_token(user_id)
            logging.info(f"Refresh token retrieved successfully for user {user_id}")
            return result
        except Exception as e:
            logging.error(f"Error getting refresh token: {e}")
            raise e

    @check_redist_initialized
    def delete_refresh_token(self, user_id: str): # refresh_token_id is not used here based on the current logic
        try:
            return self.redis_client.delete(f"refresh_tokens:{user_id}") > 0 # Returns True if at least one key was deleted
        except Exception as e:
            logging.error(f"Error deleting refresh token: {e}")
            raise e

    def _handle_missing_refresh_token(self, user_id: str):
        """
        Handle the case where no refresh token is found for the user.
        Logs this as a potential security event.
        """
        logging.warning(f"No refresh token found for user {user_id}. This could be a security issue or the user needs to re-authenticate.")
        return None
