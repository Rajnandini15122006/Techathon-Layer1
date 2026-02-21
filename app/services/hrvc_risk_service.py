"""
Layer 3: HRVC Risk Engine
Computes Hazard × Vulnerability / Capacity risk scores
"""
import numpy as np
from sqlalchemy.orm import Session
from app.models.grid_cell import GridCell
import logging

logger = logging.getLogger(__name__)

class HRVCRiskService:
    """
    HRVC Risk Scoring Engine
    Risk = (Hazard × Vulnerability) / Capacity
    """
    
    @staticmethod
    def normalize(value, min_val, max_val):
        """Normalize value to 0-100 scale"""
        if max_val == min_val:
            return 50.0
        return ((value - min_val) / (max_val - min_val)) * 100
    
    @staticmethod
    def compute_hazard_score(cell: GridCell, stats: dict) -> float:
        """
        Hazard Score (0-100)
        Higher = More hazardous
        
        Factors:
        - flood_depth_avg (40%) - Historical flooding
        - elevation_mean (30%) - Lower elevation = higher risk
        - drain_distance (30%) - Closer to drain = higher risk
        """
        scores = []
        
        # Flood depth (higher = worse)
        if cell.flood_depth_avg is not None:
            flood_score = HRVCRiskService.normalize(
                cell.flood_depth_avg,
                stats['flood_depth_min'],
                stats['flood_depth_max']
            )
            scores.append(flood_score * 0.4)
        
        # Elevation (lower = worse, so invert)
        if cell.elevation_mean is not None:
            elev_score = 100 - HRVCRiskService.normalize(
                cell.elevation_mean,
                stats['elevation_min'],
                stats['elevation_max']
            )
            scores.append(elev_score * 0.3)
        
        # Drain distance (closer = worse, so invert)
        if cell.drain_distance is not None:
            drain_score = 100 - HRVCRiskService.normalize(
                cell.drain_distance,
                stats['drain_distance_min'],
                stats['drain_distance_max']
            )
            scores.append(drain_score * 0.3)
        
        return sum(scores) if scores else 50.0
    
    @staticmethod
    def compute_vulnerability_score(cell: GridCell, stats: dict) -> float:
        """
        Vulnerability Score (0-100)
        Higher = More vulnerable population
        
        Factors:
        - population_density (50%) - More people = higher vulnerability
        - slum_density (40%) - Informal settlements = higher vulnerability
        - land_use (10%) - Residential > Commercial > Others
        """
        scores = []
        
        # Population density
        if cell.population_density is not None:
            pop_score = HRVCRiskService.normalize(
                cell.population_density,
                stats['population_min'],
                stats['population_max']
            )
            scores.append(pop_score * 0.5)
        
        # Slum density
        if cell.slum_density is not None:
            slum_score = HRVCRiskService.normalize(
                cell.slum_density,
                stats['slum_density_min'],
                stats['slum_density_max']
            )
            scores.append(slum_score * 0.4)
        
        # Land use
        land_use_scores = {
            'Residential': 80,
            'Commercial': 60,
            'Mixed': 70,
            'Agricultural': 30,
            'Forest': 10
        }
        if cell.land_use:
            scores.append(land_use_scores.get(cell.land_use, 50) * 0.1)
        
        return sum(scores) if scores else 50.0
    
    @staticmethod
    def compute_capacity_score(cell: GridCell, stats: dict) -> float:
        """
        Capacity Score (0-100)
        Higher = Better capacity to handle disaster
        
        Factors:
        - infra_count (60%) - More infrastructure = better capacity
        - complaint_density (40%) - More complaints = worse capacity (inverted)
        """
        scores = []
        
        # Infrastructure count
        if cell.infra_count is not None:
            infra_score = HRVCRiskService.normalize(
                cell.infra_count,
                stats['infra_count_min'],
                stats['infra_count_max']
            )
            scores.append(infra_score * 0.6)
        
        # Complaint density (inverted - more complaints = worse capacity)
        if cell.complaint_density is not None:
            complaint_score = 100 - HRVCRiskService.normalize(
                cell.complaint_density,
                stats['complaint_density_min'],
                stats['complaint_density_max']
            )
            scores.append(complaint_score * 0.4)
        
        # Ensure minimum capacity of 10 to avoid division by zero
        return max(sum(scores) if scores else 50.0, 10.0)
    
    @staticmethod
    def compute_risk_level(risk_score: float) -> str:
        """Categorize risk score into levels"""
        if risk_score >= 75:
            return "Critical"
        elif risk_score >= 50:
            return "High"
        elif risk_score >= 25:
            return "Medium"
        else:
            return "Low"
    
    @staticmethod
    def compute_all_risks(db: Session) -> dict:
        """
        Compute HRVC risk scores for all grid cells
        """
        logger.info("=" * 80)
        logger.info("COMPUTING HRVC RISK SCORES")
        logger.info("=" * 80)
        
        # Get all cells
        cells = db.query(GridCell).all()
        if not cells:
            raise ValueError("No grid cells found. Generate grid first.")
        
        logger.info(f"Processing {len(cells)} grid cells...")
        
        # Compute statistics for normalization
        stats = {
            'flood_depth_min': min(c.flood_depth_avg for c in cells if c.flood_depth_avg is not None),
            'flood_depth_max': max(c.flood_depth_avg for c in cells if c.flood_depth_avg is not None),
            'elevation_min': min(c.elevation_mean for c in cells if c.elevation_mean is not None),
            'elevation_max': max(c.elevation_mean for c in cells if c.elevation_mean is not None),
            'drain_distance_min': min(c.drain_distance for c in cells if c.drain_distance is not None),
            'drain_distance_max': max(c.drain_distance for c in cells if c.drain_distance is not None),
            'population_min': min(c.population_density for c in cells if c.population_density is not None),
            'population_max': max(c.population_density for c in cells if c.population_density is not None),
            'slum_density_min': min(c.slum_density for c in cells if c.slum_density is not None),
            'slum_density_max': max(c.slum_density for c in cells if c.slum_density is not None),
            'infra_count_min': min(c.infra_count for c in cells if c.infra_count is not None),
            'infra_count_max': max(c.infra_count for c in cells if c.infra_count is not None),
            'complaint_density_min': min(c.complaint_density for c in cells if c.complaint_density is not None),
            'complaint_density_max': max(c.complaint_density for c in cells if c.complaint_density is not None),
        }
        
        # Compute scores for each cell
        risk_scores = []
        for cell in cells:
            # Compute component scores
            hazard = HRVCRiskService.compute_hazard_score(cell, stats)
            vulnerability = HRVCRiskService.compute_vulnerability_score(cell, stats)
            capacity = HRVCRiskService.compute_capacity_score(cell, stats)
            
            # Final risk = (H × V) / C
            risk = (hazard * vulnerability) / capacity
            
            # Normalize to 0-100
            risk = min(risk, 100.0)
            
            # Update cell
            cell.hazard_score = round(hazard, 2)
            cell.vulnerability_score = round(vulnerability, 2)
            cell.capacity_score = round(capacity, 2)
            cell.risk_score = round(risk, 2)
            cell.risk_level = HRVCRiskService.compute_risk_level(risk)
            
            risk_scores.append(risk)
        
        # Commit all updates
        db.commit()
        
        # Generate summary statistics
        risk_scores = np.array(risk_scores)
        risk_levels = [c.risk_level for c in cells]
        
        summary = {
            "status": "success",
            "total_cells": len(cells),
            "risk_statistics": {
                "mean": float(risk_scores.mean()),
                "median": float(np.median(risk_scores)),
                "min": float(risk_scores.min()),
                "max": float(risk_scores.max()),
                "std": float(risk_scores.std())
            },
            "risk_distribution": {
                "Critical": risk_levels.count("Critical"),
                "High": risk_levels.count("High"),
                "Medium": risk_levels.count("Medium"),
                "Low": risk_levels.count("Low")
            }
        }
        
        logger.info("=" * 80)
        logger.info("HRVC RISK COMPUTATION COMPLETE")
        logger.info(f"Mean Risk Score: {summary['risk_statistics']['mean']:.2f}")
        logger.info(f"Risk Distribution:")
        for level, count in summary['risk_distribution'].items():
            pct = (count / len(cells)) * 100
            logger.info(f"  {level}: {count} cells ({pct:.1f}%)")
        logger.info("=" * 80)
        
        return summary
