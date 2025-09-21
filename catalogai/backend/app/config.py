"""Configuration management for CatalogAI backend."""

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings
from typing import Optional, Any


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database configuration
    db_url: str = Field(default="sqlite:///app.db", description="Database URL")
    
    # ML model thresholds
    thresh_auth: float = Field(default=0.15, ge=0.0, le=1.0, description="Threshold for authentic classification")
    thresh_syn: float = Field(default=0.70, ge=0.0, le=1.0, description="Threshold for synthetic classification")
    
    # File upload limits
    max_image_mb: int = Field(default=8, ge=1, le=50, description="Maximum image size in MB")
    
    # Logging configuration
    log_level: str = Field(default="INFO", description="Logging level")
    
    # API configuration
    cors_origins: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://0.0.0.0:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
        ],
        description="CORS allowed origins",
    )

    # Support comma-separated CORS_ORIGINS env var
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Any) -> Any:
        if isinstance(v, str):
            # Allow JSON-style [..] or comma-separated string
            if v.startswith('['):
                return v
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    @field_validator('thresh_auth', 'thresh_syn')
    @classmethod
    def validate_thresholds(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError('Threshold must be between 0.0 and 1.0')
        return v
    
    @model_validator(mode='after')
    def validate_threshold_order(self) -> 'Settings':
        if self.thresh_syn <= self.thresh_auth:
            raise ValueError('thresh_syn must be greater than thresh_auth')
        return self
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }


# Global settings instance
settings = Settings()