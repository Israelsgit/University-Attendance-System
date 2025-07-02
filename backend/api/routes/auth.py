"""
Authentication Routes
Handles user authentication, registration, and profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import logging

from config.database import get_db
from api.models.user import User
from api.schemas.auth import (
    UserLogin, UserRegister, UserResponse, TokenResponse, 
    UserUpdate, ChangePassword, ProfileImageResponse
)
from api.utils.security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, verify_token, get_current_user
)
from services.face_recognition import face_recognition_service
from config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    employee_id: str = Form(...),
    department: str = Form(...),
    position: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Register a new user
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == email) | (User.employee_id == employee_id)
        ).first()
        
        if existing_user:
            if existing_user.email == email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Employee ID already exists"
                )
        
        # Hash password
        hashed_password = get_password_hash(password)
        
        # Create user
        user = User(
            name=name,
            email=email,
            employee_id=employee_id,
            department=department,
            position=position,
            phone=phone,
            hashed_password=hashed_password,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # Handle profile image upload
        if profile_image:
            if profile_image.content_type not in settings.ALLOWED_IMAGE_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid image format"
                )
            
            if profile_image.size > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Image file too large"
                )
            
            # Save profile image
            import os
            from pathlib import Path
            
            upload_dir = Path(settings.UPLOAD_DIR) / "profiles"
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            file_extension = profile_image.filename.split('.')[-1]
            filename = f"{employee_id}_{datetime.now().timestamp()}.{file_extension}"
            file_path = upload_dir / filename
            
            with open(file_path, "wb") as buffer:
                content = await profile_image.read()
                buffer.write(content)
            
            user.profile_image = str(file_path)
        
        # Save user to database
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create tokens
        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        refresh_token = create_refresh_token(data={"sub": user.email, "user_id": user.id})
        
        logger.info(f"✅ User registered successfully: {user.email}")
        
        return {
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Registration error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login user with email and password
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == user_credentials.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(user_credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create tokens
        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        refresh_token = create_refresh_token(data={"sub": user.email, "user_id": user.id})
        
        logger.info(f"✅ User logged in successfully: {user.email}")
        
        return {
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    try:
        # Verify refresh token
        payload = verify_token(credentials.credentials)
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        refresh_token = create_refresh_token(data={"sub": user.email, "user_id": user.id})
        
        return {
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    """
    return {"user": current_user.to_dict(include_sensitive=True)}

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile
    """
    try:
        # Update user fields
        update_data = profile_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)
        
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"✅ Profile updated for user: {current_user.email}")
        
        return {"user": current_user.to_dict()}
        
    except Exception as e:
        logger.error(f"❌ Profile update error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )

@router.post("/profile/image", response_model=ProfileImageResponse)
async def upload_profile_image(
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and update profile image
    """
    try:
        # Validate image
        if image.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image format"
            )
        
        if image.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image file too large"
            )
        
        # Save image
        import os
        from pathlib import Path
        
        upload_dir = Path(settings.UPLOAD_DIR) / "profiles"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_extension = image.filename.split('.')[-1]
        filename = f"{current_user.employee_id}_{datetime.now().timestamp()}.{file_extension}"
        file_path = upload_dir / filename
        
        with open(file_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        
        # Update user profile
        current_user.profile_image = str(file_path)
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"✅ Profile image updated for user: {current_user.email}")
        
        return {
            "message": "Profile image updated successfully",
            "image_url": str(file_path),
            "user": current_user.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Image upload error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image upload failed"
        )

@router.put("/password")
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    """
    try:
        # Verify current password
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        new_hashed_password = get_password_hash(password_data.new_password)
        
        # Update password
        current_user.hashed_password = new_hashed_password
        current_user.last_password_change = datetime.utcnow()
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"✅ Password changed for user: {current_user.email}")
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Password change error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

@router.post("/face-encoding")
async def save_face_encoding(
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save face encoding for user
    """
    try:
        # Validate image
        if image.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image format"
            )
        
        # Read image data
        image_data = await image.read()
        
        # Process face encoding
        result = face_recognition_service.save_face_encoding(current_user.id, image_data)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        # Update user record
        current_user.face_encoding = result["face_encoding"]
        current_user.face_image_path = result["face_image_path"]
        current_user.face_confidence_threshold = result["confidence_threshold"]
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"✅ Face encoding saved for user: {current_user.email}")
        
        return {
            "message": "Face encoding saved successfully",
            "confidence_threshold": result["confidence_threshold"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Face encoding error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Face encoding failed"
        )

@router.post("/logout")
async def logout_user(
    current_user: User = Depends(get_current_user)
):
    """
    Logout user (invalidate token)
    """
    # In a production environment, you would add the token to a blacklist
    # For now, we'll just return a success message
    logger.info(f"✅ User logged out: {current_user.email}")
    
    return {"message": "Logged out successfully"}

@router.delete("/account")
async def delete_account(
    password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user account (soft delete)
    """
    try:
        # Verify password
        if not verify_password(password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is incorrect"
            )
        
        # Soft delete (deactivate account)
        current_user.is_active = False
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"✅ Account deactivated for user: {current_user.email}")
        
        return {"message": "Account deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Account deletion error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion failed"
        )