"""
Configuration settings for the authentication service.
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings."""
    
    # Service settings
    SERVICE_NAME: str = "auth-service"  # Name of the service, used for logging and identification
    SERVICE_VERSION: str = "1.0.0"      # Version of the service, used for logging and identification
    DEBUG: bool = False                 # Debug mode, used for logging and error handling
    
    # Redis settings
    REDIS_MODE: str = "local"           # Mode of Redis (local or production), used for Redis client initialization
    REDIS_HOST: str = "localhost"       # Host of Redis server, used for Redis client initialization
    REDIS_PORT: int = 6379              # Port of Redis server, used for Redis client initialization
    REDIS_DB: int = 0                   # Database number of Redis, used for Redis client initialization
    REDIS_PASSWORD: Optional[str] = None  # Password for Redis, used for Redis client initialization
    REDIS_SSL: bool = False             # Whether to use SSL for Redis, used for Redis client initialization
    
    # Redis Cloud settings (for production)
    REDIS_CLOUD_URL: Optional[str] = None  # URL for Redis Cloud, used for Redis client initialization
    REDIS_CLOUD_USERNAME: Optional[str] = None  # Username for Redis Cloud, used for Redis client initialization
    REDIS_CLOUD_PASSWORD: Optional[str] = None  # Password for Redis Cloud, used for Redis client initialization
    
    # Firebase settings
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")  # Path to Firebase credentials, used for Firebase client initialization
    
    # OAuth2 settings
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")  # Google OAuth client ID, used for Google OAuth
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")  # Google OAuth client secret, used for Google OAuth
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/google/callback")  # Google OAuth redirect URI, used for Google OAuth
    
    APPLE_CLIENT_ID: str = os.getenv("APPLE_CLIENT_ID", "")  # Apple OAuth client ID, used for Apple OAuth
    APPLE_TEAM_ID: str = os.getenv("APPLE_TEAM_ID", "")  # Apple OAuth team ID, used for Apple OAuth
    APPLE_KEY_ID: str = os.getenv("APPLE_KEY_ID", "")  # Apple OAuth key ID, used for Apple OAuth
    APPLE_PRIVATE_KEY: str = os.getenv("APPLE_PRIVATE_KEY", "")  # Apple OAuth private key, used for Apple OAuth
    APPLE_REDIRECT_URI: str = os.getenv("APPLE_REDIRECT_URI", "http://localhost:3000/auth/apple/callback")  # Apple OAuth redirect URI, used for Apple OAuth
    
    MICROSOFT_CLIENT_ID: str = os.getenv("MICROSOFT_CLIENT_ID", "")  # Microsoft OAuth client ID, used for Microsoft OAuth
    MICROSOFT_CLIENT_SECRET: str = os.getenv("MICROSOFT_CLIENT_SECRET", "")  # Microsoft OAuth client secret, used for Microsoft OAuth
    MICROSOFT_REDIRECT_URI: str = os.getenv("MICROSOFT_REDIRECT_URI", "http://localhost:3000/auth/microsoft/callback")  # Microsoft OAuth redirect URI, used for Microsoft OAuth
    
    # Security settings
    OAUTH_STATE_SECRET: str = os.getenv("OAUTH_STATE_SECRET", "your-secret-key")  # Secret for OAuth state, used for OAuth state validation
    SECRET_KEY: str = "your-secret-key"  # Secret key for JWT, used for JWT signing
    ALGORITHM: str = "HS256"  # Algorithm for JWT, used for JWT signing
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Expiration time for access tokens, used for JWT signing
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # Expiration time for refresh tokens, used for JWT signing
    RATE_LIMIT_WINDOW: int = 3600  # Window for rate limiting, used for rate limiting
    RATE_LIMIT_MAX_REQUESTS: int = 100  # Maximum requests per window, used for rate limiting
    PASSWORD_MIN_LENGTH: int = 8  # Minimum password length, used for password validation
    PASSWORD_REQUIRE_SPECIAL: bool = True  # Whether to require special characters in passwords, used for password validation
    PASSWORD_REQUIRE_NUMBERS: bool = True  # Whether to require numbers in passwords, used for password validation
    PASSWORD_REQUIRE_UPPERCASE: bool = True  # Whether to require uppercase letters in passwords, used for password validation
    TOKEN_EXPIRY: int = 900  # Expiration time for tokens, used for token validation
    
    SSL_KEY_PATH: str = "secrets/secret.key"  # Path to SSL key, used for SSL/TLS
    SSL_CERT_PATH: str = "secrets/secret.crt"  # Path to SSL certificate, used for SSL/TLS
    MAX_WORKERS: int = 10  # Maximum number of workers, used for gRPC server
    CONNECTION_IDLE_TIMEOUT: int = 10  # Idle timeout for connections, used for gRPC server
    KEEPALIVE_TIMEOUT: int = 10  # Timeout for keepalive, used for gRPC server
    KEEPALIVE_INTERVAL: int = 2  # Interval for keepalive, used for gRPC server
    CONNECTION_MAX_AGE: int = 10  # Maximum age for connections, used for gRPC server
    MAX_CONNECTIONS: int = 1000  # Maximum number of connections, used for gRPC server
    CONNECTION_GRACE_PERIOD: int = 10  # Grace period for connections, used for gRPC server
    MAX_CONCURRENT_STREAMS: int = 100  # Maximum number of concurrent streams, used for gRPC server
    MAX_LOGIN_ATTEMPTS: int = 5  # Maximum number of login attempts, used for login validation
    LOCKOUT_DURATION: int = 300  # Duration of lockout, used for login validation
    REDIS_SSL: bool = False  # Whether to use SSL for Redis, used for Redis client initialization
    ENCRYPTION_KEY: str = "I_x2RlYoaCpyHehyvBu0R801lmrtRcbuPdK2ugeaIyo="  # Key for encryption, used for encryption
    AUTH_SERVICE_PORT: int = 50051  # Port for the gRPC server, used for gRPC server

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

settings = Settings() 