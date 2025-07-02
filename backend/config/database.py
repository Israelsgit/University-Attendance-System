"""
Database Configuration and Connection
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config.settings import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

def get_db() -> Session:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all database tables
    """
    try:
        # Import models to register them
        from api.models import user, attendance, leave_request
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        raise

def drop_tables():
    """
    Drop all database tables (use with caution!)
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ Database tables dropped successfully")
    except Exception as e:
        logger.error(f"❌ Error dropping database tables: {e}")
        raise

def init_database():
    """
    Initialize database with default data
    """
    try:
        from api.models.user import User
        from api.utils.security import get_password_hash
        
        db = SessionLocal()
        
        # Check if admin user exists
        admin_user = db.query(User).filter(User.email == "admin@attendanceai.com").first()
        
        if not admin_user:
            # Create default admin user
            admin_user = User(
                name="System Administrator",
                email="admin@attendanceai.com",
                employee_id="ADMIN001",
                department="IT",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_admin=True,
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            logger.info("✅ Default admin user created")
        
        db.close()
        
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise

# Database utilities
class DatabaseManager:
    """Database management utilities"""
    
    @staticmethod
    def backup_database(backup_path: str = None):
        """Backup database"""
        if backup_path is None:
            from datetime import datetime
            backup_path = f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        try:
            import shutil
            if "sqlite" in settings.DATABASE_URL:
                db_path = settings.DATABASE_URL.replace("sqlite:///", "")
                shutil.copy2(db_path, backup_path)
                logger.info(f"✅ Database backed up to {backup_path}")
            else:
                logger.warning("⚠️ Database backup only supported for SQLite")
        except Exception as e:
            logger.error(f"❌ Error backing up database: {e}")
            raise
    
    @staticmethod
    def restore_database(backup_path: str):
        """Restore database from backup"""
        try:
            import shutil
            if "sqlite" in settings.DATABASE_URL:
                db_path = settings.DATABASE_URL.replace("sqlite:///", "")
                shutil.copy2(backup_path, db_path)
                logger.info(f"✅ Database restored from {backup_path}")
            else:
                logger.warning("⚠️ Database restore only supported for SQLite")
        except Exception as e:
            logger.error(f"❌ Error restoring database: {e}")
            raise
    
    @staticmethod
    def get_db_stats():
        """Get database statistics"""
        try:
            db = SessionLocal()
            from api.models.user import User
            from api.models.attendance import AttendanceRecord
            from api.models.leave_request import LeaveRequest
            
            stats = {
                "users": db.query(User).count(),
                "attendance_records": db.query(AttendanceRecord).count(),
                "leave_requests": db.query(LeaveRequest).count(),
            }
            
            db.close()
            return stats
        except Exception as e:
            logger.error(f"❌ Error getting database stats: {e}")
            return {}

# Export commonly used items
__all__ = [
    "engine",
    "SessionLocal", 
    "Base",
    "get_db",
    "create_tables",
    "drop_tables",
    "init_database",
    "DatabaseManager"
]