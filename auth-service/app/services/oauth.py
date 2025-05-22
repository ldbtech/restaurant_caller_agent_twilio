"""
OAuth2 service implementation for third-party authentication providers.

This module implements OAuth2 authentication flows for Google, Apple, and Microsoft.
It handles token verification, user creation/retrieval, and OAuth2 URL generation.

Key features:
- Secure token verification for each provider
- Automatic user creation/retrieval in Firebase
- State parameter generation for CSRF protection
- Comprehensive error handling and logging
- Type hints for better code maintainability

Example:
    oauth_service = OAuth2Service()
    user_info = await oauth_service.verify_google_token(token)
"""

import os
import json
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import httpx
from authlib.integrations.httpx_client import OAuth2Client
from google.oauth2 import id_token
from google.auth.transport import requests
from jose import jwt
import firebase_admin
from firebase_admin import auth
from app.core.config import settings

logger = logging.getLogger(__name__)

class OAuth2Service:
    """
    OAuth2 service for handling third-party authentication.
    
    This class manages OAuth2 authentication flows for multiple providers,
    including token verification, user management, and URL generation.
    
    Attributes:
        google_client_id (str): Google OAuth2 client ID
        google_client_secret (str): Google OAuth2 client secret
        apple_client_id (str): Apple OAuth2 client ID
        apple_team_id (str): Apple team ID
        apple_key_id (str): Apple key ID
        apple_private_key (str): Apple private key
        microsoft_client_id (str): Microsoft OAuth2 client ID
        microsoft_client_secret (str): Microsoft OAuth2 client secret
    """
    
    def __init__(self):
        """Initialize OAuth2 service with provider configurations."""
        # Load configuration from settings
        self.google_client_id = settings.GOOGLE_CLIENT_ID
        self.google_client_secret = settings.GOOGLE_CLIENT_SECRET
        self.apple_client_id = settings.APPLE_CLIENT_ID
        self.apple_team_id = settings.APPLE_TEAM_ID
        self.apple_key_id = settings.APPLE_KEY_ID
        self.apple_private_key = settings.APPLE_PRIVATE_KEY
        self.microsoft_client_id = settings.MICROSOFT_CLIENT_ID
        self.microsoft_client_secret = settings.MICROSOFT_CLIENT_SECRET
        
        # Initialize OAuth2 clients
        self._initialize_oauth_clients()
        
    def _initialize_oauth_clients(self) -> None:
        """Initialize OAuth2 clients for each provider."""
        self.google_client = OAuth2Client(
            client_id=self.google_client_id,
            client_secret=self.google_client_secret,
            token_endpoint='https://oauth2.googleapis.com/token'
        )
        
        self.microsoft_client = OAuth2Client(
            client_id=self.microsoft_client_id,
            client_secret=self.microsoft_client_secret,
            token_endpoint='https://login.microsoftonline.com/common/oauth2/v2.0/token'
        )

    async def verify_google_token(self, token: str) -> Dict:
        """
        Verify Google OAuth2 token and return user info.
        
        Args:
            token (str): Google OAuth2 token to verify
            
        Returns:
            Dict: User information including ID, email, and tokens
            
        Raises:
            ValueError: If token verification fails
            Exception: For other unexpected errors
        """
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                self.google_client_id
            )
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid issuer')
                
            # Get or create Firebase user
            user = await self._get_or_create_firebase_user(
                email=idinfo['email'],
                display_name=idinfo.get('name', ''),
                photo_url=idinfo.get('picture', ''),
                email_verified=idinfo.get('email_verified', False)
            )
            
            return self._create_auth_response(user, "google")
            
        except Exception as e:
            logger.error(f"Google token verification failed: {str(e)}")
            raise

    async def verify_apple_token(self, token: str) -> Dict:
        """
        Verify Apple OAuth2 token and return user info.
        
        Args:
            token (str): Apple OAuth2 token to verify
            
        Returns:
            Dict: User information including ID, email, and tokens
            
        Raises:
            ValueError: If token verification fails
            Exception: For other unexpected errors
        """
        try:
            # Verify the token
            header = jwt.get_unverified_header(token)
            key = await self._get_apple_public_key(header['kid'])
            
            decoded = jwt.decode(
                token,
                key,
                algorithms=['ES256'],
                audience=self.apple_client_id,
                issuer='https://appleid.apple.com'
            )
            
            # Get or create Firebase user
            user = await self._get_or_create_firebase_user(
                email=decoded['email'],
                display_name=decoded.get('name', {}).get('firstName', ''),
                email_verified=True
            )
            
            return self._create_auth_response(user, "apple")
            
        except Exception as e:
            logger.error(f"Apple token verification failed: {str(e)}")
            raise

    async def verify_microsoft_token(self, token: str) -> Dict:
        """
        Verify Microsoft OAuth2 token and return user info.
        
        Args:
            token (str): Microsoft OAuth2 token to verify
            
        Returns:
            Dict: User information including ID, email, and tokens
            
        Raises:
            ValueError: If token verification fails
            Exception: For other unexpected errors
        """
        try:
            # Verify the token
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://graph.microsoft.com/v1.0/me',
                    headers={'Authorization': f'Bearer {token}'}
                )
                response.raise_for_status()
                user_info = response.json()
            
            # Get or create Firebase user
            user = await self._get_or_create_firebase_user(
                email=user_info['mail'],
                display_name=user_info.get('displayName', ''),
                email_verified=True
            )
            
            return self._create_auth_response(user, "microsoft")
            
        except Exception as e:
            logger.error(f"Microsoft token verification failed: {str(e)}")
            raise

    async def _get_or_create_firebase_user(
        self,
        email: str,
        display_name: str = '',
        photo_url: str = '',
        email_verified: bool = False
    ) -> auth.UserRecord:
        """
        Get or create a Firebase user.
        
        Args:
            email (str): User's email address
            display_name (str, optional): User's display name
            photo_url (str, optional): User's photo URL
            email_verified (bool, optional): Whether email is verified
            
        Returns:
            auth.UserRecord: Firebase user record
        """
        try:
            return auth.get_user_by_email(email)
        except auth.UserNotFoundError:
            return auth.create_user(
                email=email,
                display_name=display_name,
                photo_url=photo_url,
                email_verified=email_verified
            )

    def _create_auth_response(self, user: auth.UserRecord, provider: str) -> Dict:
        """
        Create authentication response with user info and tokens.
        
        Args:
            user (auth.UserRecord): Firebase user record
            provider (str): OAuth provider name
            
        Returns:
            Dict: Authentication response with user info and tokens
        """
        access_token = auth.create_custom_token(user.uid)
        refresh_token = auth.create_custom_token(user.uid, {"refresh": True})
        
        return {
            "user_id": user.uid,
            "email": user.email,
            "display_name": user.display_name,
            "photo_url": user.photo_url,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "provider": provider
        }

    async def _get_apple_public_key(self, key_id: str) -> str:
        """
        Get Apple's public key for token verification.
        
        Args:
            key_id (str): Key ID from token header
            
        Returns:
            str: Public key for token verification
            
        Raises:
            ValueError: If public key not found
            Exception: For other unexpected errors
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get('https://appleid.apple.com/auth/keys')
                response.raise_for_status()
                keys = response.json()['keys']
                
                for key in keys:
                    if key['kid'] == key_id:
                        return key['n']
                        
            raise ValueError('Apple public key not found')
            
        except Exception as e:
            logger.error(f"Failed to get Apple public key: {str(e)}")
            raise

    def get_oauth_url(self, provider: str) -> str:
        """
        Get OAuth2 authorization URL for the specified provider.
        
        Args:
            provider (str): OAuth provider name ("google", "apple", or "microsoft")
            
        Returns:
            str: OAuth2 authorization URL
            
        Raises:
            ValueError: If provider is not supported
        """
        if provider == 'google':
            return self._get_google_oauth_url()
        elif provider == 'apple':
            return self._get_apple_oauth_url()
        elif provider == 'microsoft':
            return self._get_microsoft_oauth_url()
        else:
            raise ValueError(f'Unsupported OAuth provider: {provider}')

    def _get_google_oauth_url(self) -> str:
        """Get Google OAuth2 authorization URL."""
        return (
            'https://accounts.google.com/o/oauth2/v2/auth'
            '?client_id={}'
            '&redirect_uri={}'
            '&response_type=token'
            '&scope=email profile'
            '&state={}'
        ).format(
            self.google_client_id,
            settings.GOOGLE_REDIRECT_URI,
            self._generate_state()
        )

    def _get_apple_oauth_url(self) -> str:
        """Get Apple OAuth2 authorization URL."""
        return (
            'https://appleid.apple.com/auth/authorize'
            '?client_id={}'
            '&redirect_uri={}'
            '&response_type=code id_token'
            '&scope=email name'
            '&state={}'
            '&response_mode=fragment'
        ).format(
            self.apple_client_id,
            settings.APPLE_REDIRECT_URI,
            self._generate_state()
        )

    def _get_microsoft_oauth_url(self) -> str:
        """Get Microsoft OAuth2 authorization URL."""
        return (
            'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
            '?client_id={}'
            '&redirect_uri={}'
            '&response_type=token'
            '&scope=openid profile email'
            '&state={}'
        ).format(
            self.microsoft_client_id,
            settings.MICROSOFT_REDIRECT_URI,
            self._generate_state()
        )

    def _generate_state(self) -> str:
        """
        Generate a secure state parameter for OAuth2 flow.
        
        Returns:
            str: JWT-encoded state parameter
        """
        return jwt.encode(
            {
                'timestamp': int(datetime.utcnow().timestamp()),
                'random': os.urandom(16).hex()
            },
            settings.OAUTH_STATE_SECRET,
            algorithm='HS256'
        )
