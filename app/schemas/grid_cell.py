from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class GridCellBase(BaseModel):
    elevation_mean: Optional[float] = None
    slope_mean: Optional[float] = None
    drain_distance: Optional[float] = None
    land_use: Optional[str] = None
    population_density: Optional[float] = None
    slum_density: Optional[float] = None
    flood_history_score: int = 0
    infra_score: int = 0

class GridCellCreate(GridCellBase):
    geom: str  # WKT format

class GridCellResponse(GridCellBase):
    id: UUID
    geom: str  # GeoJSON format
    created_at: datetime
    
    class Config:
        from_attributes = True
