"""
Drainage Stress Simulation Service
Simulates rainfall → drain load → overflow → flooding
"""
from typing import Dict, List, Optional
import math
from datetime import datetime


class DrainageSimulator:
    """Simulates urban drainage stress and flooding"""
    
    # Runoff coefficients by land use type
    RUNOFF_COEFFICIENTS = {
        'built_up': 0.85,
        'residential': 0.65,
        'commercial': 0.80,
        'industrial': 0.75,
        'vegetation': 0.35,
        'water_body': 0.95,
        'mixed': 0.70
    }
    
    # Grid cell area (250m x 250m = 62,500 m²)
    CELL_AREA_M2 = 62500
    
    # Scaling factor for flood depth calculation
    FLOOD_DEPTH_SCALING = 0.001  # Convert volume to depth
    
    def __init__(self):
        pass
    
    def simulate_timestep(
        self,
        grid_cells: List[Dict],
        rainfall_intensity: float,  # mm/hour
        duration_minutes: float,
        timestep: int = 0
    ) -> List[Dict]:
        """
        Simulate drainage stress for one timestep
        
        Args:
            grid_cells: List of grid cell data with drain_capacity, land_use
            rainfall_intensity: Rainfall in mm/hour
            duration_minutes: Duration in minutes
            timestep: Current timestep number
            
        Returns:
            List of grid cells with simulation results
        """
        results = []
        
        for cell in grid_cells:
            result = self._simulate_cell(
                cell,
                rainfall_intensity,
                duration_minutes
            )
            result['timestep'] = timestep
            results.append(result)
        
        return results
    
    def _simulate_cell(
        self,
        cell: Dict,
        rainfall_intensity: float,
        duration_minutes: float
    ) -> Dict:
        """Simulate drainage stress for a single cell"""
        
        # Get cell properties
        land_use = cell.get('land_use', 'mixed')
        drain_capacity = cell.get('drain_capacity', 50.0)  # m³/s
        elevation = cell.get('elevation', 600.0)  # meters
        
        # Get runoff coefficient
        runoff_coef = self.RUNOFF_COEFFICIENTS.get(land_use, 0.70)
        
        # Convert rainfall to volume
        # rainfall_intensity (mm/hr) → m/hr → m³
        rainfall_m_per_hour = rainfall_intensity / 1000.0
        rainfall_volume_m3 = rainfall_m_per_hour * self.CELL_AREA_M2
        
        # Calculate runoff volume (accounting for infiltration)
        runoff_volume_m3 = rainfall_volume_m3 * runoff_coef
        
        # Convert to flow rate (m³/s)
        duration_seconds = duration_minutes * 60
        runoff_rate_m3_per_s = runoff_volume_m3 / duration_seconds if duration_seconds > 0 else 0
        
        # Calculate stress ratio
        stress_ratio = runoff_rate_m3_per_s / drain_capacity if drain_capacity > 0 else 999
        
        # Determine status
        if stress_ratio < 0.6:
            status = 'SAFE'
            status_code = 0
        elif stress_ratio < 0.85:
            status = 'HIGH_LOAD'
            status_code = 1
        elif stress_ratio <= 1.0:
            status = 'CRITICAL'
            status_code = 2
        else:
            status = 'OVERFLOW'
            status_code = 3
        
        # Calculate flood depth (only if overflow)
        flood_depth_m = 0.0
        if stress_ratio > 1.0:
            excess_volume = (runoff_rate_m3_per_s - drain_capacity) * duration_seconds
            # Spread excess water over cell area
            flood_depth_m = (excess_volume / self.CELL_AREA_M2) * 100  # Convert to cm
            flood_depth_m = min(flood_depth_m, 200.0)  # Cap at 2 meters
        
        # Calculate suggested drain upgrade
        suggested_capacity = drain_capacity
        if stress_ratio > 0.85:
            suggested_capacity = drain_capacity * 1.2  # 20% increase
        
        return {
            'cell_id': cell.get('cell_id'),
            'latitude': cell.get('latitude'),
            'longitude': cell.get('longitude'),
            'ward_name': cell.get('ward_name', 'Unknown'),
            'land_use': land_use,
            'elevation': elevation,
            'drain_capacity': drain_capacity,
            'runoff_coefficient': runoff_coef,
            'rainfall_volume_m3': round(rainfall_volume_m3, 2),
            'runoff_volume_m3': round(runoff_volume_m3, 2),
            'runoff_rate_m3_per_s': round(runoff_rate_m3_per_s, 2),
            'stress_ratio': round(stress_ratio, 3),
            'status': status,
            'status_code': status_code,
            'flood_depth_cm': round(flood_depth_m, 2),
            'suggested_capacity': round(suggested_capacity, 2)
        }
    
    def simulate_full_event(
        self,
        grid_cells: List[Dict],
        rainfall_intensity: float,
        total_duration_minutes: float,
        timestep_minutes: int = 5
    ) -> Dict:
        """
        Simulate entire rainfall event with multiple timesteps
        
        Returns:
            Dict with timestep results and summary statistics
        """
        num_timesteps = int(total_duration_minutes / timestep_minutes)
        all_timesteps = []
        
        for t in range(num_timesteps):
            timestep_results = self.simulate_timestep(
                grid_cells,
                rainfall_intensity,
                timestep_minutes,
                timestep=t
            )
            all_timesteps.append(timestep_results)
        
        # Calculate summary statistics
        final_results = all_timesteps[-1] if all_timesteps else []
        summary = self._calculate_summary(final_results)
        
        return {
            'timesteps': all_timesteps,
            'summary': summary,
            'simulation_params': {
                'rainfall_intensity': rainfall_intensity,
                'total_duration_minutes': total_duration_minutes,
                'timestep_minutes': timestep_minutes,
                'num_timesteps': num_timesteps
            }
        }
    
    def _calculate_summary(self, results: List[Dict]) -> Dict:
        """Calculate summary statistics from simulation results"""
        if not results:
            return {}
        
        total_cells = len(results)
        safe_cells = sum(1 for r in results if r['status'] == 'SAFE')
        high_load_cells = sum(1 for r in results if r['status'] == 'HIGH_LOAD')
        critical_cells = sum(1 for r in results if r['status'] == 'CRITICAL')
        overflow_cells = sum(1 for r in results if r['status'] == 'OVERFLOW')
        
        total_flood_volume = sum(
            r['flood_depth_cm'] * self.CELL_AREA_M2 / 100  # Convert to m³
            for r in results if r['flood_depth_cm'] > 0
        )
        
        flooded_area_km2 = (overflow_cells * self.CELL_AREA_M2) / 1_000_000
        
        avg_stress = sum(r['stress_ratio'] for r in results) / total_cells if total_cells > 0 else 0
        max_stress = max((r['stress_ratio'] for r in results), default=0)
        
        # Get top 5 critical zones
        critical_zones = sorted(
            [r for r in results if r['status_code'] >= 2],
            key=lambda x: x['stress_ratio'],
            reverse=True
        )[:5]
        
        return {
            'total_cells': total_cells,
            'safe_cells': safe_cells,
            'high_load_cells': high_load_cells,
            'critical_cells': critical_cells,
            'overflow_cells': overflow_cells,
            'flooded_area_km2': round(flooded_area_km2, 3),
            'total_flood_volume_m3': round(total_flood_volume, 2),
            'avg_stress_ratio': round(avg_stress, 3),
            'max_stress_ratio': round(max_stress, 3),
            'critical_zones': critical_zones
        }
