from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database settings
    DATABASE_URL: str = "sqlite:///scheduler.db"

    # Application settings
    DEFAULT_PERIODS_PER_DAY: int = 4
    MAX_SOLVE_TIME_SECONDS: int = 60
    
    # JWT Authentication settings
    jwt_secret_key: str = "pWbRD1RAI4UJkTZo7btZp0RYpZlVBiOIb3kM3dkAxPimS3d7lSmuN3b6HXDbtwLUOkHT9HXJp3kSsh3nGp2MEg"  # In production, use a secure secret
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30
    
    # CSRF settings
    secret_key: str = "your-session-secret-key"  # For session middleware
    csrf_secret: str = "your-csrf-secret-key"
    session_max_age: int = 14 * 24 * 60 * 60  # 14 days in seconds
    cookie_secure: bool = False  # Set to True in production with HTTPS
    
    # Redis settings (for distributed rate limiting)
    redis_url: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

