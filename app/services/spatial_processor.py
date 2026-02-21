"""
Production-grade spatial processing for grid attribute computation
"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

try:
    import geopandas as gpd
    import numpy as np
    import rasterio
    from rasterio.mask import mask as raster_mask
    from rasterstats import zonal_stats
    from shapely.geometry import Point
    GEOSPATIAL_AVAILABLE = True
except ImportError:
    GEOSPATIAL_AVAILABLE = False
    logger.warning("Geospatial libraries not available")

class SpatialProcessor:
    """Handles all spatial computations for grid cells"""
    
    @staticmethod
    def compute_elevation_from_dem(grid_gdf: gpd.GeoDataFrame, dem_path: Optional[str]) -> gpd.GeoDataFrame:
        """
        Compute mean elevation for each grid cell from DEM raster
        Uses zonal statistics for accurate computation
        """
        if not dem_path:
            logger.warning("No DEM path provided, setting elevation_mean to NULL")
            grid_gdf['elevation_mean'] = None
            return grid_gdf
        
        try:
            logger.info(f"Computing elevation from DEM: {dem_path}")
            
            # Convert to EPSG:4326 for raster operations if needed
            grid_temp = grid_gdf.to_crs("EPSG:4326")
            
            # Use zonal_stats for efficient raster extraction
            stats = zonal_stats(
                grid_temp.geometry,
                dem_path,
                stats=['mean'],
                nodata=-9999,
                all_touched=True
            )
            
            grid_gdf['elevation_mean'] = [s['mean'] if s and s['mean'] is not None else None for s in stats]
            
            valid_count = grid_gdf['elevation_mean'].notna().sum()
            logger.info(f"Computed elevation for {valid_count}/{len(grid_gdf)} cells")
            
        except Exception as e:
            logger.error(f"Error computing elevation: {e}")
            grid_gdf['elevation_mean'] = None
        
        return grid_gdf
    
    @staticmethod
    def compute_drain_distance(grid_gdf: gpd.GeoDataFrame, drains_path: Optional[str]) -> gpd.GeoDataFrame:
        """
        Compute distance to nearest drain line in meters
        Uses spatial index for performance
        """
        if not drains_path:
            logger.warning("No drains path provided, setting drain_distance to NULL")
            grid_gdf['drain_distance'] = None
            return grid_gdf
        
        try:
            logger.info(f"Computing drain distances from: {drains_path}")
            
            drains_gdf = gpd.read_file(drains_path)
            
            # Ensure same CRS
            if drains_gdf.crs != grid_gdf.crs:
                drains_gdf = drains_gdf.to_crs(grid_gdf.crs)
            
            # Create spatial index for drains
            drains_sindex = drains_gdf.sindex
            
            distances = []
            for idx, cell in grid_gdf.iterrows():
                centroid = cell.geometry.centroid
                
                # Find nearest drain using spatial index
                possible_matches_idx = list(drains_sindex.nearest(centroid.bounds, 1))
                
                if possible_matches_idx:
                    nearest_drain = drains_gdf.iloc[possible_matches_idx[0]].geometry
                    distance = centroid.distance(nearest_drain)
                    distances.append(distance)
                else:
                    distances.append(None)
            
            grid_gdf['drain_distance'] = distances
            
            valid_count = grid_gdf['drain_distance'].notna().sum()
            logger.info(f"Computed drain distance for {valid_count}/{len(grid_gdf)} cells")
            
        except Exception as e:
            logger.error(f"Error computing drain distance: {e}")
            grid_gdf['drain_distance'] = None
        
        return grid_gdf
    
    @staticmethod
    def compute_land_use(grid_gdf: gpd.GeoDataFrame, land_use_path: Optional[str]) -> gpd.GeoDataFrame:
        """
        Determine dominant land use category using spatial join
        """
        if not land_use_path:
            logger.warning("No land use path provided, setting land_use to NULL")
            grid_gdf['land_use'] = None
            return grid_gdf
        
        try:
            logger.info(f"Computing land use from: {land_use_path}")
            
            land_use_gdf = gpd.read_file(land_use_path)
            
            # Ensure same CRS
            if land_use_gdf.crs != grid_gdf.crs:
                land_use_gdf = land_use_gdf.to_crs(grid_gdf.crs)
            
            # Spatial join to find overlapping land use polygons
            joined = gpd.sjoin(grid_gdf, land_use_gdf, how='left', predicate='intersects')
            
            # Find land use column (common names)
            land_use_col = None
            for col in ['land_use', 'landuse', 'type', 'class', 'category']:
                if col in joined.columns:
                    land_use_col = col
                    break
            
            if land_use_col:
                # Get most common land use per cell
                grid_gdf['land_use'] = joined.groupby(joined.index)[land_use_col].agg(
                    lambda x: x.mode()[0] if len(x.mode()) > 0 else None
                )
            else:
                logger.warning("No land use column found in dataset")
                grid_gdf['land_use'] = None
            
            valid_count = grid_gdf['land_use'].notna().sum()
            logger.info(f"Computed land use for {valid_count}/{len(grid_gdf)} cells")
            
        except Exception as e:
            logger.error(f"Error computing land use: {e}")
            grid_gdf['land_use'] = None
        
        return grid_gdf
    
    @staticmethod
    def compute_population_density(grid_gdf: gpd.GeoDataFrame, census_path: Optional[str]) -> gpd.GeoDataFrame:
        """
        Compute population density from census data using spatial join
        """
        if not census_path:
            logger.warning("No census path provided, setting population_density to NULL")
            grid_gdf['population_density'] = None
            return grid_gdf
        
        try:
            logger.info(f"Computing population density from: {census_path}")
            
            census_gdf = gpd.read_file(census_path)
            
            # Ensure same CRS
            if census_gdf.crs != grid_gdf.crs:
                census_gdf = census_gdf.to_crs(grid_gdf.crs)
            
            # Find population column
            pop_col = None
            for col in ['population', 'pop', 'total_pop', 'pop_total']:
                if col in census_gdf.columns:
                    pop_col = col
                    break
            
            if pop_col:
                # Spatial join
                joined = gpd.sjoin(grid_gdf, census_gdf, how='left', predicate='intersects')
                
                # Sum population and divide by cell area
                cell_area = grid_gdf.geometry.area.iloc[0]  # All cells same size
                grid_gdf['population_density'] = joined.groupby(joined.index)[pop_col].sum() / cell_area
                grid_gdf['population_density'] = grid_gdf['population_density'].fillna(0)
            else:
                logger.warning("No population column found in census data")
                grid_gdf['population_density'] = None
            
            valid_count = (grid_gdf['population_density'] > 0).sum() if grid_gdf['population_density'] is not None else 0
            logger.info(f"Computed population density for {valid_count}/{len(grid_gdf)} cells")
            
        except Exception as e:
            logger.error(f"Error computing population density: {e}")
            grid_gdf['population_density'] = None
        
        return grid_gdf

    
    @staticmethod
    def compute_slum_density(grid_gdf: gpd.GeoDataFrame, slum_path: Optional[str]) -> gpd.GeoDataFrame:
        """
        Compute slum density as percentage of cell area covered by slums
        """
        if not slum_path:
            logger.warning("No slum path provided, setting slum_density to NULL")
            grid_gdf['slum_density'] = None
            return grid_gdf
        
        try:
            logger.info(f"Computing slum density from: {slum_path}")
            
            slum_gdf = gpd.read_file(slum_path)
            
            # Ensure same CRS
            if slum_gdf.crs != grid_gdf.crs:
                slum_gdf = slum_gdf.to_crs(grid_gdf.crs)
            
            # Spatial join and compute intersection area
            slum_densities = []
            for idx, cell in grid_gdf.iterrows():
                cell_area = cell.geometry.area
                
                # Find intersecting slums
                intersecting = slum_gdf[slum_gdf.intersects(cell.geometry)]
                
                if len(intersecting) > 0:
                    # Calculate total slum area within cell
                    slum_area = sum([cell.geometry.intersection(slum.geometry).area 
                                    for _, slum in intersecting.iterrows()])
                    density = (slum_area / cell_area) * 100  # Percentage
                    slum_densities.append(min(density, 100))  # Cap at 100%
                else:
                    slum_densities.append(0.0)
            
            grid_gdf['slum_density'] = slum_densities
            
            valid_count = (grid_gdf['slum_density'] > 0).sum()
            logger.info(f"Computed slum density for {valid_count}/{len(grid_gdf)} cells")
            
        except Exception as e:
            logger.error(f"Error computing slum density: {e}")
            grid_gdf['slum_density'] = None
        
        return grid_gdf
    
    @staticmethod
    def compute_flood_depth(grid_gdf: gpd.GeoDataFrame, flood_path: Optional[str]) -> gpd.GeoDataFrame:
        """
        Compute average historical flood depth from raster or vector data
        """
        if not flood_path:
            logger.warning("No flood path provided, setting flood_depth_avg to NULL")
            grid_gdf['flood_depth_avg'] = None
            return grid_gdf
        
        try:
            logger.info(f"Computing flood depth from: {flood_path}")
            
            # Check if raster or vector
            if flood_path.endswith(('.tif', '.tiff', '.img')):
                # Raster data - use zonal stats
                grid_temp = grid_gdf.to_crs("EPSG:4326")
                
                stats = zonal_stats(
                    grid_temp.geometry,
                    flood_path,
                    stats=['mean'],
                    nodata=-9999,
                    all_touched=True
                )
                
                grid_gdf['flood_depth_avg'] = [s['mean'] if s and s['mean'] is not None else 0.0 for s in stats]
            else:
                # Vector data - spatial join
                flood_gdf = gpd.read_file(flood_path)
                
                if flood_gdf.crs != grid_gdf.crs:
                    flood_gdf = flood_gdf.to_crs(grid_gdf.crs)
                
                # Find depth column
                depth_col = None
                for col in ['depth', 'flood_depth', 'water_depth', 'inundation']:
                    if col in flood_gdf.columns:
                        depth_col = col
                        break
                
                if depth_col:
                    joined = gpd.sjoin(grid_gdf, flood_gdf, how='left', predicate='intersects')
                    grid_gdf['flood_depth_avg'] = joined.groupby(joined.index)[depth_col].mean().fillna(0)
                else:
                    # Count flood events if no depth column
                    joined = gpd.sjoin(grid_gdf, flood_gdf, how='left', predicate='intersects')
                    grid_gdf['flood_depth_avg'] = joined.groupby(joined.index).size().reindex(grid_gdf.index, fill_value=0)
            
            valid_count = (grid_gdf['flood_depth_avg'] > 0).sum()
            logger.info(f"Computed flood depth for {valid_count}/{len(grid_gdf)} cells")
            
        except Exception as e:
            logger.error(f"Error computing flood depth: {e}")
            grid_gdf['flood_depth_avg'] = None
        
        return grid_gdf
    
    @staticmethod
    def compute_infrastructure_count(grid_gdf: gpd.GeoDataFrame, infra_path: Optional[str]) -> gpd.GeoDataFrame:
        """
        Count hospitals and shelters within each grid cell
        """
        if not infra_path:
            logger.warning("No infrastructure path provided, setting infra_count to 0")
            grid_gdf['infra_count'] = 0
            return grid_gdf
        
        try:
            logger.info(f"Computing infrastructure count from: {infra_path}")
            
            infra_gdf = gpd.read_file(infra_path)
            
            # Ensure same CRS
            if infra_gdf.crs != grid_gdf.crs:
                infra_gdf = infra_gdf.to_crs(grid_gdf.crs)
            
            # Filter for hospitals and shelters if type column exists
            type_cols = ['type', 'category', 'amenity', 'facility']
            for col in type_cols:
                if col in infra_gdf.columns:
                    infra_gdf = infra_gdf[infra_gdf[col].str.contains(
                        'hospital|shelter|clinic|health|emergency', 
                        case=False, 
                        na=False
                    )]
                    break
            
            # Spatial join and count
            joined = gpd.sjoin(grid_gdf, infra_gdf, how='left', predicate='contains')
            grid_gdf['infra_count'] = joined.groupby(joined.index).size().reindex(grid_gdf.index, fill_value=0)
            
            valid_count = (grid_gdf['infra_count'] > 0).sum()
            logger.info(f"Found infrastructure in {valid_count}/{len(grid_gdf)} cells")
            
        except Exception as e:
            logger.error(f"Error computing infrastructure count: {e}")
            grid_gdf['infra_count'] = 0
        
        return grid_gdf
    
    @staticmethod
    def compute_complaint_density(grid_gdf: gpd.GeoDataFrame, complaint_path: Optional[str]) -> gpd.GeoDataFrame:
        """
        Compute flood complaint density (complaints per cell area)
        """
        if not complaint_path:
            logger.warning("No complaint path provided, setting complaint_density to 0")
            grid_gdf['complaint_density'] = 0.0
            return grid_gdf
        
        try:
            logger.info(f"Computing complaint density from: {complaint_path}")
            
            complaint_gdf = gpd.read_file(complaint_path)
            
            # Ensure same CRS
            if complaint_gdf.crs != grid_gdf.crs:
                complaint_gdf = complaint_gdf.to_crs(grid_gdf.crs)
            
            # Spatial join and count
            joined = gpd.sjoin(grid_gdf, complaint_gdf, how='left', predicate='contains')
            complaint_counts = joined.groupby(joined.index).size().reindex(grid_gdf.index, fill_value=0)
            
            # Normalize by cell area (complaints per sq km)
            cell_area_km2 = grid_gdf.geometry.area.iloc[0] / 1_000_000
            grid_gdf['complaint_density'] = complaint_counts / cell_area_km2
            
            valid_count = (grid_gdf['complaint_density'] > 0).sum()
            logger.info(f"Found complaints in {valid_count}/{len(grid_gdf)} cells")
            
        except Exception as e:
            logger.error(f"Error computing complaint density: {e}")
            grid_gdf['complaint_density'] = 0.0
        
        return grid_gdf
