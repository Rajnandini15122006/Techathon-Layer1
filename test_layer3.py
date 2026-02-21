"""
Test script for Layer 3: HRVC Risk Engine
Run this after generating synthetic grid data
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_hrvc_risk():
    print("=" * 80)
    print("TESTING LAYER 3: HRVC RISK ENGINE")
    print("=" * 80)
    
    # Step 1: Compute HRVC risk scores
    print("\n1. Computing HRVC risk scores...")
    response = requests.post(f"{BASE_URL}/risk/compute-hrvc")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Risk computation successful!")
        print(f"\nTotal cells processed: {result['total_cells']}")
        print(f"\nRisk Statistics:")
        print(f"  Mean: {result['risk_statistics']['mean']:.2f}")
        print(f"  Median: {result['risk_statistics']['median']:.2f}")
        print(f"  Min: {result['risk_statistics']['min']:.2f}")
        print(f"  Max: {result['risk_statistics']['max']:.2f}")
        print(f"\nRisk Distribution:")
        for level, count in result['risk_distribution'].items():
            pct = (count / result['total_cells']) * 100
            print(f"  {level}: {count} cells ({pct:.1f}%)")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return
    
    # Step 2: Get high-risk cells
    print("\n2. Fetching high-risk cells (risk >= 50)...")
    response = requests.get(f"{BASE_URL}/risk/high-risk-cells?min_risk=50&limit=10")
    
    if response.status_code == 200:
        data = response.json()
        high_risk_count = len(data.get('features', []))
        print(f"✅ Found {high_risk_count} high-risk cells")
        
        if high_risk_count > 0:
            print("\nTop 3 highest risk cells:")
            for i, feature in enumerate(data['features'][:3]):
                props = feature['properties']
                print(f"\n  Cell {i+1}:")
                print(f"    Risk Score: {props['risk_score']:.2f} ({props['risk_level']})")
                print(f"    Hazard: {props['hazard_score']:.2f}")
                print(f"    Vulnerability: {props['vulnerability_score']:.2f}")
                print(f"    Capacity: {props['capacity_score']:.2f}")
    else:
        print(f"❌ Error: {response.status_code}")
    
    print("\n" + "=" * 80)
    print("LAYER 3 TEST COMPLETE")
    print("=" * 80)
    print("\n✅ Open http://localhost:8000 to see risk visualization on map")
    print("   - Cells are now color-coded by HRVC risk score")
    print("   - Click any cell to see detailed risk breakdown")

if __name__ == "__main__":
    test_hrvc_risk()
