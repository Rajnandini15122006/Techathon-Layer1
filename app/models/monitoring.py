"""
Monitoring Engine Database Models
Production-grade models for real-time monitoring, escalation, and audit logging.
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from datetime import datetime
import uuid

from app.database import Base


class RainfallLog(Base):
    """Hourly rainfall measurements for audit trail"""
    __tablename__ = "rainfall_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rainfall_mm = Column(Float, nullable=False, comment="Rainfall in mm for the hour")
    location = Column(String(100), comment="Measurement location or grid area")
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    source = Column(String(50), comment="Data source: API, sensor, synthetic")
    
    def __repr__(self):
        return f"<RainfallLog {self.rainfall_mm}mm at {self.timestamp}>"


class RiverLevelLog(Base):
    """River level measurements and stress calculations"""
    __tablename__ = "river_level_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    river_name = Column(String(100), nullable=False, comment="River name (e.g., Mula, Mutha)")
    level_meters = Column(Float, nullable=False, comment="Water level in meters")
    stress_ratio = Column(Float, nullable=False, comment="Normalized stress 0-1")
    danger_level = Column(String(20), comment="safe, warning, danger, critical")
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<RiverLevelLog {self.river_name} {self.level_meters}m at {self.timestamp}>"


class GridStateSnapshot(Base):
    """Hourly snapshot of grid state for comparison and trending"""
    __tablename__ = "grid_state_snapshot"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grid_id = Column(String(50), nullable=False, index=True, comment="Grid cell identifier")
    
    # USPS Components
    usps_score = Column(Float, nullable=False, comment="Overall USPS score")
    rain_stress = Column(Float, comment="Rainfall stress component")
    drain_stress = Column(Float, comment="Drainage load stress")
    traffic_stress = Column(Float, comment="Traffic congestion stress")
    hospital_stress = Column(Float, comment="Hospital occupancy stress")
    power_stress = Column(Float, comment="Power grid stress")
    river_stress = Column(Float, comment="River proximity stress")
    
    # HRVC Risk
    risk_score = Column(Float, nullable=False, comment="HRVC risk score")
    hazard_score = Column(Float, comment="Hazard component")
    vulnerability_score = Column(Float, comment="Vulnerability component")
    capacity_score = Column(Float, comment="Capacity component")
    
    # Severity Classification
    severity_level = Column(String(20), nullable=False, comment="stable, watch, high_alert, critical")
    
    # Deltas from previous snapshot
    delta_usps = Column(Float, comment="Change in USPS from previous hour")
    delta_risk = Column(Float, comment="Change in risk from previous hour")
    
    # Metadata
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    monitoring_cycle_id = Column(UUID(as_uuid=True), ForeignKey('monitoring_cycle_log.id'))
    
    def __repr__(self):
        return f"<GridStateSnapshot {self.grid_id} USPS:{self.usps_score} Risk:{self.risk_score}>"


class Alert(Base):
    """Alert records for escalation tracking"""
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grid_id = Column(String(50), nullable=False, index=True)
    
    # Alert Classification
    severity = Column(String(20), nullable=False, comment="watch, high_alert, critical")
    alert_type = Column(String(50), comment="usps_spike, risk_increase, threshold_breach")
    
    # Alert Details
    reason = Column(Text, nullable=False, comment="Human-readable reason for alert")
    generated_message = Column(Text, comment="AI-generated alert message for authorities")
    
    # Metrics at time of alert
    usps_score = Column(Float)
    risk_score = Column(Float)
    delta_usps = Column(Float)
    delta_risk = Column(Float)
    
    # Alert Lifecycle
    status = Column(String(20), default='active', comment="active, acknowledged, resolved, false_positive")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    # Audit
    monitoring_cycle_id = Column(UUID(as_uuid=True), ForeignKey('monitoring_cycle_log.id'))
    
    def __repr__(self):
        return f"<Alert {self.severity} for {self.grid_id} at {self.created_at}>"


class MonitoringCycleLog(Base):
    """Audit log for each monitoring cycle execution"""
    __tablename__ = "monitoring_cycle_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Execution Timing
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    end_time = Column(DateTime)
    duration_seconds = Column(Float, comment="Execution duration")
    
    # Cycle Metrics
    rainfall_delta = Column(Float, comment="Total rainfall in this cycle (mm)")
    grids_updated = Column(Integer, default=0, comment="Number of grids processed")
    alerts_triggered = Column(Integer, default=0, comment="New alerts created")
    
    # Execution Status
    status = Column(String(20), nullable=False, default='running', comment="running, success, failed")
    error_message = Column(Text, comment="Error details if failed")
    retry_count = Column(Integer, default=0, comment="Number of retry attempts")
    
    # Performance Metrics
    db_queries = Column(Integer, comment="Number of database queries")
    api_calls = Column(Integer, comment="Number of external API calls")
    
    def __repr__(self):
        return f"<MonitoringCycleLog {self.status} at {self.start_time}>"


class DrainLoadState(Base):
    """Current drain load state for each grid (updated hourly)"""
    __tablename__ = "drain_load_state"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grid_id = Column(String(50), nullable=False, unique=True, index=True)
    
    # Drain Load Metrics
    current_load = Column(Float, nullable=False, default=0.0, comment="Current drain load (0-1)")
    capacity = Column(Float, nullable=False, default=1.0, comment="Maximum drain capacity")
    load_percentage = Column(Float, comment="Load as percentage of capacity")
    
    # Accumulation
    accumulated_rainfall = Column(Float, default=0.0, nullable=False, comment="Accumulated rainfall (mm)")
    runoff_coefficient = Column(Float, default=0.7, comment="Runoff coefficient for this grid")
    
    # Decay Parameters
    decay_rate = Column(Float, default=0.1, comment="Hourly decay rate when no rain")
    last_rainfall_time = Column(DateTime, comment="Last time rainfall was recorded")
    
    # Metadata
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<DrainLoadState {self.grid_id} Load:{self.load_percentage}%>"
