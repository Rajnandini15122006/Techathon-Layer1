"""
Quick test script for HRVC Risk Engine
"""
from app.services.risk_engine import RiskEngine
from app.services.synthetic_data_generator_simple import SyntheticDataGenerator

def test_risk_calculation():
    """Test risk calculation with sample data"""
    print("=" * 80)
    print("TESTING HRVC RISK ENGINE")
    print("=" * 80)
    
    engine = RiskEngine()
    
    # Test case 1: High risk scenario
    print("\n1. HIGH RISK SCENARIO (Urban flood-prone area)")
    high_risk_cell = {
        'rainfall_mm': 180,
        'river_level_m': 8.5,
        'soil_saturation_pct': 95,
        'population_density': 45000,
        'traffic_density': 900,
        'slum_percentage': 15,
        'elderly_percentage': 16,
        'low_elevation_percentage': 55,
        'shelter_count': 2,
        'hospital_beds': 80,
        'drain_strength': 35
    }
    
    result = engine.calculate_risk_score(high_risk_cell)
    print(f"Risk Score: {result['risk_score']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Components: {result['components']}")
    
    # Test case 2: Low risk scenario
    print("\n2. LOW RISK SCENARIO (Well-prepared suburban area)")
    low_risk_cell = {
        'rainfall_mm': 60,
        'river_level_m': 1.2,
        'soil_saturation_pct': 30,
        'population_density': 8000,
        'traffic_density': 150,
        'slum_percentage': 2,
        'elderly_percentage': 10,
        'low_elevation_percentage': 15,
        'shelter_count': 5,
        'hospital_beds': 300,
        'drain_strength': 85
    }
    
    result = engine.calculate_risk_score(low_risk_cell)
    print(f"Risk Score: {result['risk_score']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Components: {result['components']}")
    
    # Test case 3: Generate synthetic grid
    print("\n3. SYNTHETIC GRID GENERATION")
    generator = SyntheticDataGenerator()
    grid_cells = generator.generate_grid_with_data(18.45, 18.55, 73.80, 73.90, 1.0)
    print(f"Generated {len(grid_cells)} grid cells")
    
    # Calculate risks for all cells
    grid_with_risks = engine.calculate_grid_risks(grid_cells)
    
    # Get ward priorities
    ward_priorities = engine.get_ward_priorities(grid_with_risks)
    
    print(f"\n4. WARD PRIORITIES (Top 5)")
    for ward in ward_priorities[:5]:
        print(f"  {ward['priority_rank']}. {ward['ward_name']}: "
              f"Risk={ward['avg_risk']:.2f} ({ward['priority_level']}) - "
              f"{ward['high_risk_cells']} high-risk cells")
    
    # Statistics
    risk_scores = [cell['risk_score'] for cell in grid_with_risks]
    print(f"\n5. OVERALL STATISTICS")
    print(f"  Total Cells: {len(grid_with_risks)}")
    print(f"  Average Risk: {sum(risk_scores) / len(risk_scores):.2f}")
    print(f"  Max Risk: {max(risk_scores):.2f}")
    print(f"  Min Risk: {min(risk_scores):.2f}")
    print(f"  Critical Cells (≥80): {sum(1 for s in risk_scores if s >= 80)}")
    print(f"  High Risk Cells (60-79): {sum(1 for s in risk_scores if 60 <= s < 80)}")
    print(f"  Medium Risk Cells (40-59): {sum(1 for s in risk_scores if 40 <= s < 60)}")
    print(f"  Low Risk Cells (<40): {sum(1 for s in risk_scores if s < 40)}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE ✓")
    print("=" * 80)

if __name__ == "__main__":
    test_risk_calculation()
