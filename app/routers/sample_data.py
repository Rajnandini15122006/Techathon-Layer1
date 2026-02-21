from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models.grid_cell import GridCell
import random
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Sample Data"])

try:
    from geoalchemy2.shape import from_shape
    from shapely.geometry import box
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False

@router.post("/generate-sample-data")
def generate_sample_data(db: Session = Depends(get_db)):
    """
    Generate sample grid cells for Pune area for demonstration
    """
    try:
        if not SHAPELY_AVAILABLE:
            # Use raw SQL to insert sample data without shapely
            logger.info("Using SQL-based sample data generation")
            
            # Pune approximate bounds
            min_lon, min_lat = 73.75, 18.45
            cell_size = 0.00225
            
            cells_inserted = 0
            
            for i in range(10):
                for j in range(10):
                    lon = min_lon + (i * cell_size)
                    lat = min_lat + (j * cell_size)
                    
                    # Create WKT polygon
                    wkt = f"POLYGON(({lon} {lat}, {lon + cell_size} {lat}, {lon + cell_size} {lat + cell_size}, {lon} {lat + cell_size}, {lon} {lat}))"
                    
                    # Random attributes matching new schema
                    elevation = random.uniform(500, 650)
                    drain_dist = random.uniform(50, 500)
                    land_use = random.choice(['Residential', 'Commercial', 'Industrial', 'Green Space', 'Mixed'])
                    pop_density = random.uniform(0.0001, 0.01)
                    slum_density = random.uniform(0, 5.0)  # Percentage
                    flood_depth = random.uniform(0, 2.5)
                    infra_count = random.randint(0, 3)
                    complaint_density = random.uniform(0, 10.0)
                    
                    # Insert using raw SQL with new schema
                    query = text("""
                        INSERT INTO grid_cells 
                        (geom, elevation_mean, drain_distance, land_use, 
                         population_density, slum_density, flood_depth_avg, 
                         infra_count, complaint_density)
                        VALUES 
                        (ST_GeomFromText(:wkt, 4326), :elevation, :drain_dist, :land_use,
                         :pop_density, :slum_density, :flood_depth, :infra_count, :complaint_density)
                    """)
                    
                    db.execute(query, {
                        'wkt': wkt,
                        'elevation': elevation,
                        'drain_dist': drain_dist,
                        'land_use': land_use,
                        'pop_density': pop_density,
                        'slum_density': slum_density,
                        'flood_depth': flood_depth,
                        'infra_count': infra_count,
                        'complaint_density': complaint_density
                    })
                    cells_inserted += 1
            
            db.commit()
            
            return {
                "message": "Sample data generated successfully (using SQL)",
                "count": cells_inserted,
                "area": "Pune (sample)",
                "cell_size": "250m × 250m"
            }
        
        # Shapely-based implementation
        logger.info("Using shapely-based sample data generation")
        
        # Pune approximate bounds
        min_lon, min_lat = 73.75, 18.45
        max_lon, max_lat = 73.95, 18.60
        
        # Grid cell size in degrees (approximately 250m)
        cell_size = 0.00225
        
        cells = []
        cell_count = 0
        
        # Generate grid
        lon = min_lon
        while lon < max_lon:
            lat = min_lat
            while lat < max_lat:
                # Create polygon
                polygon = box(lon, lat, lon + cell_size, lat + cell_size)
                
                # Random attributes matching new schema
                cell = GridCell(
                    geom=from_shape(polygon, srid=4326),
                    elevation_mean=random.uniform(500, 650),
                    drain_distance=random.uniform(50, 500),
                    land_use=random.choice(['Residential', 'Commercial', 'Industrial', 'Green Space', 'Mixed']),
                    population_density=random.uniform(0.0001, 0.01),
                    slum_density=random.uniform(0, 5.0),  # Percentage
                    flood_depth_avg=random.uniform(0, 2.5),
                    infra_count=random.randint(0, 3),
                    complaint_density=random.uniform(0, 10.0)
                )
                cells.append(cell)
                cell_count += 1
                
                # Limit to 100 cells for demo
                if cell_count >= 100:
                    break
                
                lat += cell_size
            
            if cell_count >= 100:
                break
            lon += cell_size
        
        # Bulk insert
        db.bulk_save_objects(cells)
        db.commit()
        
        logger.info(f"Successfully generated {cell_count} sample cells")
        
        return {
            "message": "Sample data generated successfully",
            "count": cell_count,
            "area": "Pune (sample)",
            "cell_size": "250m × 250m"
        }
        
    except Exception as e:
        logger.error(f"Error generating sample data: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error generating sample data: {str(e)}")
