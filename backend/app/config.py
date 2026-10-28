"""
Apex Logistics AI — Application Configuration
Emotion-Gated Autonomous Logistics Platform v6.0.0
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment"""
    
    # Application
    app_name: str = "Apex Logistics AI"
    app_version: str = "6.0.0"
    debug: bool = True
    
    # Database
    database_url: str = "sqlite:///./data/app.db"
    
    # API
    api_prefix: str = "/api"
    
    # Sentiment Analysis Thresholds
    negative_threshold: float = 0.65
    escalation_threshold: float = 0.85
    
    # Security (for future use)
    secret_key: str = "behavioral-ai-secret-key-change-in-production"
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()
