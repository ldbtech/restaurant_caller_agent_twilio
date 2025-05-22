import pytest
from unittest.mock import Mock, patch
from app.services.oauth import OAuth2Service
from firebase_admin import auth
from firebase_admin.auth import UserRecord

@pytest.fixture
def mock_firebase_auth():
    """Mock Firebase Auth."""
    with patch('firebase_admin.auth') as mock:
        yield mock

@pytest.fixture
def mock_httpx():
    """Mock httpx client."""
    with patch('httpx.AsyncClient') as mock:
        yield mock

@pytest.fixture
def oauth_service(mock_firebase_auth, mock_httpx):
    """Create OAuth2Service instance with mocked dependencies."""
    return OAuth2Service()

@pytest.mark.asyncio
async def test_verify_google_token(oauth_service, mock_firebase_auth):
    """Test Google OAuth token verification."""
    # Mock Google token verification
    mock_google_token = {
        "sub": "test123",
        "email": "test@example.com",
        "name": "Test User",
        "picture": "https://example.com/photo.jpg"
    }
    
    # Mock Firebase user
    mock_user = Mock(spec=UserRecord)
    mock_user.uid = "test123"
    mock_user.email = "test@example.com"
    mock_user.display_name = "Test User"
    mock_user.photo_url = "https://example.com/photo.jpg"
    mock_user.email_verified = True
    
    with patch('google.oauth2.id_token.verify_oauth2_token') as mock_verify:
        mock_verify.return_value = mock_google_token
        mock_firebase_auth.get_user_by_email.return_value = mock_user
        
        # Test Google token verification
        user_info = await oauth_service.verify_google_token("valid_google_token")
        
        assert user_info["user_id"] == "test123"
        assert user_info["email"] == "test@example.com"
        assert user_info["display_name"] == "Test User"
        assert user_info["photo_url"] == "https://example.com/photo.jpg"
        assert "access_token" in user_info
        assert "refresh_token" in user_info

@pytest.mark.asyncio
async def test_verify_apple_token(oauth_service, mock_firebase_auth):
    """Test Apple OAuth token verification."""
    # Mock Apple token verification
    mock_apple_token = {
        "sub": "test123",
        "email": "test@example.com",
        "name": "Test User"
    }
    
    # Mock Firebase user
    mock_user = Mock(spec=UserRecord)
    mock_user.uid = "test123"
    mock_user.email = "test@example.com"
    mock_user.display_name = "Test User"
    mock_user.photo_url = None
    mock_user.email_verified = True
    
    with patch('jose.jwt.decode') as mock_decode:
        mock_decode.return_value = mock_apple_token
        mock_firebase_auth.get_user_by_email.return_value = mock_user
        
        # Test Apple token verification
        user_info = await oauth_service.verify_apple_token("valid_apple_token")
        
        assert user_info["user_id"] == "test123"
        assert user_info["email"] == "test@example.com"
        assert user_info["display_name"] == "Test User"
        assert "access_token" in user_info
        assert "refresh_token" in user_info

def test_get_oauth_url(oauth_service):
    """Test getting OAuth URLs."""
    # Test Google OAuth URL
    google_url = oauth_service.get_oauth_url("google")
    assert "google" in google_url.lower()
    assert "client_id" in google_url
    
    # Test Apple OAuth URL
    apple_url = oauth_service.get_oauth_url("apple")
    assert "apple" in apple_url.lower()
    assert "client_id" in apple_url
    
    # Test Microsoft OAuth URL
    microsoft_url = oauth_service.get_oauth_url("microsoft")
    assert "microsoft" in microsoft_url.lower()
    assert "client_id" in microsoft_url
    
    # Test invalid provider
    with pytest.raises(ValueError):
        oauth_service.get_oauth_url("invalid_provider") 