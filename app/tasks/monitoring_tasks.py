"""
Celery Tasks for Monitoring Engine
Background tasks for hourly monitoring cycles.
"""
import logging
from typing import Dict
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.database import SessionLocal
from app.services.monitoring_engine import MonitoringEngine

logger = logging.getLogger(__name__)


@celery_app.task(
    name='app.tasks.monitoring_tasks.run_hourly_monitoring_cycle',
    bind=True,
    max_retries=3,
    default_retry_delay=300  # 5 minutes
)
def run_hourly_monitoring_cycle(self) -> Dict:
    """
    Celery task for hourly monitoring cycle.
    
    This task:
    - Runs every hour automatically via Celery Beat
    - Prevents overlapping execution
    - Retries up to 3 times on failure
    - Maintains complete audit trail
    
    Returns:
        Dict with cycle summary
    """
    db: Session = SessionLocal()
    
    try:
        logger.info("Celery task started: run_hourly_monitoring_cycle")
        
        # Create monitoring engine
        engine = MonitoringEngine(db)
        
        # Run monitoring cycle
        result = engine.run_hourly_monitoring_cycle()
        
        logger.info(f"Monitoring cycle completed: {result}")
        
        return result
        
    except Exception as exc:
        logger.error(f"Monitoring cycle failed: {str(exc)}", exc_info=True)
        
        # Retry the task
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error("Max retries exceeded for monitoring cycle")
            return {
                'status': 'failed',
                'error': str(exc),
                'max_retries_exceeded': True
            }
    
    finally:
        db.close()


@celery_app.task(name='app.tasks.monitoring_tasks.run_monitoring_now')
def run_monitoring_now() -> Dict:
    """
    Manual trigger for monitoring cycle (for testing or emergency runs).
    
    Returns:
        Dict with cycle summary
    """
    db: Session = SessionLocal()
    
    try:
        logger.info("Manual monitoring cycle triggered")
        
        engine = MonitoringEngine(db)
        result = engine.run_hourly_monitoring_cycle()
        
        return result
        
    except Exception as exc:
        logger.error(f"Manual monitoring cycle failed: {str(exc)}", exc_info=True)
        return {
            'status': 'failed',
            'error': str(exc)
        }
    
    finally:
        db.close()
