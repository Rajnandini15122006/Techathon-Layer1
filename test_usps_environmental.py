"""
Test USPS with Environmental Engine Integration
"""

from app.services.environmental_engine import get_environmental_engine
from app.services.usps_data_generator import USPSDataGenerator

print("="*70)
print("TESTING USPS + ENVIRONMENTAL ENGINE INTEGRATION")
print("="*70)

# Get engine
env_engine = get_environmental_engine()

# Generate sample grid
generator = USPSDataGenerator()
grid_cells = generator.generate_grid_with_usps_data(
    lat_min=18.50,
    lat_max=18.52,
    lon_min=73.85,
    lon_max=73.87,
    grid_size_km=1.0
)

print(f"\n✓ Generated {len(grid_cells)} grid cells")

# Test environmental calculation on first cell
cell = grid_cells[0]
print(f"\n📍 Testing Cell: {cell['cell_id']}")
print(f"   Location: ({cell['latitude']:.4f}, {cell['longitude']:.4f})")
print(f"   Land Use: {cell.get('land_use', 'Mixed')}")

# Simulate environmental conditions
rainfall_mm = 45.0
accumulated_1hr = 50.0
traffic_level = 0.6

print(f"\n🌧️ Environmental Conditions:")
print(f"   Rainfall: {rainfall_mm} mm/hr")
print(f"   Accumulated (1hr): {accumulated_1hr} mm")
print(f"   Traffic Level: {traffic_level}")

# Calculate environmental state
env_state = env_engine.compute_environmental_state(
    rainfall_mm=rainfall_mm,
    accumulated_1hr=accumulated_1hr,
    land_use=cell.get('land_use', 'Mixed'),
    grid_area_m2=62500.0,
    drain_capacity_m3=cell.get('drain_capacity', 1000.0),
    traffic_congestion=traffic_level
)

print(f"\n📊 Environmental Analysis:")
print(f"   Rain Index: {env_state['rain']['rain_index']:.3f}")
print(f"   Runoff (SCS-CN): {env_state['drain']['runoff_mm']:.2f} mm")
print(f"   Curve Number: {env_state['drain']['curve_number']}")
print(f"   Drain Stress: {env_state['drain']['drain_stress']:.3f}")
print(f"   Traffic Index: {env_state['traffic']['traffic_index']:.3f}")

print(f"\n🎯 USPS Assessment:")
print(f"   USPS Score: {env_state['usps']['usps_score']:.3f} ({env_state['usps']['usps_score']*100:.1f}%)")
print(f"   Severity: {env_state['usps']['severity_level']}")
print(f"   Weights: Rain={env_state['usps']['weights']['rain']:.1f}, "
      f"Drain={env_state['usps']['weights']['drain']:.1f}, "
      f"Traffic={env_state['usps']['weights']['traffic']:.1f}")

print(f"\n✅ Integration Test Complete!")
print(f"\nThe Environmental Engine is working and integrated with USPS!")
print(f"\nYou can now:")
print(f"  1. Start server: python start_server.py")
print(f"  2. Test endpoint: GET /api/usps/environmental-usps")
print(f"  3. View in dashboard: http://localhost:8000/static/usps_dashboard.html")
