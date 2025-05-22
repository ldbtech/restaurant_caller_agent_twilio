import pytest
from unittest.mock import Mock, patch
from app.services.auth_service import AuthService
from app.models.auth_models import UserInfoResponse
from firebase_admin import auth
from firebase_admin.auth import UserRecord

@pytest.fixture
def mock_firebase_auth():
    """Mock Firebase Auth."""
    with patch('firebase_admin.auth') as mock:
        yield mock

@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    with patch('redis.Redis') as mock:
        yield mock

@pytest.fixture
def auth_service(mock_firebase_auth, mock_redis):
    """Create AuthService instance with mocked dependencies."""
    return AuthService()

def test_register_user(auth_service, mock_firebase_auth):
    """Test user registration."""
    # Mock Firebase user creation
    mock_user = Mock(spec=UserRecord)
    mock_user.uid = "test123"
    mock_user.email = "test@example.com"
    mock_user.display_name = "Test User"
    mock_firebase_auth.create_user.return_value = mock_user
    
    # Test registration
    result = auth_service.register_user(
        email="test@example.com",
        password="Test123!@#",
        display_name="Test User",
        role="student"
    )
    
    assert result["user_id"] == "test123"
    assert result["email"] == "test@example.com"
    assert result["display_name"] == "Test User"
    assert result["role"] == "student"
    assert "access_token" in result
    assert "refresh_token" in result

@pytest.mark.asyncio
async def test_authenticate_user(auth_service, mock_firebase_auth):
    """Test user authentication."""
    # Mock Firebase user
    mock_user = Mock(spec=UserRecord)
    mock_user.uid = "test123"
    mock_user.email = "test@example.com"
    mock_user.display_name = "Test User"
    mock_user.photo_url = None
    mock_user.email_verified = True
    mock_firebase_auth.get_user_by_email.return_value = mock_user
    
    # Test authentication
    user, token = await auth_service.authenticate_user(
        email="test@example.com",
        password="Test123!@#"
    )
    
    assert isinstance(user, UserInfoResponse)
    assert user.id == "test123"
    assert user.email == "test@example.com"
    assert user.display_name == "Test User"
    assert user.is_verified is True
    assert token is not None

@pytest.mark.asyncio
async def test_verify_token(auth_service, mock_firebase_auth):
    """Test token verification."""
    # Mock Firebase token verification
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "test123",
        "email": "test@example.com"
    }
    
    # Mock Firebase user
    mock_user = Mock(spec=UserRecord)
    mock_user.uid = "test123"
    mock_user.email = "test@example.com"
    mock_user.display_name = "Test User"
    mock_user.photo_url = None
    mock_user.email_verified = True
    mock_firebase_auth.get_user.return_value = mock_user
    
    # Test token verification
    user = await auth_service.verify_token("valid_token")
    
    assert isinstance(user, UserInfoResponse)
    assert user.id == "test123"
    assert user.email == "test@example.com"
    assert user.display_name == "Test User"
    assert user.is_verified is True

def test_get_user_profile(auth_service, mock_firebase_auth):
    """Test getting user profile."""
    # Mock Firebase user
    mock_user = Mock(spec=UserRecord)
    mock_user.uid = "test123"
    mock_user.email = "test@example.com"
    mock_user.display_name = "Test User"
    mock_user.custom_claims = {"role": "student"}
    mock_user.user_metadata.creation_timestamp = 1234567890
    mock_user.user_metadata.last_sign_in_timestamp = 1234567890
    mock_firebase_auth.get_user.return_value = mock_user
    
    # Test getting user profile
    profile = auth_service.get_user_profile("test123")
    
    assert profile["user_id"] == "test123"
    assert profile["email"] == "test@example.com"
    assert profile["display_name"] == "Test User"
    assert profile["role"] == "student"
    assert "created_at" in profile
    assert "updated_at" in profile 