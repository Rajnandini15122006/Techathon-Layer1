"""
Decision & Pre-Positioning Engine
Converts risk analysis into actionable deployment recommendations
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import math


class DecisionEngine:
    """
    Intelligent resource deployment and pre-positioning engine
    Integrates USPS, HRVC, and Drainage data to generate actionable decisions
    """
    
    # Resource types and their capabilities
    RESOURCE_TYPES = {
        'pump': {
            'capacity_m3_per_hour': 500,
            'deployment_time_minutes': 30,
            'effective_radius_km': 1.0,
            'cost_per_hour': 5000
        },
        'ambulance': {
            'capacity_patients': 2,
            'deployment_time_minutes': 15,
            'effective_radius_km': 3.0,
            'cost_per_hour': 2000
        },
        'rescue_boat': {
            'capacity_people': 8,
            'deployment_time_minutes': 45,
            'effective_radius_km': 2.0,
            'cost_per_hour': 3000
        },
        'mobile_generator': {
            'capacity_kw': 100,
            'deployment_time_minutes': 60,
            'effective_radius_km': 0.5,
            'cost_per_hour': 4000
        },
        'traffic_control': {
            'capacity_intersections': 3,
            'deployment_time_minutes': 20,
            'effective_radius_km': 1.5,
            'cost_per_hour': 1500
        }
    }
    
    # Priority thresholds
    CRITICAL_USPS_THRESHOLD = 0.80
    CRITICAL_HRVC_THRESHOLD = 0.75
    CRITICAL_DRAINAGE_THRESHOLD = 0.85
    
    def __init__(self):
        self.deployment_history = []
    
    def generate_deployment_plan(
        self,
        usps_data: List[Dict],
        hrvc_data: List[Dict],
        drainage_data: Optional[List[Dict]] = None,
        available_resources: Optional[Dict] = None
    ) -> Dict:
        """
        Generate comprehensive deployment plan based on all risk indicators
        
        Args:
            usps_data: USPS saturation data per cell
            hrvc_data: HRVC risk scores per cell
            drainage_data: Drainage stress data per cell (optional)
            available_resources: Current resource inventory
            
        Returns:
            Deployment plan with prioritized actions
        """
        # Merge all risk indicators
        integrated_risk = self._integrate_risk_data(usps_data, hrvc_data, drainage_data)
        
        # Identify critical zones
        critical_zones = self._identify_critical_zones(integrated_risk)
        
        # Calculate resource requirements
        resource_needs = self._calculate_resource_needs(critical_zones)
        
        # Generate deployment recommendations
        deployments = self._optimize_deployments(
            critical_zones,
            resource_needs,
            available_resources or self._get_default_resources()
        )
        
        # Generate alerts
        alerts = self._generate_alerts(critical_zones, deployments)
        
        # Calculate impact metrics
        impact = self._calculate_impact_metrics(deployments, critical_zones)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'critical_zones': critical_zones,
            'deployments': deployments,
            'alerts': alerts,
            'impact_metrics': impact,
            'resource_utilization': self._calculate_resource_utilization(deployments, available_resources)
        }
    
    def _integrate_risk_data(
        self,
        usps_data: List[Dict],
        hrvc_data: List[Dict],
        drainage_data: Optional[List[Dict]]
    ) -> List[Dict]:
        """Integrate multiple risk indicators into unified risk score"""
        integrated = []
        
        # Create lookup dictionaries
        usps_lookup = {d['cell_id']: d for d in usps_data}
        hrvc_lookup = {d['cell_id']: d for d in hrvc_data}
        drainage_lookup = {d['cell_id']: d for d in drainage_data} if drainage_data else {}
        
        # Get all unique cell IDs
        all_cells = set(usps_lookup.keys()) | set(hrvc_lookup.keys())
        
        for cell_id in all_cells:
            usps = usps_lookup.get(cell_id, {})
            hrvc = hrvc_lookup.get(cell_id, {})
            drainage = drainage_lookup.get(cell_id, {})
            
            # Calculate composite risk score (weighted average)
            usps_score = usps.get('overall_saturation', 0) * 0.35
            hrvc_score = hrvc.get('risk_score', 0) * 0.40
            drainage_score = drainage.get('stress_ratio', 0) * 0.25
            
            composite_risk = usps_score + hrvc_score + drainage_score
            
            # Determine risk level
            if composite_risk >= 0.80:
                risk_level = 'CRITICAL'
                priority = 1
            elif composite_risk >= 0.65:
                risk_level = 'HIGH'
                priority = 2
            elif composite_risk >= 0.50:
                risk_level = 'MODERATE'
                priority = 3
            else:
                risk_level = 'LOW'
                priority = 4
            
            integrated.append({
                'cell_id': cell_id,
                'latitude': usps.get('latitude') or hrvc.get('latitude'),
                'longitude': usps.get('longitude') or hrvc.get('longitude'),
                'ward_name': usps.get('ward_name') or hrvc.get('ward_name', 'Unknown'),
                'composite_risk': round(composite_risk, 3),
                'risk_level': risk_level,
                'priority': priority,
                'usps_saturation': usps.get('overall_saturation', 0),
                'hrvc_risk': hrvc.get('risk_score', 0),
                'drainage_stress': drainage.get('stress_ratio', 0),
                'population': hrvc.get('exposure', 1000),
                'vulnerability': hrvc.get('vulnerability', 0.5),
                'subsystem_status': usps.get('subsystems', {}),
                'flood_depth': drainage.get('flood_depth_cm', 0)
            })
        
        # Sort by composite risk (highest first)
        integrated.sort(key=lambda x: x['composite_risk'], reverse=True)
        
        return integrated
    
    def _identify_critical_zones(self, integrated_risk: List[Dict]) -> List[Dict]:
        """Identify zones requiring immediate intervention"""
        critical = []
        
        for zone in integrated_risk:
            if zone['risk_level'] in ['CRITICAL', 'HIGH']:
                # Determine specific threats
                threats = []
                if zone['usps_saturation'] >= self.CRITICAL_USPS_THRESHOLD:
                    threats.append('SYSTEM_SATURATION')
                if zone['hrvc_risk'] >= self.CRITICAL_HRVC_THRESHOLD:
                    threats.append('HIGH_VULNERABILITY')
                if zone['drainage_stress'] >= self.CRITICAL_DRAINAGE_THRESHOLD:
                    threats.append('DRAINAGE_OVERFLOW')
                
                # Calculate estimated impact
                estimated_affected = int(zone['population'] * zone['vulnerability'])
                
                critical.append({
                    **zone,
                    'threats': threats,
                    'estimated_affected_population': estimated_affected,
                    'requires_immediate_action': zone['composite_risk'] >= 0.80
                })
        
        return critical
    
    def _calculate_resource_needs(self, critical_zones: List[Dict]) -> Dict:
        """Calculate required resources for each critical zone"""
        needs = []
        
        for zone in critical_zones:
            zone_needs = {
                'cell_id': zone['cell_id'],
                'ward_name': zone['ward_name'],
                'latitude': zone['latitude'],
                'longitude': zone['longitude'],
                'resources': []
            }
            
            # Pumps for drainage issues
            if zone['drainage_stress'] >= 0.85:
                num_pumps = math.ceil(zone['drainage_stress'] * 2)
                zone_needs['resources'].append({
                    'type': 'pump',
                    'quantity': num_pumps,
                    'reason': f"Drainage stress at {zone['drainage_stress']:.0%}"
                })
            
            # Ambulances for vulnerable populations
            if zone['hrvc_risk'] >= 0.70 and zone['estimated_affected_population'] > 500:
                num_ambulances = math.ceil(zone['estimated_affected_population'] / 1000)
                zone_needs['resources'].append({
                    'type': 'ambulance',
                    'quantity': num_ambulances,
                    'reason': f"{zone['estimated_affected_population']} vulnerable people"
                })
            
            # Rescue boats for severe flooding
            if zone['flood_depth'] > 30:  # > 30cm
                num_boats = math.ceil(zone['estimated_affected_population'] / 500)
                zone_needs['resources'].append({
                    'type': 'rescue_boat',
                    'quantity': num_boats,
                    'reason': f"Flood depth {zone['flood_depth']:.0f}cm"
                })
            
            # Generators for power stress
            subsystems = zone.get('subsystem_status', {})
            if subsystems.get('power_stress', 0) >= 0.80:
                zone_needs['resources'].append({
                    'type': 'mobile_generator',
                    'quantity': 1,
                    'reason': f"Power stress at {subsystems.get('power_stress', 0):.0%}"
                })
            
            # Traffic control for congestion
            if subsystems.get('road_congestion', 0) >= 0.75:
                zone_needs['resources'].append({
                    'type': 'traffic_control',
                    'quantity': 1,
                    'reason': f"Road congestion at {subsystems.get('road_congestion', 0):.0%}"
                })
            
            if zone_needs['resources']:
                needs.append(zone_needs)
        
        return {'zones': needs}
    
    def _optimize_deployments(
        self,
        critical_zones: List[Dict],
        resource_needs: Dict,
        available_resources: Dict
    ) -> List[Dict]:
        """Optimize resource deployment based on priority and availability"""
        deployments = []
        resource_inventory = available_resources.copy()
        
        # Sort zones by priority and risk
        sorted_zones = sorted(
            resource_needs['zones'],
            key=lambda z: next(
                (cz['composite_risk'] for cz in critical_zones if cz['cell_id'] == z['cell_id']),
                0
            ),
            reverse=True
        )
        
        for zone in sorted_zones:
            zone_deployments = []
            
            for resource_req in zone['resources']:
                resource_type = resource_req['type']
                needed = resource_req['quantity']
                available = resource_inventory.get(resource_type, 0)
                
                # Deploy what's available (up to what's needed)
                to_deploy = min(needed, available)
                
                if to_deploy > 0:
                    resource_info = self.RESOURCE_TYPES[resource_type]
                    eta = datetime.now() + timedelta(minutes=resource_info['deployment_time_minutes'])
                    
                    zone_deployments.append({
                        'resource_type': resource_type,
                        'quantity': to_deploy,
                        'reason': resource_req['reason'],
                        'eta': eta.isoformat(),
                        'deployment_time_minutes': resource_info['deployment_time_minutes'],
                        'status': 'RECOMMENDED'
                    })
                    
                    # Update inventory
                    resource_inventory[resource_type] -= to_deploy
            
            if zone_deployments:
                deployments.append({
                    'cell_id': zone['cell_id'],
                    'ward_name': zone['ward_name'],
                    'latitude': zone['latitude'],
                    'longitude': zone['longitude'],
                    'priority': next(
                        (cz['priority'] for cz in critical_zones if cz['cell_id'] == zone['cell_id']),
                        3
                    ),
                    'resources': zone_deployments
                })
        
        return deployments
    
    def _generate_alerts(self, critical_zones: List[Dict], deployments: List[Dict]) -> List[Dict]:
        """Generate public alerts and notifications"""
        alerts = []
        
        for zone in critical_zones:
            if zone['requires_immediate_action']:
                # Find deployment for this zone
                deployment = next(
                    (d for d in deployments if d['cell_id'] == zone['cell_id']),
                    None
                )
                
                alert = {
                    'alert_id': f"ALERT-{zone['cell_id']}-{datetime.now().strftime('%Y%m%d%H%M')}",
                    'severity': 'CRITICAL' if zone['composite_risk'] >= 0.85 else 'HIGH',
                    'ward_name': zone['ward_name'],
                    'latitude': zone['latitude'],
                    'longitude': zone['longitude'],
                    'threats': zone['threats'],
                    'estimated_affected': zone['estimated_affected_population'],
                    'message': self._generate_alert_message(zone),
                    'actions_taken': [r['resource_type'] for r in deployment['resources']] if deployment else [],
                    'timestamp': datetime.now().isoformat()
                }
                
                alerts.append(alert)
        
        return alerts
    
    def _generate_alert_message(self, zone: Dict) -> str:
        """Generate human-readable alert message"""
        threats_text = []
        
        if 'DRAINAGE_OVERFLOW' in zone['threats']:
            threats_text.append(f"drainage overflow ({zone['drainage_stress']:.0%})")
        if 'SYSTEM_SATURATION' in zone['threats']:
            threats_text.append(f"system saturation ({zone['usps_saturation']:.0%})")
        if 'HIGH_VULNERABILITY' in zone['threats']:
            threats_text.append(f"high vulnerability (risk {zone['hrvc_risk']:.2f})")
        
        threats_str = ", ".join(threats_text)
        
        return (
            f"ALERT: {zone['ward_name']} - Critical conditions detected: {threats_str}. "
            f"Approximately {zone['estimated_affected_population']} people may be affected. "
            f"Emergency resources are being deployed."
        )
    
    def _calculate_impact_metrics(self, deployments: List[Dict], critical_zones: List[Dict]) -> Dict:
        """Calculate expected impact of deployments"""
        total_resources = sum(
            sum(r['quantity'] for r in d['resources'])
            for d in deployments
        )
        
        total_affected = sum(z['estimated_affected_population'] for z in critical_zones)
        
        zones_covered = len(deployments)
        zones_critical = len([z for z in critical_zones if z['requires_immediate_action']])
        
        coverage_rate = (zones_covered / zones_critical * 100) if zones_critical > 0 else 100
        
        return {
            'total_resources_deployed': total_resources,
            'total_population_protected': total_affected,
            'zones_covered': zones_covered,
            'zones_requiring_action': zones_critical,
            'coverage_rate_percent': round(coverage_rate, 1),
            'estimated_response_time_minutes': self._calculate_avg_response_time(deployments)
        }
    
    def _calculate_avg_response_time(self, deployments: List[Dict]) -> float:
        """Calculate average response time across all deployments"""
        if not deployments:
            return 0
        
        total_time = 0
        count = 0
        
        for deployment in deployments:
            for resource in deployment['resources']:
                total_time += resource['deployment_time_minutes']
                count += 1
        
        return round(total_time / count, 1) if count > 0 else 0
    
    def _calculate_resource_utilization(
        self,
        deployments: List[Dict],
        available_resources: Optional[Dict]
    ) -> Dict:
        """Calculate resource utilization rates"""
        if not available_resources:
            return {}
        
        deployed = {}
        for deployment in deployments:
            for resource in deployment['resources']:
                r_type = resource['resource_type']
                deployed[r_type] = deployed.get(r_type, 0) + resource['quantity']
        
        utilization = {}
        for r_type, available in available_resources.items():
            used = deployed.get(r_type, 0)
            utilization[r_type] = {
                'available': available,
                'deployed': used,
                'remaining': available - used,
                'utilization_percent': round((used / available * 100) if available > 0 else 0, 1)
            }
        
        return utilization
    
    def _get_default_resources(self) -> Dict:
        """Get default resource inventory"""
        return {
            'pump': 20,
            'ambulance': 15,
            'rescue_boat': 10,
            'mobile_generator': 8,
            'traffic_control': 12
        }
