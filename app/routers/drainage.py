"""
Drainage Simulation API Router
Endpoints for drainage stress simulation
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from app.services.drainage_simulator import DrainageSimulator
from app.services.synthetic_data_generator_simple import SyntheticDataGenerator
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/drainage", tags=["drainage"])
simulator = DrainageSimulator()


class SimulationRequest(BaseModel):
    """Request model for drainage simulation"""
    rainfall_intensity: float = Field(..., ge=0, le=300, description="Rainfall intensity in mm/hour")
    rain_duration: float = Field(..., ge=1, le=1440, description="Rain duration in minutes")
    lat_min: float = Field(18.45, description="Minimum latitude")
    lat_max: float = Field(18.60, description="Maximum latitude")
    lon_min: float = Field(73.75, description="Minimum longitude")
    lon_max: float = Field(73.95, description="Maximum longitude")
    timestep_minutes: Optional[int] = Field(5, ge=1, le=60, description="Timestep in minutes")


@router.post("/simulate")
async def simulate_drainage(request: SimulationRequest):
    """
    Simulate drainage stress for given rainfall conditions
    
    Returns timestep-by-timestep simulation results
    """
    try:
        # Generate grid cells with drainage data
        generator = SyntheticDataGenerator()
        grid_cells = generator.generate_grid_with_data(
            request.lat_min,
            request.lat_max,
            request.lon_min,
            request.lon_max,
            grid_size_km=0.25  # 250m cells
        )
        
        # Add drainage-specific properties
        for cell in grid_cells:
            # Assign drain capacity based on land use and elevation
            land_use = cell.get('land_use', 'mixed')
            elevation = cell.get('elevation', 600)
            
            # Base drain capacity (m³/s)
            if land_use == 'built_up':
                base_capacity = 60.0
            elif land_use == 'residential':
                base_capacity = 45.0
            elif land_use == 'commercial':
                base_capacity = 70.0
            elif land_use == 'industrial':
                base_capacity = 55.0
            elif land_use == 'vegetation':
                base_capacity = 30.0
            else:
                base_capacity = 50.0
            
            # Adjust for elevation (lower elevation = better drainage)
            elevation_factor = 1.0 + ((elevation - 600) / 100) * 0.1
            cell['drain_capacity'] = base_capacity / elevation_factor
        
        # Run full simulation
        results = simulator.simulate_full_event(
            grid_cells,
            request.rainfall_intensity,
            request.rain_duration,
            request.timestep_minutes
        )
        
        return {
            "status": "success",
            "simulation": results
        }
    
    except Exception as e:
        logger.error(f"Simulation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate-single-timestep")
async def simulate_single_timestep(request: SimulationRequest):
    """
    Simulate drainage stress for a single timestep
    Faster for real-time visualization
    """
    try:
        # Generate grid cells
        generator = SyntheticDataGenerator()
        grid_cells = generator.generate_grid_with_data(
            request.lat_min,
            request.lat_max,
            request.lon_min,
            request.lon_max,
            grid_size_km=0.25
        )
        
        # Add drainage properties
        for cell in grid_cells:
            land_use = cell.get('land_use', 'mixed')
            elevation = cell.get('elevation', 600)
            
            if land_use == 'built_up':
                base_capacity = 60.0
            elif land_use == 'residential':
                base_capacity = 45.0
            elif land_use == 'commercial':
                base_capacity = 70.0
            elif land_use == 'industrial':
                base_capacity = 55.0
            elif land_use == 'vegetation':
                base_capacity = 30.0
            else:
                base_capacity = 50.0
            
            elevation_factor = 1.0 + ((elevation - 600) / 100) * 0.1
            cell['drain_capacity'] = base_capacity / elevation_factor
        
        # Simulate single timestep
        results = simulator.simulate_timestep(
            grid_cells,
            request.rainfall_intensity,
            request.rain_duration,
            timestep=0
        )
        
        # Calculate summary
        summary = simulator._calculate_summary(results)
        
        return {
            "status": "success",
            "grid_cells": results,
            "summary": summary,
            "params": {
                "rainfall_intensity": request.rainfall_intensity,
                "rain_duration": request.rain_duration
            }
        }
    
    except Exception as e:
        logger.error(f"Simulation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drain-capacity-stats")
async def get_drain_capacity_stats(
    lat_min: float = Query(18.45),
    lat_max: float = Query(18.60),
    lon_min: float = Query(73.75),
    lon_max: float = Query(73.95)
):
    """Get drainage capacity statistics for the area"""
    try:
        generator = SyntheticDataGenerator()
        grid_cells = generator.generate_grid_with_data(
            lat_min, lat_max, lon_min, lon_max, grid_size_km=0.25
        )
        
        # Add drainage properties
        for cell in grid_cells:
            land_use = cell.get('land_use', 'mixed')
            elevation = cell.get('elevation', 600)
            
            if land_use == 'built_up':
                base_capacity = 60.0
            elif land_use == 'residential':
                base_capacity = 45.0
            else:
                base_capacity = 50.0
            
            elevation_factor = 1.0 + ((elevation - 600) / 100) * 0.1
            cell['drain_capacity'] = base_capacity / elevation_factor
        
        # Calculate statistics
        capacities = [c['drain_capacity'] for c in grid_cells]
        
        return {
            "status": "success",
            "total_cells": len(grid_cells),
            "avg_capacity": round(sum(capacities) / len(capacities), 2) if capacities else 0,
            "min_capacity": round(min(capacities), 2) if capacities else 0,
            "max_capacity": round(max(capacities), 2) if capacities else 0,
            "total_capacity_m3_per_s": round(sum(capacities), 2)
        }
    
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
