from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.hrvc_risk_service import HRVCRiskService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/risk", tags=["HRVC Risk Engine"])

@router.post("/compute-hrvc")
def compute_hrvc_risk(db: Session = Depends(get_db)):
    """
    Compute HRVC (Hazard × Vulnerability / Capacity) risk scores for all grid cells
    
    This endpoint:
    1. Computes Hazard score (flood depth, elevation, drain distance)
    2. Computes Vulnerability score (population, slums, land use)
    3. Computes Capacity score (infrastructure, complaint history)
    4. Calculates final Risk = (H × V) / C
    5. Assigns risk levels: Low/Medium/High/Critical
    
    Returns summary statistics and risk distribution
    """
    try:
        logger.info("Starting HRVC risk computation...")
        result = HRVCRiskService.compute_all_risks(db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error computing HRVC risk: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/high-risk-cells")
def get_high_risk_cells(
    min_risk: float = 50.0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get grid cells with risk score above threshold
    
    - **min_risk**: Minimum risk score (default: 50.0)
    - **limit**: Maximum number of cells to return
    """
    from app.models.grid_cell import GridCell
    from sqlalchemy import text
    
    query = text("""
        SELECT jsonb_build_object(
            'type', 'FeatureCollection',
            'features', jsonb_agg(feature)
        ) as geojson
        FROM (
            SELECT jsonb_build_object(
                'type', 'Feature',
                'id', id::text,
                'geometry', ST_AsGeoJSON(geom)::jsonb,
                'properties', jsonb_build_object(
                    'risk_score', risk_score,
                    'risk_level', risk_level,
                    'hazard_score', hazard_score,
                    'vulnerability_score', vulnerability_score,
                    'capacity_score', capacity_score,
                    'flood_depth_avg', flood_depth_avg,
                    'population_density', population_density,
                    'infra_count', infra_count
                )
            ) as feature
            FROM grid_cells
            WHERE risk_score >= :min_risk
            ORDER BY risk_score DESC
            LIMIT :limit
        ) features
    """)
    
    result = db.execute(query, {"min_risk": min_risk, "limit": limit}).fetchone()
    return result[0] if result and result[0] else {"type": "FeatureCollection", "features": []}
