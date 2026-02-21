"""
Add risk columns to grid_cells table
Run this once to update your database schema
"""
from sqlalchemy import create_engine, text
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Add risk scoring columns to grid_cells table"""
    engine = create_engine(settings.database_url)
    
    logger.info("Adding risk columns to grid_cells table...")
    
    with engine.connect() as conn:
        # Add columns if they don't exist
        try:
            conn.execute(text("""
                ALTER TABLE grid_cells 
                ADD COLUMN IF NOT EXISTS hazard_score FLOAT,
                ADD COLUMN IF NOT EXISTS vulnerability_score FLOAT,
                ADD COLUMN IF NOT EXISTS capacity_score FLOAT,
                ADD COLUMN IF NOT EXISTS risk_score FLOAT,
                ADD COLUMN IF NOT EXISTS risk_level VARCHAR;
            """))
            conn.commit()
            logger.info("✅ Risk columns added successfully!")
        except Exception as e:
            logger.error(f"Error adding columns: {e}")
            raise
    
    logger.info("Database migration complete!")

if __name__ == "__main__":
    migrate_database()
