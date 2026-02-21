"""
Layer 2: Urban System Pressure Score (USPS) Engine
CORE INNOVATION: Measures system saturation BEFORE failure

Detects cascading risk when multiple subsystems approach threshold
"""
from typing import Dict, List, Tuple
import math


class USPSEngine:
    """
    Urban System Pressure Score Engine
    Measures infrastructure stress before catastrophic failure
    """
    
    def __init__(self):
        # Critical thresholds for each subsystem (%)
        self.thresholds = {
            'rain_accumulation': 80,      # 80% of drainage capacity
            'drain_capacity_load': 85,    # 85% drain saturation
            'road_congestion': 75,        # 75% road capacity
            'hospital_occupancy': 90,     # 90% hospital beds occupied
            'power_stress': 85            # 85% substation load
        }
        
        # Weights for each subsystem in overall USPS
        self.weights = {
            'rain_accumulation': 0.25,
            'drain_capacity_load': 0.25,
            'road_congestion': 0.20,
            'hospital_occupancy': 0.15,
            'power_stress': 0.15
        }
        
        # Cascading risk multiplier thresholds
        self.cascade_thresholds = {
            'warning': 2,      # 2+ systems near threshold
            'critical': 3,     # 3+ systems near threshold
            'emergency': 4     # 4+ systems near threshold
        }
    
    def calculate_subsystem_pressure(
        self, 
        current_value: float, 
        threshold: float
    ) -> float:
        """
        Calculate pressure score for a single subsystem
        Returns 0-100 where 100 = at threshold
        
        Uses exponential curve to emphasize approaching threshold
        """
        if current_value <= 0:
            return 0.0
        
        # Percentage of threshold
        pressure_ratio = (current_value / threshold) * 100
        
        # Apply exponential curve for values approaching threshold
        if pressure_ratio > 70:
            # Exponential increase as we approach threshold
            excess = pressure_ratio - 70
            pressure_ratio = 70 + (excess * 1.5)
        
        return min(pressure_ratio, 100.0)
    
    def calculate_usps(self, cell_data: Dict) -> Dict:
        """
        Calculate Urban System Pressure Score for a grid cell
        
        Args:
            cell_data: Dict with subsystem values
            
        Returns:
            Dict with USPS score, subsystem pressures, and cascade analysis
        """
        # Calculate pressure for each subsystem
        subsystem_pressures = {}
        
        # Rain accumulation pressure
        rain_accum = cell_data.get('rain_accumulation_pct', 0)
        subsystem_pressures['rain_accumulation'] = self.calculate_subsystem_pressure(
            rain_accum, self.thresholds['rain_accumulation']
        )
        
        # Drain capacity load pressure
        drain_load = cell_data.get('drain_capacity_load_pct', 0)
        subsystem_pressures['drain_capacity_load'] = self.calculate_subsystem_pressure(
            drain_load, self.thresholds['drain_capacity_load']
        )
        
        # Road congestion pressure
        road_congestion = cell_data.get('road_congestion_pct', 0)
        subsystem_pressures['road_congestion'] = self.calculate_subsystem_pressure(
            road_congestion, self.thresholds['road_congestion']
        )
        
        # Hospital occupancy pressure
        hospital_occ = cell_data.get('hospital_occupancy_pct', 0)
        subsystem_pressures['hospital_occupancy'] = self.calculate_subsystem_pressure(
            hospital_occ, self.thresholds['hospital_occupancy']
        )
        
        # Power substation stress pressure
        power_stress = cell_data.get('power_stress_pct', 0)
        subsystem_pressures['power_stress'] = self.calculate_subsystem_pressure(
            power_stress, self.thresholds['power_stress']
        )
        
        # Calculate weighted USPS
        usps_score = sum(
            subsystem_pressures[key] * self.weights[key]
            for key in subsystem_pressures
        )
        
        # Detect cascading risk
        cascade_analysis = self.analyze_cascading_risk(subsystem_pressures)
        
        # Apply cascade multiplier if multiple systems stressed
        if cascade_analysis['systems_at_risk'] >= 2:
            cascade_multiplier = 1 + (cascade_analysis['systems_at_risk'] * 0.1)
            usps_score = min(usps_score * cascade_multiplier, 100.0)
        
        return {
            'usps_score': round(usps_score, 2),
            'pressure_level': self._get_pressure_level(usps_score),
            'subsystem_pressures': {k: round(v, 2) for k, v in subsystem_pressures.items()},
            'cascade_analysis': cascade_analysis,
            'recommendations': self._generate_recommendations(
                usps_score, subsystem_pressures, cascade_analysis
            )
        }
    
    def analyze_cascading_risk(self, subsystem_pressures: Dict) -> Dict:
        """
        Analyze risk of cascading failure
        Returns warning level and affected systems
        """
        # Count systems approaching threshold (>70% pressure)
        systems_at_risk = []
        critical_systems = []
        
        for system, pressure in subsystem_pressures.items():
            if pressure >= 90:
                critical_systems.append(system)
                systems_at_risk.append(system)
            elif pressure >= 70:
                systems_at_risk.append(system)
        
        # Determine cascade level
        num_at_risk = len(systems_at_risk)
        if num_at_risk >= self.cascade_thresholds['emergency']:
            cascade_level = 'EMERGENCY'
            cascade_risk = 'EXTREME'
        elif num_at_risk >= self.cascade_thresholds['critical']:
            cascade_level = 'CRITICAL'
            cascade_risk = 'HIGH'
        elif num_at_risk >= self.cascade_thresholds['warning']:
            cascade_level = 'WARNING'
            cascade_risk = 'MODERATE'
        else:
            cascade_level = 'NORMAL'
            cascade_risk = 'LOW'
        
        return {
            'cascade_level': cascade_level,
            'cascade_risk': cascade_risk,
            'systems_at_risk': num_at_risk,
            'critical_systems': critical_systems,
            'stressed_systems': systems_at_risk,
            'cascade_warning': num_at_risk >= 2
        }
    
    def calculate_grid_usps(self, grid_cells: List[Dict]) -> List[Dict]:
        """Calculate USPS for all grid cells"""
        results = []
        for cell in grid_cells:
            usps_data = self.calculate_usps(cell)
            results.append({
                **cell,
                **usps_data
            })
        return results
    
    def get_critical_cells(
        self, 
        grid_cells: List[Dict], 
        threshold: float = 70.0
    ) -> List[Dict]:
        """Get cells with USPS above threshold"""
        return [
            cell for cell in grid_cells 
            if cell.get('usps_score', 0) >= threshold
        ]
    
    def get_cascade_warnings(self, grid_cells: List[Dict]) -> List[Dict]:
        """Get cells with cascading risk warnings"""
        return [
            cell for cell in grid_cells
            if cell.get('cascade_analysis', {}).get('cascade_warning', False)
        ]
    
    @staticmethod
    def _get_pressure_level(score: float) -> str:
        """Convert USPS score to categorical level"""
        if score >= 90:
            return 'CRITICAL'
        elif score >= 75:
            return 'SEVERE'
        elif score >= 60:
            return 'HIGH'
        elif score >= 40:
            return 'MODERATE'
        elif score >= 20:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    @staticmethod
    def _generate_recommendations(
        usps_score: float,
        subsystem_pressures: Dict,
        cascade_analysis: Dict
    ) -> List[str]:
        """Generate actionable recommendations based on USPS"""
        recommendations = []
        
        # Critical overall pressure
        if usps_score >= 90:
            recommendations.append("URGENT: Activate emergency response protocols")
            recommendations.append("Deploy all available resources to this area")
        elif usps_score >= 75:
            recommendations.append("Prepare emergency response teams")
            recommendations.append("Alert nearby hospitals and shelters")
        
        # Cascading risk warnings
        if cascade_analysis['cascade_level'] == 'EMERGENCY':
            recommendations.append("⚠️ CASCADING FAILURE IMMINENT - Multiple systems critical")
            recommendations.append("Evacuate vulnerable populations immediately")
        elif cascade_analysis['cascade_level'] == 'CRITICAL':
            recommendations.append("⚠️ High risk of cascading failure across systems")
            recommendations.append("Prepare evacuation routes and shelters")
        elif cascade_analysis['cascade_level'] == 'WARNING':
            recommendations.append("Monitor for cascading effects across systems")
        
        # Subsystem-specific recommendations
        if subsystem_pressures.get('drain_capacity_load', 0) >= 80:
            recommendations.append("🌊 Drainage system near capacity - deploy pumps")
        
        if subsystem_pressures.get('road_congestion', 0) >= 70:
            recommendations.append("🚗 Road congestion high - activate traffic management")
        
        if subsystem_pressures.get('hospital_occupancy', 0) >= 85:
            recommendations.append("🏥 Hospital capacity stressed - prepare overflow facilities")
        
        if subsystem_pressures.get('power_stress', 0) >= 80:
            recommendations.append("⚡ Power grid stressed - prepare backup generators")
        
        if subsystem_pressures.get('rain_accumulation', 0) >= 75:
            recommendations.append("🌧️ Rain accumulation critical - expect flooding")
        
        return recommendations
