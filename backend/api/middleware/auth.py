"""
Authentication Middleware
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from api.utils.security import verify_token
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    """Optional authentication middleware for specific routes"""
    
    def __init__(self, app, protected_paths: list = None):
        super().__init__(app)
        self.protected_paths = protected_paths or []
    
    async def dispatch(self, request: Request, call_next):
        # Check if path requires authentication
        path = request.url.path
        
        if any(path.startswith(protected_path) for protected_path in self.protected_paths):
            # Extract token from header
            authorization = request.headers.get("Authorization")
            
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing or invalid authorization header"
                )
            
            token = authorization.split(" ")[1]
            payload = verify_token(token)
            
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )
            
            # Add user info to request state
            request.state.user_id = payload.get("user_id")
            request.state.user_email = payload.get("sub")
            request.state.user_role = payload.get("role")
        
        response = await call_next(request)
        return response
