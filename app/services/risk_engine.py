"""
HRVC Risk Engine - Layer 3
Calculates risk scores per grid cell using:
Risk = (Hazard × Exposure × Vulnerability) ÷ Capacity
"""
from typing import Dict, List, Optional
import math


class RiskEngine:
    """Calculates flood risk scores for grid cells"""
    
    def __init__(self):
        # Normalization weights for each component
        self.hazard_weights = {
            'rainfall': 0.4,
            'river_level': 0.35,
            'soil_saturation': 0.25
        }
        
        self.exposure_weights = {
            'population_density': 0.6,
            'traffic_density': 0.4
        }
        
        self.vulnerability_weights = {
            'slum_percentage': 0.4,
            'elderly_percentage': 0.3,
            'low_elevation_percentage': 0.3
        }
        
        self.capacity_weights = {
            'shelter_count': 0.4,
            'hospital_beds': 0.35,
            'drain_strength': 0.25
        }
    
    def calculate_hazard_score(self, cell_data: Dict) -> float:
        """Calculate hazard component (0-100)"""
        rainfall = self._normalize(cell_data.get('rainfall_mm', 0), 0, 200)
        river_level = self._normalize(cell_data.get('river_level_m', 0), 0, 10)
        soil_sat = self._normalize(cell_data.get('soil_saturation_pct', 0), 0, 100)
        
        hazard = (
            rainfall * self.hazard_weights['rainfall'] +
            river_level * self.hazard_weights['river_level'] +
            soil_sat * self.hazard_weights['soil_saturation']
        )
        return hazard * 100
    
    def calculate_exposure_score(self, cell_data: Dict) -> float:
        """Calculate exposure component (0-100)"""
        pop_density = self._normalize(cell_data.get('population_density', 0), 0, 50000)
        traffic_density = self._normalize(cell_data.get('traffic_density', 0), 0, 1000)
        
        exposure = (
            pop_density * self.exposure_weights['population_density'] +
            traffic_density * self.exposure_weights['traffic_density']
        )
        return exposure * 100
    
    def calculate_vulnerability_score(self, cell_data: Dict) -> float:
        """Calculate vulnerability component (0-100)"""
        slum_pct = cell_data.get('slum_percentage', 0)
        elderly_pct = cell_data.get('elderly_percentage', 0)
        low_elev_pct = cell_data.get('low_elevation_percentage', 0)
        
        vulnerability = (
            slum_pct * self.vulnerability_weights['slum_percentage'] +
            elderly_pct * self.vulnerability_weights['elderly_percentage'] +
            low_elev_pct * self.vulnerability_weights['low_elevation_percentage']
        )
        return vulnerability
    
    def calculate_capacity_score(self, cell_data: Dict) -> float:
        """Calculate capacity component (0-100)"""
        shelters = self._normalize(cell_data.get('shelter_count', 0), 0, 10)
        hospital_beds = self._normalize(cell_data.get('hospital_beds', 0), 0, 500)
        drain_strength = self._normalize(cell_data.get('drain_strength', 0), 0, 100)
        
        capacity = (
            shelters * self.capacity_weights['shelter_count'] +
            hospital_beds * self.capacity_weights['hospital_beds'] +
            drain_strength * self.capacity_weights['drain_strength']
        )
        return max(capacity * 100, 1)  # Avoid division by zero
    
    def calculate_risk_score(self, cell_data: Dict) -> Dict:
        """
        Calculate overall risk score and components
        Returns dict with risk_score and breakdown
        """
        hazard = self.calculate_hazard_score(cell_data)
        exposure = self.calculate_exposure_score(cell_data)
        vulnerability = self.calculate_vulnerability_score(cell_data)
        capacity = self.calculate_capacity_score(cell_data)
        
        # Risk = (H × E × V) ÷ C
        risk_score = (hazard * exposure * vulnerability) / (capacity * 100)
        risk_score = min(risk_score, 100)  # Cap at 100
        
        return {
            'risk_score': round(risk_score, 2),
            'risk_level': self._get_risk_level(risk_score),
            'components': {
                'hazard': round(hazard, 2),
                'exposure': round(exposure, 2),
                'vulnerability': round(vulnerability, 2),
                'capacity': round(capacity, 2)
            }
        }
    
    def calculate_grid_risks(self, grid_cells: List[Dict]) -> List[Dict]:
        """Calculate risk for all grid cells"""
        results = []
        for cell in grid_cells:
            risk_data = self.calculate_risk_score(cell)
            results.append({
                **cell,
                **risk_data
            })
        return results
    
    def get_ward_priorities(self, grid_cells: List[Dict]) -> List[Dict]:
        """
        Aggregate grid cells by ward and return priority list
        Sorted by average risk score
        """
        ward_data = {}
        
        for cell in grid_cells:
            ward_id = cell.get('ward_id', 'unknown')
            if ward_id not in ward_data:
                ward_data[ward_id] = {
                    'ward_id': ward_id,
                    'ward_name': cell.get('ward_name', f'Ward {ward_id}'),
                    'total_risk': 0,
                    'cell_count': 0,
                    'high_risk_cells': 0,
                    'max_risk': 0
                }
            
            risk_score = cell.get('risk_score', 0)
            ward_data[ward_id]['total_risk'] += risk_score
            ward_data[ward_id]['cell_count'] += 1
            ward_data[ward_id]['max_risk'] = max(ward_data[ward_id]['max_risk'], risk_score)
            
            if risk_score >= 70:
                ward_data[ward_id]['high_risk_cells'] += 1
        
        # Calculate averages and sort
        ward_list = []
        for ward in ward_data.values():
            ward['avg_risk'] = round(ward['total_risk'] / ward['cell_count'], 2)
            ward['priority_level'] = self._get_risk_level(ward['avg_risk'])
            ward_list.append(ward)
        
        # Sort by average risk (descending)
        ward_list.sort(key=lambda x: x['avg_risk'], reverse=True)
        
        # Add priority rank
        for idx, ward in enumerate(ward_list, 1):
            ward['priority_rank'] = idx
        
        return ward_list
    
    @staticmethod
    def _normalize(value: float, min_val: float, max_val: float) -> float:
        """Normalize value to 0-1 range"""
        if max_val == min_val:
            return 0
        return max(0, min(1, (value - min_val) / (max_val - min_val)))
    
    @staticmethod
    def _get_risk_level(score: float) -> str:
        """Convert risk score to categorical level"""
        if score >= 80:
            return 'CRITICAL'
        elif score >= 60:
            return 'HIGH'
        elif score >= 40:
            return 'MEDIUM'
        elif score >= 20:
            return 'LOW'
        else:
            return 'MINIMAL'
