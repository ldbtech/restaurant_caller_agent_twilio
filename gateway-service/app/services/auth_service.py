from .base_service import BaseService
from app.services.grpc_client import get_grpc_client
from app.protos_generated import auth_service_pb2

class AuthService(BaseService):
    def __init__(self):
        super().__init__("auth")
        self.client = get_grpc_client()
        self.stub = self.client.get_stub("auth")
    
    def register_user(self, email: str, password: str, display_name: str, role: str = "student"):
        request = auth_service_pb2.RegisterRequest(
            email=email,
            password=password,
            display_name=display_name,
            role=role
        )
        response = self._make_grpc_call(self.stub.Register, request)
        # Convert gRPC response to dictionary
        return {
            "access_token": response.access_token,
            "refresh_token": response.refresh_token,
            "user_id": response.user_id,
            "email": response.email,
            "display_name": response.display_name,
            "role": response.role
        }
    
    def login_user(self, email: str, password: str):
        request = auth_service_pb2.LoginRequest(
            email=email,
            password=password
        )
        response = self._make_grpc_call(self.stub.Login, request)
        # Convert gRPC response to dictionary
        return {
            "access_token": response.access_token,
            "refresh_token": response.refresh_token,
            "user_id": response.user_id,
            "email": response.email,
            "display_name": response.display_name,
            "role": response.role
        }
    
    def validate_token(self, token: str):
        request = auth_service_pb2.ValidateTokenRequest(
            token=token
        )
        response = self._make_grpc_call(self.stub.ValidateToken, request)
        # Convert gRPC response to dictionary
        return {
            "is_valid": response.is_valid,
            "user_id": response.user_id,
            "claims": dict(response.claims),
            "error_message": response.error_message
        } 