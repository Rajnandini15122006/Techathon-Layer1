# Data Sources for PuneRakshak Layer 1

## Where to Get Spatial Data for Pune

### 1. Pune City Boundary
**Sources:**
- OpenStreetMap: https://www.openstreetmap.org/
  - Use Overpass Turbo: https://overpass-turbo.eu/
  - Query: `area["name"="Pune"]->.a; (relation(area.a)["boundary"="administrative"];); out geom;`
- DataMeet: http://projects.datameet.org/maps/
- Pune Municipal Corporation (PMC) official website

**Format:** Shapefile or GeoJSON

### 2. Digital Elevation Model (DEM)
**Sources:**
- SRTM 30m: https://earthexplorer.usgs.gov/
- ASTER GDEM: https://asterweb.jpl.nasa.gov/gdem.asp
- Bhuvan (ISRO): https://bhuvan.nrsc.gov.in/

**Format:** GeoTIFF (.tif)

### 3. Drainage Network
**Sources:**
- OpenStreetMap (waterways)
- Survey of India topographic maps
- PMC Engineering Department
- Bhuvan Water Resources

**Format:** Shapefile (line features)

### 4. Land Use / Land Cover
**Sources:**
- Bhuvan Thematic Services: https://bhuvan.nrsc.gov.in/
- NRSC Land Use Land Cover
- OpenStreetMap (building footprints, land use polygons)
- PMC Development Plan

**Format:** Shapefile (polygon features)

### 5. Census / Population Data
**Sources:**
- Census of India 2011: https://censusindia.gov.in/
- DataMeet Census Data: http://projects.datameet.org/
- PMC Ward-wise population data
- WorldPop: https://www.worldpop.org/

**Format:** Shapefile with population attribute

### 6. Slum Locations
**Sources:**
- PMC Slum Rehabilitation Authority
- Census of India (slum data)
- OpenStreetMap (informal settlements)
- Academic research papers on Pune slums

**Format:** Shapefile (point or polygon features)

### 7. Historical Flood Data
**Sources:**
- PMC Disaster Management Cell
- India Meteorological Department (IMD)
- Dartmouth Flood Observatory: https://floodobservatory.colorado.edu/
- News reports and citizen complaints (georeferenced)
- Research papers on Pune flooding

**Format:** GeoTIFF (flood depth raster) or Shapefile (flood extent polygons)

### 8. Infrastructure (Hospitals, Shelters)
**Sources:**
- OpenStreetMap: `amenity=hospital`, `amenity=shelter`
- PMC Health Department
- National Disaster Management Authority (NDMA) shelter list
- Google Maps API

**Format:** Shapefile (point features)

### 9. Flood Complaints
**Sources:**
- PMC Citizen Portal complaints
- 311 service requests
- Social media georeferenced posts
- News reports (georeferenced)

**Format:** Shapefile or CSV with coordinates

## Data Preparation Tips

### Converting OSM to Shapefile
```bash
# Using ogr2ogr
ogr2ogr -f "ESRI Shapefile" output.shp input.geojson

# Using QGIS
# File > Save As > Format: ESRI Shapefile
```

### Ensuring Correct CRS
All data should ideally be in:
- **EPSG:4326** (WGS84) for input
- System will automatically reproject to **EPSG:32643** (UTM 43N) for processing

### File Structure
```
data/
├── pune_boundary.shp
├── pune_boundary.shx
├── pune_boundary.dbf
├── pune_boundary.prj
├── pune_dem.tif
├── drains.shp
├── drains.shx
├── drains.dbf
├── drains.prj
└── ... (other files)
```

## Sample Data for Testing

If you don't have real data yet, you can:

1. **Use the sample data generator** (creates random data):
   ```
   POST /generate-sample-data
   ```

2. **Download sample datasets**:
   - Small test boundary from OSM
   - SRTM DEM tile covering Pune
   - OSM waterways export

3. **Create minimal test files** in QGIS:
   - Draw a simple polygon for boundary
   - Add a few points for infrastructure
   - Create basic land use zones

## Data Quality Requirements

- **Boundary**: Must be a valid polygon, no gaps
- **DEM**: Should cover entire Pune area, consistent resolution
- **Drains**: Line features, connected network preferred
- **Land Use**: Polygons with 'type' or 'land_use' attribute
- **Census**: Polygons or points with 'population' attribute
- **Slums**: Points or polygons
- **Floods**: Raster with depth values or polygons with depth attribute
- **Infrastructure**: Points with 'type' or 'amenity' attribute
- **Complaints**: Points with location coordinates

## Contact for Data

- **Pune Municipal Corporation**: https://www.pmc.gov.in/
- **Maharashtra Remote Sensing Applications Centre**: https://mrsac.gov.in/
- **Survey of India**: https://www.surveyofindia.gov.in/
- **DataMeet Community**: https://datameet.org/

## Legal & Attribution

- Ensure you have rights to use the data
- Attribute sources appropriately
- Follow open data licenses (ODbL for OSM)
- Respect data privacy for sensitive information
