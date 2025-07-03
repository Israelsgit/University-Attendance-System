"""
Enhanced Database Configuration and Connection for University System
"""

from sqlalchemy import create_engine, MetaData, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
import os
from pathlib import Path
from config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database engine configuration
engine_kwargs = {
    "echo": settings.DB_ECHO,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
}

# SQLite specific configuration
if "sqlite" in settings.DATABASE_URL:
    engine_kwargs.update({
        "connect_args": {
            "check_same_thread": False,
            "timeout": 60
        },
        "poolclass": StaticPool,
    })
# PostgreSQL specific configuration
elif "postgresql" in settings.DATABASE_URL:
    engine_kwargs.update({
        "connect_args": {
            "connect_timeout": 60,
            "options": "-c timezone=UTC"
        }
    })

# Create database engine
try:
    engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
    logger.info(f"Database engine created: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'Local DB'}")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Create base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

def get_db() -> Session:
    """
    Dependency to get database session with proper cleanup
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_tables():
    """
    Create all database tables
    """
    try:
        logger.info("Importing database models...")
        
        # Import all models to register them with SQLAlchemy
        from api.models import user, course, enrollment, class_session, attendance
        
        logger.info("Creating database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Database tables created successfully")
        
        # Verify tables were created
        try:
            with engine.connect() as conn:
                if "sqlite" in settings.DATABASE_URL:
                    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
                    tables = [row[0] for row in result]
                elif "postgresql" in settings.DATABASE_URL:
                    result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public';"))
                    tables = [row[0] for row in result]
                else:
                    tables = ["Tables verification not available"]
                
                logger.info(f"Created tables: {', '.join(tables)}")
        except Exception as e:
            logger.warning(f"Could not verify tables: {e}")
            
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        raise

def drop_tables():
    """
    Drop all database tables (use with caution!)
    """
    try:
        logger.warning("⚠️ Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ Database tables dropped successfully")
    except Exception as e:
        logger.error(f"❌ Error dropping database tables: {e}")
        raise

def init_database():
    """
    Initialize database with default admin user
    """
    try:
        from api.models.user import User, UserRole
        from api.utils.security import get_password_hash
        from datetime import datetime
        
        db = SessionLocal()
        
        try:
            # Check if any users exist
            user_count = db.query(User).count()
            
            if user_count == 0:
                logger.info("Creating default admin user...")
                
                # Create default admin user
                admin_user = User(
                    full_name="System Administrator",
                    email="admin@bowen.edu.ng",
                    staff_id="ADMIN001",
                    hashed_password=get_password_hash("admin123"),
                    university=settings.UNIVERSITY_NAME,
                    college="Administration",
                    department="Information Technology",
                    role=UserRole.ADMIN,
                    employment_date=datetime.now(),
                    is_active=True,
                    is_verified=True,
                    is_face_registered=True
                )
                
                db.add(admin_user)
                db.commit()
                
                logger.info("✅ Default admin user created successfully")
                logger.info("📧 Admin login: admin@bowen.edu.ng / admin123")
            else:
                logger.info(f"ℹ️ Database already has {user_count} users")
                
        except Exception as e:
            logger.error(f"❌ Error creating admin user: {e}")
            db.rollback()
            raise
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

def check_database_connection() -> bool:
    """
    Check if database connection is working
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def get_database_info() -> dict:
    """
    Get database information
    """
    try:
        with engine.connect() as connection:
            # Get database version
            if "postgresql" in settings.DATABASE_URL:
                result = connection.execute(text("SELECT version()"))
                version = result.scalar()
            elif "sqlite" in settings.DATABASE_URL:
                result = connection.execute(text("SELECT sqlite_version()"))
                version = f"SQLite {result.scalar()}"
            else:
                version = "Unknown"
                
            # Get table count
            if "sqlite" in settings.DATABASE_URL:
                result = connection.execute(text("SELECT COUNT(*) FROM sqlite_master WHERE type='table'"))
                table_count = result.scalar()
            elif "postgresql" in settings.DATABASE_URL:
                result = connection.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
                table_count = result.scalar()
            else:
                table_count = 0
                
            return {
                "url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL,
                "version": version,
                "echo": settings.DB_ECHO,
                "table_count": table_count,
                "connection_pool_size": engine.pool.size() if hasattr(engine.pool, 'size') else 'N/A'
            }
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return {"error": str(e)}

def ensure_directories():
    """Ensure required directories exist"""
    directories = [
        "uploads/faces",
        "uploads/documents",
        "models",
        "logs",
        "templates/email",
        "backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directory ensured: {directory}")

def reset_database():
    """Reset database completely (for development only)"""
    if settings.ENVIRONMENT == "production":
        raise Exception("Cannot reset database in production environment")
    
    logger.warning("⚠️ Resetting database...")
    drop_tables()
    create_tables()
    init_database()
    logger.info("✅ Database reset completed")

# Database event listeners
@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    """Configure database connection on connect"""
    if "sqlite" in settings.DATABASE_URL:
        # Enable foreign keys for SQLite
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    logger.debug("Database connection established and configured")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkout from pool"""
    logger.debug("Database connection checked out from pool")

# Initialize directories on import
ensure_directories()

# Test connection on import
if not check_database_connection():
    logger.warning("⚠️ Initial database connection test failed")