"""
Monitoring Engine API Router
Endpoints for monitoring system control and status.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Dict, List
from datetime import datetime, timedelta

from app.database import get_db
from app.services.monitoring_engine import MonitoringEngine
from app.models.monitoring import (
    MonitoringCycleLog, Alert, RainfallLog, 
    RiverLevelLog, GridStateSnapshot
)
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Optional Celery import - system works without it
try:
    from app.tasks.monitoring_tasks import run_monitoring_now
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


@router.post("/run-now")
async def trigger_monitoring_now(db: Session = Depends(get_db)) -> Dict:
    """
    Manually trigger a monitoring cycle immediately.
    
    Use this for:
    - Testing the monitoring system
    - Emergency monitoring runs
    - On-demand system checks
    
    Returns:
        Monitoring cycle summary
    """
    try:
        # Try Celery if available
        if CELERY_AVAILABLE:
            task = run_monitoring_now.delay()
            return {
                "status": "triggered",
                "message": "Monitoring cycle started (Celery)",
                "task_id": task.id,
                "note": "Check /api/monitoring/status for results"
            }
        else:
            # Run synchronously if Celery not available
            logger.info("Running monitoring cycle synchronously...")
            engine = MonitoringEngine(db)
            result = engine.run_hourly_monitoring_cycle()
            logger.info(f"Monitoring cycle completed: {result}")
            return result
    
    except Exception as e:
        logger.error(f"Monitoring cycle error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run monitoring cycle: {str(e)}"
        )


@router.get("/status")
async def get_monitoring_status(db: Session = Depends(get_db)) -> Dict:
    """
    Get current monitoring system status.
    
    Returns:
        - Last run time
        - Last execution status
        - Active alerts count
        - Next scheduled run
        - Recent metrics
    """
    engine = MonitoringEngine(db)
    status = engine.get_monitoring_status()
    
    return status


@router.get("/cycles")
async def get_monitoring_cycles(
    limit: int = 24,
    db: Session = Depends(get_db)
) -> List[Dict]:
    """
    Get recent monitoring cycle logs.
    
    Args:
        limit: Number of cycles to return (default: 24 hours)
    
    Returns:
        List of monitoring cycle logs
    """
    cycles = db.query(MonitoringCycleLog).order_by(
        desc(MonitoringCycleLog.start_time)
    ).limit(limit).all()
    
    return [
        {
            "id": str(cycle.id),
            "start_time": cycle.start_time.isoformat(),
            "end_time": cycle.end_time.isoformat() if cycle.end_time else None,
            "duration_seconds": cycle.duration_seconds,
            "status": cycle.status,
            "rainfall_mm": cycle.rainfall_delta,
            "grids_updated": cycle.grids_updated,
            "alerts_triggered": cycle.alerts_triggered,
            "error_message": cycle.error_message
        }
        for cycle in cycles
    ]


@router.get("/alerts/active")
async def get_active_alerts(db: Session = Depends(get_db)) -> List[Dict]:
    """
    Get all active alerts.
    
    Returns:
        List of active alerts requiring attention
    """
    alerts = db.query(Alert).filter(
        Alert.status == 'active'
    ).order_by(desc(Alert.created_at)).all()
    
    return [
        {
            "id": str(alert.id),
            "grid_id": alert.grid_id,
            "severity": alert.severity,
            "alert_type": alert.alert_type,
            "reason": alert.reason,
            "message": alert.generated_message,
            "usps_score": alert.usps_score,
            "risk_score": alert.risk_score,
            "created_at": alert.created_at.isoformat(),
            "status": alert.status
        }
        for alert in alerts
    ]


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Acknowledge an alert.
    
    Args:
        alert_id: Alert UUID
    
    Returns:
        Updated alert status
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = 'acknowledged'
    alert.acknowledged_at = datetime.utcnow()
    db.commit()
    
    return {
        "status": "success",
        "message": "Alert acknowledged",
        "alert_id": str(alert.id)
    }


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Mark an alert as resolved.
    
    Args:
        alert_id: Alert UUID
    
    Returns:
        Updated alert status
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = 'resolved'
    alert.resolved_at = datetime.utcnow()
    db.commit()
    
    return {
        "status": "success",
        "message": "Alert resolved",
        "alert_id": str(alert.id)
    }


@router.get("/rainfall/recent")
async def get_recent_rainfall(
    hours: int = 24,
    db: Session = Depends(get_db)
) -> List[Dict]:
    """
    Get recent rainfall measurements.
    
    Args:
        hours: Number of hours to look back (default: 24)
    
    Returns:
        List of rainfall measurements
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    rainfall_logs = db.query(RainfallLog).filter(
        RainfallLog.timestamp >= cutoff_time
    ).order_by(desc(RainfallLog.timestamp)).all()
    
    return [
        {
            "rainfall_mm": log.rainfall_mm,
            "location": log.location,
            "timestamp": log.timestamp.isoformat(),
            "source": log.source
        }
        for log in rainfall_logs
    ]


@router.get("/river-levels/current")
async def get_current_river_levels(db: Session = Depends(get_db)) -> List[Dict]:
    """
    Get current river level measurements.
    
    Returns:
        Latest river level data for all monitored rivers
    """
    # Get latest measurement for each river
    rivers = ['Mula River', 'Mutha River']
    river_data = []
    
    for river_name in rivers:
        latest = db.query(RiverLevelLog).filter(
            RiverLevelLog.river_name == river_name
        ).order_by(desc(RiverLevelLog.timestamp)).first()
        
        if latest:
            river_data.append({
                "river_name": latest.river_name,
                "level_meters": latest.level_meters,
                "stress_ratio": latest.stress_ratio,
                "danger_level": latest.danger_level,
                "timestamp": latest.timestamp.isoformat()
            })
    
    return river_data


@router.get("/grid-state/{grid_id}")
async def get_grid_state_history(
    grid_id: str,
    hours: int = 24,
    db: Session = Depends(get_db)
) -> List[Dict]:
    """
    Get state history for a specific grid.
    
    Args:
        grid_id: Grid identifier
        hours: Number of hours to look back (default: 24)
    
    Returns:
        List of grid state snapshots
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    snapshots = db.query(GridStateSnapshot).filter(
        GridStateSnapshot.grid_id == grid_id,
        GridStateSnapshot.timestamp >= cutoff_time
    ).order_by(desc(GridStateSnapshot.timestamp)).all()
    
    return [
        {
            "timestamp": snap.timestamp.isoformat(),
            "usps_score": snap.usps_score,
            "risk_score": snap.risk_score,
            "severity_level": snap.severity_level,
            "delta_usps": snap.delta_usps,
            "delta_risk": snap.delta_risk,
            "components": {
                "rain_stress": snap.rain_stress,
                "drain_stress": snap.drain_stress,
                "traffic_stress": snap.traffic_stress,
                "hospital_stress": snap.hospital_stress,
                "power_stress": snap.power_stress,
                "river_stress": snap.river_stress
            }
        }
        for snap in snapshots
    ]


@router.get("/dashboard-summary")
async def get_dashboard_summary(db: Session = Depends(get_db)) -> Dict:
    """
    Get comprehensive dashboard summary for monitoring system.
    
    Returns:
        Summary of all monitoring metrics
    """
    try:
        # Get last cycle
        last_cycle = db.query(MonitoringCycleLog).order_by(
            desc(MonitoringCycleLog.start_time)
        ).first()
        
        # Count alerts by severity
        critical_alerts = db.query(Alert).filter(
            Alert.status == 'active',
            Alert.severity == 'critical'
        ).count()
        
        high_alerts = db.query(Alert).filter(
            Alert.status == 'active',
            Alert.severity == 'high_alert'
        ).count()
        
        watch_alerts = db.query(Alert).filter(
            Alert.status == 'active',
            Alert.severity == 'watch'
        ).count()
        
        # Get latest rainfall
        latest_rainfall = db.query(RainfallLog).order_by(
            desc(RainfallLog.timestamp)
        ).first()
        
        # Get grids by severity
        latest_snapshots = db.query(GridStateSnapshot).filter(
            GridStateSnapshot.timestamp >= datetime.utcnow() - timedelta(hours=2)
        ).all()
        
        severity_counts = {
            'critical': sum(1 for s in latest_snapshots if s.severity_level == 'critical'),
            'high_alert': sum(1 for s in latest_snapshots if s.severity_level == 'high_alert'),
            'watch': sum(1 for s in latest_snapshots if s.severity_level == 'watch'),
            'stable': sum(1 for s in latest_snapshots if s.severity_level == 'stable')
        }
        
        return {
            "last_cycle": {
                "time": last_cycle.start_time.isoformat() if last_cycle else None,
                "status": last_cycle.status if last_cycle else None,
                "duration_seconds": last_cycle.duration_seconds if last_cycle else None
            },
            "active_alerts": {
                "critical": critical_alerts,
                "high_alert": high_alerts,
                "watch": watch_alerts,
                "total": critical_alerts + high_alerts + watch_alerts
            },
            "grid_severity": severity_counts,
            "latest_rainfall_mm": latest_rainfall.rainfall_mm if latest_rainfall else 0.0,
            "system_status": "operational" if last_cycle and last_cycle.status == 'success' else "ready"
        }
    except Exception as e:
        logger.error(f"Dashboard summary error: {str(e)}")
        # Return default values if tables don't exist yet
        return {
            "last_cycle": {"time": None, "status": None, "duration_seconds": None},
            "active_alerts": {"critical": 0, "high_alert": 0, "watch": 0, "total": 0},
            "grid_severity": {"critical": 0, "high_alert": 0, "watch": 0, "stable": 0},
            "latest_rainfall_mm": 0.0,
            "system_status": "initializing",
            "note": "Run a monitoring cycle to initialize the system"
        }
