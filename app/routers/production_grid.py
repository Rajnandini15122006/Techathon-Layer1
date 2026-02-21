from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.production_grid_service import ProductionGridService
from pydantic import BaseModel
from typing import Optional
import logging
import os
import tempfile

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/production", tags=["Production Grid"])

class GridGenerationRequest(BaseModel):
    boundary_path: str
    dem_path: Optional[str] = None
    drain_path: Optional[str] = None
    land_use_path: Optional[str] = None
    census_path: Optional[str] = None
    slum_path: Optional[str] = None
    flood_path: Optional[str] = None
    infra_path: Optional[str] = None
    complaint_path: Optional[str] = None
    cell_size: float = 250

@router.post("/generate-grid")
def generate_production_grid(
    request: GridGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate production-grade spatial grid with real data
    
    All paths should point to actual spatial data files:
    - boundary_path: Required - Pune city boundary (shapefile/GeoJSON)
    - dem_path: Optional - Digital Elevation Model raster
    - drain_path: Optional - Drainage network (shapefile/GeoJSON)
    - land_use_path: Optional - Land use polygons
    - census_path: Optional - Census data with population
    - slum_path: Optional - Slum locations
    - flood_path: Optional - Historical flood data (raster or vector)
    - infra_path: Optional - Infrastructure points (hospitals, shelters)
    - complaint_path: Optional - Flood complaint locations
    
    Returns detailed statistics about grid generation
    """
    try:
        logger.info("Received production grid generation request")
        logger.info(f"Boundary: {request.boundary_path}")
        
        # Validate boundary file exists
        if not os.path.exists(request.boundary_path):
            raise HTTPException(
                status_code=400,
                detail=f"Boundary file not found: {request.boundary_path}"
            )
        
        # Generate grid
        stats = ProductionGridService.generate_full_spatial_grid(
            db=db,
            boundary_path=request.boundary_path,
            dem_path=request.dem_path,
            drain_path=request.drain_path,
            land_use_path=request.land_use_path,
            census_path=request.census_path,
            slum_path=request.slum_path,
            flood_path=request.flood_path,
            infra_path=request.infra_path,
            complaint_path=request.complaint_path,
            cell_size=request.cell_size
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Error generating production grid: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
