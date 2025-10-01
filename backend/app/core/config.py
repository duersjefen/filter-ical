"""Application configuration following FastAPI best practices."""

import os
from enum import Enum
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Environment settings
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    
    # Application settings
    app_name: str = "Filter iCal"
    
    # Database settings
    database_url: str = "sqlite:///./data/icalviewer.db"
    test_database_url: str = "sqlite:///./data/test_icalviewer.db"
    
    # Server settings  
    host: str = "0.0.0.0"
    port: int = 3000
    
    # CORS settings
    allowed_origins: List[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]
    
    # Background job settings
    sync_interval_minutes: int = 5
    enable_background_tasks: bool = True
    dev_sync_interval_minutes: int = 2  # Faster feedback in development
    
    # Demo data settings
    auto_seed_demo_data: bool = True  # Auto-seed in development
    force_seed_demo_data: bool = False  # Force re-seed even if data exists
    
    # Redis cache settings
    redis_url: str = "redis://localhost:6379"
    cache_ttl_seconds: int = 300  # 5 minutes

    # Development settings
    verbose_logging: bool = False  # Extra logging in development

    # Admin authentication
    admin_password: str = "change-me-in-production"  # Override via ADMIN_PASSWORD env var

    # Email settings (for domain request notifications)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""  # Set via SMTP_USERNAME env var
    smtp_password: str = ""  # Set via SMTP_PASSWORD env var
    smtp_from_email: str = "noreply@filter-ical.de"
    admin_email: str = ""  # Set via ADMIN_EMAIL env var - receives domain request notifications
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    domains_config_path: Path = base_dir / "domains" / "domains.yaml"
    openapi_spec_path: Path = base_dir / "openapi.yaml"

    class Config:
        # Default to .env.development for local development (in project root)
        # Production will override via environment variables
        env_file = str(Path(__file__).parent.parent.parent / ".." / ".env.development")
        case_sensitive = False
        extra = "ignore"  # Ignore extra env vars (e.g., frontend-specific vars)
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == Environment.TESTING
    
    @property
    def should_seed_demo_data(self) -> bool:
        """Check if demo data should be seeded."""
        return self.is_development and self.auto_seed_demo_data
    
    @property
    def should_enable_background_tasks(self) -> bool:
        """Check if background tasks should be enabled."""
        if self.is_testing:
            return False  # Never in testing
        return self.enable_background_tasks
    
    @property
    def actual_sync_interval_minutes(self) -> int:
        """Get the actual sync interval based on environment."""
        if self.is_development:
            return self.dev_sync_interval_minutes
        return self.sync_interval_minutes
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Auto-detect environment from common variables
        if not kwargs.get('environment'):
            if os.getenv('TESTING', '').lower() == 'true':
                self.environment = Environment.TESTING
            elif os.getenv('PRODUCTION', '').lower() == 'true':
                self.environment = Environment.PRODUCTION
            elif os.getenv('DEV_MODE', '').lower() == 'true':
                self.environment = Environment.DEVELOPMENT
            # Default to development if in Docker dev environment
            elif os.getenv('UVICORN_CMD_ARGS') or '--reload' in ' '.join(os.sys.argv if hasattr(os, 'sys') else []):
                self.environment = Environment.DEVELOPMENT
        
        # Set debug mode for development
        if self.is_development and not kwargs.get('debug'):
            self.debug = True
        
        # Set verbose logging for development
        if self.is_development and not kwargs.get('verbose_logging'):
            self.verbose_logging = True


# Global settings instance
settings = Settings()


def get_database_url() -> str:
    """Get appropriate database URL based on environment."""
    if settings.is_testing:
        return settings.test_database_url
    return settings.database_url