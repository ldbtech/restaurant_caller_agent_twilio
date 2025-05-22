"""
Unit tests for Redis handler.
"""
import pytest
from unittest.mock import Mock, patch
from app.services.redis_handler import RedisHandler

def test_redis_handler_initialization(mock_redis):
    """Test Redis handler initialization."""
    handler = RedisHandler()
    assert handler.client is not None

def test_store_token(redis_handler, mock_redis):
    """Test storing a token."""
    key = "test:token"
    token = "test_token"
    expiry = 3600
    
    redis_handler.store_token(key, token, expiry)
    mock_redis.setex.assert_called_once_with(key, expiry, token)

def test_get_token(redis_handler, mock_redis):
    """Test getting a token."""
    key = "test:token"
    expected_token = "test_token"
    mock_redis.get.return_value = expected_token
    
    token = redis_handler.get_token(key)
    assert token == expected_token
    mock_redis.get.assert_called_once_with(key)

def test_delete_token(redis_handler, mock_redis):
    """Test deleting a token."""
    key = "test:token"
    
    redis_handler.delete_token(key)
    mock_redis.delete.assert_called_once_with(key)

def test_store_refresh_token(redis_handler, mock_redis):
    """Test storing a refresh token."""
    user_id = "test_user"
    refresh_token_id = "test_refresh_token"
    
    redis_handler.store_refresh_token(user_id, refresh_token_id)
    mock_redis.hset.assert_called_once()

def test_get_refresh_token(redis_handler, mock_redis):
    """Test getting a refresh token."""
    user_id = "test_user"
    expected_data = {
        "token_id": "test_token",
        "created_at": "2024-01-01T00:00:00",
        "expires_at": "2024-01-31T00:00:00"
    }
    mock_redis.hgetall.return_value = expected_data
    
    result = redis_handler.get_refresh_token(user_id)
    assert result == expected_data
    mock_redis.hgetall.assert_called_once_with(f"refresh_tokens:{user_id}")

def test_delete_refresh_token(redis_handler, mock_redis):
    """Test deleting a refresh token."""
    user_id = "test_user"
    mock_redis.delete.return_value = 1
    
    result = redis_handler.delete_refresh_token(user_id)
    assert result is True
    mock_redis.delete.assert_called_once_with(f"refresh_tokens:{user_id}")

def test_log_security_event(redis_handler, mock_redis):
    """Test logging a security event."""
    event_type = "test_event"
    event_data = {"test": "data"}
    
    redis_handler.log_security_event(event_type, event_data)
    mock_redis.lpush.assert_called_once()
    mock_redis.ltrim.assert_called_once_with("security_events", 0, 999)

def test_redis_error_handling(redis_handler, mock_redis):
    """Test Redis error handling."""
    mock_redis.get.side_effect = Exception("Redis error")
    
    # Test get_token error handling
    result = redis_handler.get_token("test:token")
    assert result is None
    
    # Test store_token error handling
    redis_handler.store_token("test:token", "token", 3600)
    # Should not raise exception
    
    # Test delete_token error handling
    redis_handler.delete_token("test:token")
    # Should not raise exception 