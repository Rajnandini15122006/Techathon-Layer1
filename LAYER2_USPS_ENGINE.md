# Layer 2: Urban System Pressure Score (USPS) Engine 🔴

## 🎯 CORE INNOVATION

The USPS Engine measures **system saturation BEFORE failure** and detects **cascading risk** when multiple subsystems approach their thresholds simultaneously.

## What Makes This Unique

Traditional systems detect failures AFTER they happen. USPS predicts system collapse by monitoring pressure across 5 critical urban subsystems and identifying dangerous correlations.

## The USPS Formula

```
USPS = Weighted Sum of Subsystem Pressures + Cascade Multiplier

Where each subsystem pressure = (Current Value / Threshold) × 100

Cascade Multiplier applied when 2+ systems approach threshold
```

## 5 Critical Subsystems

### 1. Rain Accumulation (25%)
- Measures: % of drainage capacity filled
- Threshold: 80%
- Impact: Flooding risk

### 2. Drain Capacity Load (25%)
- Measures: % of drain system saturated
- Threshold: 85%
- Impact: System overflow

### 3. Road Congestion (20%)
- Measures: % of road capacity used
- Threshold: 75%
- Impact: Evacuation blocked

### 4. Hospital Occupancy (15%)
- Measures: % of hospital beds occupied
- Threshold: 90%
- Impact: Medical capacity exhausted

### 5. Power Substation Stress (15%)
- Measures: % of power capacity used
- Threshold: 85%
- Impact: Grid failure

## Pressure Levels

| USPS Score | Level | Meaning |
|------------|-------|---------|
| 90-100 | CRITICAL | System failure imminent |
| 75-89 | SEVERE | Multiple systems stressed |
| 60-74 | HIGH | Significant pressure |
| 40-59 | MODERATE | Elevated monitoring |
| 20-39 | LOW | Normal operations |
| 0-19 | MINIMAL | No concerns |

## Cascading Risk Detection

The engine identifies when multiple systems approach failure:

- **EMERGENCY**: 4+ systems at risk → Cascading failure imminent
- **CRITICAL**: 3+ systems at risk → High cascade risk
- **WARNING**: 2+ systems at risk → Monitor for cascade
- **NORMAL**: 0-1 systems at risk → No cascade risk

## API Endpoints

### Calculate USPS
```bash
GET /api/usps/calculate?lat_min=18.45&lat_max=18.55&lon_min=73.80&lon_max=73.90
```

### Get Cascade Warnings
```bash
GET /api/usps/cascade-warnings?lat_min=18.45&lat_max=18.55&lon_min=73.80&lon_max=73.90
```

### Get Critical Cells
```bash
GET /api/usps/critical-cells?lat_min=18.45&lat_max=18.55&lon_min=73.80&lon_max=73.90&threshold=70
```

### Subsystem Status
```bash
GET /api/usps/subsystem-status?lat_min=18.45&lat_max=18.55&lon_min=73.80&lon_max=73.90
```

## Dashboard

Access at: `http://localhost:8000/static/usps_dashboard.html`

Features:
- Real-time subsystem pressure monitoring
- Cascading failure warnings
- Critical cell identification
- Actionable recommendations

## Testing

```bash
python test_usps_engine.py
```

## Implementation Files

- `app/services/usps_engine.py` - Core USPS calculation
- `app/routers/usps.py` - API endpoints
- `app/services/usps_data_generator.py` - Test data
- `app/static/usps_dashboard.html` - Dashboard
- `test_usps_engine.py` - Test suite

## Why This Matters

USPS replaces multiple separate modules:
- ❌ Drain simulation
- ❌ Infrastructure overload detection
- ❌ Stress monitoring

All merged into ONE unified pressure score with cascading risk detection.

This is your standout innovation! 🚀
