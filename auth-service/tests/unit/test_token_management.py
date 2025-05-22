"""
Unit tests for Token Management service.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from app.services.token_management import TokenManagement

def test_generate_access_token(token_management, test_user_data):
    """Test access token generation."""
    token = token_management.generate_access_token(test_user_data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0

def test_generate_refresh_token(token_management, test_user_data):
    """Test refresh token generation."""
    token = token_management.generate_refresh_token(test_user_data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0

def test_verify_token(token_management, test_token_data):
    """Test token verification."""
    # Test valid token
    with patch('jwt.decode') as mock_decode:
        mock_decode.return_value = test_token_data
        result = token_management.verify_token(test_token_data['token'])
        assert result == test_token_data
    
    # Test invalid token
    with patch('jwt.decode') as mock_decode:
        mock_decode.side_effect = Exception("Invalid token")
        result = token_management.verify_token("invalid_token")
        assert result is None

def test_refresh_access_token(token_management, test_user_data, test_token_data):
    """Test access token refresh."""
    # Test successful refresh
    with patch.object(token_management, 'verify_token') as mock_verify:
        mock_verify.return_value = test_token_data
        new_token = token_management.refresh_access_token(test_token_data['refresh_token'])
        assert new_token is not None
        assert isinstance(new_token, str)
    
    # Test invalid refresh token
    with patch.object(token_management, 'verify_token') as mock_verify:
        mock_verify.return_value = None
        new_token = token_management.refresh_access_token("invalid_token")
        assert new_token is None

def test_revoke_token(token_management, mock_redis):
    """Test token revocation."""
    token = "test_token"
    token_management.revoke_token(token)
    
    # Verify token was added to blacklist
    mock_redis.setex.assert_called_once()

def test_get_token_payload(token_management, test_token_data):
    """Test token payload extraction."""
    # Test valid token
    with patch('jwt.decode') as mock_decode:
        mock_decode.return_value = test_token_data
        payload = token_management.get_token_payload(test_token_data['token'])
        assert payload == test_token_data
    
    # Test invalid token
    with patch('jwt.decode') as mock_decode:
        mock_decode.side_effect = Exception("Invalid token")
        payload = token_management.get_token_payload("invalid_token")
        assert payload is None

def test_token_expiration(token_management, test_user_data):
    """Test token expiration handling."""
    # Generate token with short expiration
    token_management.access_token_expiry = timedelta(seconds=1)
    token = token_management.generate_access_token(test_user_data)
    
    # Wait for token to expire
    import time
    time.sleep(2)
    
    # Verify token is expired
    result = token_management.verify_token(token)
    assert result is None

def test_token_error_handling(token_management):
    """Test token error handling."""
    # Test invalid token format
    assert token_management.verify_token("invalid.token.format") is None
    
    # Test missing required claims
    with patch('jwt.decode') as mock_decode:
        mock_decode.return_value = {}  # Empty payload
        assert token_management.verify_token("token") is None
    
    # Test invalid signature
    with patch('jwt.decode') as mock_decode:
        mock_decode.side_effect = Exception("Invalid signature")
        assert token_management.verify_token("token") is None 