"""
Decision & Pre-Positioning API Router
Actionable deployment recommendations
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from app.services.decision_engine import DecisionEngine
from app.services.usps_engine import USPSEngine
from app.services.risk_engine import RiskEngine
from app.services.drainage_simulator import DrainageSimulator
from app.services.synthetic_data_generator_simple import SyntheticDataGenerator
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/decision", tags=["decision"])
decision_engine = DecisionEngine()
usps_engine = USPSEngine()
risk_engine = RiskEngine()
drainage_sim = DrainageSimulator()


class DeploymentRequest(BaseModel):
    """Request model for deployment plan generation"""
    lat_min: float = Field(18.45, description="Minimum latitude")
    lat_max: float = Field(18.60, description="Maximum latitude")
    lon_min: float = Field(73.75, description="Minimum longitude")
    lon_max: float = Field(73.95, description="Maximum longitude")
    include_drainage: Optional[bool] = Field(False, description="Include drainage simulation")
    rainfall_intensity: Optional[float] = Field(50.0, description="Rainfall intensity (mm/hr) if drainage included")
    available_resources: Optional[Dict[str, int]] = Field(None, description="Available resource inventory")


@router.post("/generate-plan")
async def generate_deployment_plan(request: DeploymentRequest):
    """
    Generate comprehensive deployment plan integrating all risk indicators
    
    Returns actionable recommendations for resource deployment
    """
    try:
        # Generate grid data
        generator = SyntheticDataGenerator()
        grid_cells = generator.generate_grid_with_data(
            request.lat_min,
            request.lat_max,
            request.lon_min,
            request.lon_max,
            grid_size_km=0.25
        )
        
        # Calculate USPS saturation
        usps_results = []
        for cell in grid_cells:
            result = usps_engine.calculate_usps(cell)
            usps_results.append({
                'cell_id': cell['cell_id'],
                'latitude': cell['latitude'],
                'longitude': cell['longitude'],
                'ward_name': cell['ward_name'],
                'overall_saturation': result['overall_saturation'],
                'subsystems': result['subsystems']
            })
        
        # Calculate HRVC risk
        hrvc_results = []
        for cell in grid_cells:
            risk_score = risk_engine.calculate_risk(
                cell['hazard'],
                cell['exposure'],
                cell['vulnerability'],
                cell['capacity']
            )
            hrvc_results.append({
                'cell_id': cell['cell_id'],
                'latitude': cell['latitude'],
                'longitude': cell['longitude'],
                'ward_name': cell['ward_name'],
                'risk_score': risk_score,
                'exposure': cell['population_density'],
                'vulnerability': cell['vulnerability']
            })
        
        # Calculate drainage stress (if requested)
        drainage_results = None
        if request.include_drainage:
            # Add drainage capacity to cells
            for cell in grid_cells:
                land_use = cell.get('land_use', 'mixed')
                if land_use == 'built_up':
                    cell['drain_capacity'] = 60.0
                elif land_use == 'residential':
                    cell['drain_capacity'] = 45.0
                else:
                    cell['drain_capacity'] = 50.0
            
            drainage_results = drainage_sim.simulate_timestep(
                grid_cells,
                request.rainfall_intensity,
                30  # 30 minutes duration
            )
        
        # Generate deployment plan
        plan = decision_engine.generate_deployment_plan(
            usps_results,
            hrvc_results,
            drainage_results,
            request.available_resources
        )
        
        return {
            "status": "success",
            "deployment_plan": plan
        }
    
    except Exception as e:
        logger.error(f"Deployment plan generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/critical-zones")
async def get_critical_zones(
    lat_min: float = Query(18.45),
    lat_max: float = Query(18.60),
    lon_min: float = Query(73.75),
    lon_max: float = Query(73.95)
):
    """Get list of critical zones requiring immediate attention"""
    try:
        # Generate grid data
        generator = SyntheticDataGenerator()
        grid_cells = generator.generate_grid_with_data(
            lat_min, lat_max, lon_min, lon_max, grid_size_km=0.25
        )
        
        # Calculate USPS
        usps_results = []
        for cell in grid_cells:
            result = usps_engine.calculate_usps(cell)
            usps_results.append({
                'cell_id': cell['cell_id'],
                'latitude': cell['latitude'],
                'longitude': cell['longitude'],
                'ward_name': cell['ward_name'],
                'overall_saturation': result['overall_saturation']
            })
        
        # Calculate HRVC
        hrvc_results = []
        for cell in grid_cells:
            risk_score = risk_engine.calculate_risk(
                cell['hazard'],
                cell['exposure'],
                cell['vulnerability'],
                cell['capacity']
            )
            hrvc_results.append({
                'cell_id': cell['cell_id'],
                'latitude': cell['latitude'],
                'longitude': cell['longitude'],
                'ward_name': cell['ward_name'],
                'risk_score': risk_score,
                'exposure': cell['population_density'],
                'vulnerability': cell['vulnerability']
            })
        
        # Integrate and identify critical zones
        integrated = decision_engine._integrate_risk_data(usps_results, hrvc_results, None)
        critical = decision_engine._identify_critical_zones(integrated)
        
        return {
            "status": "success",
            "total_zones": len(integrated),
            "critical_zones": len(critical),
            "zones": critical[:20]  # Top 20 critical zones
        }
    
    except Exception as e:
        logger.error(f"Critical zones error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resource-inventory")
async def get_resource_inventory():
    """Get current resource inventory and capabilities"""
    return {
        "status": "success",
        "resources": decision_engine.RESOURCE_TYPES,
        "default_inventory": decision_engine._get_default_resources()
    }


@router.post("/simulate-deployment")
async def simulate_deployment(
    cell_id: str = Query(..., description="Cell ID to deploy resources to"),
    resource_type: str = Query(..., description="Type of resource to deploy"),
    quantity: int = Query(1, description="Number of resources to deploy")
):
    """Simulate deployment of specific resource to a location"""
    try:
        if resource_type not in decision_engine.RESOURCE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid resource type. Must be one of: {list(decision_engine.RESOURCE_TYPES.keys())}"
            )
        
        resource_info = decision_engine.RESOURCE_TYPES[resource_type]
        
        from datetime import datetime, timedelta
        eta = datetime.now() + timedelta(minutes=resource_info['deployment_time_minutes'])
        
        return {
            "status": "success",
            "deployment": {
                "cell_id": cell_id,
                "resource_type": resource_type,
                "quantity": quantity,
                "eta": eta.isoformat(),
                "deployment_time_minutes": resource_info['deployment_time_minutes'],
                "effective_radius_km": resource_info['effective_radius_km'],
                "estimated_cost_per_hour": resource_info['cost_per_hour'] * quantity
            }
        }
    
    except Exception as e:
        logger.error(f"Deployment simulation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
