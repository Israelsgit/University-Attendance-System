"""
User Management Routes for University System
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
import logging

from config.database import get_db
from api.models.user import User, UserRole, StudentLevel
from api.schemas.auth import UserResponse
from api.utils.security import get_current_user, get_current_admin, get_current_lecturer

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    return {"user": current_user.to_dict()}

@router.put("/profile")
async def update_user_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    try:
        # Update allowed fields only
        allowed_fields = ["phone", "address", "profile_image"]
        
        for field, value in profile_data.items():
            if field in allowed_fields and hasattr(current_user, field):
                setattr(current_user, field, value)
        
        db.commit()
        db.refresh(current_user)
        
        return {"message": "Profile updated successfully", "user": current_user.to_dict()}
        
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

@router.get("/students")
async def get_students(
    course_id: Optional[int] = Query(None),
    department: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_lecturer: User = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Get students list (lecturer only)"""
    try:
        query = db.query(User).filter(User.role == UserRole.STUDENT)
        
        # Filter by department if lecturer is not admin
        if current_lecturer.role != UserRole.ADMIN:
            query = query.filter(User.department == current_lecturer.department)
        
        # Apply filters
        if department:
            query = query.filter(User.department == department)
        
        if level:
            query = query.filter(User.level == StudentLevel(level))
        
        if search:
            query = query.filter(
                or_(
                    User.full_name.contains(search),
                    User.email.contains(search),
                    User.student_id.contains(search),
                    User.matric_number.contains(search)
                )
            )
        
        students = query.all()
        
        return {
            "students": [student.to_dict() for student in students],
            "total": len(students)
        }
        
    except Exception as e:
        logger.error(f"Error getting students: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get students"
        )

@router.get("/lecturers")
async def get_lecturers(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get lecturers list (admin only)"""
    try:
        lecturers = db.query(User).filter(
            User.role.in_([UserRole.LECTURER, UserRole.HOD])
        ).all()
        
        return {
            "lecturers": [lecturer.to_dict() for lecturer in lecturers],
            "total": len(lecturers)
        }
        
    except Exception as e:
        logger.error(f"Error getting lecturers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get lecturers"
        )

@router.put("/{user_id}/activate")
async def activate_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Activate user account (admin only)"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = True
        db.commit()
        
        return {"message": f"User {user.full_name} activated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating user: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate user"
        )

@router.put("/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Deactivate user account (admin only)"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = False
        db.commit()
        
        return {"message": f"User {user.full_name} deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating user: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate user"
        )