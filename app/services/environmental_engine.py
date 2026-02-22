"""
Layer 2: Real-Time Environmental Modeling & USPS Engine

This module implements production-grade environmental stress modeling for urban disaster risk assessment.
Uses deterministic hydrological formulas (SCS-CN method) and structured index modeling.

Components:
- RainModule: Rainfall normalization and indexing
- DrainStressModule: SCS-CN runoff estimation and drain stress calculation
- TrafficModule: Traffic congestion indexing
- USPSCalculator: Urban System Pressure Score computation
- EnvironmentalStateStorage: Time-series data management

Design Principles:
- Disaster risk decomposition (hazard + vulnerability)
- Multi-criteria composite scoring
- Transparent weighted aggregation
- Audit-ready calculations
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math

logger = logging.getLogger(__name__)


@dataclass
class EnvironmentalConfig:
    """Configuration for environmental modeling"""
    # Rain module
    max_expected_rainfall: float = 100.0  # mm/hr
    
    # Drain stress module (SCS-CN parameters)
    cn_buildup: float = 92.5  # Curve Number for built-up areas
    cn_residential: float = 80.0  # Curve Number for residential
    cn_vegetation: float = 62.5  # Curve Number for vegetation
    
    # USPS weights (must sum to 1.0)
    weight_rain: float = 0.4  # Primary hazard trigger
    weight_drain: float = 0.4  # Hazard amplifier
    weight_traffic: float = 0.2  # Systemic vulnerability
    
    # Severity thresholds
    threshold_stable: float = 0.3
    threshold_watch: float = 0.6
    threshold_high_alert: float = 0.8


class RainModule:
    """
    Rain Module: Rainfall normalization and indexing
    
    Converts raw rainfall data into normalized index (0-1) for composite scoring.
    Uses configurable maximum expected rainfall for normalization.
    """
    
    def __init__(self, config: EnvironmentalConfig):
        self.config = config
        logger.info(f"RainModule initialized with max_expected_rainfall={config.max_expected_rainfall} mm/hr")
    
    def normalize_rainfall(self, rainfall_mm: float) -> float:
        """
        Normalize rainfall intensity to 0-1 scale
        
        Args:
            rainfall_mm: Current rainfall in mm/hr
            
        Returns:
            Normalized rain index (0-1)
        """
        if rainfall_mm < 0:
            logger.warning(f"Negative rainfall value: {rainfall_mm}, setting to 0")
            rainfall_mm = 0
        
        rain_index = min(rainfall_mm / self.config.max_expected_rainfall, 1.0)
        
        logger.debug(f"Rainfall {rainfall_mm} mm/hr normalized to index {rain_index:.3f}")
        return rain_index
    
    def compute_rain_index(self, rainfall_mm: float, accumulated_1hr: float) -> Dict:
        """
        Compute comprehensive rain metrics
        
        Args:
            rainfall_mm: Current rainfall intensity (mm/hr)
            accumulated_1hr: Accumulated rainfall in last 1 hour (mm)
            
        Returns:
            Dictionary with rain metrics
        """
        rain_index = self.normalize_rainfall(rainfall_mm)
        accumulated_index = self.normalize_rainfall(accumulated_1hr)
        
        return {
            'rainfall_mm': rainfall_mm,
            'accumulated_1hr': accumulated_1hr,
            'rain_index': rain_index,
            'accumulated_index': accumulated_index,
            'timestamp': datetime.utcnow()
        }


class DrainStressModule:
    """
    Drain Stress Module: SCS-CN runoff estimation and drain stress calculation
    
    Implements Soil Conservation Service Curve Number (SCS-CN) method for runoff estimation.
    Computes drain stress as ratio of runoff volume to drain capacity.
    
    SCS-CN Formula:
        If P <= 0.2S: runoff = 0
        Else: runoff = ((P - 0.2S)^2) / (P + 0.8S)
    Where:
        P = rainfall (mm)
        S = (1000 / CN) - 10
        CN = Curve Number (depends on land use)
    """
    
    def __init__(self, config: EnvironmentalConfig):
        self.config = config
        logger.info("DrainStressModule initialized with SCS-CN method")
    
    def get_curve_number(self, land_use: str) -> float:
        """
        Get Curve Number based on land use type
        
        Args:
            land_use: Land use classification
            
        Returns:
            Curve Number (CN)
        """
        land_use_lower = land_use.lower()
        
        if 'built' in land_use_lower or 'urban' in land_use_lower or 'commercial' in land_use_lower:
            return self.config.cn_buildup
        elif 'residential' in land_use_lower or 'mixed' in land_use_lower:
            return self.config.cn_residential
        elif 'vegetation' in land_use_lower or 'green' in land_use_lower or 'park' in land_use_lower:
            return self.config.cn_vegetation
        else:
            # Default to residential
            logger.debug(f"Unknown land use '{land_use}', defaulting to residential CN")
            return self.config.cn_residential
    
    def compute_runoff_scs_cn(self, rainfall_mm: float, land_use: str) -> float:
        """
        Compute surface runoff using SCS-CN method
        
        Args:
            rainfall_mm: Rainfall amount (mm)
            land_use: Land use type
            
        Returns:
            Runoff depth (mm)
        """
        if rainfall_mm <= 0:
            return 0.0
        
        # Get Curve Number
        cn = self.get_curve_number(land_use)
        
        # Compute potential maximum retention (S)
        s = (1000.0 / cn) - 10.0
        
        # Initial abstraction threshold
        initial_abstraction = 0.2 * s
        
        # Compute runoff
        if rainfall_mm <= initial_abstraction:
            runoff = 0.0
        else:
            numerator = (rainfall_mm - initial_abstraction) ** 2
            denominator = rainfall_mm + 0.8 * s
            runoff = numerator / denominator
        
        logger.debug(f"SCS-CN: P={rainfall_mm}mm, CN={cn}, S={s:.2f}, Runoff={runoff:.2f}mm")
        return runoff
    
    def compute_drain_stress(
        self, 
        runoff_mm: float, 
        grid_area_m2: float, 
        drain_capacity_m3: float
    ) -> float:
        """
        Compute drain stress as ratio of runoff volume to drain capacity
        
        Args:
            runoff_mm: Runoff depth (mm)
            grid_area_m2: Grid cell area (m²)
            drain_capacity_m3: Drain capacity (m³)
            
        Returns:
            Normalized drain stress (0-1)
        """
        if drain_capacity_m3 <= 0:
            logger.warning("Drain capacity is zero or negative, setting stress to 1.0")
            return 1.0
        
        # Convert runoff depth to volume
        runoff_volume_m3 = (runoff_mm / 1000.0) * grid_area_m2
        
        # Compute stress ratio
        drain_stress = runoff_volume_m3 / drain_capacity_m3
        
        # Normalize to 0-1 scale (cap at 1.0)
        drain_stress_normalized = min(drain_stress, 1.0)
        
        logger.debug(
            f"Drain stress: runoff_vol={runoff_volume_m3:.2f}m³, "
            f"capacity={drain_capacity_m3:.2f}m³, stress={drain_stress_normalized:.3f}"
        )
        
        return drain_stress_normalized
    
    def compute_drain_metrics(
        self,
        rainfall_mm: float,
        land_use: str,
        grid_area_m2: float,
        drain_capacity_m3: float
    ) -> Dict:
        """
        Compute comprehensive drain stress metrics
        
        Args:
            rainfall_mm: Rainfall amount (mm)
            land_use: Land use type
            grid_area_m2: Grid cell area (m²)
            drain_capacity_m3: Drain capacity (m³)
            
        Returns:
            Dictionary with drain metrics
        """
        runoff = self.compute_runoff_scs_cn(rainfall_mm, land_use)
        drain_stress = self.compute_drain_stress(runoff, grid_area_m2, drain_capacity_m3)
        
        return {
            'runoff_mm': runoff,
            'drain_stress': drain_stress,
            'curve_number': self.get_curve_number(land_use),
            'timestamp': datetime.utcnow()
        }


class TrafficModule:
    """
    Traffic Module: Traffic congestion indexing
    
    Normalizes traffic conditions to 0-1 scale representing systemic vulnerability.
    Uses travel time ratio as primary metric.
    """
    
    def __init__(self):
        logger.info("TrafficModule initialized")
    
    def normalize_traffic(
        self, 
        current_travel_time: float, 
        free_flow_travel_time: float
    ) -> float:
        """
        Normalize traffic congestion to 0-1 scale
        
        Args:
            current_travel_time: Current travel time (minutes)
            free_flow_travel_time: Free-flow travel time (minutes)
            
        Returns:
            Normalized traffic index (0-1)
        """
        if free_flow_travel_time <= 0:
            logger.warning("Free-flow travel time is zero or negative, setting traffic index to 0")
            return 0.0
        
        if current_travel_time < free_flow_travel_time:
            logger.debug("Current travel time less than free-flow, setting to free-flow")
            current_travel_time = free_flow_travel_time
        
        # Compute ratio
        ratio = current_travel_time / free_flow_travel_time
        
        # Normalize: ratio of 1.0 = no congestion (index 0), ratio of 3.0+ = severe (index 1.0)
        # Linear scaling: (ratio - 1) / 2, capped at 1.0
        traffic_index = min((ratio - 1.0) / 2.0, 1.0)
        
        logger.debug(
            f"Traffic: current={current_travel_time}min, "
            f"free_flow={free_flow_travel_time}min, index={traffic_index:.3f}"
        )
        
        return traffic_index
    
    def compute_traffic_index(
        self,
        congestion_level: Optional[float] = None,
        current_travel_time: Optional[float] = None,
        free_flow_travel_time: Optional[float] = None
    ) -> Dict:
        """
        Compute traffic index from available data
        
        Args:
            congestion_level: Direct congestion index (0-1) if available
            current_travel_time: Current travel time (minutes)
            free_flow_travel_time: Free-flow travel time (minutes)
            
        Returns:
            Dictionary with traffic metrics
        """
        if congestion_level is not None:
            # Use direct congestion level
            traffic_index = max(0.0, min(congestion_level, 1.0))
        elif current_travel_time is not None and free_flow_travel_time is not None:
            # Compute from travel times
            traffic_index = self.normalize_traffic(current_travel_time, free_flow_travel_time)
        else:
            # No data available
            logger.warning("No traffic data available, setting index to 0")
            traffic_index = 0.0
        
        return {
            'traffic_index': traffic_index,
            'timestamp': datetime.utcnow()
        }


class USPSCalculator:
    """
    USPS Calculator: Urban System Pressure Score computation
    
    Computes composite score using weighted aggregation of:
    - Rain Index (hazard trigger)
    - Drain Stress (hazard amplifier)
    - Traffic Index (systemic vulnerability)
    
    Formula:
        USPS = w1 * RainIndex + w2 * DrainStress + w3 * TrafficIndex
    
    Severity Classification:
        0.0 - 0.3: Stable
        0.3 - 0.6: Watch
        0.6 - 0.8: High Alert
        0.8 - 1.0: Critical
    """
    
    def __init__(self, config: EnvironmentalConfig):
        self.config = config
        
        # Validate weights sum to 1.0
        total_weight = config.weight_rain + config.weight_drain + config.weight_traffic
        if not math.isclose(total_weight, 1.0, rel_tol=1e-5):
            logger.warning(f"Weights sum to {total_weight}, not 1.0. Normalizing...")
            self.config.weight_rain /= total_weight
            self.config.weight_drain /= total_weight
            self.config.weight_traffic /= total_weight
        
        logger.info(
            f"USPSCalculator initialized with weights: "
            f"rain={config.weight_rain:.2f}, drain={config.weight_drain:.2f}, "
            f"traffic={config.weight_traffic:.2f}"
        )
    
    def compute_usps(
        self,
        rain_index: float,
        drain_stress: float,
        traffic_index: float
    ) -> float:
        """
        Compute Urban System Pressure Score
        
        Args:
            rain_index: Normalized rain index (0-1)
            drain_stress: Normalized drain stress (0-1)
            traffic_index: Normalized traffic index (0-1)
            
        Returns:
            USPS score (0-1)
        """
        usps = (
            self.config.weight_rain * rain_index +
            self.config.weight_drain * drain_stress +
            self.config.weight_traffic * traffic_index
        )
        
        # Ensure bounds
        usps = max(0.0, min(usps, 1.0))
        
        logger.debug(
            f"USPS computed: rain={rain_index:.3f}, drain={drain_stress:.3f}, "
            f"traffic={traffic_index:.3f} -> USPS={usps:.3f}"
        )
        
        return usps
    
    def classify_severity(self, usps: float) -> str:
        """
        Classify USPS score into severity level
        
        Args:
            usps: USPS score (0-1)
            
        Returns:
            Severity level string
        """
        if usps < self.config.threshold_stable:
            return "Stable"
        elif usps < self.config.threshold_watch:
            return "Watch"
        elif usps < self.config.threshold_high_alert:
            return "High Alert"
        else:
            return "Critical"
    
    def compute_full_assessment(
        self,
        rain_index: float,
        drain_stress: float,
        traffic_index: float
    ) -> Dict:
        """
        Compute full USPS assessment with severity classification
        
        Args:
            rain_index: Normalized rain index (0-1)
            drain_stress: Normalized drain stress (0-1)
            traffic_index: Normalized traffic index (0-1)
            
        Returns:
            Dictionary with USPS metrics
        """
        usps = self.compute_usps(rain_index, drain_stress, traffic_index)
        severity = self.classify_severity(usps)
        
        return {
            'rain_index': rain_index,
            'drain_stress': drain_stress,
            'traffic_index': traffic_index,
            'usps_score': usps,
            'severity_level': severity,
            'timestamp': datetime.utcnow(),
            'weights': {
                'rain': self.config.weight_rain,
                'drain': self.config.weight_drain,
                'traffic': self.config.weight_traffic
            }
        }


class EnvironmentalEngine:
    """
    Main Environmental Engine: Orchestrates all modules
    
    Provides unified interface for environmental stress modeling.
    """
    
    def __init__(self, config: Optional[EnvironmentalConfig] = None):
        self.config = config or EnvironmentalConfig()
        
        # Initialize modules
        self.rain_module = RainModule(self.config)
        self.drain_module = DrainStressModule(self.config)
        self.traffic_module = TrafficModule()
        self.usps_calculator = USPSCalculator(self.config)
        
        logger.info("EnvironmentalEngine initialized successfully")
    
    def compute_environmental_state(
        self,
        # Rain inputs
        rainfall_mm: float,
        accumulated_1hr: float,
        # Drain inputs
        land_use: str,
        grid_area_m2: float,
        drain_capacity_m3: float,
        # Traffic inputs
        traffic_congestion: Optional[float] = None,
        current_travel_time: Optional[float] = None,
        free_flow_travel_time: Optional[float] = None
    ) -> Dict:
        """
        Compute complete environmental state for a grid cell
        
        Args:
            rainfall_mm: Current rainfall intensity (mm/hr)
            accumulated_1hr: Accumulated rainfall in last hour (mm)
            land_use: Land use type
            grid_area_m2: Grid cell area (m²)
            drain_capacity_m3: Drain capacity (m³)
            traffic_congestion: Direct traffic congestion index (0-1)
            current_travel_time: Current travel time (minutes)
            free_flow_travel_time: Free-flow travel time (minutes)
            
        Returns:
            Complete environmental state dictionary
        """
        # Compute rain metrics
        rain_metrics = self.rain_module.compute_rain_index(rainfall_mm, accumulated_1hr)
        
        # Compute drain metrics
        drain_metrics = self.drain_module.compute_drain_metrics(
            accumulated_1hr,  # Use accumulated rainfall for runoff
            land_use,
            grid_area_m2,
            drain_capacity_m3
        )
        
        # Compute traffic metrics
        traffic_metrics = self.traffic_module.compute_traffic_index(
            traffic_congestion,
            current_travel_time,
            free_flow_travel_time
        )
        
        # Compute USPS
        usps_assessment = self.usps_calculator.compute_full_assessment(
            rain_metrics['rain_index'],
            drain_metrics['drain_stress'],
            traffic_metrics['traffic_index']
        )
        
        # Combine all metrics
        return {
            'rain': rain_metrics,
            'drain': drain_metrics,
            'traffic': traffic_metrics,
            'usps': usps_assessment,
            'timestamp': datetime.utcnow()
        }


# Global engine instance
_engine_instance: Optional[EnvironmentalEngine] = None


def get_environmental_engine() -> EnvironmentalEngine:
    """Get or create global environmental engine instance"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = EnvironmentalEngine()
    return _engine_instance
