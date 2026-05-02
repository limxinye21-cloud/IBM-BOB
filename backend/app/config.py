"""
Configuration management for AI Packaging Reliability Copilot Backend
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AI Packaging Reliability Copilot"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite:///./packaging_data.db"
    DATABASE_ECHO: bool = False  # Set to True for SQL logging
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:8501",  # Streamlit default
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # Mock Data Generator
    MOCK_DATA_ENABLED: bool = True
    MOCK_DATA_INTERVAL: int = 30  # seconds
    MOCK_SEED: Optional[int] = 42
    
    # ML Model
    MODEL_PATH: str = "ml/saved_models/model_v1.pkl"
    CONFIDENCE_THRESHOLD: float = 0.75
    
    # watsonx.ai (optional)
    WATSONX_API_KEY: Optional[str] = None
    WATSONX_URL: Optional[str] = None
    WATSONX_PROJECT_ID: Optional[str] = None
    USE_WATSONX: bool = False
    
    # watsonx Orchestrate (optional)
    ORCHESTRATE_API_KEY: Optional[str] = None
    ORCHESTRATE_URL: Optional[str] = None
    USE_ORCHESTRATE: bool = False
    
    # Alerts
    ALERT_EMAIL: Optional[str] = None
    ALERT_WEBHOOK: Optional[str] = None
    ENABLE_ALERTS: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    
    Returns:
        Settings instance
    """
    return Settings()


# Create settings instance
settings = get_settings()


# Ensure log directory exists
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)

# Made with Bob
