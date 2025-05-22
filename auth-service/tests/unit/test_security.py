"""
Unit tests for Security service.
"""
import pytest
from unittest.mock import Mock, patch
from app.services.security import Security

def test_check_rate_limit(security_service, mock_redis):
    """Test rate limiting functionality."""
    key = "test:rate"
    limit = 5
    window = 3600
    
    # Test first request (should pass)
    mock_redis.get.return_value = None
    assert security_service.check_rate_limit(key, limit, window) is True
    
    # Test within limit
    mock_redis.get.return_value = "3"
    assert security_service.check_rate_limit(key, limit, window) is True
    
    # Test at limit
    mock_redis.get.return_value = "5"
    assert security_service.check_rate_limit(key, limit, window) is False

def test_validate_password(security_service):
    """Test password validation."""
    # Test valid password
    assert security_service.validate_password("ValidPass123!") is True
    
    # Test too short password
    assert security_service.validate_password("short") is False

def test_validate_email(security_service):
    """Test email validation."""
    # Test valid email
    assert security_service.validate_email("test@example.com") is True
    
    # Test invalid email
    assert security_service.validate_email("invalid-email") is False
    assert security_service.validate_email("test@") is False
    assert security_service.validate_email("@example.com") is False

def test_check_ip_blacklist(security_service, mock_redis):
    """Test IP blacklist checking."""
    ip = "192.168.1.1"
    
    # Test not blacklisted
    mock_redis.sismember.return_value = False
    assert security_service.check_ip_blacklist(ip) is True
    
    # Test blacklisted
    mock_redis.sismember.return_value = True
    assert security_service.check_ip_blacklist(ip) is False

def test_add_to_ip_blacklist(security_service, mock_redis):
    """Test adding IP to blacklist."""
    ip = "192.168.1.1"
    duration = 3600
    
    security_service.add_to_ip_blacklist(ip, duration)
    mock_redis.setex.assert_called_once_with(f"blacklisted_ips:{ip}", duration, "1")

def test_check_token_blacklist(security_service, mock_redis):
    """Test token blacklist checking."""
    token = "test_token"
    
    # Test not blacklisted
    mock_redis.sismember.return_value = False
    assert security_service.check_token_blacklist(token) is True
    
    # Test blacklisted
    mock_redis.sismember.return_value = True
    assert security_service.check_token_blacklist(token) is False

def test_add_to_token_blacklist(security_service, mock_redis):
    """Test adding token to blacklist."""
    token = "test_token"
    duration = 86400
    
    security_service.add_to_token_blacklist(token, duration)
    mock_redis.setex.assert_called_once_with(f"blacklisted_tokens:{token}", duration, "1")

def test_log_security_event(security_service, mock_redis):
    """Test security event logging."""
    event_type = "test_event"
    event_data = {
        "user_id": "123",
        "password": "secret",  # Should be redacted
        "token": "sensitive"   # Should be redacted
    }
    
    security_service.log_security_event(event_type, event_data)
    
    # Verify sensitive data was redacted
    mock_redis.lpush.assert_called_once()
    logged_data = mock_redis.lpush.call_args[0][1]
    assert "password" not in logged_data
    assert "token" not in logged_data

def test_security_error_handling(security_service, mock_redis):
    """Test security service error handling."""
    mock_redis.get.side_effect = Exception("Redis error")
    
    # Test rate limit error handling
    assert security_service.check_rate_limit("test", 5, 3600) is False
    
    # Test IP blacklist error handling
    assert security_service.check_ip_blacklist("192.168.1.1") is True
    
    # Test token blacklist error handling
    assert security_service.check_token_blacklist("test_token") is True 