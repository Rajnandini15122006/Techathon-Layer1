"""
Urban System Pressure Score (USPS) API Router
Layer 2: Core Innovation - System Saturation Detection
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.usps_engine import USPSEngine
from app.services.usps_data_generator import USPSDataGenerator

router = APIRouter(prefix="/api/usps", tags=["usps"])
usps_engine = USPSEngine()


@router.get("/calculate")
async def calculate_usps(
    lat_min: float = Query(18.45, description="Minimum latitude"),
    lat_max: float = Query(18.55, description="Maximum latitude"),
    lon_min: float = Query(73.80, description="Minimum longitude"),
    lon_max: float = Query(73.90, description="Maximum longitude"),
    use_synthetic: bool = Query(True, description="Use synthetic data")
):
    """Calculate Urban System Pressure Scores for grid cells"""
    try:
        # Generate synthetic data with USPS fields
        generator = USPSDataGenerator()
        grid_cells = generator.generate_grid_with_usps_data(
            lat_min, lat_max, lon_min, lon_max, grid_size_km=1.0
        )
        
        # Calculate USPS
        results = usps_engine.calculate_grid_usps(grid_cells)
        
        # Statistics
        usps_scores = [c['usps_score'] for c in results]
        cascade_warnings = usps_engine.get_cascade_warnings(results)
        critical_cells = usps_engine.get_critical_cells(results, threshold=70)
        
        return {
            "status": "success",
            "total_cells": len(results),
            "grid_cells": results,
            "summary": {
                "avg_usps": round(sum(usps_scores) / len(usps_scores), 2) if usps_scores else 0,
                "max_usps": round(max(usps_scores), 2) if usps_scores else 0,
                "critical_cells": len(critical_cells),
                "cascade_warnings": len(cascade_warnings),
                "emergency_cells": sum(1 for c in results if c['usps_score'] >= 90)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cascade-warnings")
async def get_cascade_warnings(
    lat_min: float = Query(18.45, description="Minimum latitude"),
    lat_max: float = Query(18.55, description="Maximum latitude"),
    lon_min: float = Query(73.80, description="Minimum longitude"),
    lon_max: float = Query(73.90, description="Maximum longitude")
):
    """Get cells with cascading failure risk"""
    try:
        generator = USPSDataGenerator()
        grid_cells = generator.generate_grid_with_usps_data(
            lat_min, lat_max, lon_min, lon_max, grid_size_km=1.0
        )
        
        results = usps_engine.calculate_grid_usps(grid_cells)
        cascade_cells = usps_engine.get_cascade_warnings(results)
        
        # Sort by number of systems at risk
        cascade_cells.sort(
            key=lambda x: x['cascade_analysis']['systems_at_risk'],
            reverse=True
        )
        
        return {
            "status": "success",
            "total_warnings": len(cascade_cells),
            "cascade_cells": cascade_cells,
            "summary": {
                "emergency": sum(1 for c in cascade_cells if c['cascade_analysis']['cascade_level'] == 'EMERGENCY'),
                "critical": sum(1 for c in cascade_cells if c['cascade_analysis']['cascade_level'] == 'CRITICAL'),
                "warning": sum(1 for c in cascade_cells if c['cascade_analysis']['cascade_level'] == 'WARNING')
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/critical-cells")
async def get_critical_cells(
    lat_min: float = Query(18.45, description="Minimum latitude"),
    lat_max: float = Query(18.55, description="Maximum latitude"),
    lon_min: float = Query(73.80, description="Minimum longitude"),
    lon_max: float = Query(73.90, description="Maximum longitude"),
    threshold: float = Query(70.0, description="USPS threshold", ge=0, le=100)
):
    """Get cells with USPS above threshold"""
    try:
        generator = USPSDataGenerator()
        grid_cells = generator.generate_grid_with_usps_data(
            lat_min, lat_max, lon_min, lon_max, grid_size_km=1.0
        )
        
        results = usps_engine.calculate_grid_usps(grid_cells)
        critical_cells = usps_engine.get_critical_cells(results, threshold)
        
        # Sort by USPS score
        critical_cells.sort(key=lambda x: x['usps_score'], reverse=True)
        
        return {
            "status": "success",
            "threshold": threshold,
            "total_critical": len(critical_cells),
            "critical_cells": critical_cells
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate-single")
async def calculate_single_cell_usps(cell_data: dict):
    """Calculate USPS for a single grid cell"""
    try:
        usps_data = usps_engine.calculate_usps(cell_data)
        return {
            "status": "success",
            "cell_data": cell_data,
            "usps_analysis": usps_data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subsystem-status")
async def get_subsystem_status(
    lat_min: float = Query(18.45, description="Minimum latitude"),
    lat_max: float = Query(18.55, description="Maximum latitude"),
    lon_min: float = Query(73.80, description="Minimum longitude"),
    lon_max: float = Query(73.90, description="Maximum longitude")
):
    """Get aggregated subsystem status across area"""
    try:
        generator = USPSDataGenerator()
        grid_cells = generator.generate_grid_with_usps_data(
            lat_min, lat_max, lon_min, lon_max, grid_size_km=1.0
        )
        
        results = usps_engine.calculate_grid_usps(grid_cells)
        
        # Aggregate subsystem pressures
        subsystems = ['rain_accumulation', 'drain_capacity_load', 'road_congestion', 
                     'hospital_occupancy', 'power_stress']
        
        subsystem_stats = {}
        for subsystem in subsystems:
            pressures = [
                c['subsystem_pressures'][subsystem] 
                for c in results
            ]
            subsystem_stats[subsystem] = {
                'avg_pressure': round(sum(pressures) / len(pressures), 2),
                'max_pressure': round(max(pressures), 2),
                'cells_critical': sum(1 for p in pressures if p >= 80),
                'cells_stressed': sum(1 for p in pressures if p >= 60)
            }
        
        return {
            "status": "success",
            "subsystem_status": subsystem_stats,
            "overall": {
                "total_cells": len(results),
                "avg_usps": round(sum(c['usps_score'] for c in results) / len(results), 2)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
