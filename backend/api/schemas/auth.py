"""
Authentication Pydantic Schemas
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserRegister(BaseModel):
    """User registration schema"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    employee_id: str = Field(..., min_length=3, max_length=50)
    department: str = Field(..., min_length=2, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    
    @validator('employee_id')
    def validate_employee_id(cls, v):
        if not v.isalnum():
            raise ValueError('Employee ID must be alphanumeric')
        return v.upper()
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Invalid phone number format')
        return v

class UserUpdate(BaseModel):
    """User profile update schema"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    position: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    timezone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Invalid phone number format')
        return v

class ChangePassword(BaseModel):
    """Change password schema"""
    current_password: str
    new_password: str = Field(..., min_length=6)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class UserResponse(BaseModel):
    """User response schema"""
    user: dict

class TokenResponse(BaseModel):
    """Token response schema"""
    user: dict
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class ProfileImageResponse(BaseModel):
    """Profile image upload response"""
    message: str
    image_url: str
    user: dict

class FaceEncodingResponse(BaseModel):
    """Face encoding response"""
    message: str
    confidence_threshold: float

class PasswordResetRequest(BaseModel):
    """Password reset request schema"""
    email: EmailStr

class PasswordReset(BaseModel):
    """Password reset schema"""
    token: str
    new_password: str = Field(..., min_length=6)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class EmailVerification(BaseModel):
    """Email verification schema"""
    token: str

class UserStats(BaseModel):
    """User statistics schema"""
    total_attendance_days: int
    present_days: int
    absent_days: int
    late_days: int
    average_hours: float
    total_hours: float
    attendance_rate: float

class UserPreferenceUpdate(BaseModel):
    """User preference update schema"""
    notifications: Optional[dict] = None
    theme: Optional[str] = Field(None, pattern="^(light|dark|auto)$")
    language: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)

class ApiKeyCreate(BaseModel):
    """API key creation schema"""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=255)

class ApiKeyResponse(BaseModel):
    """API key response schema"""
    id: int
    name: str
    key: str
    created_at: datetime
    last_used: Optional[datetime] = None