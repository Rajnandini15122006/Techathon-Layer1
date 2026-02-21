try:
    import geopandas as gpd
    import numpy as np
    from shapely.geometry import box, Point
    from shapely.ops import unary_union
    import rasterio
    from rasterio.mask import mask
    from rasterstats import zonal_stats
    GEOSPATIAL_AVAILABLE = True
except ImportError:
    GEOSPATIAL_AVAILABLE = False
    print("Warning: Geospatial libraries not available. Grid generation will be limited.")

from typing import Optional, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ProductionGridGenerator:
    """
    Production-grade grid generator for Pune disaster risk assessment.
    Generates complete 250m x 250m grid coverage over entire city boundary.
    """
    
    # Pune is in UTM Zone 43N
    WORKING_CRS = "EPSG:32643"  # WGS 84 / UTM zone 43N (meters)
    STORAGE_CRS = "EPSG:4326"   # WGS 84 (lat/lon for web display)
    
    def __init__(self, cell_size: float = 250):
        """
        Initialize production grid generator
        
        Args:
            cell_size: Size of grid cells in meters (default 250m)
        """
        if not GEOSPATIAL_AVAILABLE:
            raise ImportError(
                "Geospatial libraries required. Install: pip install geopandas shapely rasterio rasterstats"
            )
        self.cell_size = cell_size
        logger.info(f"Initialized ProductionGridGenerator with {cell_size}m cell size")
        logger.info(f"Working CRS: {self.WORKING_CRS}")
        logger.info(f"Storage CRS: {self.STORAGE_CRS}")
    
    def load_and_reproject(self, path: str, target_crs: str) -> gpd.GeoDataFrame:
        """Load spatial data and reproject to target CRS"""
        try:
            gdf = gpd.read_file(path)
            logger.info(f"Loaded {len(gdf)} features from {path}")
            logger.info(f"Original CRS: {gdf.crs}")
            
            if gdf.crs is None:
                logger.warning(f"No CRS found in {path}, assuming EPSG:4326")
                gdf = gdf.set_crs("EPSG:4326")
            
            if gdf.crs != target_crs:
                logger.info(f"Reprojecting from {gdf.crs} to {target_crs}")
                gdf = gdf.to_crs(target_crs)
            
            return gdf
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")
            raise
    
    def load_boundary(self, boundary_path: str) -> gpd.GeoDataFrame:
        """Load Pune boundary and reproject to working CRS (UTM)"""
        logger.info(f"Loading boundary from {boundary_path}")
        boundary_gdf = self.load_and_reproject(boundary_path, self.WORKING_CRS)
        
        # Calculate and log boundary area
        total_area_m2 = boundary_gdf.geometry.area.sum()
        total_area_km2 = total_area_m2 / 1_000_000
        logger.info(f"Boundary total area: {total_area_km2:.2f} km²")
        
        return boundary_gdf
    
    def generate_grid(self, boundary_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Generate complete uniform grid in UTM coordinates covering entire boundary
        
        This creates a full rectangular grid over the boundary extent,
        then clips to the actual boundary polygon.
        """
        logger.info("=" * 80)
        logger.info("GENERATING FULL GRID COVERAGE")
        logger.info("=" * 80)
        
        # Get bounds in UTM (meters)
        bounds = boundary_gdf.total_bounds  # minx, miny, maxx, maxy
        minx, miny, maxx, maxy = bounds
        
        logger.info(f"Boundary extent (UTM meters):")
        logger.info(f"  X: {minx:.2f} to {maxx:.2f} (width: {(maxx-minx)/1000:.2f} km)")
        logger.info(f"  Y: {miny:.2f} to {maxy:.2f} (height: {(maxy-miny)/1000:.2f} km)")
        
        # Calculate grid dimensions
        n_cols = int(np.ceil((maxx - minx) / self.cell_size))
        n_rows = int(np.ceil((maxy - miny) / self.cell_size))
        total_potential_cells = n_cols * n_rows
        
        logger.info(f"Grid dimensions: {n_cols} columns × {n_rows} rows")
        logger.info(f"Potential cells (before clipping): {total_potential_cells:,}")
        
        # Generate complete grid
        logger.info("Creating grid cells...")
        grid_cells = []
        
        for i in range(n_cols):
            x_start = minx + (i * self.cell_size)
            x_end = x_start + self.cell_size
            
            for j in range(n_rows):
                y_start = miny + (j * self.cell_size)
                y_end = y_start + self.cell_size
                
                # Create 250m x 250m cell
                cell = box(x_start, y_start, x_end, y_end)
                grid_cells.append(cell)
        
        logger.info(f"Created {len(grid_cells):,} grid cells")
        
        # Create GeoDataFrame
        grid_gdf = gpd.GeoDataFrame({'geometry': grid_cells}, crs=self.WORKING_CRS)
        
        # Verify cell size
        sample_cell_area = grid_gdf.geometry.iloc[0].area
        expected_area = self.cell_size ** 2
        logger.info(f"Sample cell area: {sample_cell_area:.2f} m² (expected: {expected_area:.2f} m²)")
        
        # Clip to boundary
        logger.info("Clipping grid to boundary polygon...")
        boundary_union = unary_union(boundary_gdf.geometry)
        
        # Use spatial index for efficient intersection
        grid_gdf['intersects'] = grid_gdf.intersects(boundary_union)
        grid_gdf = grid_gdf[grid_gdf['intersects']].copy()
        grid_gdf = grid_gdf.drop(columns=['intersects'])
        
        logger.info(f"Cells intersecting boundary: {len(grid_gdf):,}")
        
        # Clip geometries to boundary
        logger.info("Clipping cell geometries to exact boundary...")
        grid_gdf['geometry'] = grid_gdf.intersection(boundary_union)
        
        # Remove empty geometries
        grid_gdf = grid_gdf[~grid_gdf.geometry.is_empty].copy()
        grid_gdf = grid_gdf[grid_gdf.geometry.area > 0].copy()
        
        # Reset index
        grid_gdf = grid_gdf.reset_index(drop=True)
        
        # Add cell ID
        grid_gdf['cell_id'] = range(len(grid_gdf))
        
        # Calculate coverage statistics
        total_grid_area_m2 = grid_gdf.geometry.area.sum()
        total_grid_area_km2 = total_grid_area_m2 / 1_000_000
        boundary_area_km2 = boundary_union.area / 1_000_000
        coverage_pct = (total_grid_area_km2 / boundary_area_km2) * 100
        
        logger.info("=" * 80)
        logger.info("GRID GENERATION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Final grid cells: {len(grid_gdf):,}")
        logger.info(f"Grid coverage area: {total_grid_area_km2:.2f} km²")
        logger.info(f"Boundary area: {boundary_area_km2:.2f} km²")
        logger.info(f"Coverage: {coverage_pct:.1f}%")
        logger.info(f"Average cell area: {(total_grid_area_m2/len(grid_gdf)):.2f} m²")
        logger.info("=" * 80)
        
        return grid_gdf
    
    def compute_elevation(self, grid_gdf: gpd.GeoDataFrame, dem_path: Optional[str]) -> gpd.GeoDataFrame:
        """Compute mean elevation for each grid cell from DEM raster"""
        if not dem_path:
            grid_gdf['elevation_mean'] = None
            return grid_gdf
        
        try:
            with rasterio.open(dem_path) as src:
                elevations = []
                for geom in grid_gdf.geometry:
                    try:
                        out_image, _ = mask(src, [geom], crop=True, nodata=src.nodata)
                        valid_data = out_image[out_image != src.nodata]
                        if len(valid_data) > 0:
                            elevations.append(float(np.mean(valid_data)))
                        else:
                            elevations.append(None)
                    except Exception:
                        elevations.append(None)
                
                grid_gdf['elevation_mean'] = elevations
                logger.info("Computed elevation for grid cells")
        except Exception as e:
            logger.error(f"Error computing elevation: {e}")
            grid_gdf['elevation_mean'] = None
        
        return grid_gdf
    
    def compute_slope(self, grid_gdf: gpd.GeoDataFrame, dem_path: Optional[str]) -> gpd.GeoDataFrame:
        """Compute mean slope for each grid cell"""
        # Simplified - in production, compute slope from DEM
        grid_gdf['slope_mean'] = None
        return grid_gdf
    
    def compute_drain_distance(self, grid_gdf: gpd.GeoDataFrame, drains_path: Optional[str]) -> gpd.GeoDataFrame:
        """Compute distance to nearest drain for each grid cell"""
        if not drains_path:
            grid_gdf['drain_distance'] = None
            return grid_gdf
        
        try:
            drains_gdf = gpd.read_file(drains_path)
            if drains_gdf.crs != "EPSG:4326":
                drains_gdf = drains_gdf.to_crs("EPSG:4326")
            
            drain_union = unary_union(drains_gdf.geometry)
            grid_gdf['drain_distance'] = grid_gdf.geometry.centroid.distance(drain_union) * 111000  # Convert to meters
            logger.info("Computed drain distances")
        except Exception as e:
            logger.error(f"Error computing drain distance: {e}")
            grid_gdf['drain_distance'] = None
        
        return grid_gdf
    
    def spatial_join_land_use(self, grid_gdf: gpd.GeoDataFrame, land_use_path: Optional[str]) -> gpd.GeoDataFrame:
        """Spatial join with land use data"""
        if not land_use_path:
            grid_gdf['land_use'] = None
            return grid_gdf
        
        try:
            land_use_gdf = gpd.read_file(land_use_path)
            if land_use_gdf.crs != "EPSG:4326":
                land_use_gdf = land_use_gdf.to_crs("EPSG:4326")
            
            joined = gpd.sjoin(grid_gdf, land_use_gdf, how='left', predicate='intersects')
            # Assuming land use column is named 'land_use' or 'type'
            if 'land_use' in joined.columns:
                grid_gdf['land_use'] = joined.groupby(joined.index)['land_use'].first()
            elif 'type' in joined.columns:
                grid_gdf['land_use'] = joined.groupby(joined.index)['type'].first()
            else:
                grid_gdf['land_use'] = None
            logger.info("Joined land use data")
        except Exception as e:
            logger.error(f"Error joining land use: {e}")
            grid_gdf['land_use'] = None
        
        return grid_gdf
    
    def spatial_join_population(self, grid_gdf: gpd.GeoDataFrame, census_path: Optional[str]) -> gpd.GeoDataFrame:
        """Spatial join with census population data"""
        if not census_path:
            grid_gdf['population_density'] = None
            return grid_gdf
        
        try:
            census_gdf = gpd.read_file(census_path)
            if census_gdf.crs != "EPSG:4326":
                census_gdf = census_gdf.to_crs("EPSG:4326")
            
            joined = gpd.sjoin(grid_gdf, census_gdf, how='left', predicate='intersects')
            # Assuming population column exists
            if 'population' in joined.columns:
                grid_gdf['population_density'] = joined.groupby(joined.index)['population'].sum() / (self.cell_size ** 2)
            else:
                grid_gdf['population_density'] = None
            logger.info("Joined population data")
        except Exception as e:
            logger.error(f"Error joining population: {e}")
            grid_gdf['population_density'] = None
        
        return grid_gdf
    
    def spatial_join_slums(self, grid_gdf: gpd.GeoDataFrame, slums_path: Optional[str]) -> gpd.GeoDataFrame:
        """Spatial join with slum data"""
        if not slums_path:
            grid_gdf['slum_density'] = None
            return grid_gdf
        
        try:
            slums_gdf = gpd.read_file(slums_path)
            if slums_gdf.crs != "EPSG:4326":
                slums_gdf = slums_gdf.to_crs("EPSG:4326")
            
            joined = gpd.sjoin(grid_gdf, slums_gdf, how='left', predicate='intersects')
            grid_gdf['slum_density'] = joined.groupby(joined.index).size() / (self.cell_size ** 2)
            grid_gdf['slum_density'] = grid_gdf['slum_density'].fillna(0)
            logger.info("Joined slum data")
        except Exception as e:
            logger.error(f"Error joining slum data: {e}")
            grid_gdf['slum_density'] = None
        
        return grid_gdf
    
    def compute_flood_history(self, grid_gdf: gpd.GeoDataFrame, flood_path: Optional[str]) -> gpd.GeoDataFrame:
        """Compute historical flood count"""
        if not flood_path:
            grid_gdf['flood_history_score'] = 0
            return grid_gdf
        
        try:
            flood_gdf = gpd.read_file(flood_path)
            if flood_gdf.crs != "EPSG:4326":
                flood_gdf = flood_gdf.to_crs("EPSG:4326")
            
            joined = gpd.sjoin(grid_gdf, flood_gdf, how='left', predicate='intersects')
            grid_gdf['flood_history_score'] = joined.groupby(joined.index).size().fillna(0).astype(int)
            logger.info("Computed flood history")
        except Exception as e:
            logger.error(f"Error computing flood history: {e}")
            grid_gdf['flood_history_score'] = 0
        
        return grid_gdf
    
    def compute_infrastructure(self, grid_gdf: gpd.GeoDataFrame, infra_path: Optional[str]) -> gpd.GeoDataFrame:
        """Compute infrastructure count (hospitals, shelters)"""
        if not infra_path:
            grid_gdf['infra_score'] = 0
            return grid_gdf
        
        try:
            infra_gdf = gpd.read_file(infra_path)
            if infra_gdf.crs != "EPSG:4326":
                infra_gdf = infra_gdf.to_crs("EPSG:4326")
            
            joined = gpd.sjoin(grid_gdf, infra_gdf, how='left', predicate='intersects')
            grid_gdf['infra_score'] = joined.groupby(joined.index).size().fillna(0).astype(int)
            logger.info("Computed infrastructure score")
        except Exception as e:
            logger.error(f"Error computing infrastructure: {e}")
            grid_gdf['infra_score'] = 0
        
        return grid_gdf
