"""
Environmental API Router

Endpoints for real-time environmental monitoring and USPS computation.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from app.database import get_db
from app.services.environmental_engine import get_environmental_engine, EnvironmentalConfig
from app.models.environmental import RainfallLog, DrainStressLog, TrafficLog, USPSLog
from app.models.grid_cell import GridCell

router = APIRouter(prefix="/environmental", tags=["environmental"])


# Pydantic models
class EnvironmentalUpdateRequest(BaseModel):
    """Request model for environmental update"""
    grid_id: int
    rainfall_mm: float = Field(..., ge=0, description="Current rainfall intensity (mm/hr)")
    accumulated_1hr: float = Field(..., ge=0, description="Accumulated rainfall in last hour (mm)")
    traffic_congestion: Optional[float] = Field(None, ge=0, le=1, description="Traffic congestion index (0-1)")
    current_travel_time: Optional[float] = Field(None, gt=0, description="Current travel time (minutes)")
    free_flow_travel_time: Optional[float] = Field(None, gt=0, description="Free-flow travel time (minutes)")


class USPSResponse(BaseModel):
    """Response model for USPS data"""
    grid_id: int
    rain_index: float
    drain_stress: float
    traffic_index: float
    usps_score: float
    severity_level: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


class EnvironmentalStateResponse(BaseModel):
    """Complete environmental state response"""
    grid_id: int
    rain: dict
    drain: dict
    traffic: dict
    usps: dict
    timestamp: datetime


@router.post("/update", response_model=EnvironmentalStateResponse)
async def update_environmental_state(
    request: EnvironmentalUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update environmental state for a grid cell
    
    Computes:
    - Rain index from rainfall data
    - Drain stress using SCS-CN method
    - Traffic index from congestion data
    - USPS score from weighted aggregation
    
    Stores all metrics in time-series logs.
    """
    # Get grid cell data
    grid_cell = db.query(GridCell).filter(GridCell.id == request.grid_id).first()
    if not grid_cell:
        raise HTTPException(status_code=404, detail=f"Grid cell {request.grid_id} not found")
    
    # Get environmental engine
    engine = get_environmental_engine()
    
    # Compute environmental state
    try:
        state = engine.compute_environmental_state(
            rainfall_mm=request.rainfall_mm,
            accumulated_1hr=request.accumulated_1hr,
            land_use=grid_cell.land_use or "Mixed",
            grid_area_m2=62500.0,  # 250m x 250m
            drain_capacity_m3=grid_cell.drain_capacity or 1000.0,
            traffic_congestion=request.traffic_congestion,
            current_travel_time=request.current_travel_time,
            free_flow_travel_time=request.free_flow_travel_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing environmental state: {str(e)}")
    
    # Store in database
    try:
        # Rainfall log
        rainfall_log = RainfallLog(
            grid_id=request.grid_id,
            rainfall_mm=request.rainfall_mm,
            accumulated_1hr=request.accumulated_1hr,
            rain_index=state['rain']['rain_index']
        )
        db.add(rainfall_log)
        
        # Drain stress log
        drain_log = DrainStressLog(
            grid_id=request.grid_id,
            runoff_mm=state['drain']['runoff_mm'],
            drain_stress=state['drain']['drain_stress'],
            curve_number=state['drain']['curve_number']
        )
        db.add(drain_log)
        
        # Traffic log
        traffic_log = TrafficLog(
            grid_id=request.grid_id,
            traffic_index=state['traffic']['traffic_index']
        )
        db.add(traffic_log)
        
        # USPS log
        usps_log = USPSLog(
            grid_id=request.grid_id,
            rain_index=state['usps']['rain_index'],
            drain_stress=state['usps']['drain_stress'],
            traffic_index=state['usps']['traffic_index'],
            usps_score=state['usps']['usps_score'],
            severity_level=state['usps']['severity_level']
        )
        db.add(usps_log)
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error storing environmental data: {str(e)}")
    
    return EnvironmentalStateResponse(
        grid_id=request.grid_id,
        rain=state['rain'],
        drain=state['drain'],
        traffic=state['traffic'],
        usps=state['usps'],
        timestamp=state['timestamp']
    )


@router.get("/usps/{grid_id}", response_model=USPSResponse)
async def get_latest_usps(
    grid_id: int,
    db: Session = Depends(get_db)
):
    """Get latest USPS score for a grid cell"""
    usps_log = db.query(USPSLog).filter(
        USPSLog.grid_id == grid_id
    ).order_by(desc(USPSLog.timestamp)).first()
    
    if not usps_log:
        raise HTTPException(status_code=404, detail=f"No USPS data found for grid {grid_id}")
    
    return usps_log


@router.get("/latest", response_model=List[USPSResponse])
async def get_latest_all_grids(
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get latest USPS scores for all grid cells
    
    Optional filtering by severity level.
    """
    # Subquery to get latest timestamp per grid
    from sqlalchemy import func
    subquery = db.query(
        USPSLog.grid_id,
        func.max(USPSLog.timestamp).label('max_timestamp')
    ).group_by(USPSLog.grid_id).subquery()
    
    # Join to get full records
    query = db.query(USPSLog).join(
        subquery,
        (USPSLog.grid_id == subquery.c.grid_id) & 
        (USPSLog.timestamp == subquery.c.max_timestamp)
    )
    
    # Apply severity filter if provided
    if severity:
        query = query.filter(USPSLog.severity_level == severity)
    
    # Apply limit
    results = query.limit(limit).all()
    
    return results


@router.get("/history/{grid_id}")
async def get_usps_history(
    grid_id: int,
    hours: int = Query(24, ge=1, le=168, description="Hours of history to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Get USPS history for a grid cell
    
    Returns time-series data for the specified time period.
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    usps_history = db.query(USPSLog).filter(
        USPSLog.grid_id == grid_id,
        USPSLog.timestamp >= cutoff_time
    ).order_by(USPSLog.timestamp).all()
    
    if not usps_history:
        raise HTTPException(
            status_code=404, 
            detail=f"No USPS history found for grid {grid_id} in last {hours} hours"
        )
    
    return {
        'grid_id': grid_id,
        'period_hours': hours,
        'data_points': len(usps_history),
        'history': [
            {
                'timestamp': log.timestamp,
                'usps_score': log.usps_score,
                'severity_level': log.severity_level,
                'rain_index': log.rain_index,
                'drain_stress': log.drain_stress,
                'traffic_index': log.traffic_index
            }
            for log in usps_history
        ]
    }


@router.get("/summary")
async def get_environmental_summary(db: Session = Depends(get_db)):
    """
    Get system-wide environmental summary
    
    Returns aggregate statistics across all grid cells.
    """
    from sqlalchemy import func
    
    # Get latest USPS data
    subquery = db.query(
        USPSLog.grid_id,
        func.max(USPSLog.timestamp).label('max_timestamp')
    ).group_by(USPSLog.grid_id).subquery()
    
    latest_usps = db.query(USPSLog).join(
        subquery,
        (USPSLog.grid_id == subquery.c.grid_id) & 
        (USPSLog.timestamp == subquery.c.max_timestamp)
    ).all()
    
    if not latest_usps:
        return {
            'total_grids': 0,
            'severity_distribution': {},
            'average_usps': 0.0,
            'max_usps': 0.0,
            'critical_grids': 0
        }
    
    # Compute statistics
    severity_counts = {}
    usps_scores = []
    
    for log in latest_usps:
        severity_counts[log.severity_level] = severity_counts.get(log.severity_level, 0) + 1
        usps_scores.append(log.usps_score)
    
    return {
        'total_grids': len(latest_usps),
        'severity_distribution': severity_counts,
        'average_usps': sum(usps_scores) / len(usps_scores) if usps_scores else 0.0,
        'max_usps': max(usps_scores) if usps_scores else 0.0,
        'critical_grids': severity_counts.get('Critical', 0),
        'high_alert_grids': severity_counts.get('High Alert', 0),
        'watch_grids': severity_counts.get('Watch', 0),
        'stable_grids': severity_counts.get('Stable', 0),
        'timestamp': datetime.utcnow()
    }


@router.post("/bulk-update")
async def bulk_update_environmental(
    updates: List[EnvironmentalUpdateRequest],
    db: Session = Depends(get_db)
):
    """
    Bulk update environmental state for multiple grid cells
    
    Optimized for batch processing.
    """
    engine = get_environmental_engine()
    results = []
    errors = []
    
    for request in updates:
        try:
            # Get grid cell
            grid_cell = db.query(GridCell).filter(GridCell.id == request.grid_id).first()
            if not grid_cell:
                errors.append(f"Grid {request.grid_id}: not found")
                continue
            
            # Compute state
            state = engine.compute_environmental_state(
                rainfall_mm=request.rainfall_mm,
                accumulated_1hr=request.accumulated_1hr,
                land_use=grid_cell.land_use or "Mixed",
                grid_area_m2=62500.0,
                drain_capacity_m3=grid_cell.drain_capacity or 1000.0,
                traffic_congestion=request.traffic_congestion,
                current_travel_time=request.current_travel_time,
                free_flow_travel_time=request.free_flow_travel_time
            )
            
            # Store logs
            db.add(RainfallLog(
                grid_id=request.grid_id,
                rainfall_mm=request.rainfall_mm,
                accumulated_1hr=request.accumulated_1hr,
                rain_index=state['rain']['rain_index']
            ))
            
            db.add(DrainStressLog(
                grid_id=request.grid_id,
                runoff_mm=state['drain']['runoff_mm'],
                drain_stress=state['drain']['drain_stress'],
                curve_number=state['drain']['curve_number']
            ))
            
            db.add(TrafficLog(
                grid_id=request.grid_id,
                traffic_index=state['traffic']['traffic_index']
            ))
            
            db.add(USPSLog(
                grid_id=request.grid_id,
                rain_index=state['usps']['rain_index'],
                drain_stress=state['usps']['drain_stress'],
                traffic_index=state['usps']['traffic_index'],
                usps_score=state['usps']['usps_score'],
                severity_level=state['usps']['severity_level']
            ))
            
            results.append({
                'grid_id': request.grid_id,
                'usps_score': state['usps']['usps_score'],
                'severity': state['usps']['severity_level']
            })
            
        except Exception as e:
            errors.append(f"Grid {request.grid_id}: {str(e)}")
    
    # Commit all at once
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error committing bulk update: {str(e)}")
    
    return {
        'success_count': len(results),
        'error_count': len(errors),
        'results': results,
        'errors': errors if errors else None
    }
