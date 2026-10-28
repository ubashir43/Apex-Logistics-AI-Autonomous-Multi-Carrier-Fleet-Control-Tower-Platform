"""
PostgreSQL Database Configuration
Production-ready database with connection pooling
Maintains SQLite fallback for development
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import logging

logger = logging.getLogger(__name__)

# Get database URL from environment or use SQLite as fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")

# Determine if using PostgreSQL
IS_POSTGRES = DATABASE_URL.startswith("postgresql")

# Ensure canonical SQLite path regardless of whether started from repo root or backend/
if not IS_POSTGRES and (DATABASE_URL == "sqlite:///./data/app.db" or "data/app.db" in DATABASE_URL):
    if os.path.exists("./data/app.db"):
        DATABASE_URL = f"sqlite:///{os.path.abspath('./data/app.db')}"
    elif os.path.exists("../data/app.db"):
        DATABASE_URL = f"sqlite:///{os.path.abspath('../data/app.db')}"
    elif os.path.exists("backend/data/app.db"):
        DATABASE_URL = f"sqlite:///{os.path.abspath('backend/data/app.db')}"
    else:
        os.makedirs("./data", exist_ok=True)
        DATABASE_URL = f"sqlite:///{os.path.abspath('./data/app.db')}"

# Engine configuration
engine_kwargs = {
    "echo": False,  # Set to True for SQL logging
}

if IS_POSTGRES:
    # PostgreSQL production configuration
    engine_kwargs.update({
        "poolclass": QueuePool,
        "pool_size": 20,  # Number of permanent connections
        "max_overflow": 10,  # Additional connections when pool is full
        "pool_timeout": 30,  # Seconds to wait for connection
        "pool_recycle": 3600,  # Recycle connections every hour
        "pool_pre_ping": True,  # Test connections before use
    })
    logger.info("🐘 Using PostgreSQL database (production mode)")
else:
    # SQLite development configuration
    engine_kwargs.update({
        "connect_args": {"check_same_thread": False}
    })
    logger.info("📁 Using SQLite database (development mode)")

# Ensure SQLite directory exists if using relative path
if not IS_POSTGRES and "sqlite:///" in DATABASE_URL:
    try:
        db_path = DATABASE_URL.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    except Exception:
        pass

# Create engine
engine = create_engine(DATABASE_URL, **engine_kwargs)

if not IS_POSTGRES:
    from sqlalchemy import event
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()
        except Exception:
            pass


# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model class
Base = declarative_base()


# Dependency for FastAPI
def get_db():
    """
    Get database session for FastAPI dependency injection
    
    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database health check
def check_database_health() -> dict:
    """
    Check database connection health
    
    Returns:
        dict with status, database_type, and connection info
    """
    try:
        # Try to connect
        connection = engine.connect()
        connection.close()
        
        return {
            "status": "healthy",
            "database_type": "postgresql" if IS_POSTGRES else "sqlite",
            "url": DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else "local",
            "pool_size": engine.pool.size() if IS_POSTGRES else "N/A",
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "database_type": "postgresql" if IS_POSTGRES else "sqlite",
        }


# Initialize database tables
def init_database():
    """
    Create all database tables
    Should be called on application startup
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
