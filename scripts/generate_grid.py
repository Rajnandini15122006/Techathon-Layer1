"""
Script to generate and populate grid cells in the database
Usage: python scripts/generate_grid.py --boundary data/pune_boundary.geojson
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
import logging
from app.services.grid_generator import GridGenerator
from app.services.grid_service import GridService
from app.database import SessionLocal, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Generate grid cells for Pune')
    parser.add_argument('--boundary', required=True, help='Path to Pune boundary file')
    parser.add_argument('--dem', help='Path to DEM raster file')
    parser.add_argument('--drains', help='Path to drains shapefile')
    parser.add_argument('--land-use', help='Path to land use shapefile')
    parser.add_argument('--census', help='Path to census data')
    parser.add_argument('--slums', help='Path to slums data')
    parser.add_argument('--floods', help='Path to flood history data')
    parser.add_argument('--infrastructure', help='Path to infrastructure data')
    parser.add_argument('--cell-size', type=float, default=250, help='Grid cell size in meters')
    
    args = parser.parse_args()
    
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    
    # Generate grid
    logger.info("Starting grid generation...")
    generator = GridGenerator(cell_size=args.cell_size)
    
    # Load boundary
    logger.info(f"Loading boundary from {args.boundary}")
    boundary_gdf = generator.load_boundary(args.boundary)
    
    # Generate grid
    logger.info("Generating grid cells...")
    grid_gdf = generator.generate_grid(boundary_gdf)
    
    # Compute attributes
    logger.info("Computing elevation...")
    grid_gdf = generator.compute_elevation(grid_gdf, args.dem)
    
    logger.info("Computing slope...")
    grid_gdf = generator.compute_slope(grid_gdf, args.dem)
    
    logger.info("Computing drain distances...")
    grid_gdf = generator.compute_drain_distance(grid_gdf, args.drains)
    
    logger.info("Joining land use data...")
    grid_gdf = generator.spatial_join_land_use(grid_gdf, args.land_use)
    
    logger.info("Joining population data...")
    grid_gdf = generator.spatial_join_population(grid_gdf, args.census)
    
    logger.info("Joining slum data...")
    grid_gdf = generator.spatial_join_slums(grid_gdf, args.slums)
    
    logger.info("Computing flood history...")
    grid_gdf = generator.compute_flood_history(grid_gdf, args.floods)
    
    logger.info("Computing infrastructure score...")
    grid_gdf = generator.compute_infrastructure(grid_gdf, args.infrastructure)
    
    # Insert into database
    logger.info("Inserting grid cells into database...")
    db = SessionLocal()
    try:
        count = GridService.bulk_insert_grid_cells(db, grid_gdf)
        logger.info(f"Successfully inserted {count} grid cells")
    except Exception as e:
        logger.error(f"Error inserting grid cells: {e}")
        db.rollback()
    finally:
        db.close()
    
    logger.info("Grid generation complete!")

if __name__ == "__main__":
    main()
