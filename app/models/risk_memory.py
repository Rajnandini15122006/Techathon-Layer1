"""
Phase 2: Risk Memory & Hotspot Evolution Database Models
Production-grade, audit-ready models for government use
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class RiskPrediction(Base):
    """Store predicted risk scores for comparison with actual outcomes"""
    __tablename__ = 'risk_predictions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grid_id = Column(Integer, ForeignKey('grid_cells.id'), nullable=False, index=True)
    predicted_risk_score = Column(Float, nullable=False)
    predicted_usps_score = Column(Float, nullable=False)
    severity_level = Column(String(20), nullable=False)  # low, medium, high, critical
    rainfall_intensity = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_risk_pred_grid_time', 'grid_id', 'timestamp'),
    )


class ActualImpact(Base):
    """Store actual observed impact for validation"""
    __tablename__ = 'actual_impact'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grid_id = Column(Integer, ForeignKey('grid_cells.id'), nullable=False, index=True)
    observed_flood_depth = Column(Float, nullable=False)  # cm
    infrastructure_damage_count = Column(Integer, default=0)
    road_blockage_flag = Column(Integer, default=0)  # 0=no, 1=yes
    verified_damage_level = Column(String(20), nullable=False)  # low, medium, high
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_actual_impact_grid_time', 'grid_id', 'timestamp'),
    )


class ResponseLog(Base):
    """Track emergency response times for performance analysis"""
    __tablename__ = 'response_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grid_id = Column(Integer, ForeignKey('grid_cells.id'), nullable=False, index=True)
    alert_id = Column(String(100), nullable=False)
    response_start_time = Column(DateTime, nullable=False)
    response_end_time = Column(DateTime)
    response_time_minutes = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


class CitizenReportsSummary(Base):
    """Aggregate citizen complaints for hotspot detection"""
    __tablename__ = 'citizen_reports_summary'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grid_id = Column(Integer, ForeignKey('grid_cells.id'), nullable=False, index=True)
    complaint_count = Column(Integer, default=0)
    average_severity = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


class RiskMemorySummary(Base):
    """Materialized summary for each grid cell's historical performance"""
    __tablename__ = 'risk_memory_summary'
    
    grid_id = Column(Integer, ForeignKey('grid_cells.id'), primary_key=True)
    avg_prediction_error = Column(Float, default=0.0)
    repeat_overflow_count = Column(Integer, default=0)
    hotspot_score = Column(Float, default=0.0)
    hotspot_status = Column(String(20), default='stable')  # stable, watchlist, emerging, chronic
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_hotspot_score', 'hotspot_score'),
        Index('idx_hotspot_status', 'hotspot_status'),
    )


class ModelWeightHistory(Base):
    """Track model weight adjustments for transparency and audit"""
    __tablename__ = 'model_weight_history'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    hazard_weight = Column(Float, nullable=False)
    exposure_weight = Column(Float, nullable=False)
    vulnerability_weight = Column(Float, nullable=False)
    capacity_weight = Column(Float, nullable=False)
    adjustment_reason = Column(String(500))
    affected_grid_count = Column(Integer, default=0)
