"""
Enhanced FastAPI Application for University Attendance System
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
import logging
from pathlib import Path

# Import route modules - fallback to local routes if modules don't exist
try:
    from api.routes import auth, attendance, courses, analytics, users
    HAS_ALL_ROUTES = True
except ImportError:
    # Use the auth routes we've created
    from api.routes import auth
    HAS_ALL_ROUTES = False
    logging.warning("Some route modules not found. Using basic auth routes only.")

# Import configuration
try:
    from api.middleware import setup_middleware
    HAS_MIDDLEWARE_SETUP = True
except ImportError:
    HAS_MIDDLEWARE_SETUP = False
    logging.warning("Middleware setup module not found. Using basic middleware.")

try:
    from config.database import create_tables, check_database_connection, init_database
    from config.settings import settings
    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False
    logging.error("Database modules not found. Creating minimal settings.")
    
    # Minimal settings fallback
    class Settings:
        UNIVERSITY_NAME = "Bowen University"
        VERSION = "1.0.0"
        DEBUG = True
        ENVIRONMENT = "development"
        LOG_LEVEL = "INFO"
        LOG_FILE = "logs/app.log"
        API_HOST = "0.0.0.0"
        API_PORT = 8000
        API_V1_STR = "/api"
        WORKERS = 1
    
    settings = Settings()

try:
    from services.face_recognition import face_recognition_service
    HAS_FACE_RECOGNITION = True
except ImportError:
    HAS_FACE_RECOGNITION = False
    logging.warning("Face recognition service not found.")

# Configure logging
logging.basicConfig(
    level=getattr(logging, getattr(settings, 'LOG_LEVEL', 'INFO')),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(getattr(settings, 'LOG_FILE', 'app.log')) 
        if os.path.dirname(getattr(settings, 'LOG_FILE', '')) and 
           os.path.exists(os.path.dirname(getattr(settings, 'LOG_FILE', ''))) 
        else logging.StreamHandler(),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting University Attendance System API...")
    
    # Create upload directories
    upload_dirs = ["uploads/faces", "uploads/documents", "models", "logs"]
    for dir_path in upload_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created directory: {dir_path}")
    
    # Initialize database if available
    if HAS_DATABASE:
        try:
            # Check database connection
            if check_database_connection():
                logger.info("✅ Database connection successful")
                
                # Create tables
                create_tables()
                logger.info("✅ Database tables created/verified")
                
                # Initialize with default data
                init_database()
                logger.info("✅ Database initialized with default data")
            else:
                logger.error("❌ Database connection failed")
        except Exception as e:
            logger.error(f"❌ Database error: {e}")
            # Don't raise - let the app start without database for development
    else:
        logger.warning("⚠️ Database modules not available - running without database")
    
    # Initialize face recognition service if available
    if HAS_FACE_RECOGNITION:
        try:
            await face_recognition_service.initialize()
            logger.info("✅ Face recognition service initialized")
        except Exception as e:
            logger.warning(f"⚠️ Face recognition service warning: {e}")
    else:
        logger.warning("⚠️ Face recognition service not available")
    
    logger.info(f"✅ {getattr(settings, 'UNIVERSITY_NAME', 'University')} Attendance System started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down University Attendance System...")

# Create FastAPI app
app = FastAPI(
    title=f"{getattr(settings, 'UNIVERSITY_NAME', 'University')} Attendance API",
    description="University Facial Recognition Attendance Management System",
    version=getattr(settings, 'VERSION', '1.0.0'),
    docs_url="/docs" if getattr(settings, 'DEBUG', True) else None,
    redoc_url="/redoc" if getattr(settings, 'DEBUG', True) else None,
    lifespan=lifespan
)

# CORS Configuration - CRITICAL FOR FRONTEND
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",  # Vite development server
        "http://127.0.0.1:5173",
        "https://*.bowen.edu.ng",  # Production domains
        "*"  # Allow all origins in development (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language", 
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
        "X-CSRF-Token",
        "X-Forwarded-For",
        "X-Forwarded-Proto",
    ],
    expose_headers=["*"],
    max_age=3600,
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.bowen.edu.ng", "*"]  # Allow all in development
)

# Setup additional middleware if available
if HAS_MIDDLEWARE_SETUP:
    try:
        setup_middleware(app)
        logger.info("✅ Additional middleware configured")
    except Exception as e:
        logger.warning(f"⚠️ Additional middleware setup failed: {e}")

# Static files
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    logger.info("✅ Static files mounted at /uploads")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc) if getattr(settings, 'DEBUG', True) else "Something went wrong"
        }
    )

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    db_status = "unknown"
    if HAS_DATABASE:
        try:
            db_status = "connected" if check_database_connection() else "disconnected"
        except:
            db_status = "error"
    
    return {
        "status": "healthy",
        "message": f"{getattr(settings, 'UNIVERSITY_NAME', 'University')} Attendance API is running",
        "version": getattr(settings, 'VERSION', '1.0.0'),
        "university": getattr(settings, 'UNIVERSITY_NAME', 'University'),
        "environment": getattr(settings, 'ENVIRONMENT', 'development'),
        "database": db_status,
        "face_recognition": "available" if HAS_FACE_RECOGNITION else "unavailable",
        "timestamp": "2024-01-01T00:00:00Z"  # You can use datetime.now().isoformat()
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {getattr(settings, 'UNIVERSITY_NAME', 'University')} Attendance System",
        "version": getattr(settings, 'VERSION', '1.0.0'),
        "docs": "/docs" if getattr(settings, 'DEBUG', True) else "Documentation not available in production",
        "health": "/health",
        "api": getattr(settings, 'API_V1_STR', '/api')
    }

# API prefix
API_PREFIX = getattr(settings, 'API_V1_STR', '/api')

# Include auth router (always available)
app.include_router(auth.router, prefix=f"{API_PREFIX}/auth", tags=["Authentication"])
logger.info("✅ Auth routes included")

# Include other routers if available
if HAS_ALL_ROUTES:
    try:
        app.include_router(courses.router, prefix=f"{API_PREFIX}/courses", tags=["Courses"])
        logger.info("✅ Courses routes included")
    except Exception as e:
        logger.warning(f"⚠️ Failed to include courses routes: {e}")
    
    try:
        app.include_router(attendance.router, prefix=f"{API_PREFIX}/attendance", tags=["Attendance"])
        logger.info("✅ Attendance routes included")
    except Exception as e:
        logger.warning(f"⚠️ Failed to include attendance routes: {e}")
    
    try:
        app.include_router(analytics.router, prefix=f"{API_PREFIX}/analytics", tags=["Analytics"])
        logger.info("✅ Analytics routes included")
    except Exception as e:
        logger.warning(f"⚠️ Failed to include analytics routes: {e}")
    
    try:
        app.include_router(users.router, prefix=f"{API_PREFIX}/users", tags=["Users"])
        logger.info("✅ Users routes included")
    except Exception as e:
        logger.warning(f"⚠️ Failed to include users routes: {e}")
else:
    logger.warning("⚠️ Some route modules not available - running with auth routes only")

# Additional error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": "Endpoint not found", 
            "error": "The requested resource does not exist",
            "path": str(request.url.path)
        }
    )

@app.exception_handler(405)
async def method_not_allowed_handler(request, exc):
    return JSONResponse(
        status_code=405,
        content={
            "success": False,
            "message": "Method not allowed",
            "error": f"Method {request.method} not allowed for {request.url.path}"
        }
    )

@app.exception_handler(422)
async def validation_error_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "error": "Please check your request data",
            "details": exc.detail if hasattr(exc, 'detail') else None
        }
    )

# CORS preflight handler for all routes
@app.options("/{rest_of_path:path}")
async def preflight_handler(request, rest_of_path: str):
    """Handle CORS preflight requests"""
    response = JSONResponse(content={"message": "OK"})
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response

# Development endpoints (only in debug mode)
if getattr(settings, 'DEBUG', True):
    @app.get("/debug/routes")
    async def debug_routes():
        """Debug endpoint to list all routes"""
        routes = []
        for route in app.routes:
            if hasattr(route, 'methods'):
                routes.append({
                    "path": route.path,
                    "methods": list(route.methods),
                    "name": route.name
                })
        return {"routes": routes}
    
    @app.get("/debug/settings")
    async def debug_settings():
        """Debug endpoint to show current settings"""
        return {
            "university": getattr(settings, 'UNIVERSITY_NAME', 'Not set'),
            "version": getattr(settings, 'VERSION', 'Not set'),
            "environment": getattr(settings, 'ENVIRONMENT', 'Not set'),
            "debug": getattr(settings, 'DEBUG', 'Not set'),
            "api_prefix": API_PREFIX,
            "has_database": HAS_DATABASE,
            "has_face_recognition": HAS_FACE_RECOGNITION,
            "has_all_routes": HAS_ALL_ROUTES
        }

if __name__ == "__main__":
    # Run the application
    host = getattr(settings, 'API_HOST', '0.0.0.0')
    port = getattr(settings, 'API_PORT', 8000)
    debug = getattr(settings, 'DEBUG', True)
    workers = getattr(settings, 'WORKERS', 1) if not debug else 1
    
    logger.info(f"🚀 Starting server on {host}:{port}")
    logger.info(f"📊 Debug mode: {debug}")
    logger.info(f"👥 Workers: {workers}")
    logger.info(f"📚 Documentation: http://{host}:{port}/docs")
    logger.info(f"❤️ Health check: http://{host}:{port}/health")
    
    uvicorn.run(
        "app:app",  # Changed from "api.app:app" to "app:app"
        host=host,
        port=port,
        reload=debug,
        workers=workers,
        log_level=getattr(settings, 'LOG_LEVEL', 'INFO').lower(),
        access_log=True,
        use_colors=True
    )