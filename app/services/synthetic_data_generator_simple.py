"""
Simple Synthetic Data Generator for Risk Engine
Generates grid cells with HRVC risk fields without geospatial dependencies
"""
import random
from typing import List, Dict


class SyntheticDataGenerator:
    """Generate synthetic grid data for risk calculation"""
    
    def generate_grid_with_data(
        self, 
        lat_min: float, 
        lat_max: float, 
        lon_min: float, 
        lon_max: float, 
        grid_size_km: float = 1.0
    ) -> List[Dict]:
        """
        Generate grid cells with synthetic HRVC data
        
        Args:
            lat_min, lat_max: Latitude bounds
            lon_min, lon_max: Longitude bounds
            grid_size_km: Grid cell size in kilometers
        
        Returns:
            List of grid cells with all HRVC fields
        """
        # Approximate degrees per km
        lat_step = grid_size_km / 111.0
        lon_step = grid_size_km / (111.0 * 0.9)  # Adjust for latitude
        
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
                
                # Generate HRVC fields based on location
                cell = self._generate_cell_data(
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
    
    def _generate_cell_data(
        self, 
        cell_id: int, 
        ward_id: int, 
        lat: float, 
        lon: float, 
        dist_from_center: float
    ) -> Dict:
        """Generate all HRVC fields for a single cell"""
        
        # HAZARD COMPONENT
        # Rainfall: Higher in monsoon season, varies by location
        rainfall_mm = random.uniform(50, 200)
        
        # River level: Higher near water bodies (simulated)
        river_proximity = random.random()
        river_level_m = river_proximity * random.uniform(0, 10)
        
        # Soil saturation: Correlates with rainfall and drainage
        soil_saturation_pct = min(100, rainfall_mm / 2 + random.uniform(-20, 20))
        
        # EXPOSURE COMPONENT
        # Population density: Higher near city center
        if dist_from_center < 5:
            pop_density = random.uniform(20000, 50000)
        elif dist_from_center < 10:
            pop_density = random.uniform(10000, 25000)
        else:
            pop_density = random.uniform(1000, 10000)
        
        # Traffic density: Correlates with population
        traffic_density = pop_density * random.uniform(0.01, 0.03)
        
        # VULNERABILITY COMPONENT
        # Slum percentage: Higher in certain areas
        if dist_from_center < 3:
            slum_percentage = random.uniform(0, 5)
        elif dist_from_center < 8:
            slum_percentage = random.uniform(5, 15)
        else:
            slum_percentage = random.uniform(0, 8)
        
        # Elderly percentage
        elderly_percentage = random.uniform(8, 18)
        
        # Low elevation percentage (flood-prone areas)
        low_elevation_percentage = random.uniform(10, 60)
        
        # CAPACITY COMPONENT
        # Shelter count: More in urban areas
        if dist_from_center < 5:
            shelter_count = random.randint(2, 8)
        elif dist_from_center < 10:
            shelter_count = random.randint(1, 4)
        else:
            shelter_count = random.randint(0, 2)
        
        # Hospital beds: Concentrated in urban core
        if dist_from_center < 5:
            hospital_beds = random.randint(100, 500)
        elif dist_from_center < 10:
            hospital_beds = random.randint(20, 150)
        else:
            hospital_beds = random.randint(0, 50)
        
        # Drain strength: Better in developed areas
        if dist_from_center < 5:
            drain_strength = random.uniform(60, 95)
        elif dist_from_center < 10:
            drain_strength = random.uniform(40, 70)
        else:
            drain_strength = random.uniform(20, 50)
        
        return {
            'cell_id': cell_id,
            'latitude': lat,
            'longitude': lon,
            'ward_id': ward_id,
            'ward_name': f'Ward {ward_id}',
            
            # Hazard
            'rainfall_mm': round(rainfall_mm, 2),
            'river_level_m': round(river_level_m, 2),
            'soil_saturation_pct': round(soil_saturation_pct, 2),
            
            # Exposure
            'population_density': round(pop_density, 2),
            'traffic_density': round(traffic_density, 2),
            
            # Vulnerability
            'slum_percentage': round(slum_percentage, 2),
            'elderly_percentage': round(elderly_percentage, 2),
            'low_elevation_percentage': round(low_elevation_percentage, 2),
            
            # Capacity
            'shelter_count': shelter_count,
            'hospital_beds': hospital_beds,
            'drain_strength': round(drain_strength, 2),
            
            # USPS fields
            'rain_accumulation_mm': round(rainfall_mm * random.uniform(0.8, 1.2), 2),
            'drain_capacity_percent': round(100 - soil_saturation_pct * random.uniform(0.5, 1.0), 2),
            'road_congestion_percent': round(min(100, traffic_density / 500 * 100), 2),
            'hospital_occupancy_percent': round(random.uniform(40, 90), 2),
            'power_load_percent': round(random.uniform(50, 95), 2),
            
            # HRVC aggregated fields
            'hazard': round((rainfall_mm/200 + river_level_m/10 + soil_saturation_pct/100) / 3, 3),
            'exposure': round(pop_density / 50000, 3),
            'vulnerability': round((slum_percentage + elderly_percentage + low_elevation_percentage) / 300, 3),
            'capacity': round((shelter_count/8 + hospital_beds/500 + drain_strength/100) / 3, 3),
            
            # Additional fields
            'land_use': random.choice(['built_up', 'residential', 'commercial', 'vegetation', 'mixed']),
            'elevation': round(random.uniform(550, 650), 2)
        }
