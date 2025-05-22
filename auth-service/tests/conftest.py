"""
Shared test fixtures for authentication service tests.
"""
import pytest
from unittest.mock import Mock, patch
import firebase_admin
from app.core.config import settings
from app.services.redis_handler import RedisHandler
from app.services.security import Security
from app.services.token_management import TokenManagement
from app.services.auth_service import AuthService

@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    with patch('redis.Redis') as mock:
        yield mock

@pytest.fixture
def mock_firebase():
    """Mock Firebase Admin SDK."""
    with patch('firebase_admin.auth') as mock:
        yield mock

@pytest.fixture
def redis_handler(mock_redis):
    """Redis handler instance with mocked Redis client."""
    return RedisHandler()

@pytest.fixture
def security_service(redis_handler):
    """Security service instance."""
    return Security()

@pytest.fixture
def token_management(redis_handler):
    """Token management service instance."""
    return TokenManagement()

@pytest.fixture
def auth_service(redis_handler, mock_firebase):
    """Auth service instance with mocked dependencies."""
    return AuthService()

@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "Test123!@#",
        "display_name": "Test User",
        "role": "student"
    }

@pytest.fixture
def test_token_data():
    """Sample token data for testing."""
    return {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "user_id": "test_user_id"
    } 