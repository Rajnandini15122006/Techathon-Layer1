from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.services.grid_service import GridService
from app.schemas.grid_cell import GridCellResponse

router = APIRouter(prefix="/grid-cells", tags=["Grid Cells"])

@router.get("/", response_model=dict)
def get_grid_cells(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=20000),
    format: str = Query("geojson", regex="^(geojson|json)$"),
    db: Session = Depends(get_db)
):
    """
    Get all grid cells
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **format**: Response format (geojson or json)
    """
    if format == "geojson":
        return GridService.get_grid_cells_geojson(db, skip=skip, limit=limit)
    else:
        cells = GridService.get_all_grid_cells(db, skip=skip, limit=limit)
        return {"data": cells, "count": len(cells)}

@router.get("/{cell_id}")
def get_grid_cell(
    cell_id: UUID,
    format: str = Query("geojson", regex="^(geojson|json)$"),
    db: Session = Depends(get_db)
):
    """
    Get a specific grid cell by ID
    
    - **cell_id**: UUID of the grid cell
    - **format**: Response format (geojson or json)
    """
    if format == "geojson":
        cell = GridService.get_grid_cell_geojson(db, cell_id)
    else:
        cell = GridService.get_grid_cell_by_id(db, cell_id)
    
    if not cell:
        raise HTTPException(status_code=404, detail="Grid cell not found")
    
    return cell
