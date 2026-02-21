# Layer 3: HRVC Risk Engine

## Overview

Layer 3 implements the **HRVC (Hazard × Vulnerability / Capacity)** risk scoring engine that computes comprehensive disaster risk scores for each grid cell.

## Architecture

```
Risk Score = (Hazard × Vulnerability) / Capacity
```

### Components

1. **Hazard Score (H)** - 0-100
   - Flood depth history (40%)
   - Elevation (30%) - lower = higher risk
   - Drain proximity (30%) - closer = higher risk

2. **Vulnerability Score (V)** - 0-100
   - Population density (50%)
   - Slum density (40%)
   - Land use type (10%)

3. **Capacity Score (C)** - 0-100
   - Infrastructure count (60%)
   - Complaint history (40%) - inverted

4. **Risk Levels**
   - Low: 0-25
   - Medium: 25-50
   - High: 50-75
   - Critical: 75-100

## Database Schema

New columns added to `grid_cells` table:

```sql
hazard_score          FLOAT    -- Hazard component (0-100)
vulnerability_score   FLOAT    -- Vulnerability component (0-100)
capacity_score        FLOAT    -- Capacity component (0-100)
risk_score           FLOAT    -- Final HRVC risk (0-100)
risk_level           VARCHAR  -- Low/Medium/High/Critical
```

## API Endpoints

### POST /risk/compute-hrvc

Computes HRVC risk scores for all grid cells.

**Response:**
```json
{
  "status": "success",
  "total_cells": 11377,
  "risk_statistics": {
    "mean": 45.2,
    "median": 42.8,
    "min": 8.5,
    "max": 98.3,
    "std": 18.7
  },
  "risk_distribution": {
    "Critical": 1250,
    "High": 3200,
    "Medium": 4500,
    "Low": 2427
  }
}
```

### GET /risk/high-risk-cells

Get cells with risk score above threshold.

**Parameters:**
- `min_risk` (default: 50.0) - Minimum risk score
- `limit` (default: 100) - Max cells to return

**Response:** GeoJSON FeatureCollection with risk properties

## Usage

### Step 1: Generate Grid Data
```bash
# Start server
python run_local.py

# Generate synthetic grid
curl -X POST http://localhost:8000/synthetic/generate-pune-grid
```

### Step 2: Compute Risk Scores
```bash
# Compute HRVC risk
curl -X POST http://localhost:8000/risk/compute-hrvc
```

### Step 3: Query High-Risk Areas
```bash
# Get critical risk cells
curl http://localhost:8000/risk/high-risk-cells?min_risk=75
```

### Step 4: Visualize
Open http://localhost:8000 to see:
- Color-coded risk map
- Risk scores in cell popups
- H/V/C component breakdown

## Testing

Run the test script:
```bash
python test_layer3.py
```

## Implementation Files

- `app/models/grid_cell.py` - Added risk columns
- `app/services/hrvc_risk_service.py` - Risk computation logic
- `app/routers/hrvc_risk.py` - API endpoints
- `app/static/index.html` - Updated UI with risk visualization

## Risk Computation Logic

### Hazard Score
```python
H = (flood_depth * 0.4) + 
    ((max_elev - elevation) * 0.3) + 
    ((max_drain - drain_dist) * 0.3)
```

### Vulnerability Score
```python
V = (population_density * 0.5) + 
    (slum_density * 0.4) + 
    (land_use_factor * 0.1)
```

### Capacity Score
```python
C = (infrastructure_count * 0.6) + 
    ((max_complaints - complaints) * 0.4)
```

### Final Risk
```python
Risk = (H × V) / max(C, 10)  # Min capacity = 10 to avoid division by zero
```

## Next Steps

Layer 3 provides the foundation for:
- **Layer 4**: Resource prepositioning based on risk scores
- **Layer 5**: Alert scheduling for high-risk areas
- **Layer 6**: Risk evolution tracking over time

## Notes

- All scores normalized to 0-100 scale
- Risk computation is idempotent (can be re-run)
- Scores update in database for persistence
- UI automatically shows risk when available
