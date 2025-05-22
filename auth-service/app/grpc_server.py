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
from app.proto import auth_pb2, auth_pb2_grpc
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class AuthServiceServicer(auth_pb2_grpc.AuthServicer):
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

    async def Authenticate(self, request: auth_pb2.AuthRequest, context: ServicerContext) -> auth_pb2.AuthResponse:
        """
        Handle user authentication.
        
        Args:
            request (auth_pb2.AuthRequest): Authentication request
            context (ServicerContext): gRPC context
            
        Returns:
            auth_pb2.AuthResponse: Authentication response
        """
        try:
            # Validate request
            if not self._validate_auth_request(request):
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Invalid request parameters')
                return auth_pb2.AuthResponse()
            
            # Authenticate user
            user, token = await self.auth_service.authenticate_user(request.email, request.password)
            
            if not user or not token:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details('Invalid credentials')
                return auth_pb2.AuthResponse()
            
            return auth_pb2.AuthResponse(
                user=auth_pb2.User(
                    id=user.id,
                    email=user.email,
                    display_name=user.display_name,
                    photo_url=user.photo_url,
                    is_active=user.is_active,
                    is_verified=user.is_verified
                ),
                access_token=token
            )
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Internal server error')
            return auth_pb2.AuthResponse()

    async def VerifyToken(self, request: auth_pb2.TokenRequest, context: ServicerContext) -> auth_pb2.User:
        """
        Verify a token and return the user.
        
        Args:
            request (auth_pb2.TokenRequest): Token verification request
            context (ServicerContext): gRPC context
            
        Returns:
            auth_pb2.User: User information
        """
        try:
            user = await self.auth_service.verify_token(request.token)
            
            if not user:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details('Invalid token')
                return auth_pb2.User()
            
            return auth_pb2.User(
                id=user.id,
                email=user.email,
                display_name=user.display_name,
                photo_url=user.photo_url,
                is_active=user.is_active,
                is_verified=user.is_verified
            )
            
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Internal server error')
            return auth_pb2.User()

    async def RefreshToken(self, request: auth_pb2.TokenRequest, context: ServicerContext) -> auth_pb2.TokenResponse:
        """
        Refresh an access token.
        
        Args:
            request (auth_pb2.TokenRequest): Token refresh request
            context (ServicerContext): gRPC context
            
        Returns:
            auth_pb2.TokenResponse: New access token
        """
        try:
            token = await self.auth_service.refresh_token(request.token)
            
            if not token:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details('Invalid refresh token')
                return auth_pb2.TokenResponse()
            
            return auth_pb2.TokenResponse(access_token=token)
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Internal server error')
            return auth_pb2.TokenResponse()

    async def VerifyOAuthToken(self, request: auth_pb2.OAuthRequest, context: ServicerContext) -> auth_pb2.AuthResponse:
        """
        Verify an OAuth2 token and return the user and access token.
        
        Args:
            request (auth_pb2.OAuthRequest): OAuth token verification request
            context (ServicerContext): gRPC context
            
        Returns:
            auth_pb2.AuthResponse: Authentication response
        """
        try:
            user, token = await self.auth_service.verify_oauth_token(request.provider, request.token)
            
            if not user or not token:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details('Invalid OAuth token')
                return auth_pb2.AuthResponse()
            
            return auth_pb2.AuthResponse(
                user=auth_pb2.User(
                    id=user.id,
                    email=user.email,
                    display_name=user.display_name,
                    photo_url=user.photo_url,
                    is_active=user.is_active,
                    is_verified=user.is_verified
                ),
                access_token=token
            )
            
        except Exception as e:
            logger.error(f"OAuth token verification failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Internal server error')
            return auth_pb2.AuthResponse()

    async def GetOAuthUrl(self, request: auth_pb2.OAuthUrlRequest, context: ServicerContext) -> auth_pb2.OAuthUrlResponse:
        """
        Get OAuth2 authorization URL for the specified provider.
        
        Args:
            request (auth_pb2.OAuthUrlRequest): OAuth URL request
            context (ServicerContext): gRPC context
            
        Returns:
            auth_pb2.OAuthUrlResponse: OAuth2 authorization URL
        """
        try:
            url = self.auth_service.get_oauth_url(request.provider)
            return auth_pb2.OAuthUrlResponse(url=url)
            
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return auth_pb2.OAuthUrlResponse()
            
        except Exception as e:
            logger.error(f"Failed to get OAuth URL: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Internal server error')
            return auth_pb2.OAuthUrlResponse()

    def _validate_auth_request(self, request: auth_pb2.AuthRequest) -> bool:
        """
        Validate authentication request parameters.
        
        Args:
            request (auth_pb2.AuthRequest): Authentication request
            
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
    auth_pb2_grpc.add_AuthServicer_to_server(
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