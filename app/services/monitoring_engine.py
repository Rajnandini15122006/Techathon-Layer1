"""Real-Time Monitoring & Escalation Engine"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.monitoring import (RainfallLog, RiverLevelLog, GridStateSnapshot, Alert, MonitoringCycleLog, DrainLoadState)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MonitoringEngine:
    USPS_SPIKE_THRESHOLD = 15.0
    RISK_SPIKE_THRESHOLD = 10.0
    CRITICAL_USPS = 80.0
    HIGH_ALERT_USPS = 65.0
    WATCH_USPS = 50.0
    CRITICAL_RISK = 75.0
    HIGH_ALERT_RISK = 60.0
    WATCH_RISK = 45.0
    DECAY_RATE = 0.15
    
    def __init__(self, db: Session):
        self.db = db
        self.cycle_log = None
    
    def run_hourly_monitoring_cycle(self) -> Dict:
        logger.info("STARTING HOURLY MONITORING CYCLE")
        self.cycle_log = MonitoringCycleLog(start_time=datetime.utcnow(), status='running')
        self.db.add(self.cycle_log)
        self.db.commit()
        try:
            rainfall_delta = self._fetch_hourly_rainfall()
            grids_updated = self._update_drain_loads(rainfall_delta)
            river_stress = self._update_river_levels()
            snapshots = self._recalculate_grid_states(river_stress)
            alerts_triggered = self._detect_and_escalate(snapshots)
            self.cycle_log.end_time = datetime.utcnow()
            self.cycle_log.duration_seconds = (self.cycle_log.end_time - self.cycle_log.start_time).total_seconds()
            self.cycle_log.status = 'success'
            self.cycle_log.rainfall_delta = rainfall_delta
            self.cycle_log.grids_updated = grids_updated
            self.cycle_log.alerts_triggered = alerts_triggered
            self.db.commit()
            return {'status': 'success', 'cycle_id': str(self.cycle_log.id), 'duration_seconds': self.cycle_log.duration_seconds, 'rainfall_mm': rainfall_delta, 'grids_updated': grids_updated, 'alerts_triggered': alerts_triggered}
        except Exception as e:
            logger.error(f"MONITORING CYCLE FAILED: {str(e)}")
            if self.cycle_log:
                self.cycle_log.end_time = datetime.utcnow()
                self.cycle_log.status = 'failed'
                self.cycle_log.error_message = str(e)
                self.db.commit()
            raise
    
    def _fetch_hourly_rainfall(self) -> float:
        current_hour = datetime.utcnow().hour
        base_rainfall = 8.0 + (current_hour - 14) * 2.0 if 14 <= current_hour <= 20 else (3.0 + (current_hour - 6) * 0.5 if 6 <= current_hour <= 13 else 1.0)
        rainfall_mm = base_rainfall * (1.0 + 0.3 * ((datetime.utcnow().timetuple().tm_yday % 180) / 180.0))
        self.db.add(RainfallLog(rainfall_mm=rainfall_mm, location="Pune", timestamp=datetime.utcnow(), source="synthetic"))
        self.db.commit()
        return rainfall_mm
    
    def _update_drain_loads(self, rainfall_mm: float) -> int:
        for i in range(1, 101):
            grid_id = f"grid_{i}"
            drain_state = self.db.query(DrainLoadState).filter(DrainLoadState.grid_id == grid_id).first()
            if not drain_state:
                drain_state = DrainLoadState(grid_id=grid_id, current_load=0.0, capacity=100.0, runoff_coefficient=0.7, decay_rate=self.DECAY_RATE)
                self.db.add(drain_state)
            if rainfall_mm > 0:
                drain_state.current_load += rainfall_mm * drain_state.runoff_coefficient
                if drain_state.accumulated_rainfall is None: drain_state.accumulated_rainfall = 0.0; drain_state.accumulated_rainfall += rainfall_mm
            else:
                drain_state.current_load *= (1.0 - drain_state.decay_rate)
            drain_state.current_load = max(0.0, drain_state.current_load)
            drain_state.load_percentage = (drain_state.current_load / drain_state.capacity) * 100.0
            drain_state.last_updated = datetime.utcnow()
        self.db.commit()
        return 100
    
    def _update_river_levels(self) -> float:
        total_stress = 0.0
        for river in [{'name': 'Mula River', 'normal': 3.0, 'danger': 5.5}, {'name': 'Mutha River', 'normal': 2.8, 'danger': 5.0}]:
            recent = self.db.query(RainfallLog).order_by(desc(RainfallLog.timestamp)).limit(6).all()
            level = river['normal'] + sum(r.rainfall_mm for r in recent) * 0.05
            stress = 0.0 if level <= river['normal'] else (1.0 if level >= river['danger'] else (level - river['normal']) / (river['danger'] - river['normal']))
            self.db.add(RiverLevelLog(river_name=river['name'], level_meters=level, stress_ratio=stress, danger_level='critical' if stress >= 0.9 else ('danger' if stress >= 0.7 else ('warning' if stress >= 0.5 else 'safe')), timestamp=datetime.utcnow()))
            total_stress += stress
        self.db.commit()
        return total_stress / 2
    
    def _recalculate_grid_states(self, river_stress: float) -> List[GridStateSnapshot]:
        snapshots = []
        for drain_state in self.db.query(DrainLoadState).all():
            rain_stress = min(100.0, drain_state.accumulated_rainfall * 2.0)
            usps_score = rain_stress * 0.25 + drain_state.load_percentage * 0.30 + (40.0 + drain_state.load_percentage * 0.3) * 0.15 + 55.0 * 0.10 + 45.0 * 0.10 + river_stress * 100.0 * 0.10
            risk_score = ((rain_stress + drain_state.load_percentage + river_stress * 100.0) / 3.0 * 60.0) / 70.0
            severity = 'critical' if max(usps_score, risk_score) >= 80 else ('high_alert' if max(usps_score, risk_score) >= 65 else ('watch' if max(usps_score, risk_score) >= 50 else 'stable'))
            prev = self.db.query(GridStateSnapshot).filter(GridStateSnapshot.grid_id == drain_state.grid_id).order_by(desc(GridStateSnapshot.timestamp)).first()
            snapshot = GridStateSnapshot(grid_id=drain_state.grid_id, usps_score=usps_score, rain_stress=rain_stress, drain_stress=drain_state.load_percentage, traffic_stress=40.0, hospital_stress=55.0, power_stress=45.0, river_stress=river_stress*100, risk_score=risk_score, hazard_score=rain_stress, vulnerability_score=60.0, capacity_score=70.0, severity_level=severity, delta_usps=usps_score - prev.usps_score if prev else 0.0, delta_risk=risk_score - prev.risk_score if prev else 0.0, timestamp=datetime.utcnow(), monitoring_cycle_id=self.cycle_log.id)
            self.db.add(snapshot)
            snapshots.append(snapshot)
        self.db.commit()
        return snapshots
    
    def _detect_and_escalate(self, snapshots: List[GridStateSnapshot]) -> int:
        alerts = 0
        for snap in snapshots:
            reason = None
            if snap.delta_usps >= self.USPS_SPIKE_THRESHOLD:
                reason = f"USPS spike: +{snap.delta_usps:.1f}"
            elif snap.delta_risk >= self.RISK_SPIKE_THRESHOLD:
                reason = f"Risk spike: +{snap.delta_risk:.1f}"
            if reason and not self.db.query(Alert).filter(Alert.grid_id == snap.grid_id, Alert.status == 'active', Alert.created_at >= datetime.utcnow() - timedelta(hours=2)).first():
                self.db.add(Alert(grid_id=snap.grid_id, severity=snap.severity_level, alert_type='spike', reason=reason, generated_message=f"Alert: {reason}", usps_score=snap.usps_score, risk_score=snap.risk_score, delta_usps=snap.delta_usps, delta_risk=snap.delta_risk, status='active', monitoring_cycle_id=self.cycle_log.id))
                alerts += 1
        self.db.commit()
        return alerts
    
    def get_monitoring_status(self) -> Dict:
        last = self.db.query(MonitoringCycleLog).order_by(desc(MonitoringCycleLog.start_time)).first()
        return {'last_run_time': last.start_time.isoformat() if last else None, 'last_status': last.status if last else None, 'active_alerts': self.db.query(Alert).filter(Alert.status == 'active').count(), 'next_scheduled_run': (datetime.utcnow().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)).isoformat()}
