"""
Production-grade grid generation service
Orchestrates the full spatial grid generation pipeline
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

try:
    import geopandas as gpd
    from geoalchemy2.shape import from_shape
    from app.services.grid_generator import ProductionGridGenerator
    from app.services.spatial_processor import SpatialProcessor
    GEOSPATIAL_AVAILABLE = True
except ImportError:
    GEOSPATIAL_AVAILABLE = False
    logger.warning("Geospatial libraries not available for production grid generation")

from app.models.grid_cell import GridCell

class ProductionGridService:
    """
    Orchestrates full production grid generation with all spatial attributes
    """
    
    @staticmethod
    def generate_full_spatial_grid(
        db: Session,
        boundary_path: str,
        dem_path: Optional[str] = None,
        drain_path: Optional[str] = None,
        land_use_path: Optional[str] = None,
        census_path: Optional[str] = None,
        slum_path: Optional[str] = None,
        flood_path: Optional[str] = None,
        infra_path: Optional[str] = None,
        complaint_path: Optional[str] = None,
        cell_size: float = 250
    ) -> Dict:
        """
        Generate complete spatial grid with all attributes
        
        Returns:
            Dictionary with generation statistics
        """
        if not GEOSPATIAL_AVAILABLE:
            raise ImportError(
                "Geospatial libraries required for production grid generation. "
                "Install with: pip install geopandas shapely rasterio rasterstats"
            )
        
        try:
            logger.info("=" * 80)
            logger.info("STARTING PRODUCTION GRID GENERATION")
            logger.info("=" * 80)
            
            # Initialize generator
            generator = ProductionGridGenerator(cell_size=cell_size)
            processor = SpatialProcessor()
            
            # Step 1: Load boundary and generate grid
            logger.info("\n[1/10] Loading boundary...")
            boundary_gdf = generator.load_boundary(boundary_path)
            
            logger.info("\n[2/10] Generating grid in UTM coordinates...")
            grid_gdf = generator.generate_grid(boundary_gdf)
            
            # Step 3-9: Compute all attributes
            logger.info("\n[3/10] Computing elevation from DEM...")
            grid_gdf = processor.compute_elevation_from_dem(grid_gdf, dem_path)
            
            logger.info("\n[4/10] Computing drain distances...")
            grid_gdf = processor.compute_drain_distance(grid_gdf, drain_path)
            
            logger.info("\n[5/10] Computing land use...")
            grid_gdf = processor.compute_land_use(grid_gdf, land_use_path)
            
            logger.info("\n[6/10] Computing population density...")
            grid_gdf = processor.compute_population_density(grid_gdf, census_path)
            
            logger.info("\n[7/10] Computing slum density...")
            grid_gdf = processor.compute_slum_density(grid_gdf, slum_path)
            
            logger.info("\n[8/10] Computing flood depth...")
            grid_gdf = processor.compute_flood_depth(grid_gdf, flood_path)
            
            logger.info("\n[9/10] Computing infrastructure count...")
            grid_gdf = processor.compute_infrastructure_count(grid_gdf, infra_path)
            
            logger.info("\n[10/10] Computing complaint density...")
            grid_gdf = processor.compute_complaint_density(grid_gdf, complaint_path)
            
            # Convert back to EPSG:4326 for storage
            logger.info("\nConverting geometries to EPSG:4326 for storage...")
            grid_gdf = grid_gdf.to_crs("EPSG:4326")
            
            # Prepare for database insertion
            logger.info("\nPreparing data for database insertion...")
            records = []
            for idx, row in grid_gdf.iterrows():
                record = GridCell(
                    geom=from_shape(row.geometry, srid=4326),
                    elevation_mean=float(row['elevation_mean']) if row['elevation_mean'] is not None else None,
                    drain_distance=float(row['drain_distance']) if row['drain_distance'] is not None else None,
                    land_use=str(row['land_use']) if row['land_use'] is not None else None,
                    population_density=float(row['population_density']) if row['population_density'] is not None else None,
                    slum_density=float(row['slum_density']) if row['slum_density'] is not None else None,
                    flood_depth_avg=float(row['flood_depth_avg']) if row['flood_depth_avg'] is not None else None,
                    infra_count=int(row['infra_count']) if row['infra_count'] is not None else 0,
                    complaint_density=float(row['complaint_density']) if row['complaint_density'] is not None else 0.0
                )
                records.append(record)
            
            # Bulk insert
            logger.info(f"\nInserting {len(records)} grid cells into database...")
            db.bulk_save_objects(records)
            db.commit()
            
            # Generate statistics
            stats = {
                "status": "success",
                "total_cells": len(grid_gdf),
                "cell_size_m": cell_size,
                "crs_working": "EPSG:32643",
                "crs_storage": "EPSG:4326",
                "attributes_computed": {
                    "elevation": grid_gdf['elevation_mean'].notna().sum(),
                    "drain_distance": grid_gdf['drain_distance'].notna().sum(),
                    "land_use": grid_gdf['land_use'].notna().sum(),
                    "population": grid_gdf['population_density'].notna().sum(),
                    "slum_density": grid_gdf['slum_density'].notna().sum(),
                    "flood_depth": grid_gdf['flood_depth_avg'].notna().sum(),
                    "infrastructure": (grid_gdf['infra_count'] > 0).sum(),
                    "complaints": (grid_gdf['complaint_density'] > 0).sum()
                },
                "data_sources": {
                    "boundary": boundary_path,
                    "dem": dem_path or "Not provided",
                    "drains": drain_path or "Not provided",
                    "land_use": land_use_path or "Not provided",
                    "census": census_path or "Not provided",
                    "slums": slum_path or "Not provided",
                    "floods": flood_path or "Not provided",
                    "infrastructure": infra_path or "Not provided",
                    "complaints": complaint_path or "Not provided"
                }
            }
            
            logger.info("\n" + "=" * 80)
            logger.info("GRID GENERATION COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)
            logger.info(f"Total cells generated: {stats['total_cells']}")
            logger.info(f"Attributes computed: {stats['attributes_computed']}")
            
            return stats
            
        except Exception as e:
            logger.error(f"\nERROR during grid generation: {e}", exc_info=True)
            db.rollback()
            raise
