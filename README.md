# PuneRakshak - Disaster Risk Assessment Platform

Layer 1: Data & Micro-Grid Spatial Foundation

## Overview

PuneRakshak divides Pune city into 250m × 250m grid cells and stores static geographic and demographic attributes for disaster risk assessment.

## 🚀 Quick Start

1. **Setup Database**: Create a Neon PostgreSQL database (see [NEON_SETUP.md](NEON_SETUP.md))
2. **Configure**: Copy `.env.example` to `.env` and add your database URL
3. **Run Server**: `python run_local.py`
4. **Open UI**: Visit http://localhost:8000
5. **Get Real Data**: Click "📊 Use Real Pune Data" button or see [DATA_INTEGRATION_GUIDE.md](DATA_INTEGRATION_GUIDE.md)

## 📊 Data Options

### Option 1: Synthetic Data (Testing)
- Click "Generate Synthetic Pune Grid" in the UI
- Creates 11,377 realistic grid cells with spatial patterns
- Perfect for testing and development

### Option 2: Real Data (Production)
- **Quick Start (15 min)**: See [DATA_INTEGRATION_GUIDE.md](DATA_INTEGRATION_GUIDE.md)
- **Data Sources**: See [REAL_DATA_SOURCES.md](REAL_DATA_SOURCES.md)
- **Helper Script**: Run `python scripts/download_pune_data.py`

## Tech Stack

- Python 3.11
- FastAPI
- PostgreSQL + PostGIS
- GeoPandas, Shapely, Rasterio
- SQLAlchemy + GeoAlchemy2
- Docker & Docker Compose

## Project Structure

```
/
├── app/
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── routers/         # API endpoints
│   ├── config.py        # Configuration
│   ├── database.py      # Database setup
│   └── main.py          # FastAPI app
├── scripts/
│   └── generate_grid.py # Grid generation script
├── data/                # Place your data files here
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Setup

### 1. Configure Neon Database

1. Create a Neon PostgreSQL database at https://neon.tech
2. Enable PostGIS extension in your Neon database:
   - Go to your Neon project dashboard
   - Navigate to SQL Editor
   - Run: `CREATE EXTENSION IF NOT EXISTS postgis;`
3. Copy your connection string from Neon dashboard

### 2. Configure Environment

1. Copy environment file:
```bash
copy .env.example .env
```

2. Edit `.env` and add your Neon connection string:
```
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
```

### 3. Run the Application

**Option A: Using Docker (API only)**
```bash
docker compose up -d
```

**Option B: Run locally**
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000
API documentation at http://localhost:8000/docs

## Generate Grid Cells

### Using Synthetic Data (Quick Test)
```bash
# Start server
python run_local.py

# Generate synthetic grid via API
curl -X POST "http://localhost:8000/synthetic/generate-pune-grid"

# Or use the web UI button
```

### Using Real Data (Production)

**Step 1: Download Data** (see [DATA_INTEGRATION_GUIDE.md](DATA_INTEGRATION_GUIDE.md))
- Pune boundary from OpenStreetMap
- Elevation data from SRTM
- Waterways, land use, census data, etc.

**Step 2: Generate Grid**
```bash
curl -X POST "http://localhost:8000/production/generate-grid" \
  -H "Content-Type: application/json" \
  -d '{
    "boundary_path": "data/pune_boundary.geojson",
    "dem_path": "data/pune_dem.tif",
    "drain_path": "data/drains.geojson"
  }'
```

**Helper Script:**
```bash
python scripts/download_pune_data.py
```

## API Endpoints

### Grid Data
- **GET /grid-cells** - Get all grid cells (supports GeoJSON format)
- **GET /grid-cells/{id}** - Get specific grid cell
- **POST /synthetic/generate-pune-grid** - Generate synthetic test data
- **POST /production/generate-grid** - Generate grid from real data

### Documentation
- **GET /docs** - Interactive API documentation (Swagger UI)
- **GET /** - Web UI with interactive map

### GET /grid-cells
Get all grid cells with pagination

Query parameters:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100, max: 1000)
- `format`: Response format - `geojson` or `json` (default: geojson)

Example:
```bash
curl "http://localhost:8000/grid-cells?limit=10&format=geojson"
```

### GET /grid-cells/{id}
Get a specific grid cell by UUID

Query parameters:
- `format`: Response format - `geojson` or `json` (default: geojson)

Example:
```bash
curl "http://localhost:8000/grid-cells/{uuid}"
```

## Database Schema

Table: `grid_cells`

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| geom | Geometry(Polygon) | Grid cell polygon (SRID 4326) |
| elevation_mean | Float | Mean elevation from DEM |
| slope_mean | Float | Mean slope |
| drain_distance | Float | Distance to nearest drain (meters) |
| land_use | String | Land use type |
| population_density | Float | Population per sq meter |
| slum_density | Float | Slum density |
| flood_history_score | Integer | Historical flood count |
| infra_score | Integer | Infrastructure count |
| created_at | DateTime | Creation timestamp |

## Data Requirements

- **Boundary**: Shapefile or GeoJSON of Pune city boundary
- **DEM**: Digital Elevation Model raster (optional)
- **Drains**: Drainage network shapefile (optional)
- **Land Use**: Land use classification shapefile (optional)
- **Census**: Population census data (optional)
- **Slums**: Slum locations (optional)
- **Floods**: Historical flood events (optional)
- **Infrastructure**: Hospitals, shelters, etc. (optional)

All spatial data should be in EPSG:4326 (WGS84) or will be automatically reprojected.

## Development

### Local Development (without Docker)

1. Ensure you have Python 3.11+ installed
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure `.env` with your Neon connection string

4. Run the API:
```bash
uvicorn app.main:app --reload
```

### Enable PostGIS in Neon

If you get a PostGIS error, enable it manually:

1. Connect to your Neon database using psql or SQL Editor
2. Run:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

3. Verify installation:
```sql
SELECT PostGIS_version();
```

## Notes

- Grid cells are 250m × 250m (configurable via `cell_size` parameter)
- All coordinates use EPSG:4326 (WGS84) for storage
- Grid generation uses EPSG:32643 (UTM Zone 43N) for accurate measurements
- PostGIS extension is automatically enabled
- Risk scoring will be implemented in Layer 2

## 📚 Documentation

- **[DEMO_GUIDE_FOR_JUDGES.md](DEMO_GUIDE_FOR_JUDGES.md)** - 5-minute demo script to impress judges
- **[REALTIME_API_SETUP.md](REALTIME_API_SETUP.md)** - Setup real-time weather API (optional, 2 min)
- **[DATA_INTEGRATION_GUIDE.md](DATA_INTEGRATION_GUIDE.md)** - Complete guide to obtaining and using real Pune data
- **[REAL_DATA_SOURCES.md](REAL_DATA_SOURCES.md)** - Detailed list of free data sources (OSM, SRTM, Kaggle, etc.)
- **[NEON_SETUP.md](NEON_SETUP.md)** - Setting up Neon PostgreSQL database
- **[QUICK_START.md](QUICK_START.md)** - Quick start guide for the platform

## 🎯 Features

- ✅ 250m × 250m spatial grid generation
- ✅ PostGIS spatial database (Neon serverless)
- ✅ Interactive web map with Leaflet
- ✅ **Real-time weather monitoring** (OpenWeatherMap API)
- ✅ **Live disaster risk assessment** (Flood, Heat, Storm)
- ✅ **24-hour predictive forecast**
- ✅ Synthetic data generator for testing
- ✅ Real data integration from multiple sources
- ✅ RESTful API with FastAPI
- ✅ GeoJSON support
- ✅ Comprehensive spatial attribute computation
- 🔄 Risk scoring (Layer 2 - coming soon)
- 🔄 Real-time monitoring (Layer 3 - coming soon)
