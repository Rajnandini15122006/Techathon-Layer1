"""
Risk Engine API Router
Endpoints for risk calculation and ward priorities
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.risk_engine import RiskEngine
from app.services.synthetic_data_generator_simple import SyntheticDataGenerator

router = APIRouter(prefix="/api/risk", tags=["risk"])
risk_engine = RiskEngine()


@router.get("/calculate")
async def calculate_risks(
    lat_min: float = Query(18.45, description="Minimum latitude"),
    lat_max: float = Query(18.55, description="Maximum latitude"),
    lon_min: float = Query(73.80, description="Minimum longitude"),
    lon_max: float = Query(73.90, description="Maximum longitude"),
    use_synthetic: bool = Query(True, description="Use synthetic data")
):
    """Calculate risk scores for grid cells in specified area"""
    try:
        # For now, always use synthetic data
        # TODO: Add database integration when needed
        generator = SyntheticDataGenerator()
        grid_cells = generator.generate_grid_with_data(
            lat_min, lat_max, lon_min, lon_max, grid_size_km=1.0
        )
        
        # Calculate risks
        results = risk_engine.calculate_grid_risks(grid_cells)
        
        return {
            "status": "success",
            "total_cells": len(results),
            "grid_cells": results,
            "summary": {
                "avg_risk": round(sum(c['risk_score'] for c in results) / len(results), 2) if results else 0,
                "max_risk": max((c['risk_score'] for c in results), default=0),
                "critical_cells": sum(1 for c in results if c['risk_score'] >= 80),
                "high_risk_cells": sum(1 for c in results if 60 <= c['risk_score'] < 80)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ward-priorities")
async def get_ward_priorities(
    lat_min: float = Query(18.45, description="Minimum latitude"),
    lat_max: float = Query(18.55, description="Maximum latitude"),
    lon_min: float = Query(73.80, description="Minimum longitude"),
    lon_max: float = Query(73.90, description="Maximum longitude"),
    use_synthetic: bool = Query(True, description="Use synthetic data")
):
    """Get ward priority list sorted by risk"""
    try:
        # For now, always use synthetic data
        generator = SyntheticDataGenerator()
        grid_cells = generator.generate_grid_with_data(
            lat_min, lat_max, lon_min, lon_max, grid_size_km=1.0
        )
        
        # Calculate risks first
        grid_with_risks = risk_engine.calculate_grid_risks(grid_cells)
        
        # Get ward priorities
        ward_priorities = risk_engine.get_ward_priorities(grid_with_risks)
        
        return {
            "status": "success",
            "total_wards": len(ward_priorities),
            "ward_priorities": ward_priorities
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate-single")
async def calculate_single_cell_risk(cell_data: dict):
    """Calculate risk for a single grid cell"""
    try:
        risk_data = risk_engine.calculate_risk_score(cell_data)
        return {
            "status": "success",
            "cell_data": cell_data,
            "risk_analysis": risk_data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
