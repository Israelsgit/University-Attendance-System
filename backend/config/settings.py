"""
Application Settings and Configuration - Combined with University Settings
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator, EmailStr
import secrets

# Import your existing university settings
from .university_settings import UniversitySettings  # Perfect - same directory

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = f"{UniversitySettings.UNIVERSITY_NAME} Attendance System"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # API Configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    API_V1_STR: str = "/api"
    WORKERS: int = 1
    
    # University Information (from your existing settings)
    UNIVERSITY_NAME: str = UniversitySettings.UNIVERSITY_NAME
    UNIVERSITY_SHORT_NAME: str = UniversitySettings.UNIVERSITY_SHORT_NAME
    UNIVERSITY_EMAIL_DOMAIN: str = UniversitySettings.UNIVERSITY_EMAIL_DOMAIN
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = "sqlite:///./university_attendance.db"
    DB_ECHO: bool = False  # Set to True for SQL query logging
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
    
    # File Upload
    UPLOAD_DIRECTORY: str = "uploads"
    MAX_FILE_SIZE: int = UniversitySettings.MAX_FACE_IMAGE_SIZE
    ALLOWED_IMAGE_TYPES: List[str] = UniversitySettings.ALLOWED_IMAGE_TYPES
    
    # Face Recognition (from your settings)
    FACE_CONFIDENCE_THRESHOLD: float = UniversitySettings.FACE_CONFIDENCE_THRESHOLD
    FACE_VERIFICATION_THRESHOLD: float = UniversitySettings.FACE_VERIFICATION_THRESHOLD
    
    # Academic Settings (from your settings)
    CURRENT_SESSION: str = UniversitySettings.CURRENT_SESSION
    CURRENT_SEMESTER: str = UniversitySettings.CURRENT_SEMESTER
    STUDENT_LEVELS: List[str] = UniversitySettings.STUDENT_LEVELS
    COLLEGES: List[str] = UniversitySettings.COLLEGES
    
    # Attendance Settings (from your settings)
    LATE_THRESHOLD_MINUTES: int = UniversitySettings.LATE_THRESHOLD_MINUTES
    MINIMUM_ATTENDANCE_PERCENTAGE: float = UniversitySettings.MINIMUM_ATTENDANCE_PERCENTAGE
    
    # Email Settings (for future use)
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    
    # Email Notifications (from your settings)
    LECTURER_EMAIL_NOTIFICATIONS: bool = UniversitySettings.LECTURER_EMAIL_NOTIFICATIONS
    STUDENT_EMAIL_NOTIFICATIONS: bool = UniversitySettings.STUDENT_EMAIL_NOTIFICATIONS
    ADMIN_EMAIL_NOTIFICATIONS: bool = UniversitySettings.ADMIN_EMAIL_NOTIFICATIONS
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Analytics (from your settings)
    ANALYTICS_CACHE_DURATION: int = UniversitySettings.ANALYTICS_CACHE_DURATION
    GENERATE_REPORTS_ASYNC: bool = UniversitySettings.GENERATE_REPORTS_ASYNC
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """Ensure database URL is properly formatted"""
        if not v:
            raise ValueError("DATABASE_URL cannot be empty")
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        """Ensure secret key is strong enough"""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("CORS_ORIGINS")
    def validate_cors_origins(cls, v):
        """Ensure CORS origins are properly formatted"""
        for origin in v:
            if not origin.startswith(("http://", "https://")):
                raise ValueError(f"CORS origin must start with http:// or https://: {origin}")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Ensure required directories exist
import pathlib
pathlib.Path("logs").mkdir(exist_ok=True)
pathlib.Path("uploads").mkdir(exist_ok=True)
pathlib.Path("uploads/faces").mkdir(exist_ok=True)
pathlib.Path("uploads/documents").mkdir(exist_ok=True)

# Use your existing college and department mappings
COLLEGE_DEPARTMENTS = UniversitySettings.DEPARTMENT_MAPPINGS

# Department code mappings for student ID generation
DEPARTMENT_CODES = {
    "Computer Science": "CSC",
    "Information Technology": "IFT", 
    "Cyber Security": "CYS",
    "Software Engineering": "SWE",
    "Communication Arts": "COM",
    "Mass Communication": "MCM",
    "Electrical and Electronics Engineering": "EEE",
    "Mechatronics Engineering": "MEC",
    "Chemistry and Industrial Chemistry": "CHM",
    "Food Science and Technology": "FST",
    "Mathematics and Statistics": "MAT",
    "Physics and Solar Energy": "PHY",
    "Medicine and Surgery": "MED",
    "Nursing Science": "NUR",
    "Public Health": "PHC",
    "Medical Laboratory Science": "MLS",
    "Physiotherapy": "PHT",
    "Nutrition and Dietetics": "NUT",
    "Anatomy": "ANA",
    "Accounting & Finance": "ACC",
    "Political Science": "POL",
    "Business Administration": "BUS",
    "Industrial Relations & Personnel Management": "IRP",
    "International Relations": "INT",
    "Sociology": "SOC",
    "Law": "LAW",
    "Architecture": "ARC",
    "Surveying and Geoinformatics": "SUR",
    "English Language": "ENG",
    "History and International Studies": "HIS",
    "Philosophy and Religious Studies": "PHL",
    "Music": "MUS",
    "Theatre Arts": "THR"
}

def get_departments_by_college(college: str) -> List[str]:
    """Get departments for a specific college"""
    return UniversitySettings.get_department_by_college(college)

def get_department_code(department: str) -> str:
    """Get department code for ID generation"""
    return DEPARTMENT_CODES.get(department, "GEN")

def is_valid_university_email(email: str) -> bool:
    """Check if email domain is valid for the university"""
    return UniversitySettings.is_valid_email_domain(email)

# Export settings for other modules
__all__ = [
    "settings", 
    "COLLEGE_DEPARTMENTS", 
    "DEPARTMENT_CODES",
    "get_departments_by_college",
    "get_department_code", 
    "is_valid_university_email",
    "UniversitySettings"  # Export your original class too
]