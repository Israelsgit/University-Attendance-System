"""
User Management Routes
Handles user CRUD operations, profile management, and admin functions
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
import logging
import io
import csv
from datetime import datetime

from config.database import get_db
from api.models.user import User
from api.models.attendance import AttendanceRecord
from api.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserProfile, UserListResponse,
    UserPasswordUpdate, UserStats, BulkUserCreate, UserSearchQuery,
    AdminUserUpdate, UserActivation, UserCreateResponse
)
from api.schemas.common import PaginatedResponse, SuccessResponse
from api.utils.security import get_current_user, get_password_hash, verify_password
from services.face_recognition import face_recognition_service

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile"""
    try:
        return {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "employee_id": current_user.employee_id,
            "department": current_user.department,
            "designation": current_user.designation,
            "phone": current_user.phone,
            "hire_date": current_user.hire_date,
            "profile_image_url": current_user.profile_image_url,
            "face_encoding_status": bool(current_user.face_encoding),
            "role": current_user.role,
            "manager_name": current_user.manager.name if current_user.manager else None,
            "created_at": current_user.created_at
        }
    except Exception as e:
        logger.error(f"❌ Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )

@router.put("/me", response_model=SuccessResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    try:
        # Update allowed fields
        update_data = user_update.dict(exclude_unset=True)
        
        # Remove fields that users can't update themselves
        restricted_fields = ["is_active", "is_admin", "role", "employee_id"]
        for field in restricted_fields:
            update_data.pop(field, None)
        
        # Check if email is being changed and is unique
        if "email" in update_data:
            existing_user = db.query(User).filter(
                and_(User.email == update_data["email"], User.id != current_user.id)
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Update user
        for field, value in update_data.items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)
        
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"✅ User profile updated: {current_user.email}")
        
        return SuccessResponse(
            message="Profile updated successfully",
            data={"user_id": current_user.id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Profile update error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )

@router.put("/me/password", response_model=SuccessResponse)
async def change_password(
    password_update: UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user's password"""
    try:
        # Verify current password
        if not verify_password(password_update.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        current_user.hashed_password = get_password_hash(password_update.new_password)
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"✅ Password changed: {current_user.email}")
        
        return SuccessResponse(message="Password changed successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Password change error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

@router.post("/me/face-encoding")
async def update_face_encoding(
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's face encoding"""
    try:
        # Validate image
        if image.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image format"
            )
        
        # Read image data
        image_data = await image.read()
        
        # Process face encoding
        result = face_recognition_service.process_face_encoding(image_data)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        # Update user's face encoding
        current_user.face_encoding = result["encoding"]
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"✅ Face encoding updated: {current_user.email}")
        
        return SuccessResponse(
            message="Face encoding updated successfully",
            data={"encoding_quality": result["quality"]}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Face encoding update error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Face encoding update failed"
        )

@router.get("/me/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's attendance statistics"""
    try:
        # Get this month's attendance records
        from datetime import date
        today = date.today()
        month_start = today.replace(day=1)
        
        attendance_records = db.query(AttendanceRecord).filter(
            and_(
                AttendanceRecord.user_id == current_user.id,
                AttendanceRecord.date >= month_start
            )
        ).all()
        
        # Calculate statistics
        total_days = len(attendance_records)
        present_days = len([r for r in attendance_records if r.status in ['present', 'late', 'overtime']])
        absent_days = len([r for r in attendance_records if r.status == 'absent'])
        late_days = len([r for r in attendance_records if r.status == 'late'])
        overtime_days = len([r for r in attendance_records if r.status == 'overtime'])
        
        total_hours = sum([r.total_hours or 0 for r in attendance_records])
        avg_hours = total_hours / max(present_days, 1)
        attendance_rate = (present_days / max(total_days, 1)) * 100
        
        # Leave balance calculation (simplified)
        leave_balance = 21  # Annual leave balance
        leaves_taken = len([r for r in attendance_records if r.status == 'leave'])
        
        return UserStats(
            total_attendance_days=total_days,
            present_days=present_days,
            absent_days=absent_days,
            late_days=late_days,
            overtime_days=overtime_days,
            total_hours=round(total_hours, 2),
            avg_hours=round(avg_hours, 2),
            attendance_rate=round(attendance_rate, 2),
            leave_balance=leave_balance - leaves_taken,
            leaves_taken=leaves_taken
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting user stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user statistics"
        )

# Admin routes
@router.get("/", response_model=PaginatedResponse)
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get users list (admin/manager only)"""
    try:
        # Check permissions
        if not current_user.can_view_users():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Build query
        query = db.query(User)
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.name.ilike(search_term),
                    User.email.ilike(search_term),
                    User.employee_id.ilike(search_term)
                )
            )
        
        if department:
            query = query.filter(User.department == department)
        
        if role:
            query = query.filter(User.role == role)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        users = query.offset(offset).limit(limit).all()
        
        # Convert to response format
        users_data = [
            UserListResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                employee_id=user.employee_id,
                department=user.department,
                designation=user.designation,
                is_active=user.is_active,
                role=user.role,
                last_login=user.last_login
            ) for user in users
        ]
        
        return PaginatedResponse(
            items=users_data,
            total=total,
            page=page,
            limit=limit,
            pages=(total + limit - 1) // limit,
            has_next=page * limit < total,
            has_prev=page > 1
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )

@router.post("/", response_model=UserCreateResponse)
async def create_user(
    user_create: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new user (admin only)"""
    try:
        # Check permissions
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Check if email or employee_id already exists
        existing_user = db.query(User).filter(
            or_(User.email == user_create.email, User.employee_id == user_create.employee_id)
        ).first()
        
        if existing_user:
            if existing_user.email == user_create.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Employee ID already exists"
                )
        
        # Create new user
        user_data = user_create.dict()
        password = user_data.pop("password")
        
        new_user = User(
            **user_data,
            hashed_password=get_password_hash(password)
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"✅ User created by {current_user.email}: {new_user.email}")
        
        return UserCreateResponse(
            success=True,
            message="User created successfully",
            user_id=new_user.id,
            employee_id=new_user.employee_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ User creation error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User creation failed"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user by ID (admin/manager only)"""
    try:
        # Check permissions
        if not current_user.can_view_user(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
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
        logger.error(f"❌ Error getting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user"
        )

@router.put("/{user_id}", response_model=SuccessResponse)
async def update_user(
    user_id: int,
    user_update: AdminUserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user (admin only)"""
    try:
        # Check permissions
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update user
        update_data = user_update.dict(exclude_unset=True)
        
        # Check for email uniqueness
        if "email" in update_data:
            existing_user = db.query(User).filter(
                and_(User.email == update_data["email"], User.id != user_id)
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Check for employee_id uniqueness
        if "employee_id" in update_data:
            existing_user = db.query(User).filter(
                and_(User.employee_id == update_data["employee_id"], User.id != user_id)
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Employee ID already exists"
                )
        
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        logger.info(f"✅ User updated by {current_user.email}: {user.email}")
        
        return SuccessResponse(
            message="User updated successfully",
            data={"user_id": user.id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ User update error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User update failed"
        )

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user (admin only)"""
    try:
        # Check permissions
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Prevent self-deletion
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Soft delete - deactivate instead of hard delete
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"✅ User deactivated by {current_user.email}: {user.email}")
        
        return SuccessResponse(message="User deactivated successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ User deletion error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User deletion failed"
        )

@router.put("/{user_id}/activate", response_model=SuccessResponse)
async def activate_user(
    user_id: int,
    activation: UserActivation,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Activate/deactivate user (admin only)"""
    try:
        # Check permissions
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = activation.is_active
        user.updated_at = datetime.utcnow()
        db.commit()
        
        action = "activated" if activation.is_active else "deactivated"
        logger.info(f"✅ User {action} by {current_user.email}: {user.email}")
        
        return SuccessResponse(message=f"User {action} successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ User activation error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User activation failed"
        )