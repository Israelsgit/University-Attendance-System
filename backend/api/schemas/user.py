"""
User Pydantic Schemas for Request/Response Validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime, date
import re

class UserBase(BaseModel):
    """Base user schema"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    employee_id: str = Field(..., min_length=3, max_length=20)
    department: str = Field(..., min_length=2, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    designation: Optional[str] = Field(None, max_length=100)
    hire_date: Optional[date] = None
    salary: Optional[float] = Field(None, ge=0)
    manager_id: Optional[int] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[\d\s\-\(\)]+$', v):
            raise ValueError('Invalid phone number format')
        return v
    
    @validator('employee_id')
    def validate_employee_id(cls, v):
        if not re.match(r'^[A-Z0-9]+$', v.upper()):
            raise ValueError('Employee ID must contain only letters and numbers')
        return v.upper()

class UserCreate(UserBase):
    """Schema for creating new user"""
    password: str = Field(..., min_length=8, max_length=128)
    is_admin: bool = False
    role: str = Field(default="employee")
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserUpdate(BaseModel):
    """Schema for updating user"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, min_length=2, max_length=50)
    designation: Optional[str] = Field(None, max_length=100)
    salary: Optional[float] = Field(None, ge=0)
    manager_id: Optional[int] = None
    is_active: Optional[bool] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[\d\s\-\(\)]+$', v):
            raise ValueError('Invalid phone number format')
        return v

class UserPasswordUpdate(BaseModel):
    """Schema for password update"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    is_active: bool
    is_admin: bool
    role: str
    profile_image_url: Optional[str]
    face_encoding_status: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    """Schema for user profile response"""
    id: int
    name: str
    email: str
    employee_id: str
    department: str
    designation: Optional[str]
    phone: Optional[str]
    hire_date: Optional[date]
    profile_image_url: Optional[str]
    face_encoding_status: bool
    role: str
    manager_name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    """Schema for user list response"""
    id: int
    name: str
    email: str
    employee_id: str
    department: str
    designation: Optional[str]
    is_active: bool
    role: str
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserStats(BaseModel):
    """Schema for user statistics"""
    total_attendance_days: int
    present_days: int
    absent_days: int
    late_days: int
    overtime_days: int
    total_hours: float
    avg_hours: float
    attendance_rate: float
    leave_balance: int
    leaves_taken: int

class FaceEncodingUpdate(BaseModel):
    """Schema for face encoding update"""
    encoding_data: str  # Base64 encoded face data

class BulkUserCreate(BaseModel):
    """Schema for bulk user creation"""
    users: List[UserCreate]
    send_welcome_email: bool = True

class UserSearchQuery(BaseModel):
    """Schema for user search"""
    query: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    limit: int = Field(default=50, le=100)
    offset: int = Field(default=0, ge=0)

class UserExport(BaseModel):
    """Schema for user data export"""
    format: str = Field(default="csv", pattern="^(csv|excel|json)$")
    include_inactive: bool = False
    departments: Optional[List[str]] = None

# Admin-specific schemas
class AdminUserUpdate(UserUpdate):
    """Schema for admin user updates"""
    is_admin: Optional[bool] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    employee_id: Optional[str] = Field(None, min_length=3, max_length=20)
    
    @validator('employee_id')
    def validate_employee_id(cls, v):
        if v and not re.match(r'^[A-Z0-9]+$', v.upper()):
            raise ValueError('Employee ID must contain only letters and numbers')
        return v.upper() if v else None

class UserRole(BaseModel):
    """Schema for user role management"""
    role: str = Field(..., pattern="^(admin|manager|hr|employee)$")
    permissions: Optional[List[str]] = None

class UserActivation(BaseModel):
    """Schema for user activation/deactivation"""
    is_active: bool
    reason: Optional[str] = None

# Response schemas
class UserCreateResponse(BaseModel):
    """Response schema for user creation"""
    success: bool
    message: str
    user_id: int
    employee_id: str

class UserBulkCreateResponse(BaseModel):
    """Response schema for bulk user creation"""
    success: bool
    message: str
    created_count: int
    failed_count: int
    failed_users: List[dict] = []

class UserDeleteResponse(BaseModel):
    """Response schema for user deletion"""
    success: bool
    message: str
    user_id: int