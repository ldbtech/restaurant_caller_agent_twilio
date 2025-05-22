"""
Configuration settings for the authentication service.
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    # Service settings
    SERVICE_NAME: str = "auth-service"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Firebase settings
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
    
    # OAuth2 settings
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/google/callback")
    
    APPLE_CLIENT_ID: str = os.getenv("APPLE_CLIENT_ID", "")
    APPLE_TEAM_ID: str = os.getenv("APPLE_TEAM_ID", "")
    APPLE_KEY_ID: str = os.getenv("APPLE_KEY_ID", "")
    APPLE_PRIVATE_KEY: str = os.getenv("APPLE_PRIVATE_KEY", "")
    APPLE_REDIRECT_URI: str = os.getenv("APPLE_REDIRECT_URI", "http://localhost:3000/auth/apple/callback")
    
    MICROSOFT_CLIENT_ID: str = os.getenv("MICROSOFT_CLIENT_ID", "")
    MICROSOFT_CLIENT_SECRET: str = os.getenv("MICROSOFT_CLIENT_SECRET", "")
    MICROSOFT_REDIRECT_URI: str = os.getenv("MICROSOFT_REDIRECT_URI", "http://localhost:3000/auth/microsoft/callback")
    
    # Security settings
    OAUTH_STATE_SECRET: str = os.getenv("OAUTH_STATE_SECRET", "your-secret-key")
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True

settings = Settings() 