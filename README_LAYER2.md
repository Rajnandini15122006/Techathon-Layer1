# Layer 2: USPS Engine - Quick Start

## What is USPS?

Urban System Pressure Score (USPS) measures infrastructure stress BEFORE failure and detects cascading risk across 5 critical subsystems.

## Quick Test

```bash
python test_usps_engine.py
```

## Start Server

```bash
python run_local.py
```

## Access Dashboard

```
http://localhost:8000/static/usps_dashboard.html
```

Or click "🔴 USPS Monitor" in main interface.

## API Examples

### Calculate USPS
```bash
curl "http://localhost:8000/api/usps/calculate?lat_min=18.45&lat_max=18.55&lon_min=73.80&lon_max=73.90"
```

### Get Cascade Warnings
```bash
curl "http://localhost:8000/api/usps/cascade-warnings?lat_min=18.45&lat_max=18.55&lon_min=73.80&lon_max=73.90"
```

## 5 Subsystems Monitored

1. 🌧️ Rain Accumulation
2. 🌊 Drain Capacity Load
3. 🚗 Road Congestion
4. 🏥 Hospital Occupancy
5. ⚡ Power Substation Stress

## Cascade Detection

When 2+ systems approach threshold → CASCADE WARNING
When 4+ systems critical → EMERGENCY

## Key Innovation

Traditional: Detect failure AFTER it happens
USPS: Predict failure BEFORE it happens

See `LAYER2_USPS_ENGINE.md` for complete documentation.
