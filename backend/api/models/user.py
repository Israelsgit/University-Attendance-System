"""
Enhanced User Model for University Attendance System
Updated to remove admin role and allow lecturer self-management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime
from typing import Optional
import enum

class UserRole(enum.Enum):
    LECTURER = "lecturer"
    STUDENT = "student"
    # Removed ADMIN - lecturers will have admin capabilities

class StudentLevel(enum.Enum):
    LEVEL_100 = "100"
    LEVEL_200 = "200"
    LEVEL_300 = "300"
    LEVEL_400 = "400"
    LEVEL_500 = "500"

class User(Base):
    """Enhanced User model for university system"""
    
    __tablename__ = "users"
    
    # Primary Fields
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # University-specific fields
    staff_id = Column(String(50), unique=True, nullable=True, index=True)  # For lecturers
    matric_number = Column(String(50), unique=True, nullable=True, index=True)  # For students
    
    # Academic Information
    university = Column(String(100), nullable=False, default="Bowen University", index=True)
    college = Column(String(100), nullable=False, index=True)  # e.g., "College of Information Technology"
    department = Column(String(100), nullable=False, index=True)  # e.g., "Computer Science"
    programme = Column(String(100), nullable=True, index=True)  # e.g., "Computer Science"
    level = Column(Enum(StudentLevel), nullable=True, index=True)  # For students only
    
    # Profile Information
    phone = Column(String(20), nullable=True)
    gender = Column(String(10), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    address = Column(Text, nullable=True)
    profile_image = Column(String(255), nullable=True)
    
    # Face Recognition Data
    face_encoding = Column(Text, nullable=True)  # Stored as JSON string
    face_image_path = Column(String(255), nullable=True)
    face_confidence_threshold = Column(Float, default=0.8)
    is_face_registered = Column(Boolean, default=False)
    
    # Role and Permissions
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=True)  # Auto-verify on registration
    
    # Academic dates
    admission_date = Column(DateTime, nullable=True)  # For students
    employment_date = Column(DateTime, nullable=True)  # For lecturers
    graduation_date = Column(DateTime, nullable=True)  # For graduated students
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    taught_classes = relationship("Course", back_populates="lecturer", foreign_keys="Course.lecturer_id")
    enrolled_classes = relationship("Enrollment", back_populates="student")
    attendance_records = relationship("AttendanceRecord", back_populates="student", foreign_keys="[AttendanceRecord.student_id]")
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.full_name}', role='{self.role}')>"
    
    def get_display_id(self):
        """Get appropriate ID for display (staff_id for lecturers, matric_number for students)"""
        if self.role == UserRole.LECTURER:
            return self.staff_id
        elif self.role == UserRole.STUDENT:
            return self.matric_number
        return f"USER{self.id:04d}"
    
    def is_lecturer(self):
        """Check if user is a lecturer (has admin privileges)"""
        return self.role == UserRole.LECTURER
    
    def is_student(self):
        """Check if user is a student"""
        return self.role == UserRole.STUDENT
    
    def has_admin_privileges(self):
        """Check if user has admin privileges (lecturers do)"""
        return self.role == UserRole.LECTURER
    
    def can_manage_courses(self):
        """Check if user can manage courses"""
        return self.role == UserRole.LECTURER
    
    def can_enroll_students(self):
        """Check if user can enroll students"""
        return self.role == UserRole.LECTURER
    
    def can_view_analytics(self):
        """Check if user can view system analytics"""
        return self.role == UserRole.LECTURER
    
    def can_manage_attendance(self):
        """Check if user can manage attendance records"""
        return self.role == UserRole.LECTURER
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "staff_id": self.staff_id,
            "matric_number": self.matric_number,
            "university": self.university,
            "college": self.college,
            "department": self.department,
            "programme": self.programme,
            "level": self.level.value if self.level else None,
            "phone": self.phone,
            "gender": self.gender,
            "role": self.role.value,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_face_registered": self.is_face_registered,
            "profile_image": self.profile_image,
            "admission_date": self.admission_date.isoformat() if self.admission_date else None,
            "employment_date": self.employment_date.isoformat() if self.employment_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "display_id": self.get_display_id(),
            "permissions": {
                "can_manage_courses": self.can_manage_courses(),
                "can_enroll_students": self.can_enroll_students(),
                "can_view_analytics": self.can_view_analytics(),
                "can_manage_attendance": self.can_manage_attendance(),
                "has_admin_privileges": self.has_admin_privileges()
            }
        }