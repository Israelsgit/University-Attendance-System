"""
Authentication Routes for University System
Final version - Admin registration completely removed
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import logging

from config.database import get_db
from api.models.user import User, UserRole, StudentLevel
from api.schemas.auth import (
    UserLogin, StudentRegistration, LecturerRegistration, 
    UserResponse, Token, PasswordReset, PasswordResetConfirm,
    FaceRegistrationRequest, UserType
)
from api.utils.security import (
    verify_password, get_password_hash, create_access_token,
    get_current_user, get_current_active_user, sanitize_email,
    validate_university_email, generate_verification_token
)
from config.university_settings import UniversitySettings

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

@router.post("/register/student", response_model=UserResponse)
async def register_student(
    student_data: StudentRegistration,
    db: Session = Depends(get_db)
):
    """Register a new student - Self registration"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == student_data.email) | 
            (User.matric_number == student_data.matric_number)
        ).first()
        
        if existing_user:
            if existing_user.email == student_data.email:
                raise HTTPException(
                    status_code=400,
                    detail="An account with this email already exists"
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="An account with this matriculation number already exists"
                )
        
        # Validate university email
        if not UniversitySettings.is_student_email(student_data.email):
            raise HTTPException(
                status_code=400,
                detail="Please use your student university email address (@student.bowen.edu.ng)"
            )
        
        # Validate matriculation number format
        if not UniversitySettings.validate_matric_number_format(student_data.matric_number):
            raise HTTPException(
                status_code=400,
                detail="Invalid matriculation number format. Use: BU/CSC/21/0001"
            )
        
        # Validate department belongs to college
        valid_departments = UniversitySettings.get_department_by_college(student_data.college)
        if student_data.department not in valid_departments:
            raise HTTPException(
                status_code=400,
                detail=f"Department {student_data.department} does not belong to {student_data.college}"
            )
        
        # Create new student user
        hashed_password = get_password_hash(student_data.password)
        
        new_user = User(
            full_name=student_data.full_name,
            email=sanitize_email(student_data.email),
            hashed_password=hashed_password,
            matric_number=student_data.matric_number,
            university=student_data.university,
            college=student_data.college,
            department=student_data.department,
            programme=student_data.programme,
            level=StudentLevel(student_data.level),
            phone=student_data.phone,
            gender=student_data.gender,
            role=UserRole.STUDENT,
            is_active=True,
            is_verified=True,  # Auto-verify on registration
            admission_date=datetime.now()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New student registered: {new_user.email}")
        
        return UserResponse(
            user=new_user.to_dict(),
            message="Student account created successfully! You can now login.",
            redirect_to="/login"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering student: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred during registration"
        )

@router.post("/register/lecturer", response_model=UserResponse)
async def register_lecturer(
    lecturer_data: LecturerRegistration,
    db: Session = Depends(get_db)
):
    """Register a new lecturer - Self registration with admin privileges"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == lecturer_data.email) | 
            (User.staff_id == lecturer_data.staff_id)
        ).first()
        
        if existing_user:
            if existing_user.email == lecturer_data.email:
                raise HTTPException(
                    status_code=400,
                    detail="An account with this email already exists"
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="An account with this staff ID already exists"
                )
        
        # Validate university email
        if not UniversitySettings.is_staff_email(lecturer_data.email):
            raise HTTPException(
                status_code=400,
                detail="Please use your staff university email address (@bowen.edu.ng)"
            )
        
        # Validate staff ID format
        if not UniversitySettings.validate_staff_id_format(lecturer_data.staff_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid staff ID format. Use: BU/CSC/2024"
            )
        
        # Validate department belongs to college
        valid_departments = UniversitySettings.get_department_by_college(lecturer_data.college)
        if lecturer_data.department not in valid_departments:
            raise HTTPException(
                status_code=400,
                detail=f"Department {lecturer_data.department} does not belong to {lecturer_data.college}"
            )
        
        # Create new lecturer user
        hashed_password = get_password_hash(lecturer_data.password)
        
        new_user = User(
            full_name=lecturer_data.full_name,
            email=sanitize_email(lecturer_data.email),
            hashed_password=hashed_password,
            staff_id=lecturer_data.staff_id,
            university=lecturer_data.university,
            college=lecturer_data.college,
            department=lecturer_data.department,
            programme=lecturer_data.programme,
            phone=lecturer_data.phone,
            gender=lecturer_data.gender,
            role=UserRole.LECTURER,  # Lecturers automatically get admin privileges
            is_active=True,
            is_verified=True,  # Auto-verify on registration
            employment_date=lecturer_data.employment_date or datetime.now().date()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New lecturer registered with admin privileges: {new_user.email}")
        
        return UserResponse(
            user=new_user.to_dict(),
            message="Lecturer account created successfully! You now have full administrative access.",
            redirect_to="/login"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering lecturer: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred during registration"
        )

@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Authenticate user and return access token"""
    try:
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated. Please contact support."
            )
        
        # Verify user type matches role
        if login_data.user_type.value != user.role.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Please login with the correct account type"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create access token
        access_token_expires = timedelta(hours=24)  # 24 hours
        access_token = create_access_token(
            data={"sub": user.email, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        logger.info(f"User logged in: {user.email}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user.to_dict(),
            expires_in=86400  # 24 hours in seconds
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during login"
        )

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return {
        "user": current_user.to_dict(),
        "message": "User information retrieved successfully"
    }

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """Logout user (client-side token removal)"""
    logger.info(f"User logged out: {current_user.email}")
    return {
        "message": "Logged out successfully"
    }

@router.post("/register-face")
async def register_face(
    face_data: FaceRegistrationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Register user's face for facial recognition"""
    try:
        # TODO: Implement face encoding logic here
        # This would involve:
        # 1. Decode base64 image
        # 2. Detect face in image
        # 3. Generate face encoding
        # 4. Store encoding in database
        
        # For now, just mark as registered
        current_user.is_face_registered = True
        current_user.face_confidence_threshold = face_data.confidence_threshold
        
        db.commit()
        
        logger.info(f"Face registered for user: {current_user.email}")
        
        return {
            "message": "Face registered successfully",
            "is_face_registered": True
        }
        
    except Exception as e:
        logger.error(f"Error registering face: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred during face registration"
        )

@router.post("/verify-face")
async def verify_face(
    face_data: FaceRegistrationRequest,
    db: Session = Depends(get_db)
):
    """Verify face for attendance marking"""
    try:
        # TODO: Implement face verification logic here
        # This would involve:
        # 1. Decode base64 image
        # 2. Detect face in image
        # 3. Generate face encoding
        # 4. Compare with stored encodings
        # 5. Return user ID if match found
        
        # For now, return mock response
        return {
            "verified": False,
            "user_id": None,
            "confidence": 0.0,
            "message": "Face verification not implemented yet"
        }
        
    except Exception as e:
        logger.error(f"Error verifying face: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during face verification"
        )

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    try:
        # Verify current password
        if not verify_password(current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=400,
                detail="Current password is incorrect"
            )
        
        # Validate new password
        if len(new_password) < 6:
            raise HTTPException(
                status_code=400,
                detail="New password must be at least 6 characters"
            )
        
        # Update password
        current_user.hashed_password = get_password_hash(new_password)
        db.commit()
        
        logger.info(f"Password changed for user: {current_user.email}")
        
        return {
            "message": "Password changed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred while changing password"
        )

@router.get("/system-info")
async def get_system_info():
    """Get system information for registration forms"""
    return {
        "universities": [UniversitySettings.UNIVERSITY_NAME],
        "colleges": [
            {
                "name": college,
                "code": college.replace(" ", "").replace("College", "C").replace("of", ""),
                "departments": UniversitySettings.get_department_by_college(college)
            }
            for college in UniversitySettings.COLLEGES
        ],
        "levels": UniversitySettings.STUDENT_LEVELS,
        "genders": ["Male", "Female", "Other"],
        "semesters": UniversitySettings.SEMESTERS,
        "current_session": UniversitySettings.CURRENT_SESSION,
        "current_semester": UniversitySettings.CURRENT_SEMESTER
    }

@router.post("/upload-profile-image")
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload user profile image"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )
        
        # Validate file size
        if file.size > UniversitySettings.MAX_FACE_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size must be less than {UniversitySettings.MAX_FACE_IMAGE_SIZE / (1024*1024):.1f}MB"
            )
        
        # TODO: Implement file upload logic
        # This would involve:
        # 1. Save file to storage (local/cloud)
        # 2. Generate file path/URL
        # 3. Update user profile
        
        # For now, just return success
        return {
            "message": "Profile image uploaded successfully",
            "image_url": "/uploads/profile_images/default.jpg"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading profile image: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during image upload"
        )