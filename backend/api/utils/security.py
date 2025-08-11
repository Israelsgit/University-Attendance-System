"""
Enhanced Security utilities for University System
Cleaned version with admin role completely removed
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from config.database import get_db
from api.models.user import User, UserRole
from config.settings import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Security
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=getattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES', 1440))
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, getattr(settings, 'SECRET_KEY', 'your-secret-key'), 
                            algorithm=getattr(settings, 'ALGORITHM', 'HS256'))
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, getattr(settings, 'SECRET_KEY', 'your-secret-key'), 
                           algorithms=[getattr(settings, 'ALGORITHM', 'HS256')])
        return payload
    except JWTError:
        return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, getattr(settings, 'SECRET_KEY', 'your-secret-key'), 
                           algorithms=[getattr(settings, 'ALGORITHM', 'HS256')])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_lecturer(current_user: User = Depends(get_current_active_user)) -> User:
    """Get current lecturer user (has administrative privileges)"""
    if current_user.role != UserRole.LECTURER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Lecturer privileges required"
        )
    return current_user

async def get_current_student(current_user: User = Depends(get_current_active_user)) -> User:
    """Get current student user"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access only"
        )
    return current_user

def check_permissions(required_role: str):
    """Decorator factory for checking user permissions"""
    def permission_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if required_role == "lecturer" and current_user.role != UserRole.LECTURER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Lecturer privileges required"
            )
        elif required_role == "student" and current_user.role != UserRole.STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Student access only"
            )
        return current_user
    return permission_checker

def has_permission(user: User, permission: str) -> bool:
    """Check if user has specific permission"""
    from config.university_settings import UniversitySettings
    
    user_permissions = UniversitySettings.get_user_permissions(user.role.value)
    return permission in user_permissions

def generate_verification_token(email: str) -> str:
    """Generate email verification token"""
    data = {
        "sub": email,
        "type": "email_verification",
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(data, getattr(settings, 'SECRET_KEY', 'your-secret-key'), 
                     algorithm=getattr(settings, 'ALGORITHM', 'HS256'))

def verify_verification_token(token: str) -> Optional[str]:
    """Verify email verification token and return email"""
    try:
        payload = jwt.decode(token, getattr(settings, 'SECRET_KEY', 'your-secret-key'), 
                           algorithms=[getattr(settings, 'ALGORITHM', 'HS256')])
        if payload.get("type") != "email_verification":
            return None
        return payload.get("sub")
    except JWTError:
        return None

def generate_password_reset_token(email: str) -> str:
    """Generate password reset token"""
    data = {
        "sub": email,
        "type": "password_reset",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(data, getattr(settings, 'SECRET_KEY', 'your-secret-key'), 
                     algorithm=getattr(settings, 'ALGORITHM', 'HS256'))

def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify password reset token and return email"""
    try:
        payload = jwt.decode(token, getattr(settings, 'SECRET_KEY', 'your-secret-key'), 
                           algorithms=[getattr(settings, 'ALGORITHM', 'HS256')])
        if payload.get("type") != "password_reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None

def check_rate_limit(user_id: int, action: str, limit: int = 5, window: int = 300) -> bool:
    """Basic rate limiting check (implement with Redis for production)"""
    # For now, always return True - implement with Redis/cache for production
    return True

def log_security_event(user_id: Optional[int], event: str, details: dict = None):
    """Log security events for audit trail"""
    # Implement logging to database or external service
    print(f"Security Event: {event} for user {user_id}: {details}")

def sanitize_email(email: str) -> str:
    """Sanitize and normalize email address"""
    return email.lower().strip()

def validate_university_email(email: str) -> bool:
    """Validate university email domain"""
    from config.university_settings import UniversitySettings
    return UniversitySettings.is_valid_email_domain(email)

def generate_user_id(role: UserRole, department: str = None) -> str:
    """Generate user ID based on role and department"""
    from config.university_settings import UniversitySettings
    
    if role == UserRole.LECTURER:
        return UniversitySettings.generate_staff_id(department or "GEN")
    elif role == UserRole.STUDENT:
        return UniversitySettings.generate_student_id(department or "GEN")
    return f"USER{datetime.now().year}{datetime.now().month:02d}{datetime.now().day:02d}"