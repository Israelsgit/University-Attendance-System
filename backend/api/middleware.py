"""
Custom Middleware for AttendanceAI API
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time
import logging
import uuid
from typing import Callable

# Configure logging
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        
        # Start time
        start_time = time.time()
        
        # Log request
        logger.info(
            f"🔄 Request {request_id}: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"✅ Response {request_id}: {response.status_code} "
                f"in {process_time:.3f}s"
            )
            
            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            
            return response
            
        except Exception as e:
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log error
            logger.error(
                f"❌ Error {request_id}: {str(e)} "
                f"in {process_time:.3f}s"
            )
            
            raise

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for security headers"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Remove server header for security
        if "server" in response.headers:
            del response.headers["server"]
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # In production, use Redis
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old entries
        cutoff_time = current_time - self.window_seconds
        self.requests = {
            ip: timestamps for ip, timestamps in self.requests.items()
            if any(ts > cutoff_time for ts in timestamps)
        }
        
        # Update current IP's requests
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove old timestamps for this IP
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip] 
            if ts > cutoff_time
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.max_requests:
            logger.warning(f"🚫 Rate limit exceeded for {client_ip}")
            return Response(
                content='{"error": "Rate limit exceeded"}',
                status_code=429,
                headers={"Content-Type": "application/json"}
            )
        
        # Add current timestamp
        self.requests[client_ip].append(current_time)
        
        return await call_next(request)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"❌ Unhandled error: {str(e)}", exc_info=True)
            
            return Response(
                content='{"error": "Internal server error", "message": "Something went wrong"}',
                status_code=500,
                headers={"Content-Type": "application/json"}
            )

def setup_middleware(app):
    """Setup all middleware for the application"""
    
    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Trusted hosts (in production)
    # app.add_middleware(
    #     TrustedHostMiddleware, 
    #     allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
    # )
    
    # Gzip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Rate limiting (basic implementation)
    app.add_middleware(RateLimitMiddleware, max_requests=1000, window_seconds=60)
    
    # Request logging
    app.add_middleware(LoggingMiddleware)
    
    # Global error handling
    app.add_middleware(ErrorHandlingMiddleware)
    
    logger.info("✅ Middleware setup complete")