import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import logging

# Database configuration - PostgreSQL only
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'face_tracking'),
    'username': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password')
}

# PostgreSQL connection URL
DATABASE_URL = f"postgresql://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"

# Create PostgreSQL engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Set to True for SQL query logging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

def get_db_session(database_url: str = None):
    """
    Get a database session.
    Args:
        database_url: Optional database URL override
    Returns:
        Database session
    """
    if database_url and database_url != DATABASE_URL:
        # Create temporary engine for different URL
        temp_engine = create_engine(database_url)
        temp_session = sessionmaker(autocommit=False, autoflush=False, bind=temp_engine)
        return temp_session()
    
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

def close_db_session(db):
    """
    Close database session safely.
    Args:
        db: Database session to close
    """
    try:
        db.close()
    except Exception as e:
        logging.error(f"Error closing database session: {e}")

def create_tables():
    """
    Create all database tables.
    This function creates all tables defined in the models.
    """
    try:
        # Import models to ensure they're registered with Base
        from db.db_models import (
            User, Employee, FaceEmbedding, AttendanceRecord, 
            TrackingRecord, CameraConfig, SystemLog
        )
        
        # Create all tables
        Base.metadata.create_all(bind=engine, checkfirst=True)
        logging.info("✅ PostgreSQL database tables created successfully")
        
    except Exception as e:
        logging.error(f"❌ Error creating database tables: {e}")
        raise e

def test_connection():
    """
    Test database connection.
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            return result.fetchone()[0] == 1
    except Exception as e:
        logging.error(f"Database connection test failed: {e}")
        return False

def get_database_info():
    """
    Get database information for monitoring.
    Returns:
        dict: Database connection information
    """
    return {
        "database_type": "PostgreSQL",
        "host": DATABASE_CONFIG['host'],
        "port": DATABASE_CONFIG['port'],
        "database": DATABASE_CONFIG['database'],
        "username": DATABASE_CONFIG['username'],
        "connection_url": DATABASE_URL.replace(DATABASE_CONFIG['password'], '***'),
        "pool_size": engine.pool.size(),
        "checked_out_connections": engine.pool.checkedout(),
        "overflow_connections": engine.pool.overflow(),
        "checked_in_connections": engine.pool.checkedin()
    }