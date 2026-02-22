"""
Populate Environmental Data

Generates realistic environmental data for testing the USPS dashboard.
"""

import requests
import random
from datetime import datetime

BASE_URL = "http://localhost:8000"

def populate_data():
    """Populate environmental data for grid cells"""
    
    print("="*70)
    print("POPULATING ENVIRONMENTAL DATA")
    print("="*70)
    
    # Simulate different weather scenarios across Pune
    scenarios = [
        # (rainfall_mm, accumulated_1hr, traffic_congestion, description)
        (0, 0, 0.1, "Clear weather, low traffic"),
        (15, 18, 0.3, "Light rain, moderate traffic"),
        (35, 40, 0.5, "Moderate rain, heavy traffic"),
        (60, 70, 0.7, "Heavy rain, severe traffic"),
        (85, 95, 0.8, "Very heavy rain, critical traffic"),
    ]
    
    # Get grid cells first
    try:
        response = requests.get(f"{BASE_URL}/demo/grid-geojson")
        if response.status_code == 200:
            grid_data = response.json()
            grid_cells = grid_data.get('features', [])
            print(f"\n✓ Found {len(grid_cells)} grid cells")
        else:
            print(f"\n✗ Error fetching grid cells: {response.status_code}")
            return
    except Exception as e:
        print(f"\n✗ Error connecting to server: {e}")
        print("\nMake sure the server is running:")
        print("  python run_local.py")
        return
    
    # Prepare bulk update
    updates = []
    
    for i, feature in enumerate(grid_cells[:50]):  # Update first 50 cells
        grid_id = feature['properties']['id']
        
        # Assign scenario based on grid location (simulate spatial variation)
        scenario_idx = i % len(scenarios)
        rainfall, accumulated, traffic, description = scenarios[scenario_idx]
        
        # Add some randomness
        rainfall += random.uniform(-5, 5)
        accumulated += random.uniform(-5, 5)
        traffic += random.uniform(-0.1, 0.1)
        
        # Ensure bounds
        rainfall = max(0, rainfall)
        accumulated = max(0, accumulated)
        traffic = max(0, min(1.0, traffic))
        
        updates.append({
            "grid_id": grid_id,
            "rainfall_mm": round(rainfall, 2),
            "accumulated_1hr": round(accumulated, 2),
            "traffic_congestion": round(traffic, 2)
        })
    
    # Send bulk update
    print(f"\n📤 Sending bulk update for {len(updates)} grid cells...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/environmental/bulk-update",
            json=updates
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ Bulk update successful!")
            print(f"  Success: {result['success_count']}")
            print(f"  Errors: {result['error_count']}")
            
            # Show sample results
            if result['results']:
                print(f"\n📊 Sample Results:")
                for r in result['results'][:5]:
                    print(f"  Grid {r['grid_id']}: USPS={r['usps_score']:.3f} ({r['severity']})")
        else:
            print(f"\n✗ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n✗ Error sending update: {e}")
        return
    
    # Get summary
    print(f"\n📈 Fetching system summary...")
    
    try:
        response = requests.get(f"{BASE_URL}/environmental/summary")
        if response.status_code == 200:
            summary = response.json()
            print(f"\n✓ System Summary:")
            print(f"  Total Grids: {summary['total_grids']}")
            print(f"  Average USPS: {summary['average_usps']:.3f}")
            print(f"  Max USPS: {summary['max_usps']:.3f}")
            print(f"\n  Severity Distribution:")
            for severity, count in summary['severity_distribution'].items():
                print(f"    {severity}: {count}")
        else:
            print(f"\n✗ Error fetching summary: {response.status_code}")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
    
    print("\n" + "="*70)
    print("✅ DATA POPULATION COMPLETE")
    print("="*70)
    print("\nYou can now:")
    print("  1. View USPS Dashboard: http://localhost:8000/static/usps_dashboard.html")
    print("  2. Check API docs: http://localhost:8000/docs")
    print("  3. Query environmental data:")
    print("     GET /environmental/latest")
    print("     GET /environmental/summary")
    print("     GET /environmental/usps/{grid_id}")


if __name__ == "__main__":
    populate_data()
