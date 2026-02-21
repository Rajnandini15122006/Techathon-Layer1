"""
USPS Data Generator
Generates synthetic data for Urban System Pressure Score testing
"""
import random
from typing import List, Dict


class USPSDataGenerator:
    """Generate synthetic grid data with USPS subsystem fields"""
    
    def generate_grid_with_usps_data(
        self, 
        lat_min: float, 
        lat_max: float, 
        lon_min: float, 
        lon_max: float, 
        grid_size_km: float = 1.0
    ) -> List[Dict]:
        """
        Generate grid cells with USPS subsystem data
        
        Args:
            lat_min, lat_max: Latitude bounds
            lon_min, lon_max: Longitude bounds
            grid_size_km: Grid cell size in kilometers
        
        Returns:
            List of grid cells with USPS fields
        """
        # Approximate degrees per km
        lat_step = grid_size_km / 111.0
        lon_step = grid_size_km / (111.0 * 0.9)
        
        grid_cells = []
        cell_id = 1
        ward_id = 1
        cells_per_ward = 10
        
        lat = lat_min
        while lat < lat_max:
            lon = lon_min
            while lon < lon_max:
                # Calculate cell center
                center_lat = lat + lat_step / 2
                center_lon = lon + lon_step / 2
                
                # Distance from Pune center (18.5204, 73.8567)
                dist_from_center = ((center_lat - 18.5204)**2 + (center_lon - 73.8567)**2)**0.5 * 111
                
                # Generate USPS fields based on location
                cell = self._generate_cell_usps_data(
                    cell_id, ward_id, center_lat, center_lon, dist_from_center
                )
                
                grid_cells.append(cell)
                cell_id += 1
                
                # Update ward every N cells
                if cell_id % cells_per_ward == 0:
                    ward_id += 1
                
                lon += lon_step
            lat += lat_step
        
        return grid_cells
    
    def _generate_cell_usps_data(
        self, 
        cell_id: int, 
        ward_id: int, 
        lat: float, 
        lon: float, 
        dist_from_center: float
    ) -> Dict:
        """Generate USPS subsystem data for a single cell"""
        
        # Determine if this is a high-stress area (random but spatially correlated)
        is_urban_core = dist_from_center < 5
        is_stressed = random.random() < (0.4 if is_urban_core else 0.2)
        
        # Base stress level
        if is_stressed:
            base_stress = random.uniform(60, 95)
        else:
            base_stress = random.uniform(20, 60)
        
        # Generate correlated subsystem values
        # When one system is stressed, others tend to be stressed too
        
        # Rain accumulation (% of drainage capacity)
        rain_accumulation = base_stress + random.uniform(-15, 15)
        rain_accumulation = max(0, min(100, rain_accumulation))
        
        # Drain capacity load (% of max capacity)
        # Correlates with rain accumulation
        drain_load = rain_accumulation * random.uniform(0.8, 1.2)
        drain_load = max(0, min(100, drain_load))
        
        # Road congestion (% of road capacity)
        # Higher in urban core, increases with flooding
        if is_urban_core:
            road_congestion = base_stress * random.uniform(0.9, 1.3)
        else:
            road_congestion = base_stress * random.uniform(0.5, 0.9)
        road_congestion = max(0, min(100, road_congestion))
        
        # Hospital occupancy (% of beds occupied)
        # Increases during disasters
        if is_stressed:
            hospital_occupancy = random.uniform(70, 95)
        else:
            hospital_occupancy = random.uniform(40, 75)
        
        # Power substation stress (% of capacity)
        # Correlates with overall system stress
        power_stress = base_stress * random.uniform(0.7, 1.1)
        power_stress = max(0, min(100, power_stress))
        
        # Create scenarios for cascading risk demonstration
        # 10% chance of multi-system failure scenario
        if random.random() < 0.1:
            # Simulate cascading failure scenario
            multiplier = random.uniform(1.2, 1.5)
            rain_accumulation = min(100, rain_accumulation * multiplier)
            drain_load = min(100, drain_load * multiplier)
            road_congestion = min(100, road_congestion * multiplier)
            power_stress = min(100, power_stress * multiplier)
        
        return {
            'cell_id': cell_id,
            'latitude': lat,
            'longitude': lon,
            'ward_id': ward_id,
            'ward_name': f'Ward {ward_id}',
            
            # USPS Subsystem Fields
            'rain_accumulation_pct': round(rain_accumulation, 2),
            'drain_capacity_load_pct': round(drain_load, 2),
            'road_congestion_pct': round(road_congestion, 2),
            'hospital_occupancy_pct': round(hospital_occupancy, 2),
            'power_stress_pct': round(power_stress, 2),
            
            # Additional context
            'is_urban_core': is_urban_core,
            'distance_from_center_km': round(dist_from_center, 2)
        }
