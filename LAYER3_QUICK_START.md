# 🚀 Layer 3 Quick Start

## What is Layer 3?

Layer 3 is the **HRVC Risk Engine** that computes comprehensive disaster risk scores using:
- **H**azard (flood depth, elevation, drainage)
- **V**ulnerability (population, slums, land use)
- **C**apacity (infrastructure, response capability)

**Formula:** `Risk = (Hazard × Vulnerability) / Capacity`

## 5-Minute Setup

### 1. Start Server
```bash
python run_local.py
```

### 2. Generate Grid (if not done)
```bash
curl -X POST http://localhost:8000/synthetic/generate-pune-grid
```

### 3. Compute Risk Scores
```bash
curl -X POST http://localhost:8000/risk/compute-hrvc
```

### 4. View Results
Open http://localhost:8000

## What You'll See

### On the Map
- **Green cells** = Low risk (0-25)
- **Orange cells** = Medium risk (25-50)
- **Red cells** = High risk (50-75)
- **Dark red cells** = Critical risk (75-100)

### In Cell Popups
Click any cell to see:
- Overall risk score and level
- Hazard score breakdown
- Vulnerability score breakdown
- Capacity score breakdown
- All underlying data attributes

## API Examples

### Get Risk Statistics
```bash
curl -X POST http://localhost:8000/risk/compute-hrvc
```

**Response:**
```json
{
  "total_cells": 11377,
  "risk_statistics": {
    "mean": 45.2,
    "median": 42.8,
    "min": 8.5,
    "max": 98.3
  },
  "risk_distribution": {
    "Critical": 1250,
    "High": 3200,
    "Medium": 4500,
    "Low": 2427
  }
}
```

### Get Critical Risk Areas
```bash
curl http://localhost:8000/risk/high-risk-cells?min_risk=75&limit=50
```

Returns GeoJSON of top 50 critical risk cells.

## Testing

Run automated test:
```bash
python test_layer3.py
```

## Architecture

```
Layer 1: Grid Foundation (✅ Complete)
  ↓
Layer 3: HRVC Risk Engine (✅ Complete)
  ↓
Layer 4: Resource Prepositioning (Next)
```

## Key Features

✅ **Normalized scoring** - All scores on 0-100 scale
✅ **Multi-factor analysis** - 8 input attributes
✅ **Spatial correlation** - Geographic patterns preserved
✅ **Real-time computation** - Updates in seconds
✅ **Visual feedback** - Color-coded risk map
✅ **Detailed breakdown** - H/V/C components visible

## Files Added

- `app/services/hrvc_risk_service.py` - Risk computation
- `app/routers/hrvc_risk.py` - API endpoints
- `test_layer3.py` - Test script
- `LAYER3_HRVC_GUIDE.md` - Full documentation

## Next Steps

1. ✅ Layer 1: Grid foundation
2. ✅ Layer 3: HRVC risk scoring
3. 🔄 Layer 4: Resource prepositioning
4. 🔄 Layer 5: Alert scheduling
5. 🔄 Layer 6: Risk memory & evolution

## Troubleshooting

**Error: "No grid cells found"**
- Run: `curl -X POST http://localhost:8000/synthetic/generate-pune-grid`

**Risk scores not showing on map**
- Run: `curl -X POST http://localhost:8000/risk/compute-hrvc`
- Refresh browser

**Database connection error**
- Check `.env` file has correct DATABASE_URL
- Ensure Neon database is active

## Demo Script

```bash
# 1. Generate grid
curl -X POST http://localhost:8000/synthetic/generate-pune-grid

# 2. Compute risk
curl -X POST http://localhost:8000/risk/compute-hrvc

# 3. Get high-risk areas
curl http://localhost:8000/risk/high-risk-cells?min_risk=75

# 4. Open browser
# Visit http://localhost:8000
```

## Success Criteria

✅ Risk scores computed for all cells
✅ Map shows color-coded risk levels
✅ Cell popups show H/V/C breakdown
✅ API returns risk statistics
✅ High-risk cells identifiable

---

**Layer 3 is now complete!** 🎉

The system can now identify high-risk areas based on comprehensive multi-factor analysis.
