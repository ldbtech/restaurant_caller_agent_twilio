import pytest
from app.services.grpc_client import get_grpc_client
from app.protos_generated import db_service_pb2
from datetime import datetime, timezone
import grpc
from google.protobuf.timestamp_pb2 import Timestamp

@pytest.fixture
def grpc_client():
    return get_grpc_client()

def create_timestamp(dt: datetime) -> Timestamp:
    """Convert datetime to protobuf Timestamp"""
    timestamp = Timestamp()
    timestamp.FromDatetime(dt)
    return timestamp

def test_create_user_profile(grpc_client):
    # Create a test user profile
    now = datetime.now(timezone.utc)
    user_profile = db_service_pb2.UserProfileRequest(
        id="test_user_123",
        display_name="Test ALI DAHO",
        email="test@example.com",
        role="student",
        school="Test University",
        bio="Test bio",
        avatar_url="https://example.com/avatar.jpg",
        created_at=create_timestamp(now),
        updated_at=create_timestamp(now)
    )
    
    try:
        response = grpc_client.db_stub.CreateUserProfile(user_profile)
        assert response.profile.id == "test_user_123"
        assert response.profile.display_name == "Test User"
        assert response.profile.email == "test@example.com"
    except grpc.RpcError as e:
        pytest.fail(f"Failed to create user profile: {str(e)}")

def test_get_user_profile(grpc_client):
    # First create a user
    now = datetime.now(timezone.utc)
    user_profile = db_service_pb2.UserProfileRequest(
        id="test_user_456",
        display_name="Test User 2",
        email="test2@example.com",
        role="student",
        school="Test University",
        bio="Test bio 2",
        avatar_url="https://example.com/avatar2.jpg",
        created_at=create_timestamp(now),
        updated_at=create_timestamp(now)
    )
    
    try:
        # Create the user
        create_response = grpc_client.db_stub.CreateUserProfile(user_profile)
        assert create_response.profile.id == "test_user_456"
        
        # Get the user
        get_request = db_service_pb2.GetRequest(id="test_user_456")
        get_response = grpc_client.db_stub.GetUserProfile(get_request)
        
        assert get_response.profile.id == "test_user_456"
        assert get_response.profile.display_name == "Test User 2"
        assert get_response.profile.email == "test2@example.com"
    except grpc.RpcError as e:
        pytest.fail(f"Failed to get user profile: {str(e)}")

def test_update_user_profile(grpc_client):
    # First create a user
    now = datetime.now(timezone.utc)
    user_profile = db_service_pb2.UserProfileRequest(
        id="test_user_789",
        display_name="Test User 3",
        email="test3@example.com",
        role="student",
        school="Test University",
        bio="Test bio 3",
        avatar_url="https://example.com/avatar3.jpg",
        created_at=create_timestamp(now),
        updated_at=create_timestamp(now)
    )
    
    try:
        # Create the user
        create_response = grpc_client.db_stub.CreateUserProfile(user_profile)
        assert create_response.profile.id == "test_user_789"
        
        # Update the user
        updated_now = datetime.now(timezone.utc)
        updated_profile = db_service_pb2.UserProfileRequest(
            id="test_user_789",
            display_name="Updated Test User",
            email="updated@example.com",
            role="student",
            school="Updated University",
            bio="Updated bio",
            avatar_url="https://example.com/updated_avatar.jpg",
            created_at=create_timestamp(now),
            updated_at=create_timestamp(updated_now)
        )
        
        update_response = grpc_client.db_stub.UpdateUserProfile(updated_profile)
        assert update_response.profile.id == "test_user_789"
        assert update_response.profile.display_name == "Updated Test User"
        assert update_response.profile.email == "updated@example.com"
    except grpc.RpcError as e:
        pytest.fail(f"Failed to update user profile: {str(e)}")

def test_delete_user_profile(grpc_client):
    # First create a user
    now = datetime.now(timezone.utc)
    user_profile = db_service_pb2.UserProfileRequest(
        id="test_user_delete",
        display_name="Test User Delete",
        email="delete@example.com",
        role="student",
        school="Test University",
        bio="Test bio delete",
        avatar_url="https://example.com/avatar_delete.jpg",
        created_at=create_timestamp(now),
        updated_at=create_timestamp(now)
    )
    
    try:
        # Create the user
        create_response = grpc_client.db_stub.CreateUserProfile(user_profile)
        assert create_response.profile.id == "test_user_delete"
        
        # Delete the user
        delete_request = db_service_pb2.GetRequest(id="test_user_delete")
        delete_response = grpc_client.db_stub.DeleteUserProfile(delete_request)
        
        assert delete_response.success == True
        
        # Try to get the deleted user (should fail)
        get_request = db_service_pb2.GetRequest(id="test_user_delete")
        with pytest.raises(grpc.RpcError) as exc_info:
            grpc_client.db_stub.GetUserProfile(get_request)
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
    except grpc.RpcError as e:
        pytest.fail(f"Failed to delete user profile: {str(e)}") 