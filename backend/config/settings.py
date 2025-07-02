"""
Application Settings and Configuration
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AttendanceAI API"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=True)
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///./attendance.db")
    DB_ECHO: bool = Field(default=False)
    
    # Security
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(default=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ])
    
    # File Upload
    MAX_FILE_SIZE: int = Field(default=5 * 1024 * 1024)  # 5MB
    ALLOWED_IMAGE_TYPES: List[str] = Field(default=[
        "image/jpeg", 
        "image/jpg", 
        "image/png", 
        "image/webp"
    ])
    UPLOAD_DIR: str = Field(default="uploads")
    
    # Face Recognition
    FACE_CONFIDENCE_THRESHOLD: float = Field(default=0.8)
    MAX_FACE_DETECTION_TIME: int = Field(default=30)  # seconds
    MODEL_PATH: str = Field(default="models/svm_model_160x160.pkl")
    EMBEDDINGS_PATH: str = Field(default="models/faces_embeddings_done_35classes.npz")
    HAARCASCADE_PATH: str = Field(default="models/haarcascade_frontalface_default.xml")
    
    # Email (optional)
    SMTP_SERVER: str = Field(default="")
    SMTP_PORT: int = Field(default=587)
    SMTP_USERNAME: str = Field(default="")
    SMTP_PASSWORD: str = Field(default="")
    SMTP_FROM_EMAIL: str = Field(default="")
    
    # Redis (optional for caching)
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    USE_REDIS: bool = Field(default=False)
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE: str = Field(default="logs/app.log")
    
    # Working Hours
    WORK_START_TIME: str = Field(default="09:00")
    WORK_END_TIME: str = Field(default="17:00")
    BREAK_DURATION_MINUTES: int = Field(default=60)
    OVERTIME_THRESHOLD_MINUTES: int = Field(default=480)  # 8 hours
    
    # Attendance
    LATE_THRESHOLD_MINUTES: int = Field(default=15)
    EARLY_DEPARTURE_THRESHOLD_MINUTES: int = Field(default=15)
    MAX_DAILY_HOURS: int = Field(default=12)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Create necessary directories
def create_directories():
    """Create necessary directories"""
    directories = [
        settings.UPLOAD_DIR,
        "logs",
        "models",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

# Call on import
create_directories()