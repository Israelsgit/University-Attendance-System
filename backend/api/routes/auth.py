"""
Enhanced Authentication Routes for University System
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import logging
import json

from config.database import get_db
from api.models.user import User, UserRole, StudentLevel
from api.utils.security import (
    get_password_hash, verify_password, create_access_token,
    get_current_user
)

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

class AuthResponse:
    """Helper class for consistent auth responses"""
    
    @staticmethod
    def success(data, message="Success"):
        return {
            "success": True,
            "message": message,
            **data
        }
    
    @staticmethod
    def error(message, status_code=400, details=None):
        response = {
            "success": False,
            "message": message
        }
        if details:
            response["details"] = details
        return response

@router.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    user_type: str = Form(...),
    db: Session = Depends(get_db)
):
    """Login endpoint for all user types"""
    try:
        logger.info(f"Login attempt: email={email}, user_type={user_type}")
        
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            logger.warning(f"Login failed: User not found for email {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AuthResponse.error("Invalid email or password")
            )
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Login failed: Invalid password for {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AuthResponse.error("Invalid email or password")
            )
        
        # Check if user type matches
        if user.role.value != user_type:
            logger.warning(f"Login failed: Role mismatch for {email}. Expected {user_type}, got {user.role.value}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AuthResponse.error("Invalid account type selected")
            )
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login failed: Inactive account for {email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=AuthResponse.error("Account is deactivated. Contact administrator.")
            )
        
        # Update last login
        user.last_login = datetime.now()
        db.commit()
        
        # Create access token
        token_data = {
            "sub": user.email,
            "user_id": user.id,
            "role": user.role.value
        }
        access_token = create_access_token(data=token_data)
        
        logger.info(f"Login successful: {email} as {user.role.value}")
        
        return AuthResponse.success({
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.to_dict()
        }, f"Welcome back, {user.full_name}!")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=AuthResponse.error("Internal server error")
        )

@router.post("/register")
async def register_student(
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    phone: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    date_of_birth: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    college: str = Form(...),
    department: str = Form(...),
    programme: str = Form(...),
    level: str = Form(...),
    matric_number: Optional[str] = Form(None),
    university: str = Form("Bowen University"),
    role: str = Form("student"),
    profileImage: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Register new student"""
    try:
        logger.info(f"Registration attempt: {email} - {full_name}")
        
        # Check if email already exists
        if db.query(User).filter(User.email == email).first():
            logger.warning(f"Registration failed: Email {email} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AuthResponse.error("Email already registered")
            )
        
        # Check if matric number exists (if provided)
        if matric_number and db.query(User).filter(User.matric_number == matric_number).first():
            logger.warning(f"Registration failed: Matric number {matric_number} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AuthResponse.error("Matric number already exists")
            )
        
        # Generate matric number if not provided
        if not matric_number:
            # Auto-generate based on department and year
            dept_codes = {
                "Computer Science": "CSC",
                "Information Technology": "IFT",
                "Cyber Security": "CYS",
                "Software Engineering": "SWE",
                # Add more mappings as needed
            }
            dept_code = dept_codes.get(department, "GEN")
            current_year = datetime.now().year
            year_code = str(current_year)[2:]
            
            # Find next available number
            prefix = f"BU/{dept_code}/{year_code}/"
            existing_count = db.query(User).filter(
                User.matric_number.like(f"{prefix}%")
            ).count()
            next_number = str(existing_count + 1).zfill(4)
            matric_number = f"{prefix}{next_number}"
        
        # Parse date of birth if provided
        parsed_dob = None
        if date_of_birth:
            try:
                parsed_dob = datetime.strptime(date_of_birth, "%Y-%m-%d")
            except ValueError:
                logger.warning(f"Invalid date format: {date_of_birth}")
        
        # Handle profile image upload
        profile_image_path = None
        if profileImage:
            # Here you would implement file upload logic
            # For now, we'll just log it
            logger.info(f"Profile image uploaded: {profileImage.filename}")
        
        # Create student user
        student = User(
            full_name=full_name,
            email=email,
            matric_number=matric_number,
            hashed_password=get_password_hash(password),
            university=university,
            college=college,
            department=department,
            programme=programme,
            level=StudentLevel(level),
            phone=phone,
            gender=gender,
            date_of_birth=parsed_dob,
            address=address,
            profile_image=profile_image_path,
            role=UserRole.STUDENT,
            admission_date=datetime.now(),
            is_active=True,
            is_verified=False  # Students need face registration
        )
        
        db.add(student)
        db.commit()
        db.refresh(student)
        
        logger.info(f"Student registered successfully: {email} - {matric_number}")
        
        return AuthResponse.success({
            "user": student.to_dict()
        }, "Registration successful! Please visit your lecturer to register your face for attendance tracking.")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=AuthResponse.error("Registration failed. Please try again.")
        )

@router.post("/register/lecturer")
async def register_lecturer(
    full_name: str = Form(...),
    email: str = Form(...),
    staff_id: str = Form(...),
    password: str = Form(...),
    college: str = Form(...),
    department: str = Form(...),
    programme: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    university: str = Form("Bowen University"),
    current_admin: User = Depends(get_current_user),  # Only admins can create lecturers
    db: Session = Depends(get_db)
):
    """Register new lecturer (admin only)"""
    try:
        # Check if current user is admin
        if current_admin.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=AuthResponse.error("Only administrators can register lecturers")
            )
        
        logger.info(f"Lecturer registration by admin {current_admin.email}: {email}")
        
        # Check if email already exists
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AuthResponse.error("Email already registered")
            )
        
        # Check if staff ID already exists
        if db.query(User).filter(User.staff_id == staff_id).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AuthResponse.error("Staff ID already exists")
            )
        
        # Create lecturer user
        lecturer = User(
            full_name=full_name,
            email=email,
            staff_id=staff_id,
            hashed_password=get_password_hash(password),
            university=university,
            college=college,
            department=department,
            programme=programme,
            phone=phone,
            gender=gender,
            role=UserRole.LECTURER,
            employment_date=datetime.now(),
            is_active=True,
            is_verified=True,
            is_face_registered=True  # Lecturers don't need face registration for now
        )
        
        db.add(lecturer)
        db.commit()
        db.refresh(lecturer)
        
        logger.info(f"Lecturer registered successfully: {email}")
        
        return AuthResponse.success({
            "user": lecturer.to_dict()
        }, "Lecturer registered successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lecturer registration error: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=AuthResponse.error("Registration failed")
        )

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    try:
        logger.info(f"Fetching user info for: {current_user.email}")
        
        # Refresh user data from database
        fresh_user = db.query(User).filter(User.id == current_user.id).first()
        
        if not fresh_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=AuthResponse.error("User not found")
            )
        
        return AuthResponse.success({
            "user": fresh_user.to_dict()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user info error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=AuthResponse.error("Failed to fetch user information")
        )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout user"""
    try:
        logger.info(f"User logout: {current_user.email}")
        
        # In a more complex system, you would invalidate the JWT token here
        # For now, we just return success and let the frontend clear the token
        
        return AuthResponse.success({}, "Logged out successfully")
        
    except Exception as e:
        logger.error(f"Logout error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=AuthResponse.error("Logout failed")
        )

@router.post("/face-registration")
async def register_face(
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register face encoding for a user"""
    try:
        logger.info(f"Face registration for user: {current_user.email}")
        
        if current_user.is_face_registered:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AuthResponse.error("Face already registered. Contact lecturer to re-register.")
            )
        
        # Validate image file
        if not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AuthResponse.error("Please upload a valid image file")
            )
        
        if image.size > 5 * 1024 * 1024:  # 5MB limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AuthResponse.error("Image file too large. Maximum size is 5MB")
            )
        
        # Read image data
        image_data = await image.read()
        
        # Process face registration (you'll need to implement face_recognition_service)
        try:
            # For now, we'll simulate successful face registration
            # In production, implement actual face recognition here
            
            # Simulate face encoding
            face_encoding = "simulated_face_encoding_data"
            confidence = 0.95
            
            # Update user with face registration
            current_user.face_encoding = face_encoding
            current_user.is_face_registered = True
            current_user.is_verified = True
            
            db.commit()
            
            logger.info(f"Face registered successfully for: {current_user.email}")
            
            return AuthResponse.success({
                "confidence": confidence,
                "user": current_user.to_dict()
            }, "Face registered successfully")
            
        except Exception as face_error:
            logger.error(f"Face processing error: {face_error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AuthResponse.error("Face registration failed. Please ensure your face is clearly visible.")
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Face registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=AuthResponse.error("Face registration failed")
        )

@router.put("/profile")
async def update_profile(
    full_name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    profileImage: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    try:
        logger.info(f"Profile update for: {current_user.email}")
        
        # Update fields if provided
        if full_name:
            current_user.full_name = full_name
        if phone:
            current_user.phone = phone
        if address:
            current_user.address = address
        
        # Handle profile image update
        if profileImage:
            # Validate image
            if not profileImage.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=AuthResponse.error("Please upload a valid image file")
                )
            
            # Here you would implement image upload and storage
            # For now, just log it
            logger.info(f"Profile image updated: {profileImage.filename}")
        
        current_user.updated_at = datetime.now()
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"Profile updated successfully for: {current_user.email}")
        
        return AuthResponse.success({
            "user": current_user.to_dict()
        }, "Profile updated successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=AuthResponse.error("Profile update failed")
        )

@router.put("/password")
async def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    try:
        logger.info(f"Password change for: {current_user.email}")
        
        # Verify current password
        if not verify_password(current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AuthResponse.error("Current password is incorrect")
            )
        
        # Validate new password
        if len(new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AuthResponse.error("New password must be at least 6 characters long")
            )
        
        # Update password
        current_user.hashed_password = get_password_hash(new_password)
        current_user.updated_at = datetime.now()
        db.commit()
        
        logger.info(f"Password changed successfully for: {current_user.email}")
        
        return AuthResponse.success({}, "Password changed successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=AuthResponse.error("Password change failed")
        )

# Health check endpoint for auth routes
@router.get("/health")
async def auth_health_check():
    """Health check for auth routes"""
    return {
        "status": "healthy",
        "service": "authentication",
        "timestamp": datetime.now().isoformat()
    }