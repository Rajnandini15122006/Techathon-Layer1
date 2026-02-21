# Real Data Sources for Pune - Complete Guide

## 🚀 QUICK START (15 Minutes to Real Data)

Follow these 3 steps to get started with real Pune data immediately:

### Step 1: Download Pune Boundary (5 min)
1. Go to https://overpass-turbo.eu/
2. Paste this query:
```
[out:json];
area["name"="Pune"]["admin_level"="8"]->.a;
(relation(area.a)["boundary"="administrative"];);
out geom;
```
3. Click "Run" → Wait for results
4. Click "Export" → "GeoJSON" → Save as `pune_boundary.geojson`
5. Move file to `data/pune_boundary.geojson`

### Step 2: Download Elevation Data (5 min)
1. Go to https://dwtkns.com/srtm30m/
2. Click on Pune area (around 18.5°N, 73.8°E)
3. Download the tile
4. Save as `data/pune_dem.tif`

### Step 3: Download Waterways (5 min)
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

### Step 4: Generate Your Grid!
```bash
# Start your server
python run_local.py

# In another terminal or use the UI
curl -X POST "http://localhost:8000/production/generate-grid" \
  -H "Content-Type: application/json" \
  -d '{
    "boundary_path": "data/pune_boundary.geojson",
    "dem_path": "data/pune_dem.tif",
    "drain_path": "data/drains.geojson"
  }'
```

Or use the web UI at http://localhost:8000 - I'll add a button for this!

---

## Free Data Sources (No API Key Required)

### 1. OpenStreetMap (OSM) - Best Free Source
**What you can get:** Boundaries, buildings, roads, waterways, land use, hospitals, schools

#### Method A: Overpass Turbo (Web Interface)
1. Go to https://overpass-turbo.eu/
2. Use these queries:

**Pune Boundary:**
```
[out:json];
area["name"="Pune"]["admin_level"="8"]->.a;
(
  relation(area.a)["boundary"="administrative"];
);
out geom;
```
Click "Export" → "GeoJSON" → Save as `pune_boundary.geojson`

**Waterways/Drains:**
```
[out:json];
area["name"="Pune"]->.a;
(
  way(area.a)["waterway"];
);
out geom;
```
Save as `drains.geojson`

**Hospitals:**
```
[out:json];
area["name"="Pune"]->.a;
(
  node(area.a)["amenity"="hospital"];
  way(area.a)["amenity"="hospital"];
);
out center;
```
Save as `hospitals.geojson`

**Land Use:**
```
[out:json];
area["name"="Pune"]->.a;
(
  way(area.a)["landuse"];
  relation(area.a)["landuse"];
);
out geom;
```
Save as `land_use.geojson`

#### Method B: Download from Geofabrik
1. Go to https://download.geofabrik.de/asia/india.html
2. Download "Maharashtra" OSM data
3. Use QGIS to filter Pune area

### 2. SRTM Digital Elevation Model (DEM)
**Source:** USGS Earth Explorer

**Steps:**
1. Go to https://earthexplorer.usgs.gov/
2. Create free account
3. Search coordinates: `18.5204, 73.8567` (Pune center)
4. Select "Digital Elevation" → "SRTM 1 Arc-Second Global"
5. Download the tile covering Pune
6. Save as `pune_dem.tif`

**Alternative:** https://dwtkns.com/srtm30m/
- Click on Pune area on the map
- Download 30m resolution DEM

### 3. India Census Data
**Source:** Census of India 2011

**Official Portal:**
- https://censusindia.gov.in/
- Navigate to "District Census Handbook" → "Maharashtra" → "Pune"
- Download ward-wise population data

**DataMeet (Easier):**
- https://github.com/datameet/maps
- Download India administrative boundaries with population
- Filter for Pune wards

### 4. Bhuvan (ISRO) - Indian Satellite Data
**Website:** https://bhuvan.nrsc.gov.in/

**Available Data:**
- Land Use/Land Cover
- Water Resources
- Urban planning maps
- Disaster data

**Steps:**
1. Go to Bhuvan portal
2. Search "Pune"
3. Download thematic layers (requires free registration)

## API-Based Sources (Free Tier Available)

### 5. Google Earth Engine
**What:** Satellite imagery, land cover, elevation

**Setup:**
1. Sign up at https://earthengine.google.com/
2. Use Python API to download Pune data
3. Free for research/non-commercial use

**Example Python code:**
```python
import ee
ee.Initialize()

# Define Pune boundary
pune = ee.Geometry.Rectangle([73.73, 18.41, 73.99, 18.64])

# Get elevation
elevation = ee.Image('USGS/SRTMGL1_003').clip(pune)

# Export
task = ee.batch.Export.image.toDrive(
    image=elevation,
    description='pune_dem',
    scale=30,
    region=pune
)
task.start()
```

### 6. OpenWeatherMap API
**What:** Weather, flood risk data

**Setup:**
1. Sign up at https://openweathermap.org/api
2. Free tier: 1000 calls/day
3. Get historical weather data for Pune

### 7. Humanitarian Data Exchange (HDX)
**Website:** https://data.humdata.org/

**Search for:**
- "India floods"
- "Maharashtra disaster"
- "Pune urban"

**Available:**
- Flood extent maps
- Vulnerability data
- Infrastructure locations

## Kaggle Datasets

### 8. Search Kaggle
**URL:** https://www.kaggle.com/datasets

**Search terms:**
- "India census"
- "Pune"
- "Maharashtra floods"
- "India urban"
- "OpenStreetMap India"

**Recommended datasets:**
- India Census 2011 (various uploaders)
- Indian Cities Data
- Flood datasets for India

## Government Open Data

### 9. India Open Data Portal
**Website:** https://data.gov.in/

**Search for:**
- Pune Municipal Corporation data
- Maharashtra disaster data
- Urban infrastructure

### 10. Pune Municipal Corporation (PMC)
**Website:** https://www.pmc.gov.in/

**Available:**
- Ward boundaries
- Development plans
- Slum rehabilitation data
- Complaint data (RTI requests)

## Quick Start - Minimum Required Data

To get started quickly, download these 3 essential files:

### 1. Pune Boundary (5 minutes)
- Go to https://overpass-turbo.eu/
- Paste the Pune boundary query above
- Export as GeoJSON
- Save to `data/pune_boundary.geojson`

### 2. Elevation Data (10 minutes)
- Go to https://dwtkns.com/srtm30m/
- Click on Pune area
- Download tile
- Save to `data/pune_dem.tif`

### 3. Waterways (5 minutes)
- Use Overpass Turbo waterways query
- Export as GeoJSON
- Save to `data/drains.geojson`

## Data Preparation Tools

### QGIS (Free GIS Software)
**Download:** https://qgis.org/

**Use for:**
- Viewing and editing spatial data
- Converting formats (Shapefile ↔ GeoJSON)
- Clipping data to Pune boundary
- Creating custom layers

### Python Libraries
```bash
pip install geopandas rasterio fiona
```

**Convert formats:**
```python
import geopandas as gpd

# Convert Shapefile to GeoJSON
gdf = gpd.read_file('input.shp')
gdf.to_file('output.geojson', driver='GeoJSON')
```

## Data Quality Checklist

Before using data, verify:
- [ ] CRS is EPSG:4326 or can be reprojected
- [ ] Data covers Pune area (18.41°N to 18.64°N, 73.73°E to 73.99°E)
- [ ] No missing/corrupt geometries
- [ ] Attributes are properly named
- [ ] File size is reasonable (<100MB for testing)

## Next Steps

1. **Download Pune boundary** (required)
2. **Download DEM** (recommended)
3. **Download waterways** (recommended)
4. Place files in `data/` folder
5. Use production grid endpoint:

```bash
POST /production/generate-grid
{
  "boundary_path": "data/pune_boundary.geojson",
  "dem_path": "data/pune_dem.tif",
  "drain_path": "data/drains.geojson"
}
```

## Need Help?

- **OSM Help:** https://wiki.openstreetmap.org/
- **QGIS Tutorials:** https://www.qgistutorials.com/
- **GeoPandas Docs:** https://geopandas.org/
- **DataMeet Community:** https://datameet.org/

## Legal & Attribution

- **OSM Data:** © OpenStreetMap contributors, ODbL license
- **SRTM Data:** Public domain (USGS)
- **Census Data:** Government of India, open data
- Always attribute sources in your application
