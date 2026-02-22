"""
Database Migration: Environmental Monitoring Tables

Creates tables for Layer 2 Environmental Engine:
- rainfall_log
- drain_stress_log
- traffic_log
- usps_log
"""

from app.database import engine, Base
from app.models.environmental import RainfallLog, DrainStressLog, TrafficLog, USPSLog
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """Create environmental monitoring tables"""
    logger.info("Creating environmental monitoring tables...")
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine, tables=[
            RainfallLog.__table__,
            DrainStressLog.__table__,
            TrafficLog.__table__,
            USPSLog.__table__
        ])
        
        logger.info("✓ Environmental tables created successfully")
        logger.info("  - rainfall_log")
        logger.info("  - drain_stress_log")
        logger.info("  - traffic_log")
        logger.info("  - usps_log")
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise


if __name__ == "__main__":
    migrate()
