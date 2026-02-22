"""
Urban System Pressure Score (USPS) API Router
Layer 2: Core Innovation - System Saturation Detection + Environmental Modeling
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.usps_engine import USPSEngine
from app.services.usps_data_generator import USPSDataGenerator
from app.services.environmental_engine import get_environmental_engine

router = APIRouter(prefix="/api/usps", tags=["usps"])
usps_engine = USPSEngine()
env_engine = get_environmental_engine()


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


@router.get("/environmental-usps")
async def calculate_environmental_usps(
    lat_min: float = Query(18.45, description="Minimum latitude"),
    lat_max: float = Query(18.55, description="Maximum latitude"),
    lon_min: float = Query(73.80, description="Minimum longitude"),
    lon_max: float = Query(73.90, description="Maximum longitude"),
    rainfall_mm: float = Query(25.0, description="Base rainfall (mm/hr)", ge=0),
    accumulated_1hr: float = Query(30.0, description="Base accumulated rainfall (mm)", ge=0),
    traffic_level: float = Query(0.5, description="Base traffic congestion (0-1)", ge=0, le=1)
):
    """
    Calculate USPS using Environmental Engine with SCS-CN hydrological modeling
    
    This endpoint uses production-grade environmental modeling:
    - SCS-CN method for runoff estimation
    - Deterministic drain stress calculation
    - Multi-criteria composite scoring
    - Spatial variation for realistic area-based differences
    """
    try:
        import random
        import math
        
        generator = USPSDataGenerator()
        grid_cells = generator.generate_grid_with_usps_data(
            lat_min, lat_max, lon_min, lon_max, grid_size_km=1.0
        )
        
        # Pune center coordinates for spatial variation
        pune_center_lat = 18.5204
        pune_center_lon = 73.8567
        
        # Create spatial variation patterns using sine waves for smooth gradients
        # This creates realistic weather patterns and infrastructure variations
        env_results = []
        for idx, cell in enumerate(grid_cells):
            # Calculate distance and angle from Pune center
            delta_lat = cell['latitude'] - pune_center_lat
            delta_lon = cell['longitude'] - pune_center_lon
            dist_from_center = math.sqrt(delta_lat**2 + delta_lon**2) * 111  # km
            angle = math.atan2(delta_lat, delta_lon)  # Radians
            
            # Urban core classification
            is_urban_core = dist_from_center < 5
            
            # RAINFALL VARIATION - Create weather pattern with spatial gradients
            # Use sine waves to create realistic rain bands
            rain_pattern = (
                math.sin(cell['latitude'] * 50) * 0.15 +  # North-South gradient
                math.cos(cell['longitude'] * 50) * 0.15 +  # East-West gradient
                math.sin(angle * 3) * 0.1  # Circular pattern
            )
            # Add random local variation
            rain_noise = random.uniform(-0.1, 0.1)
            rainfall_multiplier = 1.0 + rain_pattern + rain_noise
            rainfall_multiplier = max(0.5, min(1.5, rainfall_multiplier))  # Clamp to 0.5-1.5x
            
            cell_rainfall = rainfall_mm * rainfall_multiplier
            cell_accumulated = accumulated_1hr * rainfall_multiplier
            
            # TRAFFIC VARIATION - Based on distance from center and time patterns
            if is_urban_core:
                # Urban core: high base traffic with variation
                traffic_base = 0.7 + random.uniform(-0.1, 0.2)
                # Add radial pattern (some roads more congested)
                traffic_pattern = math.sin(angle * 5) * 0.15
                traffic_multiplier = traffic_base + traffic_pattern
            else:
                # Periphery: lower traffic
                traffic_base = 0.3 + random.uniform(-0.1, 0.2)
                # Distance decay
                distance_factor = max(0, 1 - (dist_from_center / 15))
                traffic_multiplier = traffic_base * (0.5 + distance_factor * 0.5)
            
            cell_traffic = traffic_level * traffic_multiplier
            cell_traffic = max(0.0, min(1.0, cell_traffic))
            
            # DRAIN CAPACITY VARIATION - Infrastructure quality
            if is_urban_core:
                # Better infrastructure in city center
                base_capacity = 1500.0
                capacity_variation = random.uniform(-300, 500)
            else:
                # Older/smaller drains in periphery
                base_capacity = 800.0
                capacity_variation = random.uniform(-200, 300)
                # Degrade with distance
                distance_penalty = (dist_from_center / 15) * 300
                capacity_variation -= distance_penalty
            
            drain_capacity = base_capacity + capacity_variation
            drain_capacity = max(400.0, drain_capacity)  # Minimum capacity
            
            # LAND USE - Based on location and patterns
            land_use_rand = random.random()
            if is_urban_core:
                if land_use_rand < 0.5:
                    land_use = 'Built-up'
                elif land_use_rand < 0.8:
                    land_use = 'Commercial'
                else:
                    land_use = 'Residential'
            else:
                if land_use_rand < 0.4:
                    land_use = 'Residential'
                elif land_use_rand < 0.7:
                    land_use = 'Mixed'
                else:
                    land_use = 'Vegetation'
            
            # Compute environmental state using SCS-CN model
            env_state = env_engine.compute_environmental_state(
                rainfall_mm=cell_rainfall,
                accumulated_1hr=cell_accumulated,
                land_use=land_use,
                grid_area_m2=62500.0,  # 250m x 250m
                drain_capacity_m3=drain_capacity,
                traffic_congestion=cell_traffic
            )
            
            # Add environmental data to cell
            cell['environmental'] = {
                'rain_index': env_state['rain']['rain_index'],
                'runoff_mm': env_state['drain']['runoff_mm'],
                'drain_stress': env_state['drain']['drain_stress'],
                'curve_number': env_state['drain']['curve_number'],
                'traffic_index': env_state['traffic']['traffic_index'],
                'usps_score': env_state['usps']['usps_score'],
                'severity_level': env_state['usps']['severity_level'],
                'land_use': land_use,
                'drain_capacity_m3': round(drain_capacity, 1),
                'actual_rainfall_mm': round(cell_rainfall, 2),
                'actual_traffic': round(cell_traffic, 3),
                'distance_from_center_km': round(dist_from_center, 2)
            }
            
            # Convert USPS (0-1) to percentage (0-100) for consistency
            cell['usps_score'] = env_state['usps']['usps_score'] * 100
            cell['severity_level'] = env_state['usps']['severity_level']
            cell['land_use'] = land_use
            
            env_results.append(cell)
        
        # Calculate statistics
        usps_scores = [c['usps_score'] for c in env_results]
        severity_counts = {}
        for cell in env_results:
            severity = cell['severity_level']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "status": "success",
            "model": "Environmental Engine (SCS-CN) with Spatial Variation",
            "parameters": {
                "base_rainfall_mm": rainfall_mm,
                "base_accumulated_1hr": accumulated_1hr,
                "base_traffic_level": traffic_level,
                "spatial_variation": "Weather patterns, distance-based traffic & infrastructure quality"
            },
            "total_cells": len(env_results),
            "grid_cells": env_results,
            "summary": {
                "avg_usps": round(sum(usps_scores) / len(usps_scores), 2) if usps_scores else 0,
                "max_usps": round(max(usps_scores), 2) if usps_scores else 0,
                "min_usps": round(min(usps_scores), 2) if usps_scores else 0,
                "severity_distribution": severity_counts,
                "critical_cells": severity_counts.get('Critical', 0),
                "high_alert_cells": severity_counts.get('High Alert', 0),
                "watch_cells": severity_counts.get('Watch', 0),
                "stable_cells": severity_counts.get('Stable', 0)
            },
            "methodology": {
                "runoff_model": "SCS-CN (Soil Conservation Service Curve Number)",
                "drain_stress": "Runoff Volume / Drain Capacity",
                "usps_formula": "0.4*Rain + 0.4*Drain + 0.2*Traffic",
                "spatial_variation": "Sine-wave weather patterns + distance-based infrastructure",
                "deterministic": False,
                "explainable": True
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

