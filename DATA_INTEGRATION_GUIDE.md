# 📊 Real Data Integration Guide for PuneRakshak

This guide walks you through obtaining and integrating real Pune data into your disaster risk assessment platform.

## 🎯 Overview

The platform supports two modes:
1. **Synthetic Data** - Realistic test data with spatial patterns (already working)
2. **Real Data** - Actual Pune spatial data from OpenStreetMap, government sources, and APIs

## 🚀 Quick Start (15 Minutes)

### Prerequisites
- Internet connection
- Web browser
- Your server running (`python run_local.py`)

### Step-by-Step Process

#### 1️⃣ Download Pune Boundary (5 min) - REQUIRED

**Option A: Overpass Turbo (Easiest)**
1. Open https://overpass-turbo.eu/
2. Paste this query in the left panel:
```
[out:json];
area["name"="Pune"]["admin_level"="8"]->.a;
(relation(area.a)["boundary"="administrative"];);
out geom;
```
3. Click the "Run" button (top left)
4. Wait for the map to show Pune boundary
5. Click "Export" → "GeoJSON"
6. Save as `data/pune_boundary.geojson` in your project folder

**Option B: Geofabrik (Alternative)**
1. Go to https://download.geofabrik.de/asia/india.html
2. Download "Maharashtra" OSM data
3. Use QGIS to extract Pune boundary

#### 2️⃣ Download Elevation Data (5 min) - RECOMMENDED

**SRTM 30m Resolution:**
1. Open https://dwtkns.com/srtm30m/
2. Click on the map around Pune (coordinates: 18.5°N, 73.8°E)
3. Download the tile (it will be named like `N18E073.hgt.zip`)
4. Extract the `.hgt` file
5. Save as `data/pune_dem.tif` (or keep as `.hgt`)

**Alternative: USGS Earth Explorer**
1. Go to https://earthexplorer.usgs.gov/
2. Create free account
3. Search coordinates: `18.5204, 73.8567`
4. Select "Digital Elevation" → "SRTM 1 Arc-Second Global"
5. Download and save as `data/pune_dem.tif`

#### 3️⃣ Download Waterways (5 min) - RECOMMENDED

1. Go back to https://overpass-turbo.eu/
2. Paste this query:
```
[out:json];
area["name"="Pune"]->.a;
(way(area.a)["waterway"];);
out geom;
```
3. Click "Run" → "Export" → "GeoJSON"
4. Save as `data/drains.geojson`

#### 4️⃣ Generate Your Production Grid!

**Using the API:**
```bash
curl -X POST "http://localhost:8000/production/generate-grid" \
  -H "Content-Type: application/json" \
  -d '{
    "boundary_path": "data/pune_boundary.geojson",
    "dem_path": "data/pune_dem.tif",
    "drain_path": "data/drains.geojson"
  }'
```

**Using Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/production/generate-grid",
    json={
        "boundary_path": "data/pune_boundary.geojson",
        "dem_path": "data/pune_dem.tif",
        "drain_path": "data/drains.geojson"
    }
)

print(response.json())
```

**Expected Output:**
```json
{
  "status": "success",
  "total_cells": 11377,
  "cell_size_m": 250,
  "attributes_computed": {
    "elevation": 11377,
    "drain_distance": 11377,
    "land_use": 0,
    "population": 0,
    ...
  }
}
```

## 📦 Optional Data Sources

### 4️⃣ Hospitals & Infrastructure

**Overpass Turbo Query:**
```
[out:json];
area["name"="Pune"]->.a;
(
  node(area.a)["amenity"="hospital"];
  way(area.a)["amenity"="hospital"];
  node(area.a)["amenity"="clinic"];
);
out center;
```
Save as: `data/hospitals.geojson`

### 5️⃣ Land Use

**Overpass Turbo Query:**
```
[out:json];
area["name"="Pune"]->.a;
(
  way(area.a)["landuse"];
  relation(area.a)["landuse"];
);
out geom;
```
Save as: `data/land_use.geojson`

### 6️⃣ Census Data

**Sources:**
- **Official:** https://censusindia.gov.in/ → District Census Handbook → Maharashtra → Pune
- **DataMeet:** https://github.com/datameet/maps (easier format)
- **Kaggle:** Search "India census 2011"

Save as: `data/census.geojson` or `data/census.csv`

### 7️⃣ Flood History

**Sources:**
- **Humanitarian Data Exchange:** https://data.humdata.org/ (search "Maharashtra floods")
- **Bhuvan (ISRO):** https://bhuvan.nrsc.gov.in/ → Disaster data
- **Kaggle:** Search "India floods" or "Maharashtra floods"

Save as: `data/floods.geojson` or `data/floods.tif`

### 8️⃣ Slum Locations

**Sources:**
- **Pune Municipal Corporation:** https://www.pmc.gov.in/ (may require RTI request)
- **OpenStreetMap:** Query for `place=slum` or `residential=slum`
- **Research datasets:** Search academic papers on Pune urban planning

Save as: `data/slums.geojson`

## 🔧 Using the Helper Script

We've included a helper script to check your data:

```bash
python scripts/download_pune_data.py
```

This will:
- Check which data files you already have
- Show download instructions
- Optionally open Overpass Turbo in your browser

## 📊 Kaggle Datasets

### Recommended Searches:
1. **"India census 2011"** - Population data by district/ward
2. **"Pune"** - City-specific datasets
3. **"Maharashtra floods"** - Historical flood data
4. **"India urban"** - Urban infrastructure data
5. **"OpenStreetMap India"** - Pre-processed OSM data

### How to Use Kaggle Data:
1. Create free account at https://www.kaggle.com/
2. Search for datasets
3. Download as CSV/JSON/Shapefile
4. Convert to GeoJSON if needed (see below)

## 🛠️ Data Preparation

### Converting Formats

**CSV to GeoJSON (with coordinates):**
```python
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Read CSV
df = pd.read_csv('data.csv')

# Create geometry (assuming 'lat' and 'lon' columns)
geometry = [Point(xy) for xy in zip(df['lon'], df['lat'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')

# Save as GeoJSON
gdf.to_file('output.geojson', driver='GeoJSON')
```

**Shapefile to GeoJSON:**
```python
import geopandas as gpd

gdf = gpd.read_file('input.shp')
gdf.to_file('output.geojson', driver='GeoJSON')
```

**Checking CRS:**
```python
import geopandas as gpd

gdf = gpd.read_file('data.geojson')
print(f"Current CRS: {gdf.crs}")

# Reproject to EPSG:4326 if needed
if gdf.crs != 'EPSG:4326':
    gdf = gdf.to_crs('EPSG:4326')
    gdf.to_file('data_reprojected.geojson', driver='GeoJSON')
```

## 🎯 Complete API Example

Once you have all data files:

```bash
curl -X POST "http://localhost:8000/production/generate-grid" \
  -H "Content-Type: application/json" \
  -d '{
    "boundary_path": "data/pune_boundary.geojson",
    "dem_path": "data/pune_dem.tif",
    "drain_path": "data/drains.geojson",
    "land_use_path": "data/land_use.geojson",
    "census_path": "data/census.geojson",
    "slum_path": "data/slums.geojson",
    "flood_path": "data/floods.geojson",
    "infra_path": "data/hospitals.geojson",
    "complaint_path": "data/complaints.geojson",
    "cell_size": 250
  }'
```

## ✅ Data Quality Checklist

Before using data, verify:
- [ ] CRS is EPSG:4326 (or can be reprojected)
- [ ] Data covers Pune area (18.41°N to 18.64°N, 73.73°E to 73.99°E)
- [ ] No missing/corrupt geometries
- [ ] Attributes are properly named
- [ ] File size is reasonable (<100MB for testing)

## 🐛 Troubleshooting

### "Boundary file not found"
- Check file path is relative to project root
- Ensure file is in `data/` folder
- Verify filename matches exactly (case-sensitive)

### "No elevation data computed"
- Check DEM file format (.tif or .hgt)
- Verify DEM covers Pune area
- Try using absolute path

### "CRS mismatch error"
- All vector data should be EPSG:4326
- Use QGIS or Python to reproject

### "Empty grid generated"
- Check boundary polygon is valid
- Verify boundary is not too small
- Ensure boundary coordinates are in correct order

## 📚 Additional Resources

- **OpenStreetMap Wiki:** https://wiki.openstreetmap.org/
- **QGIS Tutorials:** https://www.qgistutorials.com/
- **GeoPandas Docs:** https://geopandas.org/
- **Overpass API Guide:** https://wiki.openstreetmap.org/wiki/Overpass_API
- **DataMeet Community:** https://datameet.org/

## 🤝 Need Help?

1. Check `REAL_DATA_SOURCES.md` for detailed source information
2. Run `python scripts/download_pune_data.py` for guided instructions
3. Visit API docs at http://localhost:8000/docs
4. Check server logs for detailed error messages

## 📝 Next Steps

After generating your grid with real data:
1. View it in the web UI at http://localhost:8000
2. Click "Load Grid Cells" to visualize
3. Hover over cells to see computed attributes
4. Use the data for disaster risk analysis

---

**Happy mapping! 🗺️**
