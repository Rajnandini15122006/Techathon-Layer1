# 🚀 Getting Started with Real Pune Data

**Goal**: Replace synthetic test data with real Pune spatial data in 15-30 minutes.

## What You'll Get

After following this guide, you'll have:
- ✅ Real Pune city boundary
- ✅ Actual elevation data (SRTM 30m)
- ✅ Real waterway network (Mula-Mutha rivers)
- ✅ 11,000+ grid cells with computed spatial attributes
- ✅ Production-ready disaster risk assessment foundation

## Prerequisites

- ✅ Server running (`python run_local.py`)
- ✅ Internet connection
- ✅ Web browser
- ✅ 15-30 minutes of time

## Step-by-Step Process

### 1️⃣ Create Data Folder (30 seconds)

The `data/` folder already exists in your project. This is where you'll save all downloaded files.

### 2️⃣ Download Pune Boundary (5 minutes) ⭐ REQUIRED

This defines the area we'll analyze.

**Instructions:**
1. Open https://overpass-turbo.eu/ in your browser
2. Clear the query box and paste this:
```
[out:json];
area["name"="Pune"]["admin_level"="8"]->.a;
(relation(area.a)["boundary"="administrative"];);
out geom;
```
3. Click the **"Run"** button (top left, looks like a play button ▶️)
4. Wait 5-10 seconds for the query to complete
5. You should see Pune boundary highlighted on the map
6. Click **"Export"** (top menu)
7. Select **"GeoJSON"**
8. Save the file as `pune_boundary.geojson` in your `data/` folder

**Verification:**
- File size should be ~50-200 KB
- Open in text editor - should start with `{"type":"FeatureCollection"`

### 3️⃣ Download Elevation Data (5 minutes) ⭐ RECOMMENDED

This provides terrain information for flood risk analysis.

**Instructions:**
1. Open https://dwtkns.com/srtm30m/
2. Find Pune on the map (or search for coordinates: 18.5, 73.8)
3. Click on the tile covering Pune
4. Download will start automatically (file named like `N18E073.hgt.zip`)
5. Extract the `.hgt` file from the zip
6. Rename it to `pune_dem.tif` (or keep as `.hgt` - both work)
7. Move to your `data/` folder

**Verification:**
- File size should be ~25 MB
- File extension: `.hgt` or `.tif`

### 4️⃣ Download Waterways (5 minutes) ⭐ RECOMMENDED

This provides drainage network data for flood proximity analysis.

**Instructions:**
1. Go back to https://overpass-turbo.eu/
2. Clear the previous query and paste this:
```
[out:json];
area["name"="Pune"]->.a;
(way(area.a)["waterway"];);
out geom;
```
3. Click **"Run"**
4. Wait for rivers/streams to appear on map
5. Click **"Export"** → **"GeoJSON"**
6. Save as `drains.geojson` in your `data/` folder

**Verification:**
- File size should be ~100-500 KB
- Should show Mula-Mutha river system

### 5️⃣ Generate Your Production Grid! (2 minutes)

Now use the real data to generate your grid.

**Option A: Using Web UI (Easiest)**
1. Open http://localhost:8000
2. Open browser console (F12)
3. Paste this JavaScript:
```javascript
fetch('/production/generate-grid', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    boundary_path: 'data/pune_boundary.geojson',
    dem_path: 'data/pune_dem.tif',
    drain_path: 'data/drains.geojson'
  })
})
.then(r => r.json())
.then(d => console.log(d));
```
4. Press Enter and wait 30-60 seconds

**Option B: Using curl**
```bash
curl -X POST "http://localhost:8000/production/generate-grid" \
  -H "Content-Type: application/json" \
  -d '{
    "boundary_path": "data/pune_boundary.geojson",
    "dem_path": "data/pune_dem.tif",
    "drain_path": "data/drains.geojson"
  }'
```

**Option C: Using Python**
```python
import requests

response = requests.post(
    'http://localhost:8000/production/generate-grid',
    json={
        'boundary_path': 'data/pune_boundary.geojson',
        'dem_path': 'data/pune_dem.tif',
        'drain_path': 'data/drains.geojson'
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
  "crs_working": "EPSG:32643",
  "crs_storage": "EPSG:4326",
  "attributes_computed": {
    "elevation": 11377,
    "drain_distance": 11377,
    "land_use": 0,
    "population": 0,
    "slum_density": 0,
    "flood_depth": 0,
    "infrastructure": 0,
    "complaints": 0
  }
}
```

### 6️⃣ View Your Grid! (1 minute)

1. Go to http://localhost:8000
2. Click **"🔄 Load Grid Cells"**
3. You should see 11,377 grid cells covering Pune
4. Hover over cells to see elevation and drain distance data
5. Cells are colored by flood risk (based on elevation + drain proximity)

**Success! 🎉** You now have a production grid with real data!

## What's Next?

### Add More Data Sources (Optional)

You can enhance your grid with additional data:

#### Hospitals & Infrastructure
```
[out:json];
area["name"="Pune"]->.a;
(node(area.a)["amenity"="hospital"];);
out center;
```
Save as: `data/hospitals.geojson`

Then regenerate with:
```json
{
  "boundary_path": "data/pune_boundary.geojson",
  "dem_path": "data/pune_dem.tif",
  "drain_path": "data/drains.geojson",
  "infra_path": "data/hospitals.geojson"
}
```

#### Land Use
```
[out:json];
area["name"="Pune"]->.a;
(way(area.a)["landuse"];);
out geom;
```
Save as: `data/land_use.geojson`

#### More Sources
- **Census data**: Search Kaggle for "India census 2011"
- **Flood history**: Check https://data.humdata.org/
- **Slum data**: PMC website or research datasets

See [DATA_INTEGRATION_GUIDE.md](DATA_INTEGRATION_GUIDE.md) for complete details.

## Troubleshooting

### "Boundary file not found"
- Check that file is in `data/` folder (not `data/data/`)
- Verify filename is exactly `pune_boundary.geojson`
- Try absolute path: `C:/path/to/project/data/pune_boundary.geojson`

### "No elevation data computed"
- Check file extension (`.hgt` or `.tif`)
- Verify file is not corrupted (should be ~25 MB)
- Try downloading from alternative source

### "Database connection error"
- Check your `.env` file has correct Neon connection string
- Verify Neon database is not sleeping (visit Neon dashboard)
- Wait 30 seconds and try again

### "Grid generation taking too long"
- Normal time: 30-90 seconds for 11,377 cells
- Check server logs for progress
- If stuck >5 minutes, restart server and try again

### "Empty grid or wrong area"
- Verify boundary file shows Pune (open in QGIS or geojson.io)
- Check coordinates are around 18.5°N, 73.8°E
- Ensure boundary is a valid polygon

## Verification Checklist

After generation, verify:
- [ ] Total cells: ~11,000-12,000
- [ ] Elevation values: 500-650m range
- [ ] Drain distances: 0-20km range
- [ ] Grid covers entire Pune city
- [ ] No gaps or missing areas
- [ ] Cells are 250m × 250m

## Helper Tools

### Check Downloaded Files
```bash
python scripts/download_pune_data.py
```

### View Data in QGIS (Optional)
1. Download QGIS: https://qgis.org/
2. Open your GeoJSON files to verify
3. Check coordinate system (should be EPSG:4326)

### Test API
```bash
# Check if grid exists
curl "http://localhost:8000/grid-cells?limit=1"

# Get cell count
curl "http://localhost:8000/grid-cells?limit=20000&format=geojson" | grep -o "Feature" | wc -l
```

## Resources

- **Complete Guide**: [DATA_INTEGRATION_GUIDE.md](DATA_INTEGRATION_GUIDE.md)
- **Data Sources**: [REAL_DATA_SOURCES.md](REAL_DATA_SOURCES.md)
- **API Docs**: http://localhost:8000/docs
- **Overpass Turbo**: https://overpass-turbo.eu/
- **SRTM Data**: https://dwtkns.com/srtm30m/

## Need Help?

1. Check server logs for detailed error messages
2. Verify all file paths are correct
3. Ensure files are not corrupted (check file sizes)
4. Try with just boundary first, then add other data
5. Check [DATA_INTEGRATION_GUIDE.md](DATA_INTEGRATION_GUIDE.md) for detailed troubleshooting

---

**You're all set! 🎉 Your disaster risk assessment platform now uses real Pune data.**
