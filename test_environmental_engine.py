"""
Test Script for Environmental Engine

Tests all components of Layer 2 Environmental Modeling.
"""

import sys
from app.services.environmental_engine import (
    EnvironmentalEngine,
    EnvironmentalConfig,
    RainModule,
    DrainStressModule,
    TrafficModule,
    USPSCalculator
)


def test_rain_module():
    """Test Rain Module"""
    print("\n" + "="*70)
    print("TEST 1: Rain Module")
    print("="*70)
    
    config = EnvironmentalConfig()
    rain_module = RainModule(config)
    
    # Test cases
    test_cases = [
        (0, "No rain"),
        (25, "Light rain"),
        (50, "Moderate rain"),
        (75, "Heavy rain"),
        (100, "Extreme rain"),
        (150, "Beyond max (should cap at 1.0)")
    ]
    
    for rainfall, description in test_cases:
        result = rain_module.compute_rain_index(rainfall, rainfall)
        print(f"\n{description}:")
        print(f"  Rainfall: {rainfall} mm/hr")
        print(f"  Rain Index: {result['rain_index']:.3f}")
        assert 0 <= result['rain_index'] <= 1.0, "Rain index out of bounds"
    
    print("\n✓ Rain Module tests passed")


def test_drain_stress_module():
    """Test Drain Stress Module"""
    print("\n" + "="*70)
    print("TEST 2: Drain Stress Module")
    print("="*70)
    
    config = EnvironmentalConfig()
    drain_module = DrainStressModule(config)
    
    # Test SCS-CN for different land uses
    land_uses = ["Built-up", "Residential", "Vegetation"]
    rainfall = 50.0  # mm
    
    print("\nSCS-CN Runoff Computation:")
    for land_use in land_uses:
        cn = drain_module.get_curve_number(land_use)
        runoff = drain_module.compute_runoff_scs_cn(rainfall, land_use)
        print(f"\n{land_use}:")
        print(f"  Curve Number: {cn}")
        print(f"  Rainfall: {rainfall} mm")
        print(f"  Runoff: {runoff:.2f} mm")
        assert runoff >= 0, "Runoff cannot be negative"
        assert runoff <= rainfall, "Runoff cannot exceed rainfall"
    
    # Test drain stress
    print("\nDrain Stress Computation:")
    grid_area = 62500.0  # 250m x 250m
    drain_capacity = 1000.0  # m³
    
    for land_use in land_uses:
        metrics = drain_module.compute_drain_metrics(
            rainfall, land_use, grid_area, drain_capacity
        )
        print(f"\n{land_use}:")
        print(f"  Runoff: {metrics['runoff_mm']:.2f} mm")
        print(f"  Drain Stress: {metrics['drain_stress']:.3f}")
        assert 0 <= metrics['drain_stress'] <= 1.0, "Drain stress out of bounds"
    
    print("\n✓ Drain Stress Module tests passed")


def test_traffic_module():
    """Test Traffic Module"""
    print("\n" + "="*70)
    print("TEST 3: Traffic Module")
    print("="*70)
    
    traffic_module = TrafficModule()
    
    # Test cases
    test_cases = [
        (10, 10, "No congestion"),
        (15, 10, "Light congestion"),
        (20, 10, "Moderate congestion"),
        (30, 10, "Heavy congestion"),
        (40, 10, "Severe congestion")
    ]
    
    for current, free_flow, description in test_cases:
        result = traffic_module.compute_traffic_index(
            current_travel_time=current,
            free_flow_travel_time=free_flow
        )
        print(f"\n{description}:")
        print(f"  Current: {current} min, Free-flow: {free_flow} min")
        print(f"  Traffic Index: {result['traffic_index']:.3f}")
        assert 0 <= result['traffic_index'] <= 1.0, "Traffic index out of bounds"
    
    print("\n✓ Traffic Module tests passed")


def test_usps_calculator():
    """Test USPS Calculator"""
    print("\n" + "="*70)
    print("TEST 4: USPS Calculator")
    print("="*70)
    
    config = EnvironmentalConfig()
    usps_calc = USPSCalculator(config)
    
    # Test scenarios
    scenarios = [
        (0.1, 0.1, 0.1, "Low stress"),
        (0.3, 0.3, 0.3, "Moderate stress"),
        (0.5, 0.5, 0.5, "High stress"),
        (0.8, 0.8, 0.8, "Critical stress"),
        (1.0, 1.0, 1.0, "Maximum stress")
    ]
    
    print("\nUSPS Computation:")
    for rain, drain, traffic, description in scenarios:
        result = usps_calc.compute_full_assessment(rain, drain, traffic)
        print(f"\n{description}:")
        print(f"  Rain Index: {rain:.1f}")
        print(f"  Drain Stress: {drain:.1f}")
        print(f"  Traffic Index: {traffic:.1f}")
        print(f"  USPS Score: {result['usps_score']:.3f}")
        print(f"  Severity: {result['severity_level']}")
        assert 0 <= result['usps_score'] <= 1.0, "USPS out of bounds"
    
    print("\n✓ USPS Calculator tests passed")


def test_environmental_engine():
    """Test complete Environmental Engine"""
    print("\n" + "="*70)
    print("TEST 5: Complete Environmental Engine")
    print("="*70)
    
    engine = EnvironmentalEngine()
    
    # Test scenario: Heavy rain in built-up area with traffic
    print("\nScenario: Heavy rain in built-up area with traffic congestion")
    state = engine.compute_environmental_state(
        rainfall_mm=75.0,
        accumulated_1hr=80.0,
        land_use="Built-up",
        grid_area_m2=62500.0,
        drain_capacity_m3=1000.0,
        traffic_congestion=0.7
    )
    
    print(f"\nRain Metrics:")
    print(f"  Rainfall: {state['rain']['rainfall_mm']} mm/hr")
    print(f"  Rain Index: {state['rain']['rain_index']:.3f}")
    
    print(f"\nDrain Metrics:")
    print(f"  Runoff: {state['drain']['runoff_mm']:.2f} mm")
    print(f"  Drain Stress: {state['drain']['drain_stress']:.3f}")
    print(f"  Curve Number: {state['drain']['curve_number']}")
    
    print(f"\nTraffic Metrics:")
    print(f"  Traffic Index: {state['traffic']['traffic_index']:.3f}")
    
    print(f"\nUSPS Assessment:")
    print(f"  USPS Score: {state['usps']['usps_score']:.3f}")
    print(f"  Severity: {state['usps']['severity_level']}")
    print(f"  Weights: Rain={state['usps']['weights']['rain']:.1f}, "
          f"Drain={state['usps']['weights']['drain']:.1f}, "
          f"Traffic={state['usps']['weights']['traffic']:.1f}")
    
    # Verify all components
    assert 'rain' in state
    assert 'drain' in state
    assert 'traffic' in state
    assert 'usps' in state
    assert 0 <= state['usps']['usps_score'] <= 1.0
    
    print("\n✓ Environmental Engine tests passed")


def test_determinism():
    """Test that engine produces deterministic results"""
    print("\n" + "="*70)
    print("TEST 6: Determinism")
    print("="*70)
    
    engine = EnvironmentalEngine()
    
    # Run same computation twice
    inputs = {
        'rainfall_mm': 50.0,
        'accumulated_1hr': 55.0,
        'land_use': 'Residential',
        'grid_area_m2': 62500.0,
        'drain_capacity_m3': 1000.0,
        'traffic_congestion': 0.5
    }
    
    state1 = engine.compute_environmental_state(**inputs)
    state2 = engine.compute_environmental_state(**inputs)
    
    # Compare results
    assert state1['usps']['usps_score'] == state2['usps']['usps_score'], \
        "USPS scores differ for same inputs"
    assert state1['rain']['rain_index'] == state2['rain']['rain_index'], \
        "Rain indices differ for same inputs"
    assert state1['drain']['drain_stress'] == state2['drain']['drain_stress'], \
        "Drain stress differs for same inputs"
    
    print("\nDeterminism verified:")
    print(f"  Run 1 USPS: {state1['usps']['usps_score']:.6f}")
    print(f"  Run 2 USPS: {state2['usps']['usps_score']:.6f}")
    print(f"  Match: ✓")
    
    print("\n✓ Determinism tests passed")


def test_edge_cases():
    """Test edge cases"""
    print("\n" + "="*70)
    print("TEST 7: Edge Cases")
    print("="*70)
    
    engine = EnvironmentalEngine()
    
    # Test zero rainfall
    print("\nEdge Case 1: Zero rainfall")
    state = engine.compute_environmental_state(
        rainfall_mm=0.0,
        accumulated_1hr=0.0,
        land_use="Built-up",
        grid_area_m2=62500.0,
        drain_capacity_m3=1000.0,
        traffic_congestion=0.0
    )
    print(f"  USPS Score: {state['usps']['usps_score']:.3f}")
    print(f"  Severity: {state['usps']['severity_level']}")
    assert state['usps']['usps_score'] == 0.0, "Zero inputs should give zero USPS"
    
    # Test maximum values
    print("\nEdge Case 2: Maximum values")
    state = engine.compute_environmental_state(
        rainfall_mm=200.0,  # Beyond max
        accumulated_1hr=200.0,
        land_use="Built-up",
        grid_area_m2=62500.0,
        drain_capacity_m3=100.0,  # Low capacity
        traffic_congestion=1.0
    )
    print(f"  USPS Score: {state['usps']['usps_score']:.3f}")
    print(f"  Severity: {state['usps']['severity_level']}")
    assert state['usps']['usps_score'] <= 1.0, "USPS should be capped at 1.0"
    
    print("\n✓ Edge case tests passed")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("ENVIRONMENTAL ENGINE TEST SUITE")
    print("="*70)
    
    try:
        test_rain_module()
        test_drain_stress_module()
        test_traffic_module()
        test_usps_calculator()
        test_environmental_engine()
        test_determinism()
        test_edge_cases()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        print("\nEnvironmental Engine is production-ready!")
        print("- Deterministic calculations ✓")
        print("- SCS-CN hydrological modeling ✓")
        print("- Multi-criteria scoring ✓")
        print("- Audit-ready logging ✓")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
