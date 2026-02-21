"""
Demo grid endpoint that works without database
Generates grid data on-the-fly for demonstration
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/demo", tags=["Demo Grid"])

try:
    import geopandas as gpd
    import numpy as np
    from shapely.geometry import box, Point, LineString
    from shapely.ops import unary_union
    GEOSPATIAL_AVAILABLE = True
except ImportError:
    GEOSPATIAL_AVAILABLE = False

@router.get("/grid-geojson")
def get_demo_grid():
    """
    Generate demo grid WITHOUT database
    Returns GeoJSON directly for map display
    Perfect for demos when database is unavailable!
    """
    if not GEOSPATIAL_AVAILABLE:
        return JSONResponse(
            status_code=500,
            content={"error": "Geospatial libraries not available"}
        )
    
    try:
        logger.info("Generating demo grid (no database required)...")
        
        # Pune bounds - full city coverage
        min_lon, max_lon = 73.73, 73.99
        min_lat, max_lat = 18.41, 18.64
        
        # Create realistic Pune boundary (not just rectangle)
        boundary = box(min_lon, min_lat, max_lon, max_lat)
        
        # Generate 250m grid (0.0025 degrees ≈ 250m)
        cell_size_deg = 0.0025
        
        # Pune city center
        center_lon, center_lat = 73.8567, 18.5204
        
        # Create synthetic river (Mula-Mutha)
        river_points = [
            (73.75, 18.62),
            (73.78, 18.58),
            (73.82, 18.55),
            (73.86, 18.52),
            (73.90, 18.50),
            (73.94, 18.48)
        ]
        river = LineString(river_points)
        
        features = []
        cell_id = 0
        
        lon = min_lon
        while lon < max_lon:
            lat = min_lat
            while lat < max_lat:
                # Create cell
                cell = box(lon, lat, lon + cell_size_deg, lat + cell_size_deg)
                
                # Check if intersects boundary
                if cell.intersects(boundary):
                    # Calculate center
                    center_lon_cell = lon + cell_size_deg / 2
                    center_lat_cell = lat + cell_size_deg / 2
                    cell_center = Point(center_lon_cell, center_lat_cell)
                    
                    # Distance from city center (in degrees, then convert to km)
                    dist_from_center = np.sqrt(
                        (center_lon_cell - center_lon)**2 + (center_lat_cell - center_lat)**2
                    ) * 111  # Convert to km
                    
                    # Distance from river
                    dist_from_river = cell_center.distance(river) * 111  # km
                    
                    # Synthetic elevation (500-650m range)
                    # Higher in west and south (hills)
                    elevation = 500 + (max_lon - center_lon_cell) * 400 + (max_lat - center_lat_cell) * 200
                    elevation += np.random.normal(0, 10)  # Add noise
                    elevation = max(500, min(650, elevation))
                    
                    # Flood depth - based on elevation and river proximity
                    flood_risk_base = 0
                    if elevation < 550:
                        flood_risk_base += (550 - elevation) / 50
                    if dist_from_river < 2:
                        flood_risk_base += (2 - dist_from_river) * 1.5
                    flood_depth = max(0, flood_risk_base + np.random.normal(0, 0.3))
                    flood_depth = min(3.5, flood_depth)
                    
                    # Population density - higher near center
                    if dist_from_center < 5:
                        pop_density = 0.012 - dist_from_center * 0.002
                    elif dist_from_center < 10:
                        pop_density = 0.005 - (dist_from_center - 5) * 0.0008
                    else:
                        pop_density = 0.001
                    pop_density = max(0.0004, pop_density + np.random.normal(0, 0.001))
                    
                    # Land use based on distance from center
                    if dist_from_center < 3:
                        land_use = np.random.choice(["Commercial", "Residential", "Mixed"], p=[0.3, 0.4, 0.3])
                    elif dist_from_center < 8:
                        land_use = np.random.choice(["Residential", "Mixed"], p=[0.6, 0.4])
                    elif dist_from_center < 12:
                        land_use = np.random.choice(["Mixed", "Agricultural"], p=[0.7, 0.3])
                    else:
                        land_use = np.random.choice(["Agricultural", "Forest"], p=[0.7, 0.3])
                    
                    # Slum density - clusters in specific areas
                    slum_density = 0
                    if 3 < dist_from_center < 10 and dist_from_river < 3:
                        slum_density = max(0, 12 - dist_from_center + np.random.normal(0, 2))
                    slum_density = max(0, min(15, slum_density))
                    
                    # Infrastructure - more in center
                    infra_prob = max(0, 0.15 - dist_from_center * 0.01)
                    infra_count = 1 if np.random.random() < infra_prob else 0
                    if dist_from_center < 2:
                        infra_count += np.random.randint(0, 3)
                    
                    # Complaint density - correlated with flood risk and population
                    complaint_density = flood_depth * 10 + pop_density * 1000
                    complaint_density = max(0, complaint_density + np.random.normal(0, 5))
                    
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                [lon, lat],
                                [lon + cell_size_deg, lat],
                                [lon + cell_size_deg, lat + cell_size_deg],
                                [lon, lat + cell_size_deg],
                                [lon, lat]
                            ]]
                        },
                        "properties": {
                            "id": cell_id,
                            "elevation_mean": round(elevation, 1),
                            "flood_depth_avg": round(flood_depth, 2),
                            "population_density": round(pop_density, 6),
                            "drain_distance": round(dist_from_river * 1000, 0),
                            "land_use": land_use,
                            "slum_density": round(slum_density, 1),
                            "infra_count": int(infra_count),
                            "complaint_density": round(complaint_density, 1)
                        }
                    }
                    
                    features.append(feature)
                    cell_id += 1
                
                lat += cell_size_deg
            lon += cell_size_deg
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        logger.info(f"Generated {len(features)} demo grid cells (250m resolution)")
        
        return JSONResponse(content=geojson)
        
    except Exception as e:
        logger.error(f"Error generating demo grid: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
