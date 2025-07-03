"""
User Schemas for University System
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    LECTURER = "lecturer"
    STUDENT = "student"
    HOD = "hod"

class StudentLevel(str, Enum):
    LEVEL_100 = "100"
    LEVEL_200 = "200"
    LEVEL_300 = "300"
    LEVEL_400 = "400"
    LEVEL_500 = "500"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class UserBase(BaseModel):
    """Base user schema"""
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    gender: Optional[Gender] = None
    university: str = Field(default="Bowen University", max_length=100)
    college: str = Field(..., max_length=100)
    department: str = Field(..., max_length=100)
    address: Optional[str] = Field(None, max_length=500)

    @validator('full_name')
    def validate_full_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters')
        return v.strip()

    @validator('phone')
    def validate_phone(cls, v):
        if v:
            # Basic phone validation
            import re
            if not re.match(r'^[\+]?[\d\s\-\(\)]{7,20}$', v):
                raise ValueError('Invalid phone number format')
        return v

class UserCreate(UserBase):
    """Schema for creating new user"""
    password: str = Field(..., min_length=6, max_length=128)
    role: UserRole
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

class LecturerCreate(UserBase):
    """Schema for creating lecturer"""
    staff_id: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    programme: Optional[str] = Field(None, max_length=100)
    employment_date: Optional[date] = None
    
    @validator('staff_id')
    def validate_staff_id(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Staff ID must be at least 3 characters')
        return v.upper().strip()

class StudentCreate(UserBase):
    """Schema for creating student"""
    student_id: str = Field(..., min_length=3, max_length=50)
    matric_number: Optional[str] = Field(None, max_length=20)
    password: str = Field(..., min_length=6, max_length=128)
    programme: str = Field(..., max_length=100)
    level: StudentLevel
    admission_date: Optional[date] = None
    
    @validator('student_id')
    def validate_student_id(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Student ID must be at least 3 characters')
        return v.upper().strip()
    
    @validator('matric_number')
    def validate_matric_number(cls, v):
        if v:
            import re
            if not re.match(r'^[A-Z0-9]{4,10}$', v.upper()):
                raise ValueError('Invalid matriculation number format')
            return v.upper()
        return v

class UserUpdate(BaseModel):
    """Schema for updating user"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    profile_image: Optional[str] = Field(None, max_length=255)
    gender: Optional[Gender] = None

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str = Field(..., min_length=1)

class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    full_name: str
    email: str
    staff_id: Optional[str] = None
    student_id: Optional[str] = None
    matric_number: Optional[str] = None
    university: str
    college: str
    department: str
    programme: Optional[str] = None
    level: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    is_face_registered: bool
    profile_image: Optional[str] = None
    admission_date: Optional[datetime] = None
    employment_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        orm_mode = True

class UserList(BaseModel):
    """Schema for user list response"""
    users: List[UserResponse]
    total: int
    page: int = 1
    size: int = 20
    pages: int = 1

class UserProfile(BaseModel):
    """Schema for detailed user profile"""
    user: UserResponse
    attendance_summary: Optional[dict] = None
    course_summary: Optional[dict] = None
    recent_activity: Optional[List[dict]] = None

class PasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=128)
    confirm_password: str = Field(..., min_length=6, max_length=128)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class FaceRegistration(BaseModel):
    """Schema for face registration"""
    user_id: int
    confidence: Optional[float] = None
    image_path: Optional[str] = None

class UserStats(BaseModel):
    """Schema for user statistics"""
    total_users: int
    active_users: int
    lecturers: int
    students: int
    verified_users: int
    face_registered_users: int

