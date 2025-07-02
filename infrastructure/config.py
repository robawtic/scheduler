from typing import Optional

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database settings
    DATABASE_URL: str = "sqlite:///scheduler.db"

    # Application settings
    DEFAULT_PERIODS_PER_DAY: int = 4
    MAX_SOLVE_TIME_SECONDS: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 