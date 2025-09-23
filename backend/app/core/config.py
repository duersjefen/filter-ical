"""Application configuration following FastAPI best practices."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    app_name: str = "iCal Viewer API"
    debug: bool = False
    
    # Database settings
    database_url: str = "sqlite:///./data/icalviewer.db"
    
    # Development/Testing
    testing: bool = False
    test_database_url: str = "sqlite:///./data/test_icalviewer.db"
    
    # Server settings  
    host: str = "0.0.0.0"
    port: int = 3000
    
    # CORS settings
    allowed_origins: list = ["http://localhost:8000", "http://127.0.0.1:8000"]
    
    # Background job settings
    sync_interval_minutes: int = 5
    
    # Redis cache settings
    redis_url: str = "redis://localhost:6379"
    cache_ttl_seconds: int = 300  # 5 minutes
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    domains_config_path: Path = base_dir / "domains.yaml"
    openapi_spec_path: Path = base_dir / "openapi.yaml"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_database_url() -> str:
    """Get appropriate database URL based on environment."""
    if settings.testing:
        return settings.test_database_url
    return settings.database_url