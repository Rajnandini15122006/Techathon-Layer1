from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.grid_cell import GridCell
from geoalchemy2.shape import from_shape
from shapely.geometry import box
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/synthetic", tags=["Synthetic Data"])

try:
    from app.services.grid_generator import ProductionGridGenerator
    from app.services.synthetic_data_generator import SyntheticDataGenerator
    import geopandas as gpd
    GEOSPATIAL_AVAILABLE = True
except ImportError:
    GEOSPATIAL_AVAILABLE = False

@router.post("/generate-pune-grid")
def generate_synthetic_pune_grid(db: Session = Depends(get_db)):
    """
    Generate complete synthetic Pune grid with realistic spatial patterns
    
    This creates:
    - Full 250m x 250m grid covering Pune
    - Synthetic but spatially realistic attributes
    - Proper geographic correlations
    
    No real data required - uses synthetic Pune boundary
    """
    if not GEOSPATIAL_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="Geospatial libraries required. Install: pip install geopandas shapely"
        )
    
    try:
        logger.info("=" * 80)
        logger.info("GENERATING SYNTHETIC PUNE GRID")
        logger.info("=" * 80)
        
        # Create synthetic Pune boundary (approximate actual Pune extent)
        # Pune spans roughly: 18.41°N to 18.64°N, 73.73°E to 73.99°E
        logger.info("Creating synthetic Pune boundary...")
        
        # Create boundary polygon in lat/lon covering full Pune metropolitan area
        pune_boundary = box(73.73, 18.41, 73.99, 18.64)
        boundary_gdf = gpd.GeoDataFrame({'geometry': [pune_boundary]}, crs="EPSG:4326")
        
        logger.info(f"Boundary extent: 73.73°E to 73.99°E, 18.41°N to 18.64°N")
        logger.info(f"Approximate area: {(0.26 * 0.23 * 111 * 111):.1f} km²")
        
        # Initialize grid generator
        generator = ProductionGridGenerator(cell_size=250)
        
        # Reproject boundary to UTM
        boundary_utm = boundary_gdf.to_crs(generator.WORKING_CRS)
        
        # Generate grid
        logger.info("Generating grid...")
        grid_gdf = generator.generate_grid(boundary_utm)
        
        # Generate synthetic attributes
        logger.info("Generating synthetic spatial attributes...")
        synthetic_gen = SyntheticDataGenerator(grid_gdf)
        grid_with_attributes = synthetic_gen.generate_all_attributes()
        
        # Convert back to EPSG:4326 for storage
        logger.info("Converting to EPSG:4326 for storage...")
        grid_with_attributes = grid_with_attributes.to_crs("EPSG:4326")
        
        # Prepare for database insertion
        logger.info("Preparing data for database...")
        records = []
        for idx, row in grid_with_attributes.iterrows():
            record = GridCell(
                geom=from_shape(row.geometry, srid=4326),
                elevation_mean=float(row['elevation_mean']),
                drain_distance=float(row['drain_distance']),
                land_use=str(row['land_use']),
                population_density=float(row['population_density']),
                slum_density=float(row['slum_density']),
                flood_depth_avg=float(row['flood_depth_avg']),
                infra_count=int(row['infra_count']),
                complaint_density=float(row['complaint_density'])
            )
            records.append(record)
        
        # Clear existing data
        logger.info("Clearing existing grid data...")
        db.query(GridCell).delete()
        
        # Bulk insert
        logger.info(f"Inserting {len(records)} grid cells...")
        db.bulk_save_objects(records)
        db.commit()
        
        # Generate statistics
        stats = {
            "status": "success",
            "message": "Synthetic Pune grid generated successfully",
            "total_cells": len(grid_with_attributes),
            "cell_size_m": 250,
            "coverage_area_km2": round(grid_with_attributes.geometry.area.sum() / 1_000_000, 2),
            "attributes": {
                "elevation_range": f"{grid_with_attributes['elevation_mean'].min():.1f}m - {grid_with_attributes['elevation_mean'].max():.1f}m",
                "land_use_types": grid_with_attributes['land_use'].unique().tolist(),
                "total_infrastructure": int(grid_with_attributes['infra_count'].sum()),
                "avg_population_density": float(grid_with_attributes['population_density'].mean()),
                "max_flood_depth": float(grid_with_attributes['flood_depth_avg'].max())
            },
            "note": "This is synthetic data with realistic spatial patterns. Replace with real data when available."
        }
        
        logger.info("=" * 80)
        logger.info("SYNTHETIC GRID GENERATION COMPLETE")
        logger.info(f"Total cells: {stats['total_cells']}")
        logger.info(f"Coverage: {stats['coverage_area_km2']} km²")
        logger.info("=" * 80)
        
        return stats
        
    except Exception as e:
        logger.error(f"Error generating synthetic grid: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
