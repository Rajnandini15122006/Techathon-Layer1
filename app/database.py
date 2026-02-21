from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Create engine with connection pooling and SSL support for Neon
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables (PostGIS extension must be enabled manually in Neon)"""
    try:
        # Check if PostGIS is available
        with engine.connect() as conn:
            result = conn.execute(text("SELECT PostGIS_version();"))
            version = result.fetchone()
            logger.info(f"PostGIS version: {version[0]}")
    except Exception as e:
        logger.warning(f"Database connection failed: {e}")
        logger.warning("Running in DEMO MODE - Real-time API will work, but grid data unavailable")
        logger.warning("To fix: Check Neon database is active and PostGIS is enabled")
        return  # Continue without database for demo
    
    # Create tables with checkfirst=True to avoid duplicate errors
    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
        logger.info("Database tables created successfully")
    except Exception as e:
        # If index already exists, try to continue
        if "already exists" in str(e):
            logger.warning(f"Some database objects already exist: {e}")
            logger.info("Continuing with existing schema")
        else:
            logger.error(f"Error creating tables: {e}")
            logger.warning("Running in DEMO MODE - Real-time API will work")
