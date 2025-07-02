"""
User Database Model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime
from typing import Optional

class User(Base):
    """User model for authentication and profile management"""
    
    __tablename__ = "users"
    
    # Primary Fields
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile Information
    department = Column(String(100), nullable=False, index=True)
    position = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    bio = Column(Text, nullable=True)
    profile_image = Column(String(255), nullable=True)
    
    # Face Recognition Data
    face_encoding = Column(Text, nullable=True)  # Stored as JSON string
    face_image_path = Column(String(255), nullable=True)
    face_confidence_threshold = Column(Float, default=0.8)
    
    # Status and Permissions
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    role = Column(String(50), default="employee")  # employee, manager, hr, admin
    
    # Work Information
    work_schedule = Column(String(50), default="full_time")  # full_time, part_time, contract
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    manager_id = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_password_change = Column(DateTime(timezone=True), nullable=True)
    
    # Settings
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")
    notification_settings = Column(Text, nullable=True)  # JSON string
    
    # Relationships
    attendance_records = relationship("AttendanceRecord", back_populates="user")
    leave_requests = relationship(
        "LeaveRequest",
        back_populates="user",
        foreign_keys="[LeaveRequest.user_id]"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"
    
    def to_dict(self, include_sensitive: bool = False):
        """Convert user to dictionary"""
        data = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "employee_id": self.employee_id,
            "department": self.department,
            "position": self.position,
            "phone": self.phone,
            "bio": self.bio,
            "profile_image": self.profile_image,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "role": self.role,
            "work_schedule": self.work_schedule,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "timezone": self.timezone,
            "language": self.language,
        }
        
        if include_sensitive:
            data.update({
                "is_admin": self.is_admin,
                "face_confidence_threshold": self.face_confidence_threshold,
                "manager_id": self.manager_id,
            })
        
        return data
    
    def can_access_user(self, target_user_id: int) -> bool:
        """Check if user can access another user's data"""
        if self.is_admin:
            return True
        if self.id == target_user_id:
            return True
        if self.role in ["manager", "hr"] and self.department:
            # Managers can access users in their department
            return True
        return False
    
    def can_manage_attendance(self) -> bool:
        """Check if user can manage attendance records"""
        return self.role in ["admin", "hr", "manager"] or self.is_admin
    
    def get_permissions(self) -> list:
        """Get user permissions based on role"""
        base_permissions = ["read_own_profile", "update_own_profile", "read_own_attendance"]
        
        if self.role == "admin" or self.is_admin:
            return base_permissions + [
                "manage_users", "manage_attendance", "manage_system", 
                "view_analytics", "export_data", "manage_leaves"
            ]
        elif self.role == "hr":
            return base_permissions + [
                "manage_users", "manage_attendance", "view_analytics", 
                "export_data", "manage_leaves"
            ]
        elif self.role == "manager":
            return base_permissions + [
                "view_team_attendance", "approve_leaves", "view_team_analytics"
            ]
        else:
            return base_permissions + ["request_leave"]

class UserSession(Base):
    """User session tracking"""
    
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    token_id = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), nullable=True)
    device_info = Column(Text, nullable=True)  # JSON string
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, active={self.is_active})>"

class UserPreference(Base):
    """User preferences and settings"""
    
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    key = Column(String(100), nullable=False, index=True)
    value = Column(Text, nullable=True)
    data_type = Column(String(20), default="string")  # string, json, boolean, integer
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id}, key='{self.key}')>"