import pytest
from unittest.mock import Mock, patch
import grpc
from app.grpc_server import AuthServiceServicer
from app.proto import auth_pb2
from app.models.auth_models import UserInfoResponse

@pytest.fixture
def mock_auth_service():
    """Mock AuthService."""
    with patch('app.services.auth_service.AuthService') as mock:
        yield mock

@pytest.fixture
def grpc_context():
    """Create a mock gRPC context."""
    context = Mock(spec=grpc.ServicerContext)
    return context

@pytest.fixture
def auth_servicer(mock_auth_service):
    """Create AuthServiceServicer instance with mocked dependencies."""
    return AuthServiceServicer()

@pytest.mark.asyncio
async def test_authenticate(auth_servicer, grpc_context, mock_auth_service):
    """Test Authenticate gRPC method."""
    # Mock authentication response
    mock_user = UserInfoResponse(
        id="test123",
        email="test@example.com",
        display_name="Test User",
        photo_url=None,
        is_active=True,
        is_verified=True
    )
    mock_auth_service.authenticate_user.return_value = (mock_user, "test_token")
    
    # Create request
    request = auth_pb2.AuthRequest(
        email="test@example.com",
        password="Test123!@#"
    )
    
    # Test authentication
    response = await auth_servicer.Authenticate(request, grpc_context)
    
    assert response.user.id == "test123"
    assert response.user.email == "test@example.com"
    assert response.user.display_name == "Test User"
    assert response.access_token == "test_token"
    assert grpc_context.set_code.call_count == 0

@pytest.mark.asyncio
async def test_verify_token(auth_servicer, grpc_context, mock_auth_service):
    """Test VerifyToken gRPC method."""
    # Mock token verification response
    mock_user = UserInfoResponse(
        id="test123",
        email="test@example.com",
        display_name="Test User",
        photo_url=None,
        is_active=True,
        is_verified=True
    )
    mock_auth_service.verify_token.return_value = mock_user
    
    # Create request
    request = auth_pb2.TokenRequest(token="valid_token")
    
    # Test token verification
    response = await auth_servicer.VerifyToken(request, grpc_context)
    
    assert response.id == "test123"
    assert response.email == "test@example.com"
    assert response.display_name == "Test User"
    assert grpc_context.set_code.call_count == 0

@pytest.mark.asyncio
async def test_verify_oauth_token(auth_servicer, grpc_context, mock_auth_service):
    """Test VerifyOAuthToken gRPC method."""
    # Mock OAuth token verification response
    mock_user = UserInfoResponse(
        id="test123",
        email="test@example.com",
        display_name="Test User",
        photo_url=None,
        is_active=True,
        is_verified=True
    )
    mock_auth_service.verify_oauth_token.return_value = (mock_user, "test_token")
    
    # Create request
    request = auth_pb2.OAuthRequest(
        provider="google",
        token="valid_oauth_token"
    )
    
    # Test OAuth token verification
    response = await auth_servicer.VerifyOAuthToken(request, grpc_context)
    
    assert response.user.id == "test123"
    assert response.user.email == "test@example.com"
    assert response.user.display_name == "Test User"
    assert response.access_token == "test_token"
    assert grpc_context.set_code.call_count == 0

def test_get_oauth_url(auth_servicer, grpc_context, mock_auth_service):
    """Test GetOAuthUrl gRPC method."""
    # Mock OAuth URL response
    mock_auth_service.get_oauth_url.return_value = "https://oauth.example.com/auth"
    
    # Create request
    request = auth_pb2.OAuthUrlRequest(provider="google")
    
    # Test getting OAuth URL
    response = auth_servicer.GetOAuthUrl(request, grpc_context)
    
    assert response.url == "https://oauth.example.com/auth"
    assert grpc_context.set_code.call_count == 0 