"""
Test script for Urban System Pressure Score (USPS) Engine
"""
from app.services.usps_engine import USPSEngine
from app.services.usps_data_generator import USPSDataGenerator

def test_usps_calculation():
    """Test USPS calculation with sample scenarios"""
    print("=" * 80)
    print("TESTING URBAN SYSTEM PRESSURE SCORE (USPS) ENGINE")
    print("=" * 80)
    
    engine = USPSEngine()
    
    # Test case 1: Normal conditions
    print("\n1. NORMAL CONDITIONS (Low Pressure)")
    normal_cell = {
        'rain_accumulation_pct': 30,
        'drain_capacity_load_pct': 35,
        'road_congestion_pct': 40,
        'hospital_occupancy_pct': 50,
        'power_stress_pct': 25
    }
    
    result = engine.calculate_usps(normal_cell)
    print(f"USPS Score: {result['usps_score']}")
    print(f"Pressure Level: {result['pressure_level']}")
    print(f"Cascade Level: {result['cascade_analysis']['cascade_level']}")
    print(f"Systems at Risk: {result['cascade_analysis']['systems_at_risk']}")
    
    # Test case 2: High pressure - single system
    print("\n2. HIGH PRESSURE - SINGLE SYSTEM")
    single_stress_cell = {
        'rain_accumulation_pct': 85,  # Critical
        'drain_capacity_load_pct': 40,
        'road_congestion_pct': 35,
        'hospital_occupancy_pct': 45,
        'power_stress_pct': 30
    }
    
    result = engine.calculate_usps(single_stress_cell)
    print(f"USPS Score: {result['usps_score']}")
    print(f"Pressure Level: {result['pressure_level']}")
    print(f"Cascade Level: {result['cascade_analysis']['cascade_level']}")
    print(f"Recommendations: {len(result['recommendations'])} actions")
    
    # Test case 3: CASCADING FAILURE SCENARIO
    print("\n3. CASCADING FAILURE SCENARIO (Multiple Systems Critical)")
    cascade_cell = {
        'rain_accumulation_pct': 88,   # Critical
        'drain_capacity_load_pct': 92, # Critical
        'road_congestion_pct': 78,     # High
        'hospital_occupancy_pct': 91,  # Critical
        'power_stress_pct': 85         # Critical
    }
    
    result = engine.calculate_usps(cascade_cell)
    print(f"USPS Score: {result['usps_score']}")
    print(f"Pressure Level: {result['pressure_level']}")
    print(f"Cascade Level: {result['cascade_analysis']['cascade_level']}")
    print(f"Cascade Risk: {result['cascade_analysis']['cascade_risk']}")
    print(f"Systems at Risk: {result['cascade_analysis']['systems_at_risk']}")
    print(f"Critical Systems: {result['cascade_analysis']['critical_systems']}")
    print(f"\nRecommendations:")
    for i, rec in enumerate(result['recommendations'][:5], 1):
        print(f"  {i}. {rec}")
    
    # Test case 4: Generate synthetic grid
    print("\n4. SYNTHETIC GRID GENERATION")
    generator = USPSDataGenerator()
    grid_cells = generator.generate_grid_with_usps_data(18.45, 18.55, 73.80, 73.90, 1.0)
    print(f"Generated {len(grid_cells)} grid cells")
    
    # Calculate USPS for all cells
    grid_with_usps = engine.calculate_grid_usps(grid_cells)
    
    # Get cascade warnings
    cascade_warnings = engine.get_cascade_warnings(grid_with_usps)
    critical_cells = engine.get_critical_cells(grid_with_usps, threshold=70)
    
    print(f"\n5. GRID ANALYSIS")
    usps_scores = [cell['usps_score'] for cell in grid_with_usps]
    print(f"  Total Cells: {len(grid_with_usps)}")
    print(f"  Average USPS: {sum(usps_scores) / len(usps_scores):.2f}")
    print(f"  Max USPS: {max(usps_scores):.2f}")
    print(f"  Critical Cells (≥70): {len(critical_cells)}")
    print(f"  Cascade Warnings: {len(cascade_warnings)}")
    
    # Cascade breakdown
    emergency = sum(1 for c in cascade_warnings if c['cascade_analysis']['cascade_level'] == 'EMERGENCY')
    critical = sum(1 for c in cascade_warnings if c['cascade_analysis']['cascade_level'] == 'CRITICAL')
    warning = sum(1 for c in cascade_warnings if c['cascade_analysis']['cascade_level'] == 'WARNING')
    
    print(f"\n6. CASCADE WARNING BREAKDOWN")
    print(f"  Emergency: {emergency} cells")
    print(f"  Critical: {critical} cells")
    print(f"  Warning: {warning} cells")
    
    # Subsystem analysis
    print(f"\n7. SUBSYSTEM PRESSURE ANALYSIS")
    subsystems = ['rain_accumulation', 'drain_capacity_load', 'road_congestion', 
                 'hospital_occupancy', 'power_stress']
    
    for subsystem in subsystems:
        pressures = [c['subsystem_pressures'][subsystem] for c in grid_with_usps]
        avg_pressure = sum(pressures) / len(pressures)
        max_pressure = max(pressures)
        critical_count = sum(1 for p in pressures if p >= 80)
        print(f"  {subsystem}: Avg={avg_pressure:.1f}%, Max={max_pressure:.1f}%, Critical={critical_count}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE ✓")
    print("=" * 80)
    print("\nKEY INNOVATION: USPS detects system saturation BEFORE failure")
    print("Cascading risk analysis identifies when multiple systems approach threshold")
    print("=" * 80)

if __name__ == "__main__":
    test_usps_calculation()
