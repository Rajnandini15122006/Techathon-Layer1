from sqlalchemy.orm import Session
from sqlalchemy import text
from geoalchemy2.shape import from_shape, to_shape
from geoalchemy2.functions import ST_AsGeoJSON
from app.models.grid_cell import GridCell
from typing import List, Optional
from uuid import UUID
import json

class GridService:
    @staticmethod
    def create_grid_cell(db: Session, grid_data: dict) -> GridCell:
        """Create a new grid cell"""
        db_grid = GridCell(**grid_data)
        db.add(db_grid)
        db.commit()
        db.refresh(db_grid)
        return db_grid
    
    @staticmethod
    def get_all_grid_cells(db: Session, skip: int = 0, limit: int = 100) -> List[GridCell]:
        """Get all grid cells with pagination"""
        return db.query(GridCell).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_grid_cell_by_id(db: Session, cell_id: UUID) -> Optional[GridCell]:
        """Get a specific grid cell by ID"""
        return db.query(GridCell).filter(GridCell.id == cell_id).first()
    
    @staticmethod
    def get_grid_cells_geojson(db: Session, skip: int = 0, limit: int = 100) -> dict:
        """Get grid cells as GeoJSON FeatureCollection"""
        query = text("""
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features', jsonb_agg(feature)
            ) as geojson
            FROM (
                SELECT jsonb_build_object(
                    'type', 'Feature',
                    'id', id::text,
                    'geometry', ST_AsGeoJSON(geom)::jsonb,
                    'properties', jsonb_build_object(
                        'elevation_mean', elevation_mean,
                        'drain_distance', drain_distance,
                        'land_use', land_use,
                        'population_density', population_density,
                        'slum_density', slum_density,
                        'flood_depth_avg', flood_depth_avg,
                        'infra_count', infra_count,
                        'complaint_density', complaint_density,
                        'hazard_score', hazard_score,
                        'vulnerability_score', vulnerability_score,
                        'capacity_score', capacity_score,
                        'risk_score', risk_score,
                        'risk_level', risk_level,
                        'created_at', created_at
                    )
                ) as feature
                FROM grid_cells
                ORDER BY created_at
                OFFSET :skip LIMIT :limit
            ) features
        """)
        
        result = db.execute(query, {"skip": skip, "limit": limit}).fetchone()
        return result[0] if result and result[0] else {"type": "FeatureCollection", "features": []}
    
    @staticmethod
    def get_grid_cell_geojson(db: Session, cell_id: UUID) -> Optional[dict]:
        """Get a single grid cell as GeoJSON Feature"""
        query = text("""
            SELECT jsonb_build_object(
                'type', 'Feature',
                'id', id::text,
                'geometry', ST_AsGeoJSON(geom)::jsonb,
                'properties', jsonb_build_object(
                    'elevation_mean', elevation_mean,
                    'drain_distance', drain_distance,
                    'land_use', land_use,
                    'population_density', population_density,
                    'slum_density', slum_density,
                    'flood_depth_avg', flood_depth_avg,
                    'infra_count', infra_count,
                    'complaint_density', complaint_density,
                    'created_at', created_at
                )
            ) as feature
            FROM grid_cells
            WHERE id = :cell_id
        """)
        
        result = db.execute(query, {"cell_id": str(cell_id)}).fetchone()
        return result[0] if result else None
    
    @staticmethod
    def bulk_insert_grid_cells(db: Session, grid_gdf) -> int:
        """Bulk insert grid cells from GeoDataFrame"""
        from geoalchemy2.shape import from_shape
        
        records = []
        for idx, row in grid_gdf.iterrows():
            record = {
                'geom': from_shape(row.geometry, srid=4326),
                'elevation_mean': row.get('elevation_mean'),
                'slope_mean': row.get('slope_mean'),
                'drain_distance': row.get('drain_distance'),
                'land_use': row.get('land_use'),
                'population_density': row.get('population_density'),
                'slum_density': row.get('slum_density'),
                'flood_history_score': int(row.get('flood_history_score', 0)),
                'infra_score': int(row.get('infra_score', 0))
            }
            records.append(GridCell(**record))
        
        db.bulk_save_objects(records)
        db.commit()
        return len(records)
