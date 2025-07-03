
"""
Logging Middleware
"""

import time
import uuid
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Log HTTP requests and responses"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Log request
        start_time = time.time()
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response {request_id}: {response.status_code} "
            f"({process_time:.3f}s)"
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response

def setup_logging(app: FastAPI):
    """Setup logging middleware"""
    app.add_middleware(LoggingMiddleware)