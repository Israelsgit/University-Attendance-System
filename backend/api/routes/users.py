"""
Users Routes for University System
Cleaned version - Admin-only endpoints removed, lecturers have management access
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
import logging

from config.database import get_db
from api.models.user import User, UserRole
from api.schemas.user import UserResponse, UserUpdate
from api.utils.security import get_current_user, get_current_lecturer, get_current_student

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile"""
    return UserResponse.from_orm(current_user)

@router.put("/profile")
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    try:
        # Update allowed fields
        if user_update.full_name:
            current_user.full_name = user_update.full_name
        if user_update.phone:
            current_user.phone = user_update.phone
        if user_update.address:
            current_user.address = user_update.address
        if user_update.profile_image:
            current_user.profile_image = user_update.profile_image
        if user_update.gender:
            current_user.gender = user_update.gender
        
        db.commit()
        db.refresh(current_user)
        
        return {
            "message": "Profile updated successfully",
            "user": UserResponse.from_orm(current_user)
        }
        
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

@router.get("/students")
async def get_students(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    college: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    current_lecturer: User = Depends(get_current_lecturer),  # Lecturers can view students
    db: Session = Depends(get_db)
):
    """Get list of students (lecturers only - for course enrollment)"""
    try:
        query = db.query(User).filter(User.role == UserRole.STUDENT)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    User.full_name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.matric_number.ilike(f"%{search}%")
                )
            )
        
        if college:
            query = query.filter(User.college == college)
            
        if department:
            query = query.filter(User.department == department)
        
        # Pagination
        total = query.count()
        students = query.offset((page - 1) * limit).limit(limit).all()
        
        return {
            "students": [UserResponse.from_orm(student) for student in students],
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Error getting students: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get students"
        )

@router.get("/lecturers")
async def get_lecturers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    college: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    current_lecturer: User = Depends(get_current_lecturer),  # Lecturers can view other lecturers
    db: Session = Depends(get_db)
):
    """Get list of lecturers (lecturers only - for system overview)"""
    try:
        query = db.query(User).filter(User.role == UserRole.LECTURER)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    User.full_name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.staff_id.ilike(f"%{search}%")
                )
            )
        
        if college:
            query = query.filter(User.college == college)
            
        if department:
            query = query.filter(User.department == department)
        
        # Pagination
        total = query.count()
        lecturers = query.offset((page - 1) * limit).limit(limit).all()
        
        return {
            "lecturers": [UserResponse.from_orm(lecturer) for lecturer in lecturers],
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Error getting lecturers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get lecturers"
        )

@router.get("/search/students")
async def search_students(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    current_lecturer: User = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Search students for enrollment (lecturers only)"""
    try:
        students = db.query(User).filter(
            and_(
                User.role == UserRole.STUDENT,
                or_(
                    User.full_name.ilike(f"%{q}%"),
                    User.email.ilike(f"%{q}%"),
                    User.matric_number.ilike(f"%{q}%")
                )
            )
        ).limit(limit).all()
        
        return {
            "students": [
                {
                    "id": student.id,
                    "full_name": student.full_name,
                    "email": student.email,
                    "matric_number": student.matric_number,
                    "department": student.department,
                    "level": student.level.value if student.level else None
                }
                for student in students
            ]
        }
        
    except Exception as e:
        logger.error(f"Error searching students: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search students"
        )

@router.get("/{user_id}")
async def get_user_by_id(
    user_id: int,
    current_lecturer: User = Depends(get_current_lecturer),  # Lecturers can view user details
    db: Session = Depends(get_db)
):
    """Get user by ID (lecturers only - for management purposes)"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user"
        )

@router.get("/stats/overview")
async def get_user_stats(
    current_lecturer: User = Depends(get_current_lecturer),  # Lecturers get system stats
    db: Session = Depends(get_db)
):
    """Get user statistics overview (lecturers only - admin access)"""
    try:
        total_students = db.query(User).filter(User.role == UserRole.STUDENT).count()
        total_lecturers = db.query(User).filter(User.role == UserRole.LECTURER).count()
        active_students = db.query(User).filter(
            and_(User.role == UserRole.STUDENT, User.is_active == True)
        ).count()
        verified_students = db.query(User).filter(
            and_(User.role == UserRole.STUDENT, User.is_verified == True)
        ).count()
        face_registered_students = db.query(User).filter(
            and_(User.role == UserRole.STUDENT, User.is_face_registered == True)
        ).count()
        
        return {
            "total_students": total_students,
            "total_lecturers": total_lecturers,
            "active_students": active_students,
            "verified_students": verified_students,
            "face_registered_students": face_registered_students,
            "total_users": total_students + total_lecturers
        }
        
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user statistics"
        )

@router.get("/activity")
async def get_user_activity(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's own activity log"""
    try:
        # This would require an activity log table
        # For now, return empty list with placeholder structure
        return {
            "activities": [],
            "total": 0,
            "message": "Activity logging not implemented yet"
        }
        
    except Exception as e:
        logger.error(f"Error getting user activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user activity"
        )