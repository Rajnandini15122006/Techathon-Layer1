"""
Synthetic Spatial Data Generator for Pune
Creates realistic spatial patterns based on geographic logic
"""
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, LineString
from shapely.ops import unary_union
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class SyntheticDataGenerator:
    """
    Generates spatially realistic synthetic data for Pune grid
    Based on actual geographic patterns and disaster risk logic
    """
    
    # Pune approximate center (in lat/lon)
    PUNE_CENTER_LAT = 18.5204
    PUNE_CENTER_LON = 73.8567
    
    def __init__(self, grid_gdf: gpd.GeoDataFrame):
        """
        Initialize with grid in UTM coordinates
        
        Args:
            grid_gdf: GeoDataFrame with grid cells in EPSG:32643
        """
        self.grid_gdf = grid_gdf.copy()
        self.crs = grid_gdf.crs
        
        # Calculate grid center and bounds
        self.bounds = grid_gdf.total_bounds
        self.center_x = (self.bounds[0] + self.bounds[2]) / 2
        self.center_y = (self.bounds[1] + self.bounds[3]) / 2
        
        logger.info(f"Initialized synthetic data generator")
        logger.info(f"Grid center (UTM): ({self.center_x:.2f}, {self.center_y:.2f})")
        logger.info(f"Grid bounds: {self.bounds}")
    
    def generate_synthetic_river(self) -> LineString:
        """
        Generate synthetic river line flowing through Pune
        Simulates Mula-Mutha river system
        """
        # River flows roughly NW to SE through Pune
        # Create meandering river line
        
        minx, miny, maxx, maxy = self.bounds
        
        # Start from northwest
        start_x = minx + (maxx - minx) * 0.2
        start_y = maxy - (maxy - miny) * 0.1
        
        # End at southeast
        end_x = maxx - (maxx - minx) * 0.1
        end_y = miny + (maxy - miny) * 0.2
        
        # Create meandering points
        num_points = 20
        river_points = []
        
        for i in range(num_points):
            t = i / (num_points - 1)
            
            # Linear interpolation with sinusoidal meander
            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t
            
            # Add meander (perpendicular offset)
            meander_amplitude = 2000  # 2km meander
            meander = meander_amplitude * np.sin(t * np.pi * 4)
            
            # Perpendicular direction
            dx = end_x - start_x
            dy = end_y - start_y
            length = np.sqrt(dx**2 + dy**2)
            perp_x = -dy / length
            perp_y = dx / length
            
            x += perp_x * meander
            y += perp_y * meander
            
            river_points.append((x, y))
        
        river = LineString(river_points)
        logger.info(f"Generated synthetic river: {river.length/1000:.2f} km")
        
        return river
    
    def compute_elevation(self) -> np.ndarray:
        """
        Generate realistic elevation pattern
        - Higher in southwest (Sahyadri hills)
        - Lower near river
        - Smooth gradient
        """
        logger.info("Generating synthetic elevation...")
        
        elevations = []
        
        for idx, cell in self.grid_gdf.iterrows():
            centroid = cell.geometry.centroid
            x, y = centroid.x, centroid.y
            
            # Distance from center
            dx = x - self.center_x
            dy = y - self.center_y
            
            # Base elevation: higher in southwest
            # Southwest is negative dx, negative dy
            sw_factor = -dx - dy
            sw_elevation = sw_factor / 50000 * 150  # Up to 150m increase to SW
            
            # Base elevation around 560m (Pune average)
            base_elevation = 560
            
            # Add southwest gradient
            elevation = base_elevation + sw_elevation
            
            # Add some local variation (hills)
            local_variation = 20 * np.sin(x / 5000) * np.cos(y / 5000)
            elevation += local_variation
            
            # Clamp to realistic range
            elevation = np.clip(elevation, 500, 800)
            
            elevations.append(elevation)
        
        elevations = np.array(elevations)
        logger.info(f"Elevation range: {elevations.min():.1f}m to {elevations.max():.1f}m")
        
        return elevations
    
    def compute_drain_distance(self, river: LineString) -> np.ndarray:
        """
        Compute distance from each cell to synthetic river
        """
        logger.info("Computing drain distances...")
        
        distances = []
        
        for idx, cell in self.grid_gdf.iterrows():
            centroid = cell.geometry.centroid
            distance = centroid.distance(river)
            distances.append(distance)
        
        distances = np.array(distances)
        logger.info(f"Drain distance range: {distances.min():.1f}m to {distances.max()/1000:.2f}km")
        
        return distances
    
    def compute_land_use(self, distance_from_center: np.ndarray) -> np.ndarray:
        """
        Generate land use based on distance from city center
        - Urban core: Commercial/Residential
        - Middle ring: Residential
        - Outer ring: Mixed/Agricultural
        - Far areas: Forest (if in hills)
        """
        logger.info("Generating land use patterns...")
        
        land_uses = []
        elevations = self.compute_elevation()
        
        for i, (idx, cell) in enumerate(self.grid_gdf.iterrows()):
            dist = distance_from_center[i]
            elev = elevations[i]
            
            if dist < 3000:  # Within 3km of center
                if np.random.random() < 0.6:
                    land_use = "Commercial"
                else:
                    land_use = "Residential"
            elif dist < 8000:  # 3-8km from center
                land_use = "Residential"
            elif dist < 15000:  # 8-15km from center
                if elev > 650:  # Hilly areas
                    land_use = "Forest"
                else:
                    land_use = "Mixed"
            else:  # Beyond 15km
                if elev > 650:
                    land_use = "Forest"
                else:
                    land_use = "Agricultural"
            
            land_uses.append(land_use)
        
        land_uses = np.array(land_uses)
        unique, counts = np.unique(land_uses, return_counts=True)
        logger.info("Land use distribution:")
        for lu, count in zip(unique, counts):
            logger.info(f"  {lu}: {count} cells ({count/len(land_uses)*100:.1f}%)")
        
        return land_uses
    
    def compute_population_density(self, distance_from_center: np.ndarray, land_uses: np.ndarray) -> np.ndarray:
        """
        Generate population density
        - Highest in city center
        - Decreases radially
        - Depends on land use
        """
        logger.info("Generating population density...")
        
        pop_densities = []
        
        for i, land_use in enumerate(land_uses):
            dist = distance_from_center[i]
            
            # Base density by land use (people per m²)
            if land_use == "Commercial":
                base_density = 0.015
            elif land_use == "Residential":
                base_density = 0.012
            elif land_use == "Mixed":
                base_density = 0.006
            elif land_use == "Agricultural":
                base_density = 0.001
            else:  # Forest
                base_density = 0.0001
            
            # Distance decay
            distance_factor = np.exp(-dist / 10000)  # Exponential decay
            
            density = base_density * (0.3 + 0.7 * distance_factor)
            pop_densities.append(density)
        
        pop_densities = np.array(pop_densities)
        logger.info(f"Population density range: {pop_densities.min():.6f} to {pop_densities.max():.6f} per m²")
        
        return pop_densities
    
    def compute_slum_density(self, drain_distances: np.ndarray, distance_from_center: np.ndarray) -> np.ndarray:
        """
        Generate slum density
        - Higher near rivers (informal settlements)
        - Higher in middle ring (not core, not periphery)
        - Clusters along transport corridors
        """
        logger.info("Generating slum density...")
        
        slum_densities = []
        
        for i in range(len(self.grid_gdf)):
            drain_dist = drain_distances[i]
            center_dist = distance_from_center[i]
            
            # Higher near river
            river_factor = np.exp(-drain_dist / 1000)  # High within 1km of river
            
            # Higher in middle ring (3-10km from center)
            if 3000 < center_dist < 10000:
                ring_factor = 1.0
            elif center_dist < 3000:
                ring_factor = 0.3  # Lower in core
            else:
                ring_factor = 0.5  # Lower in periphery
            
            # Slum density as percentage of cell area
            slum_density = (river_factor * 8 + ring_factor * 3) * np.random.uniform(0.5, 1.5)
            slum_density = np.clip(slum_density, 0, 15)  # Max 15%
            
            slum_densities.append(slum_density)
        
        slum_densities = np.array(slum_densities)
        logger.info(f"Slum density range: {slum_densities.min():.2f}% to {slum_densities.max():.2f}%")
        
        return slum_densities
    
    def compute_flood_depth(self, elevations: np.ndarray, drain_distances: np.ndarray) -> np.ndarray:
        """
        Generate flood depth
        - Higher in low elevation areas
        - Higher near drains
        - Logical correlation
        """
        logger.info("Generating flood depth...")
        
        flood_depths = []
        
        # Normalize elevation (inverse - lower elevation = higher flood risk)
        elev_normalized = (elevations.max() - elevations) / (elevations.max() - elevations.min())
        
        # Normalize drain distance (inverse - closer = higher flood risk)
        drain_normalized = 1 - (drain_distances / drain_distances.max())
        
        for i in range(len(self.grid_gdf)):
            # Flood depth based on elevation and proximity to drain
            flood_risk = elev_normalized[i] * 0.6 + drain_normalized[i] * 0.4
            
            # Convert to flood depth (0-3 meters)
            flood_depth = flood_risk * 3.0
            
            # Add some variability
            flood_depth *= np.random.uniform(0.7, 1.3)
            
            # Only significant floods in high-risk areas
            if flood_risk < 0.3:
                flood_depth *= 0.2
            
            flood_depths.append(flood_depth)
        
        flood_depths = np.array(flood_depths)
        logger.info(f"Flood depth range: {flood_depths.min():.2f}m to {flood_depths.max():.2f}m")
        
        return flood_depths
    
    def compute_infrastructure(self, distance_from_center: np.ndarray, land_uses: np.ndarray) -> np.ndarray:
        """
        Generate infrastructure count
        - More hospitals in urban core
        - Shelters distributed
        """
        logger.info("Generating infrastructure...")
        
        infra_counts = []
        
        for i, land_use in enumerate(land_uses):
            dist = distance_from_center[i]
            
            # Probability of infrastructure
            if land_use == "Commercial" and dist < 5000:
                prob = 0.15
            elif land_use == "Residential" and dist < 8000:
                prob = 0.08
            elif land_use == "Mixed":
                prob = 0.03
            else:
                prob = 0.01
            
            # Random infrastructure count
            if np.random.random() < prob:
                count = np.random.randint(1, 4)
            else:
                count = 0
            
            infra_counts.append(count)
        
        infra_counts = np.array(infra_counts)
        total_infra = infra_counts.sum()
        logger.info(f"Total infrastructure: {total_infra} facilities")
        
        return infra_counts
    
    def compute_complaint_density(self, flood_depths: np.ndarray, pop_densities: np.ndarray) -> np.ndarray:
        """
        Generate complaint density
        - Higher where floods are worse
        - Higher where population is higher
        """
        logger.info("Generating complaint density...")
        
        # Normalize inputs
        flood_norm = flood_depths / flood_depths.max() if flood_depths.max() > 0 else flood_depths
        pop_norm = pop_densities / pop_densities.max() if pop_densities.max() > 0 else pop_densities
        
        # Complaints per km²
        complaint_densities = (flood_norm * 0.7 + pop_norm * 0.3) * 50
        
        # Add variability
        complaint_densities *= np.random.uniform(0.5, 1.5, len(complaint_densities))
        
        logger.info(f"Complaint density range: {complaint_densities.min():.2f} to {complaint_densities.max():.2f} per km²")
        
        return complaint_densities
    
    def generate_all_attributes(self) -> gpd.GeoDataFrame:
        """
        Generate all synthetic attributes with spatial logic
        """
        logger.info("=" * 80)
        logger.info("GENERATING SYNTHETIC SPATIAL DATA")
        logger.info("=" * 80)
        
        # Calculate distance from center for all cells
        logger.info("Computing distances from city center...")
        distances_from_center = []
        for idx, cell in self.grid_gdf.iterrows():
            centroid = cell.geometry.centroid
            dist = np.sqrt((centroid.x - self.center_x)**2 + (centroid.y - self.center_y)**2)
            distances_from_center.append(dist)
        distances_from_center = np.array(distances_from_center)
        
        # Generate synthetic river
        river = self.generate_synthetic_river()
        
        # Generate all attributes
        elevations = self.compute_elevation()
        drain_distances = self.compute_drain_distance(river)
        land_uses = self.compute_land_use(distances_from_center)
        pop_densities = self.compute_population_density(distances_from_center, land_uses)
        slum_densities = self.compute_slum_density(drain_distances, distances_from_center)
        flood_depths = self.compute_flood_depth(elevations, drain_distances)
        infra_counts = self.compute_infrastructure(distances_from_center, land_uses)
        complaint_densities = self.compute_complaint_density(flood_depths, pop_densities)
        
        # Add to grid
        self.grid_gdf['elevation_mean'] = elevations
        self.grid_gdf['drain_distance'] = drain_distances
        self.grid_gdf['land_use'] = land_uses
        self.grid_gdf['population_density'] = pop_densities
        self.grid_gdf['slum_density'] = slum_densities
        self.grid_gdf['flood_depth_avg'] = flood_depths
        self.grid_gdf['infra_count'] = infra_counts
        self.grid_gdf['complaint_density'] = complaint_densities
        
        logger.info("=" * 80)
        logger.info("SYNTHETIC DATA GENERATION COMPLETE")
        logger.info("=" * 80)
        
        return self.grid_gdf
