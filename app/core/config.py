"""
Configuration management for IDM Latent Space
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "IDM Latent Space API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Security
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # File Storage
    UPLOAD_DIR: Path = Path("uploads")
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: List[str] = [".syx", ".json", ".csv", ".mid", ".bin"]
    
    # Machine Learning
    MODEL_STORAGE_DIR: Path = Path("models")
    DATASET_STORAGE_DIR: Path = Path("datasets")
    CACHE_DIR: Path = Path("cache")
    
    # Processing
    MAX_WORKERS: int = 4
    BATCH_SIZE: int = 1000
    MEMORY_LIMIT: str = "8GB"
    
    # Feature Engineering
    DEFAULT_LATENT_DIMS: List[int] = [32, 64, 128, 256]
    SUPPORTED_NORMALIZATIONS: List[str] = ["min_max", "z_score", "robust", "quantile"]
    SUPPORTED_REDUCTIONS: List[str] = ["pca", "umap", "tsne", "autoencoder"]
    
    # Monitoring
    ENABLE_METRICS: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env

    def __init__(self, **data):
        super().__init__(**data)
        
        # Create directories if they don't exist
        self.UPLOAD_DIR.mkdir(exist_ok=True)
        self.MODEL_STORAGE_DIR.mkdir(exist_ok=True)
        self.DATASET_STORAGE_DIR.mkdir(exist_ok=True)
        self.CACHE_DIR.mkdir(exist_ok=True)

# Create settings instance
settings = Settings()

# Development settings
class DevelopmentSettings(Settings):
    """Development configuration"""
    DEBUG: bool = True
    DATABASE_ECHO: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

# Production settings  
class ProductionSettings(Settings):
    """Production configuration"""
    DEBUG: bool = False
    DATABASE_ECHO: bool = False
    LOG_LEVEL: str = "WARNING"
    ALLOWED_HOSTS: List[str] = ["api.idmlatentspace.com"]
    
    class Config:
        env_file = ".env"
        extra = "ignore"

# Testing settings
class TestingSettings(Settings):
    """Testing configuration"""
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./test.db"
    REDIS_URL: str = "redis://localhost:6379/1"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

def get_settings() -> Settings:
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()

# Export the appropriate settings
settings = get_settings()