"""
Helper script to download Pune data from various sources
Run: python scripts/download_pune_data.py
"""
import os
import sys
import requests
from pathlib import Path

# Create data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def download_file(url, filename):
    """Download file from URL"""
    filepath = DATA_DIR / filename
    
    if filepath.exists():
        print(f"✓ {filename} already exists")
        return True
    
    print(f"Downloading {filename}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✓ Downloaded {filename}")
        return True
    except Exception as e:
        print(f"✗ Error downloading {filename}: {e}")
        return False

def print_instructions():
    """Print manual download instructions"""
    print("\n" + "="*80)
    print("PUNE DATA DOWNLOAD GUIDE")
    print("="*80)
    
    print("\n📍 STEP 1: Pune Boundary (Required)")
    print("-" * 80)
    print("1. Go to: https://overpass-turbo.eu/")
    print("2. Paste this query:")
    print("""
[out:json];
area["name"="Pune"]["admin_level"="8"]->.a;
(relation(area.a)["boundary"="administrative"];);
out geom;
""")
    print("3. Click 'Run' → 'Export' → 'GeoJSON'")
    print("4. Save as: data/pune_boundary.geojson")
    
    print("\n🏔️ STEP 2: Elevation Data (Recommended)")
    print("-" * 80)
    print("1. Go to: https://dwtkns.com/srtm30m/")
    print("2. Click on Pune area (18.5°N, 73.8°E)")
    print("3. Download the tile")
    print("4. Save as: data/pune_dem.tif")
    
    print("\n💧 STEP 3: Waterways (Recommended)")
    print("-" * 80)
    print("1. Go to: https://overpass-turbo.eu/")
    print("2. Paste this query:")
    print("""
[out:json];
area["name"="Pune"]->.a;
(way(area.a)["waterway"];);
out geom;
""")
    print("3. Click 'Run' → 'Export' → 'GeoJSON'")
    print("4. Save as: data/drains.geojson")
    
    print("\n🏥 STEP 4: Additional Data (Optional)")
    print("-" * 80)
    print("• Hospitals/Infrastructure:")
    print("  - Overpass query: node(area.a)[\"amenity\"=\"hospital\"]")
    print("  - Save as: data/hospitals.geojson")
    print()
    print("• Land Use:")
    print("  - Overpass query: way(area.a)[\"landuse\"]")
    print("  - Save as: data/land_use.geojson")
    print()
    print("• Census Data:")
    print("  - Visit: https://censusindia.gov.in/")
    print("  - Or search Kaggle: 'India census 2011'")
    
    print("\n📊 KAGGLE DATASETS")
    print("-" * 80)
    print("Search on https://www.kaggle.com/datasets for:")
    print("  • 'India census'")
    print("  • 'Pune'")
    print("  • 'Maharashtra floods'")
    print("  • 'India urban data'")
    
    print("\n🚀 AFTER DOWNLOADING")
    print("-" * 80)
    print("Generate your grid with:")
    print("""
curl -X POST "http://localhost:8000/production/generate-grid" \\
  -H "Content-Type: application/json" \\
  -d '{
    "boundary_path": "data/pune_boundary.geojson",
    "dem_path": "data/pune_dem.tif",
    "drain_path": "data/drains.geojson"
  }'
""")
    
    print("\n" + "="*80)
    print("For complete guide, see: REAL_DATA_SOURCES.md")
    print("="*80 + "\n")

def check_existing_files():
    """Check which files already exist"""
    print("\n📁 Checking existing data files...")
    print("-" * 80)
    
    required_files = {
        "pune_boundary.geojson": "Pune boundary (Required)",
        "pune_dem.tif": "Elevation data (Recommended)",
        "drains.geojson": "Waterways (Recommended)"
    }
    
    optional_files = {
        "hospitals.geojson": "Hospitals/Infrastructure",
        "land_use.geojson": "Land use data",
        "census.geojson": "Census data",
        "floods.geojson": "Flood history",
        "slums.geojson": "Slum locations"
    }
    
    found_count = 0
    
    print("\nRequired/Recommended:")
    for filename, description in required_files.items():
        filepath = DATA_DIR / filename
        if filepath.exists():
            size = filepath.stat().st_size / 1024  # KB
            print(f"  ✓ {filename} - {description} ({size:.1f} KB)")
            found_count += 1
        else:
            print(f"  ✗ {filename} - {description} (Missing)")
    
    print("\nOptional:")
    for filename, description in optional_files.items():
        filepath = DATA_DIR / filename
        if filepath.exists():
            size = filepath.stat().st_size / 1024  # KB
            print(f"  ✓ {filename} - {description} ({size:.1f} KB)")
            found_count += 1
        else:
            print(f"  ✗ {filename} - {description} (Not found)")
    
    print(f"\nTotal files found: {found_count}")
    print("-" * 80)
    
    return found_count

def main():
    print("\n🛡️ PuneRakshak - Data Download Helper")
    
    # Check existing files
    existing = check_existing_files()
    
    if existing >= 3:
        print("\n✓ You have enough data to generate a production grid!")
        print("  Run your server and use the production endpoint.")
    else:
        print("\n⚠️  You need to download more data files.")
    
    # Print instructions
    print_instructions()
    
    # Offer to open browser
    try:
        import webbrowser
        response = input("\nOpen Overpass Turbo in browser? (y/n): ")
        if response.lower() == 'y':
            webbrowser.open('https://overpass-turbo.eu/')
            print("✓ Opened browser")
    except:
        pass

if __name__ == "__main__":
    main()
