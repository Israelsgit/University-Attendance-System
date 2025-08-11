"""
Authentication Schemas for University System
Updated to support self-registration flow without admin dependency
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

class UserType(str, Enum):
    student = "student"
    lecturer = "lecturer"

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    user_type: UserType

class StudentRegistration(BaseModel):
    full_name: str
    email: EmailStr
    matric_number: str
    password: str
    confirm_password: str
    university: str = "Bowen University"
    college: str
    department: str
    programme: str
    level: str  # "100", "200", "300", "400", "500"
    phone: Optional[str] = None
    gender: Optional[str] = None
    
    @validator('email')
    def validate_student_email(cls, v):
        # Validate that it's a student email format
        if not v.endswith('@student.bowen.edu.ng') and not v.endswith('@bowen.edu.ng'):
            raise ValueError('Please use your university email address')
        return v.lower()
    
    @validator('matric_number')
    def validate_matric_number(cls, v):
        if not v or len(v) < 8:
            raise ValueError('Matriculation number must be at least 8 characters')
        # Basic format validation (can be customized)
        import re
        if not re.match(r'^[A-Z]{2,4}/[A-Z]{2,4}/\d{2}/\d{4}$', v.upper()):
            raise ValueError('Invalid matriculation number format. Use format like: BU/CSC/21/0001')
        return v.upper()
    
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
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class LecturerRegistration(BaseModel):
    full_name: str
    email: EmailStr
    staff_id: str
    password: str
    confirm_password: str
    university: str = "Bowen University"
    college: str
    department: str
    programme: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    employment_date: Optional[date] = None
    
    @validator('email')
    def validate_lecturer_email(cls, v):
        # Validate that it's a staff email format
        if not v.endswith('@bowen.edu.ng'):
            raise ValueError('Please use your university email address')
        return v.lower()
    
    @validator('staff_id')
    def validate_staff_id(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Staff ID must be at least 3 characters')
        # Basic format validation
        import re
        if not re.match(r'^[A-Z]{2,4}/[A-Z]{2,4}/\d{4}$', v.upper()):
            raise ValueError('Invalid staff ID format. Use format like: BU/CSC/2024')
        return v.upper()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserResponse(BaseModel):
    user: dict
    message: str
    redirect_to: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict
    expires_in: int

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    confirm_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class EmailVerification(BaseModel):
    token: str

class FaceRegistrationRequest(BaseModel):
    image_data: str  # Base64 encoded image
    confidence_threshold: Optional[float] = 0.8

class FaceVerificationRequest(BaseModel):
    image_data: str  # Base64 encoded image
    
class DepartmentInfo(BaseModel):
    """Schema for department information"""
    name: str
    code: str
    college: str
    
class CollegeInfo(BaseModel):
    """Schema for college information"""
    name: str
    code: str
    departments: List[str]

class SystemInfo(BaseModel):
    """Schema for system information"""
    universities: List[str]
    colleges: List[CollegeInfo]
    departments: List[DepartmentInfo]
    levels: List[str]