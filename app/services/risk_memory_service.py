"""
Phase 2: Risk Memory & Hotspot Evolution Service
Transparent, deterministic logic for government audit compliance
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import math


class RiskMemoryService:
    """
    Risk Memory & Hotspot Evolution Engine
    - Compares predictions vs actual outcomes
    - Detects emerging hotspots
    - Adjusts model weights transparently
    """
    
    # Hotspot detection weights (transparent, auditable)
    HOTSPOT_WEIGHTS = {
        'repeat_overflow': 0.35,
        'complaint_count': 0.25,
        'prediction_error': 0.20,
        'damage_severity': 0.20
    }
    
    # Thresholds for hotspot classification
    HOTSPOT_THRESHOLDS = {
        'stable': 0.0,
        'watchlist': 0.40,
        'emerging': 0.65,
        'chronic': 0.85
    }
    
    # Prediction error tolerance
    ACCEPTABLE_ERROR = 0.15  # 15% error tolerance
    
    def __init__(self):
        self.weight_adjustment_history = []
    
    def calculate_prediction_error(
        self,
        predicted_risk: float,
        actual_impact: Dict
    ) -> float:
        """
        Calculate normalized prediction error
        
        Formula: error = |predicted - normalized_actual| / max_scale
        
        Args:
            predicted_risk: Predicted risk score (0-1)
            actual_impact: Dict with observed_flood_depth, damage_count, etc.
            
        Returns:
            Normalized error (0-1)
        """
        # Normalize actual impact to 0-1 scale
        flood_depth_norm = min(actual_impact.get('observed_flood_depth', 0) / 100, 1.0)
        damage_norm = min(actual_impact.get('infrastructure_damage_count', 0) / 10, 1.0)
        blockage_norm = actual_impact.get('road_blockage_flag', 0)
        
        # Weighted actual impact score
        actual_score = (
            flood_depth_norm * 0.5 +
            damage_norm * 0.3 +
            blockage_norm * 0.2
        )
        
        # Calculate absolute error
        error = abs(predicted_risk - actual_score)
        
        return round(error, 4)
    
    def calculate_hotspot_score(
        self,
        repeat_overflow_count: int,
        complaint_count: int,
        avg_prediction_error: float,
        damage_severity_avg: float
    ) -> float:
        """
        Calculate hotspot score using transparent weighted formula
        
        Formula:
        hotspot_score = Σ(normalized_metric * weight)
        
        Returns:
            Score between 0-1
        """
        # Normalize metrics to 0-1 scale
        overflow_norm = min(repeat_overflow_count / 10, 1.0)
        complaint_norm = min(complaint_count / 50, 1.0)
        error_norm = min(avg_prediction_error / 0.5, 1.0)
        damage_norm = min(damage_severity_avg, 1.0)
        
        # Calculate weighted score
        score = (
            overflow_norm * self.HOTSPOT_WEIGHTS['repeat_overflow'] +
            complaint_norm * self.HOTSPOT_WEIGHTS['complaint_count'] +
            error_norm * self.HOTSPOT_WEIGHTS['prediction_error'] +
            damage_norm * self.HOTSPOT_WEIGHTS['damage_severity']
        )
        
        return round(score, 4)
    
    def classify_hotspot_status(self, hotspot_score: float) -> str:
        """
        Classify grid cell hotspot status based on score
        
        Returns:
            'stable', 'watchlist', 'emerging', or 'chronic'
        """
        if hotspot_score >= self.HOTSPOT_THRESHOLDS['chronic']:
            return 'chronic'
        elif hotspot_score >= self.HOTSPOT_THRESHOLDS['emerging']:
            return 'emerging'
        elif hotspot_score >= self.HOTSPOT_THRESHOLDS['watchlist']:
            return 'watchlist'
        else:
            return 'stable'
    
    def detect_emerging_hotspots(
        self,
        grid_summaries: List[Dict]
    ) -> List[Dict]:
        """
        Identify emerging hotspots from grid summaries
        
        Returns:
            List of hotspot grids with scores and recommendations
        """
        hotspots = []
        
        for grid in grid_summaries:
            score = self.calculate_hotspot_score(
                grid.get('repeat_overflow_count', 0),
                grid.get('complaint_count', 0),
                grid.get('avg_prediction_error', 0),
                grid.get('damage_severity_avg', 0)
            )
            
            status = self.classify_hotspot_status(score)
            
            if status in ['emerging', 'chronic']:
                hotspots.append({
                    'grid_id': grid['grid_id'],
                    'ward_name': grid.get('ward_name', 'Unknown'),
                    'hotspot_score': score,
                    'status': status,
                    'repeat_overflow_count': grid.get('repeat_overflow_count', 0),
                    'complaint_count': grid.get('complaint_count', 0),
                    'avg_prediction_error': grid.get('avg_prediction_error', 0),
                    'recommendation': self._generate_recommendation(grid, status)
                })
        
        # Sort by score (highest first)
        hotspots.sort(key=lambda x: x['hotspot_score'], reverse=True)
        
        return hotspots
    
    def _generate_recommendation(self, grid: Dict, status: str) -> str:
        """Generate infrastructure upgrade recommendation"""
        recommendations = []
        
        if grid.get('repeat_overflow_count', 0) > 5:
            recommendations.append("Upgrade drainage capacity by 30-40%")
        
        if grid.get('complaint_count', 0) > 20:
            recommendations.append("Increase emergency response resources")
        
        if grid.get('avg_prediction_error', 0) > 0.3:
            recommendations.append("Install real-time monitoring sensors")
        
        if status == 'chronic':
            recommendations.append("URGENT: Structural infrastructure overhaul required")
        
        return "; ".join(recommendations) if recommendations else "Continue monitoring"
    
    def calculate_weight_adjustment(
        self,
        grid_errors: List[Dict]
    ) -> Dict[str, float]:
        """
        Calculate model weight adjustments based on systematic errors
        
        Transparent logic:
        - If consistently underpredicting: increase hazard/vulnerability weights
        - If consistently overpredicting: increase capacity weight
        
        Returns:
            Dict with adjusted weights and reasoning
        """
        if not grid_errors:
            return None
        
        # Analyze error patterns
        total_error = sum(e['error'] for e in grid_errors)
        avg_error = total_error / len(grid_errors)
        
        underpredictions = sum(1 for e in grid_errors if e['predicted'] < e['actual'])
        overpredictions = sum(1 for e in grid_errors if e['predicted'] > e['actual'])
        
        # Current weights (baseline)
        weights = {
            'hazard': 0.30,
            'exposure': 0.25,
            'vulnerability': 0.25,
            'capacity': 0.20
        }
        
        adjustment_reason = []
        
        # Adjustment logic (transparent, deterministic)
        if underpredictions > overpredictions * 1.5:
            # Systematically underpredicting - increase risk factors
            weights['hazard'] += 0.05
            weights['vulnerability'] += 0.05
            weights['capacity'] -= 0.05
            weights['exposure'] -= 0.05
            adjustment_reason.append(f"Systematic underprediction detected ({underpredictions}/{len(grid_errors)} cases)")
        
        elif overpredictions > underpredictions * 1.5:
            # Systematically overpredicting - increase capacity weight
            weights['capacity'] += 0.05
            weights['hazard'] -= 0.03
            weights['vulnerability'] -= 0.02
            adjustment_reason.append(f"Systematic overprediction detected ({overpredictions}/{len(grid_errors)} cases)")
        
        # Normalize weights to sum to 1.0
        total = sum(weights.values())
        weights = {k: round(v / total, 3) for k, v in weights.items()}
        
        return {
            'weights': weights,
            'reason': "; ".join(adjustment_reason),
            'avg_error': round(avg_error, 4),
            'affected_grids': len(grid_errors)
        }
    
    def calculate_response_metrics(
        self,
        response_logs: List[Dict]
    ) -> Dict:
        """Calculate response time statistics"""
        if not response_logs:
            return {
                'avg_response_time': 0,
                'min_response_time': 0,
                'max_response_time': 0,
                'total_responses': 0
            }
        
        response_times = [r['response_time_minutes'] for r in response_logs if r.get('response_time_minutes')]
        
        return {
            'avg_response_time': round(sum(response_times) / len(response_times), 2) if response_times else 0,
            'min_response_time': round(min(response_times), 2) if response_times else 0,
            'max_response_time': round(max(response_times), 2) if response_times else 0,
            'total_responses': len(response_logs)
        }
    
    def generate_audit_report(
        self,
        grid_id: int,
        predictions: List[Dict],
        actual_impacts: List[Dict],
        responses: List[Dict]
    ) -> Dict:
        """
        Generate comprehensive audit report for a grid cell
        
        Returns:
            Detailed report with all calculations and reasoning
        """
        # Calculate prediction accuracy
        errors = []
        for pred in predictions:
            matching_actual = next(
                (a for a in actual_impacts if abs((a['timestamp'] - pred['timestamp']).total_seconds()) < 3600),
                None
            )
            if matching_actual:
                error = self.calculate_prediction_error(
                    pred['predicted_risk_score'],
                    matching_actual
                )
                errors.append(error)
        
        avg_error = sum(errors) / len(errors) if errors else 0
        accuracy = max(0, 1 - avg_error)
        
        return {
            'grid_id': grid_id,
            'total_predictions': len(predictions),
            'total_actual_events': len(actual_impacts),
            'matched_events': len(errors),
            'avg_prediction_error': round(avg_error, 4),
            'prediction_accuracy': round(accuracy * 100, 2),
            'response_metrics': self.calculate_response_metrics(responses),
            'audit_timestamp': datetime.utcnow().isoformat(),
            'methodology': 'Transparent deterministic comparison - no black-box AI'
        }
