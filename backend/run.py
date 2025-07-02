#!/usr/bin/env python3
"""
Application Entry Point
Run this file to start the AttendanceAI API server
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import settings after adding to path
try:
    from config.settings import settings
    from config.database import init_database, create_tables
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

def setup_logging():
    """Setup application logging"""
    import logging
    from pathlib import Path
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(settings.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        "api/app.py",
        "config/settings.py", 
        "config/database.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    return True

def main():
    """Main entry point"""
    print("🚀 Starting AttendanceAI API Server...")
    
    # Setup logging
    setup_logging()
    
    # Check requirements
    if not check_requirements():
        print("❌ Missing required files. Please check your installation.")
        sys.exit(1)
    
    # Create database tables if they don't exist
    try:
        create_tables()
        print("✅ Database tables verified")
    except Exception as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    
    # Initialize database with default data
    try:
        init_database()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️ Database init warning: {e}")
    
    print(f"🌟 Server starting on http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🩺 Health Check: http://{settings.HOST}:{settings.PORT}/health")
    
    # Start the server
    uvicorn.run(
        "api.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )

if __name__ == "__main__":
    main()