"""
Leave Request Database Model
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base
import enum

class LeaveStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class LeaveType(enum.Enum):
    ANNUAL = "annual"
    SICK = "sick"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    EMERGENCY = "emergency"
    UNPAID = "unpaid"
    COMPENSATORY = "compensatory"

class LeaveRequest(Base):
    """Leave request model"""
    
    __tablename__ = "leave_requests"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Leave Details
    leave_type = Column(Enum(LeaveType), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(Integer, nullable=False)
    reason = Column(Text, nullable=False)
    
    # Status
    status = Column(Enum(LeaveStatus), default=LeaveStatus.PENDING, nullable=False)
    admin_notes = Column(Text, nullable=True)
    
    # Emergency Contact (for emergency leaves)
    emergency_contact = Column(String(100), nullable=True)
    emergency_phone = Column(String(20), nullable=True)
    
    # Medical Certificate (for sick leaves)
    medical_certificate_url = Column(String(500), nullable=True)
    
    # Timestamps
    applied_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    approved_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="leave_requests")
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    
    def __repr__(self):
        return f"<LeaveRequest(id={self.id}, user_id={self.user_id}, type={self.leave_type.value}, status={self.status.value})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else None,
            "leave_type": self.leave_type.value,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "total_days": self.total_days,
            "reason": self.reason,
            "status": self.status.value,
            "admin_notes": self.admin_notes,
            "emergency_contact": self.emergency_contact,
            "emergency_phone": self.emergency_phone,
            "medical_certificate_url": self.medical_certificate_url,
            "applied_date": self.applied_date.isoformat(),
            "approved_date": self.approved_date.isoformat() if self.approved_date else None,
            "approved_by_id": self.approved_by_id,
            "approved_by_name": self.approved_by.name if self.approved_by else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def can_be_cancelled(self):
        """Check if leave request can be cancelled"""
        return self.status in [LeaveStatus.PENDING, LeaveStatus.APPROVED]
    
    def can_be_modified(self):
        """Check if leave request can be modified"""
        return self.status == LeaveStatus.PENDING
    
    def is_current(self):
        """Check if leave is currently active"""
        from datetime import date
        today = date.today()
        return (self.status == LeaveStatus.APPROVED and 
                self.start_date <= today <= self.end_date)
    
    def is_upcoming(self):
        """Check if leave is upcoming"""
        from datetime import date
        today = date.today()
        return (self.status == LeaveStatus.APPROVED and 
                self.start_date > today)
    
    def is_past(self):
        """Check if leave is in the past"""
        from datetime import date
        today = date.today()
        return self.end_date < today
    
    def calculate_days(self):
        """Calculate total days between start and end date"""
        return (self.end_date - self.start_date).days + 1

# Create indexes for better performance
from sqlalchemy import Index

# Create indexes
Index('idx_leave_requests_user_id', LeaveRequest.user_id)
Index('idx_leave_requests_status', LeaveRequest.status)
Index('idx_leave_requests_dates', LeaveRequest.start_date, LeaveRequest.end_date)
Index('idx_leave_requests_type', LeaveRequest.leave_type)