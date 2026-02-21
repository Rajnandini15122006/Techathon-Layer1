import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.database import Base

class GridCell(Base):
    __tablename__ = "grid_cells"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    geom = Column(Geometry('POLYGON', srid=4326), nullable=False)
    
    # Spatial attributes
    elevation_mean = Column(Float, nullable=True, comment="Mean elevation in meters from DEM")
    drain_distance = Column(Float, nullable=True, comment="Distance to nearest drain in meters")
    land_use = Column(String, nullable=True, comment="Dominant land use category")
    population_density = Column(Float, nullable=True, comment="Population per square meter")
    slum_density = Column(Float, nullable=True, comment="Percentage of cell area covered by slums")
    flood_depth_avg = Column(Float, nullable=True, comment="Average historical flood depth in meters")
    infra_count = Column(Integer, default=0, comment="Count of hospitals and shelters")
    complaint_density = Column(Float, default=0.0, comment="Flood complaints per square kilometer")
    
    # Layer 3: HRVC Risk Scores
    hazard_score = Column(Float, nullable=True, comment="Hazard score (0-100)")
    vulnerability_score = Column(Float, nullable=True, comment="Vulnerability score (0-100)")
    capacity_score = Column(Float, nullable=True, comment="Capacity score (0-100)")
    risk_score = Column(Float, nullable=True, comment="Final HRVC risk score (0-100)")
    risk_level = Column(String, nullable=True, comment="Risk level: Low/Medium/High/Critical")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

# Create spatial index separately with IF NOT EXISTS
__table_args__ = (
    Index('idx_grid_cells_geom', 'geom', postgresql_using='gist', postgresql_ops={'geom': 'gist_geometry_ops_2d'}),
)
