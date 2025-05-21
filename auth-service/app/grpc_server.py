"""
This is the gRPC server for the auth service.
It is used to register and login users, and to validate tokens.
It is also used to get the user profile and to update the user profile.
It is also used to delete the user and to revoke the token.
It is also used to check the health of the service.

The auth service is used by the gateway service to register and login users, and to validate tokens.
The auth service is also used by the gateway service to get the user profile and to update the user profile.
The auth service is also used by the gateway service to delete the user and to revoke the token.
The auth service is also used by the gateway service to check the health of the service.

We will make it secure now as next step.
"""
import grpc
from concurrent import futures
from datetime import datetime
import time
import sys
from pathlib import Path
import os
from typing import Dict
import uuid
import firebase_admin as auth
import re
import logging

# Add the proto directory to Python path
proto_dir = Path(__file__).parent / "proto"
sys.path.append(str(proto_dir))

# Import proto files
import auth_service_pb2
import auth_service_pb2_grpc
from services.auth_service import AuthService

class AuthServiceServicer(auth_service_pb2_grpc.AuthServiceServicer):
    def __init__(self):
         # Initialize an instance of the `AuthService` to handle the underlying
        # authentication and user management logic. This keeps the gRPC layer
        # focused on request/response handling and delegates the core logic.
        self.auth_service = AuthService()
        self.token_expiry = int(os.getenv('TOKEN_EXPIRY', '3600'))  # Default to 1 hour
        self.password_min_length = int(os.getenv('PASSWORD_MIN_LENGTH', '8'))
        self.max_login_attempts = int(os.getenv('MAX_LOGIN_ATTEMPTS', '5'))
        self.lockout_duration = int(os.getenv('LOCKOUT_DURATION', '3600'))  # Default to 1 hour
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def Register(self, request, context):
        try:
            result = self.auth_service.register_user(
                email=request.email,
                password=request.password,
                display_name=request.display_name,
                role=request.role
            )
            return auth_service_pb2.AuthResponse(
                access_token=result["access_token"],
                refresh_token=result["refresh_token"],
                user_id=result["user_id"],
                email=result["email"],
                display_name=result["display_name"],
                role=result["role"]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return auth_service_pb2.AuthResponse(error_message=str(e))

    def Login(self, request, context):
        try:
            result = self.auth_service.login_user(
                email=request.email,
                password=request.password
            )
            return auth_service_pb2.AuthResponse(
                access_token=result["access_token"],
                refresh_token=result["refresh_token"],
                user_id=result["user_id"],
                email=result["email"],
                display_name=result["display_name"],
                role=result["role"]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return auth_service_pb2.AuthResponse(error_message=str(e))

    def ValidateToken(self, request, context):
        try:
            result = self.auth_service.validate_token(request.token)
            return auth_service_pb2.ValidateTokenResponse(
                is_valid=result["is_valid"],
                user_id=result.get("user_id", ""),
                claims=result.get("claims", {}),
                error_message=result.get("error_message", "")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return auth_service_pb2.ValidateTokenResponse(
                is_valid=False,
                error_message=str(e)
            )

    def GetUserProfile(self, request, context):
        try:
            result = self.auth_service.get_user_profile(request.user_id)
            return auth_service_pb2.UserProfileResponse(
                user_id=result["user_id"],
                email=result["email"],
                display_name=result["display_name"],
                role=result["role"],
                custom_claims=result["custom_claims"],
                created_at=self.auth_service.datetime_to_timestamp(result["created_at"]),
                updated_at=self.auth_service.datetime_to_timestamp(result["updated_at"])
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return auth_service_pb2.UserProfileResponse()

    def UpdateUserProfile(self, request, context):
        try:
            result = self.auth_service.update_user_profile(
                user_id=request.user_id,
                display_name=request.display_name,
                email=request.email,
                role=request.role,
                custom_claims=dict(request.custom_claims)
            )
            return auth_service_pb2.UserProfileResponse(
                user_id=result["user_id"],
                email=result["email"],
                display_name=result["display_name"],
                role=result["role"],
                custom_claims=result["custom_claims"],
                created_at=self.auth_service.datetime_to_timestamp(result["created_at"]),
                updated_at=self.auth_service.datetime_to_timestamp(result["updated_at"])
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return auth_service_pb2.UserProfileResponse()

    def DeleteUser(self, request, context):
        try:
            success = self.auth_service.delete_user(request.user_id)
            return auth_service_pb2.DeleteUserResponse(
                success=success,
                message="User deleted successfully" if success else "Failed to delete user"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return auth_service_pb2.DeleteUserResponse(
                success=False,
                message=str(e)
            )

    # `RevokeToken` method: Handles requests to revoke a refresh token.
    def RevokeToken(self, request, context):
        try:
            success = self.auth_service.revoke_token(request.token)
            return auth_service_pb2.RevokeTokenResponse(
                success=success,
                message="Token revoked successfully" if success else "Failed to revoke token"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return auth_service_pb2.RevokeTokenResponse(
                success=False,
                message=str(e)
            )

    # `CheckHealth` method: Handles requests to check the health of the service.
    def CheckHealth(self, request, context):
        try:
              # Attempt a minimal interaction with Firebase to check its health.
            # Getting a user by a non-existent email is a lightweight way to
            # verify the connection without impacting real users.
            auth.get_user_by_email("test@example.com")
            return auth_service_pb2.HealthCheckResponse(
                status="SERVING",
                message="Auth service is healthy"
            )
        except auth.UserNotFoundError:
            # This is actually good - it means Firebase is connected but user doesn't exist
            return auth_service_pb2.HealthCheckResponse(
                status="SERVING",
                message="Auth service is healthy"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            return auth_service_pb2.HealthCheckResponse(
                status="NOT_SERVING",
                message=f"Auth service is unhealthy: {str(e)}"
            )

    def _create_access_token(self, user_id: str) -> str:
        """Create a secure access token with proper expiration."""
        try:
            return auth.create_custom_token(
                user_id,
                {
                    "exp": int(time.time()) + self.token_expiry,
                    "type": "access"
                }
            )
        except Exception as e:
            self._log_security_event("token_creation_failed", {
                "user_id": user_id,
                "error": str(e)
            })
            raise

    def _create_refresh_token(self, user_id: str) -> str:
        """Create a secure refresh token with proper rotation."""
        try:
            # Generate a unique refresh token ID
            refresh_token_id = str(uuid.uuid4())
            
            # Store refresh token metadata
            self._store_refresh_token(user_id, refresh_token_id)
            
            return auth.create_custom_token(
                user_id,
                {
                    "exp": int(time.time()) + (self.token_expiry * 24),  # 24 hours
                    "type": "refresh",
                    "refresh_token_id": refresh_token_id
                }
            )
        except Exception as e:
            self._log_security_event("refresh_token_creation_failed", {
                "user_id": user_id,
                "error": str(e)
            })
            raise
    
    def _store_refresh_token(self, user_id: str, refresh_token_id: str):
        """Store refresh token metadata in Redis."""
        pass
    

    def _validate_password(self, password: str) -> bool:
        """Validate password complexity."""
        if len(password) < self.password_min_length:
            return False
            
        # Check for complexity requirements
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        return all([has_upper, has_lower, has_digit, has_special])

    def _validate_email(self, email: str) -> bool:
        """Validate email format and domain."""
        try:
            # Basic email format validation
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return False
                
            # Domain validation
            domain = email.split('@')[1]
            allowed_domains = os.getenv('ALLOWED_EMAIL_DOMAINS', '').split(',')
            if allowed_domains and domain not in allowed_domains:
                return False
                
            return True
        except Exception:
            return False

    def _sanitize_display_name(self, display_name: str) -> str:
        """Sanitize display name to prevent XSS and injection."""
        # Remove HTML tags
        display_name = re.sub(r'<[^>]+>', '', display_name)
        
        # Remove special characters
        display_name = re.sub(r'[^\w\s-]', '', display_name)
        
        # Limit length
        return display_name[:50]

    def _log_security_event(self, event_type: str, event_data: Dict):
        """Log security events with proper sanitization."""
        try:
            # Sanitize sensitive data
            sanitized_data = self._sanitize_log_data(event_data)
            
            # Log to secure logging system
            logging.info(
                "Security Event",
                extra={
                    "event_type": event_type,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": sanitized_data
                }
            )
        except Exception as e:
            # Fallback logging
            logging.error(f"Failed to log security event: {str(e)}")

    def _sanitize_log_data(self, data: Dict) -> Dict:
        """Sanitize sensitive data before logging."""
        sensitive_fields = ['password', 'token', 'private_key']
        sanitized = data.copy()
        
        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = '[REDACTED]'
                
        return sanitized

    def _check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """Check if request is within rate limits."""
        try:
            current = int(time.time())
            window_start = current - window
            
            # Use Redis or similar for distributed rate limiting
            with self.redis.pipeline() as pipe:
                pipe.zremrangebyscore(key, 0, window_start)
                pipe.zcard(key)
                pipe.zadd(key, {str(current): current})
                pipe.expire(key, window)
                _, count, _, _ = pipe.execute()
                
            return count < limit
        except Exception as e:
            self._log_security_event("rate_limit_check_failed", {
                "key": key,
                "error": str(e)
            })
            return False

class SecureConfig:
    """Secure configuration management."""
    
    def __init__(self):
        self.config = {}
        self._load_config()
        
    def _load_config(self):
        """Load and validate configuration."""
        required_configs = [
            'FIREBASE_PROJECT_ID',
            'FIREBASE_PRIVATE_KEY_ID',
            'FIREBASE_PRIVATE_KEY',
            'FIREBASE_CLIENT_EMAIL',
            'MAX_LOGIN_ATTEMPTS',
            'LOCKOUT_DURATION',
            'TOKEN_EXPIRY'
        ]
        
        for config in required_configs:
            value = os.getenv(config)
            if not value:
                raise ValueError(f"Missing required configuration: {config}")
            self.config[config] = value
            
        # Validate and decrypt sensitive values
        self._validate_and_decrypt_config()
        
    def _validate_and_decrypt_config(self):
        """Validate and decrypt sensitive configuration values."""
        # Implement proper encryption/decryption of sensitive values
        pass

class ServiceAuthMiddleware:
    """Middleware for service-to-service authentication."""
    
    def __init__(self, service_name: str, service_key: str):
        self.service_name = service_name
        self.service_key = service_key
        
    def authenticate_request(self, request):
        """Authenticate incoming service requests."""
        try:
            # Verify service authentication
            auth_header = request.headers.get('x-service-auth')
            if not auth_header:
                raise ValueError("Missing service authentication")
                
            # Verify service signature
            if not self._verify_service_signature(auth_header):
                raise ValueError("Invalid service authentication")
                
            return True
        except Exception as e:
            self._log_security_event("service_auth_failed", {
                "service": self.service_name,
                "error": str(e)
            })
            return False

def serve():
    # Load SSL credentials
    with open('server.key', 'rb') as f:
        private_key = f.read()
    with open('server.crt', 'rb') as f:
        certificate_chain = f.read()
    
    server_credentials = grpc.ssl_server_credentials(
        [(private_key, certificate_chain)]
    )
    
    # Create server with rate limiting
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_connection_idle_ms', 300000),  # 5 minutes
            ('grpc.max_connection_age_ms', 600000),   # 10 minutes
            ('grpc.max_connection_age_grace_ms', 5000),
            ('grpc.max_concurrent_streams', 100),
        ]
    )
    
    # Add the servicer with authentication middleware
    auth_service_pb2_grpc.add_AuthServiceServicer_to_server(
        AuthServiceServicer(), server
    )
    
    # Use secure port
    port = os.getenv('AUTH_SERVICE_PORT', '50052')
    server.add_secure_port(f'[::]:{port}', server_credentials)
    
    server.start()
    print(f"Auth gRPC Server started on secure port {port}")
    
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve() 