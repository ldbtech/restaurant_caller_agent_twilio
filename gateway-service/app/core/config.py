from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "Flikor Gateway"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS Configuration - Add your frontend domain
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # For local development
        "https://flikor.com",     # Your production domain
        "https://www.flikor.com"  # With www
    ]
    
    # Service Configurations
    DB_SERVICE_HOST: str = "localhost"
    DB_SERVICE_PORT: int = 50051
    DB_SERVICE_PROTO_PATH: str = str(Path(__file__).parent.parent / "protos_generated")
    
    AUTH_SERVICE_HOST: str = "localhost"
    AUTH_SERVICE_PORT: int = 50052
    AUTH_SERVICE_PROTO_PATH: str = str(Path(__file__).parent.parent.parent / "auth-service/app/proto")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()