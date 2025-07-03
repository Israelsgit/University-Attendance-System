"""
Authentication Schemas for University System
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserType(str, Enum):
    student = "student"
    lecturer = "lecturer"
    admin = "admin"

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    user_type: UserType

class LecturerRegistration(BaseModel):
    full_name: str
    email: EmailStr
    staff_id: str
    password: str
    university: str = "Bowen University"
    college: str
    department: str
    phone: Optional[str] = None
    gender: Optional[str] = None
    
    @validator('staff_id')
    def validate_staff_id(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Staff ID must be at least 3 characters')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

class StudentRegistration(BaseModel):
    full_name: str
    email: EmailStr
    matric_number: str
    password: str
    university: str = "Bowen University"
    college: str
    department: str
    programme: str
    level: str  # "100", "200", "300", "400", "500"
    phone: Optional[str] = None
    gender: Optional[str] = None
    
    @validator('level')
    def validate_level(cls, v):
        if v not in ["100", "200", "300", "400", "500"]:
            raise ValueError('Level must be one of: 100, 200, 300, 400, 500')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

class UserResponse(BaseModel):
    user: dict
    message: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict