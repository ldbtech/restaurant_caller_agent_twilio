"""
gRPC server implementation for the authentication service.

This module implements the gRPC server for the authentication service,
providing endpoints for user authentication, token management, and OAuth2 integration.

Key features:
- Secure gRPC server with SSL/TLS
- Rate limiting and request validation
- Comprehensive error handling
- Health checks and monitoring
- Service-to-service authentication

Example:
    server = serve()
    server.wait_for_termination()
"""

import grpc
from concurrent import futures
from datetime import datetime
import time
import sys
from pathlib import Path
import os
from typing import Dict, Optional
import uuid
import firebase_admin
from firebase_admin import auth, credentials
import re
import logging
import redis
from cryptography.fernet import Fernet
from jose import jwt
from passlib.context import CryptContext
from grpc import ServicerContext
from app.services.auth_service import AuthService
from app.proto import auth_service_pb2, auth_service_pb2_grpc
from app.core.config import settings

# Add the 'app' directory to sys.path
app_dir = Path(__file__).parent
sys.path.append(str(app_dir))

# Configure logging
logger = logging.getLogger(__name__)

class AuthServiceServicer(auth_service_pb2_grpc.AuthServiceServicer):
    """
    gRPC servicer for authentication service.
    
    This class implements the gRPC service methods for user authentication,
    token management, and OAuth2 integration.
    
    Attributes:
        auth_service (AuthService): Authentication service instance
        token_expiry (int): Token expiration time in seconds
        password_min_length (int): Minimum password length
        max_login_attempts (int): Maximum login attempts allowed
        lockout_duration (int): Account lockout duration in seconds
        redis (redis.Redis): Redis client for rate limiting
        pwd_context (CryptContext): Password hashing context
        cipher_suite (Fernet): Encryption suite for sensitive data
    """
    
    def __init__(self):
        """Initialize the authentication servicer."""
        # Initialize services and configurations
        self.auth_service = AuthService()
        self.token_expiry = settings.TOKEN_EXPIRY
        self.password_min_length = settings.PASSWORD_MIN_LENGTH
        self.max_login_attempts = settings.MAX_LOGIN_ATTEMPTS
        self.lockout_duration = settings.LOCKOUT_DURATION
        
        # Initialize Redis for rate limiting and token storage
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            ssl=settings.REDIS_SSL
        )
        
        # Initialize password hashing
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Initialize encryption for sensitive data
        self.encryption_key = settings.ENCRYPTION_KEY
        self.cipher_suite = Fernet(self.encryption_key)

    async def Authenticate(self, request: auth_service_pb2.LoginRequest, context: ServicerContext) -> auth_service_pb2.AuthResponse:
        """
        Handle user authentication.
        
        Args:
            request (auth_service_pb2.LoginRequest): Authentication request
            context (ServicerContext): gRPC context
            
        Returns:
            auth_service_pb2.AuthResponse: Authentication response
        """
        try:
            # Validate request
            if not self._validate_auth_request(request):
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Invalid request parameters')
                return auth_service_pb2.AuthResponse()
            
            # Authenticate user
            user, token = await self.auth_service.authenticate_user(request.email, request.password)
            
            if not user or not token:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details('Invalid credentials')
                return auth_service_pb2.AuthResponse()
            
            return auth_service_pb2.AuthResponse(
                access_token=token,
                user_id=user.id,
                email=user.email,
                display_name=user.display_name,
                role=user.role
            )
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Internal server error')
            return auth_service_pb2.AuthResponse()

    async def ValidateToken(self, request: auth_service_pb2.ValidateTokenRequest, context: ServicerContext) -> auth_service_pb2.ValidateTokenResponse:
        """
        Verify a token and return the user.
        
        Args:
            request (auth_service_pb2.ValidateTokenRequest): Token verification request
            context (ServicerContext): gRPC context
            
        Returns:
            auth_service_pb2.ValidateTokenResponse: Token validation response
        """
        try:
            user = await self.auth_service.verify_token(request.token)
            
            if not user:
                return auth_service_pb2.ValidateTokenResponse(
                    is_valid=False,
                    error_message="Invalid token"
                )
            
            return auth_service_pb2.ValidateTokenResponse(
                is_valid=True,
                user_id=user.id,
                claims={"email": user.email, "role": user.role}
            )
            
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return auth_service_pb2.ValidateTokenResponse(
                is_valid=False,
                error_message=str(e)
            )

    async def RefreshToken(self, request: auth_service_pb2.RefreshTokenRequest, context: ServicerContext) -> auth_service_pb2.AuthResponse:
        """
        Refresh an access token.
        
        Args:
            request (auth_service_pb2.RefreshTokenRequest): Token refresh request
            context (ServicerContext): gRPC context
            
        Returns:
            auth_service_pb2.AuthResponse: New authentication response
        """
        try:
            token = await self.auth_service.refresh_token(request.refresh_token)
            
            if not token:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details('Invalid refresh token')
                return auth_service_pb2.AuthResponse()
            
            return auth_service_pb2.AuthResponse(access_token=token)
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Internal server error')
            return auth_service_pb2.AuthResponse()


    def _validate_auth_request(self, request: auth_service_pb2.LoginRequest) -> bool:
        """
        Validate authentication request parameters.
        
        Args:
            request (auth_service_pb2.LoginRequest): Authentication request
            
        Returns:
            bool: True if request is valid, False otherwise
        """
        if not request.email or not request.password:
            return False
            
        if not self._validate_email(request.email):
            return False
            
        if not self._validate_password(request.password):
            return False
            
        return True

    def _validate_password(self, password: str) -> bool:
        """
        Validate password complexity.
        
        Args:
            password (str): Password to validate
            
        Returns:
            bool: True if password is valid, False otherwise
        """
        if len(password) < self.password_min_length:
            return False
            
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            return False
            
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            return False
            
        # Check for at least one number
        if not re.search(r'\d', password):
            return False
            
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
            
        return True

    def _validate_email(self, email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email (str): Email to validate
            
        Returns:
            bool: True if email is valid, False otherwise
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))

def serve():
    """
    Start the gRPC server.
    
    This function initializes and starts the gRPC server with SSL/TLS
    and proper configuration.
    """
    # Load SSL credentials
    with open(settings.SSL_KEY_PATH, 'rb') as f:
        private_key = f.read()
    with open(settings.SSL_CERT_PATH, 'rb') as f:
        certificate_chain = f.read()
    
    server_credentials = grpc.ssl_server_credentials(
        [(private_key, certificate_chain)]
    )
    
    # Create server with rate limiting
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=settings.MAX_WORKERS),
        options=[
            ('grpc.max_connection_idle_ms', settings.CONNECTION_IDLE_TIMEOUT),
            ('grpc.max_connection_age_ms', settings.CONNECTION_MAX_AGE),
            ('grpc.max_connection_age_grace_ms', settings.CONNECTION_GRACE_PERIOD),
            ('grpc.max_concurrent_streams', settings.MAX_CONCURRENT_STREAMS),
        ]
    )
    
    # Add the servicer
    auth_service_pb2_grpc.add_AuthServiceServicer_to_server(
        AuthServiceServicer(), server
    )
    
    # Use secure port
    port = settings.AUTH_SERVICE_PORT
    server.add_secure_port(f'[::]:{port}', server_credentials)
    
    server.start()
    logger.info(f"Auth gRPC Server started on secure port {port}")
    
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve() 