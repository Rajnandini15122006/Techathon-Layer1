"""
Environmental Data Models

Time-series storage for environmental monitoring data:
- Rainfall logs
- Drain stress logs
- Traffic logs
- USPS logs
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, Index, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class RainfallLog(Base):
    """Rainfall time-series data"""
    __tablename__ = "rainfall_log"
    
    id = Column(Integer, primary_key=True, index=True)
    grid_id = Column(Integer, index=True, nullable=False)
    rainfall_mm = Column(Float, nullable=False)
    accumulated_1hr = Column(Float, nullable=False)
    rain_index = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_rainfall_grid_time', 'grid_id', 'timestamp'),
        {'extend_existing': True}
    )


class DrainStressLog(Base):
    """Drain stress time-series data"""
    __tablename__ = "drain_stress_log"
    
    id = Column(Integer, primary_key=True, index=True)
    grid_id = Column(Integer, index=True, nullable=False)
    runoff_mm = Column(Float, nullable=False)
    drain_stress = Column(Float, nullable=False)
    curve_number = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_drain_grid_time', 'grid_id', 'timestamp'),
        {'extend_existing': True}
    )


class TrafficLog(Base):
    """Traffic congestion time-series data"""
    __tablename__ = "traffic_log"
    
    id = Column(Integer, primary_key=True, index=True)
    grid_id = Column(Integer, index=True, nullable=False)
    traffic_index = Column(Float, nullable=False)
    congestion_level = Column(String, nullable=True)  # Optional: "Low", "Medium", "High"
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_traffic_grid_time', 'grid_id', 'timestamp'),
        {'extend_existing': True}
    )


class USPSLog(Base):
    """USPS (Urban System Pressure Score) time-series data"""
    __tablename__ = "usps_log"
    
    id = Column(Integer, primary_key=True, index=True)
    grid_id = Column(Integer, index=True, nullable=False)
    rain_index = Column(Float, nullable=False)
    drain_stress = Column(Float, nullable=False)
    traffic_index = Column(Float, nullable=False)
    usps_score = Column(Float, nullable=False, index=True)
    severity_level = Column(String, nullable=False, index=True)  # Stable, Watch, High Alert, Critical
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_usps_grid_time', 'grid_id', 'timestamp'),
        Index('idx_usps_severity_time', 'severity_level', 'timestamp'),
        {'extend_existing': True}
    )
