"""
Unit tests for main Auth Service.
"""
import pytest
from unittest.mock import Mock, patch
from app.services.auth_service import AuthService

def test_login_success(auth_service, test_user_data, mock_firebase):
    """Test successful login."""
    # Mock Firebase authentication
    mock_firebase.verify_id_token.return_value = test_user_data
    
    # Test login
    result = auth_service.login(test_user_data['token'])
    
    assert result is not None
    assert 'access_token' in result
    assert 'refresh_token' in result
    assert 'user' in result

def test_login_invalid_token(auth_service, mock_firebase):
    """Test login with invalid token."""
    # Mock Firebase authentication failure
    mock_firebase.verify_id_token.side_effect = Exception("Invalid token")
    
    # Test login
    result = auth_service.login("invalid_token")
    assert result is None

def test_refresh_token_success(auth_service, test_token_data):
    """Test successful token refresh."""
    # Mock token verification
    with patch.object(auth_service.token_management, 'verify_token') as mock_verify:
        mock_verify.return_value = test_token_data
        result = auth_service.refresh_token(test_token_data['refresh_token'])
        
        assert result is not None
        assert 'access_token' in result
        assert 'refresh_token' in result

def test_refresh_token_invalid(auth_service):
    """Test token refresh with invalid token."""
    # Mock token verification failure
    with patch.object(auth_service.token_management, 'verify_token') as mock_verify:
        mock_verify.return_value = None
        result = auth_service.refresh_token("invalid_token")
        assert result is None

def test_logout_success(auth_service, mock_redis):
    """Test successful logout."""
    token = "test_token"
    result = auth_service.logout(token)
    
    assert result is True
    # Verify token was revoked
    mock_redis.setex.assert_called_once()

def test_logout_failure(auth_service, mock_redis):
    """Test logout failure."""
    # Mock Redis error
    mock_redis.setex.side_effect = Exception("Redis error")
    
    result = auth_service.logout("test_token")
    assert result is False

def test_verify_authentication_success(auth_service, test_token_data):
    """Test successful authentication verification."""
    # Mock token verification
    with patch.object(auth_service.token_management, 'verify_token') as mock_verify:
        mock_verify.return_value = test_token_data
        result = auth_service.verify_authentication(test_token_data['token'])
        
        assert result is not None
        assert result == test_token_data

def test_verify_authentication_failure(auth_service):
    """Test authentication verification failure."""
    # Mock token verification failure
    with patch.object(auth_service.token_management, 'verify_token') as mock_verify:
        mock_verify.return_value = None
        result = auth_service.verify_authentication("invalid_token")
        assert result is None

def test_rate_limit_handling(auth_service, mock_redis):
    """Test rate limit handling."""
    # Mock rate limit exceeded
    mock_redis.get.return_value = "6"  # Assuming limit is 5
    
    result = auth_service.login("test_token")
    assert result is None

def test_security_event_logging(auth_service, mock_redis):
    """Test security event logging."""
    # Test login attempt
    auth_service.login("test_token")
    
    # Verify security event was logged
    mock_redis.lpush.assert_called()
    logged_data = mock_redis.lpush.call_args[0][1]
    assert "login_attempt" in logged_data

def test_error_handling(auth_service, mock_firebase, mock_redis):
    """Test error handling in various scenarios."""
    # Test Firebase error
    mock_firebase.verify_id_token.side_effect = Exception("Firebase error")
    result = auth_service.login("test_token")
    assert result is None
    
    # Test Redis error
    mock_redis.setex.side_effect = Exception("Redis error")
    result = auth_service.logout("test_token")
    assert result is False
    
    # Test token management error
    with patch.object(auth_service.token_management, 'verify_token') as mock_verify:
        mock_verify.side_effect = Exception("Token error")
        result = auth_service.verify_authentication("test_token")
        assert result is None 