# Quick Start Guide (Without Docker)

## Step 1: Install Minimal Dependencies

```powershell
pip install -r requirements-minimal.txt
```

This installs only the core API dependencies without heavy geospatial libraries.

## Step 2: Configure Neon Database

1. Get your Neon connection string from https://neon.tech
2. Update `.env` file:
   ```
   DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
   ```

## Step 3: Enable PostGIS in Neon

Go to Neon SQL Editor and run:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

## Step 4: Run the API

```powershell
python run_local.py
```

Or:
```powershell
uvicorn app.main:app --reload
```

The API will be available at:
- http://localhost:8000
- Docs: http://localhost:8000/docs

## Step 5: Populate Grid Data (Later)

For now, the API is running but the database is empty. You can:

### Option A: Use a separate machine with geospatial libraries
Install full requirements on another machine (Linux/Mac or WSL):
```bash
pip install -r requirements.txt
python scripts/generate_grid.py --boundary data/pune_boundary.geojson
```

### Option B: Manually insert test data
Use the SQL Editor in Neon to insert sample grid cells:
```sql
INSERT INTO grid_cells (geom, elevation_mean, population_density, flood_history_score, infra_score)
VALUES (
    ST_GeomFromText('POLYGON((73.8 18.5, 73.8 18.502, 73.802 18.502, 73.802 18.5, 73.8 18.5))', 4326),
    550.5,
    0.001,
    2,
    1
);
```

### Option C: Install geospatial libraries (if you can)
If you want to generate grids locally, you'll need to install GDAL first:
- Download OSGeo4W from https://trac.osgeo.org/osgeo4w/
- Then: `pip install -r requirements.txt`

## Testing the API

Once running, test these endpoints:

```powershell
# Health check
curl http://localhost:8000/health

# Get grid cells (will be empty initially)
curl http://localhost:8000/grid-cells

# View interactive docs
# Open browser: http://localhost:8000/docs
```

## Next Steps

1. API is running ✓
2. Database is connected ✓
3. Need to populate grid data (use Option A, B, or C above)
4. Then you can query grid cells via the API
