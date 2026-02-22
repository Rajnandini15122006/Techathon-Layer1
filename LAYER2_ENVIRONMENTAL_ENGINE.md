# Layer 2: Real-Time Environmental Modeling & USPS Engine

## Overview

Layer 2 implements production-grade environmental stress modeling for urban disaster risk assessment. This layer is **dynamic**, **deterministic**, and **audit-ready**.

### Key Features
- ✅ Real-time environmental input processing
- ✅ SCS-CN hydrological modeling (industry standard)
- ✅ Structured index normalization
- ✅ Multi-criteria composite scoring (USPS)
- ✅ Time-series data storage
- ✅ Explainable calculations
- ✅ No random values or black-box AI

## Architecture

### Module Structure
```
app/services/environmental_engine.py
├── RainModule              # Rainfall normalization
├── DrainStressModule       # SCS-CN runoff & drain stress
├── TrafficModule           # Traffic congestion indexing
├── USPSCalculator          # Composite score computation
└── EnvironmentalEngine     # Main orchestrator
```

### Database Models
```
app/models/environmental.py
├── RainfallLog            # Rainfall time-series
├── DrainStressLog         # Drain stress time-series
├── TrafficLog             # Traffic time-series
└── USPSLog                # USPS time-series
```

### API Endpoints
```
app/routers/environmental.py
├── POST /environmental/update           # Update single grid
├── POST /environmental/bulk-update      # Bulk update
├── GET  /environmental/usps/{grid_id}   # Latest USPS
├── GET  /environmental/latest           # All latest USPS
├── GET  /environmental/history/{grid_id}# Time-series history
└── GET  /environmental/summary          # System summary
```

## Scientific Foundation

### 1. Rain Module

**Purpose**: Normalize rainfall data to 0-1 scale

**Formula**:
```
RainIndex = current_rainfall / max_expected_rainfall
```

**Parameters**:
- `max_expected_rainfall`: 100 mm/hr (configurable)

**Output**: Normalized rain index (0-1)

### 2. Drain Stress Module

**Purpose**: Compute surface runoff and drain stress using SCS-CN method

**SCS-CN Runoff Formula**:
```
If P ≤ 0.2S:
    Runoff = 0
Else:
    Runoff = ((P - 0.2S)²) / (P + 0.8S)

Where:
    P = Rainfall (mm)
    S = (1000 / CN) - 10
    CN = Curve Number (land use dependent)
```

**Curve Numbers (CN)**:
- Built-up/Urban: 92.5
- Residential/Mixed: 80.0
- Vegetation/Parks: 62.5

**Drain Stress Formula**:
```
DrainStress = RunoffVolume / DrainCapacity

Where:
    RunoffVolume = (Runoff_mm / 1000) × GridArea_m²
    DrainCapacity = Grid-specific capacity (m³)
```

**Output**: Normalized drain stress (0-1)

### 3. Traffic Module

**Purpose**: Normalize traffic congestion to 0-1 scale

**Formula**:
```
TrafficIndex = (TravelTimeRatio - 1) / 2

Where:
    TravelTimeRatio = CurrentTravelTime / FreeFlowTravelTime
```

**Interpretation**:
- Ratio 1.0 → Index 0.0 (no congestion)
- Ratio 3.0+ → Index 1.0 (severe congestion)

**Output**: Normalized traffic index (0-1)

### 4. USPS Calculator

**Purpose**: Compute Urban System Pressure Score using weighted aggregation

**Formula**:
```
USPS = w₁ × RainIndex + w₂ × DrainStress + w₃ × TrafficIndex
```

**Default Weights** (based on disaster risk principles):
- w₁ = 0.4 (Rain - primary hazard trigger)
- w₂ = 0.4 (Drain - hazard amplifier)
- w₃ = 0.2 (Traffic - systemic vulnerability)

**Severity Classification**:
- 0.0 - 0.3: **Stable**
- 0.3 - 0.6: **Watch**
- 0.6 - 0.8: **High Alert**
- 0.8 - 1.0: **Critical**

## API Usage

### 1. Update Environmental State

```bash
POST /environmental/update
```

**Request**:
```json
{
  "grid_id": 1,
  "rainfall_mm": 25.5,
  "accumulated_1hr": 30.0,
  "traffic_congestion": 0.6
}
```

**Response**:
```json
{
  "grid_id": 1,
  "rain": {
    "rainfall_mm": 25.5,
    "accumulated_1hr": 30.0,
    "rain_index": 0.255,
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "drain": {
    "runoff_mm": 12.3,
    "drain_stress": 0.45,
    "curve_number": 80.0,
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "traffic": {
    "traffic_index": 0.6,
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "usps": {
    "rain_index": 0.255,
    "drain_stress": 0.45,
    "traffic_index": 0.6,
    "usps_score": 0.402,
    "severity_level": "Watch",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### 2. Get Latest USPS

```bash
GET /environmental/usps/1
```

**Response**:
```json
{
  "grid_id": 1,
  "rain_index": 0.255,
  "drain_stress": 0.45,
  "traffic_index": 0.6,
  "usps_score": 0.402,
  "severity_level": "Watch",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 3. Get System Summary

```bash
GET /environmental/summary
```

**Response**:
```json
{
  "total_grids": 340,
  "severity_distribution": {
    "Stable": 180,
    "Watch": 120,
    "High Alert": 35,
    "Critical": 5
  },
  "average_usps": 0.35,
  "max_usps": 0.85,
  "critical_grids": 5,
  "high_alert_grids": 35,
  "watch_grids": 120,
  "stable_grids": 180,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 4. Get Time-Series History

```bash
GET /environmental/history/1?hours=24
```

**Response**:
```json
{
  "grid_id": 1,
  "period_hours": 24,
  "data_points": 144,
  "history": [
    {
      "timestamp": "2024-01-14T10:30:00Z",
      "usps_score": 0.25,
      "severity_level": "Stable",
      "rain_index": 0.1,
      "drain_stress": 0.2,
      "traffic_index": 0.3
    },
    ...
  ]
}
```

### 5. Bulk Update

```bash
POST /environmental/bulk-update
```

**Request**:
```json
[
  {
    "grid_id": 1,
    "rainfall_mm": 25.5,
    "accumulated_1hr": 30.0,
    "traffic_congestion": 0.6
  },
  {
    "grid_id": 2,
    "rainfall_mm": 30.0,
    "accumulated_1hr": 35.0,
    "traffic_congestion": 0.7
  }
]
```

## Configuration

### Environmental Config

```python
from app.services.environmental_engine import EnvironmentalConfig

config = EnvironmentalConfig(
    # Rain module
    max_expected_rainfall=100.0,  # mm/hr
    
    # Drain stress (SCS-CN)
    cn_buildup=92.5,
    cn_residential=80.0,
    cn_vegetation=62.5,
    
    # USPS weights
    weight_rain=0.4,
    weight_drain=0.4,
    weight_traffic=0.2,
    
    # Severity thresholds
    threshold_stable=0.3,
    threshold_watch=0.6,
    threshold_high_alert=0.8
)
```

## Database Schema

### rainfall_log
```sql
CREATE TABLE rainfall_log (
    id SERIAL PRIMARY KEY,
    grid_id INTEGER NOT NULL,
    rainfall_mm FLOAT NOT NULL,
    accumulated_1hr FLOAT NOT NULL,
    rain_index FLOAT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_rainfall_grid_time (grid_id, timestamp)
);
```

### drain_stress_log
```sql
CREATE TABLE drain_stress_log (
    id SERIAL PRIMARY KEY,
    grid_id INTEGER NOT NULL,
    runoff_mm FLOAT NOT NULL,
    drain_stress FLOAT NOT NULL,
    curve_number FLOAT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_drain_grid_time (grid_id, timestamp)
);
```

### traffic_log
```sql
CREATE TABLE traffic_log (
    id SERIAL PRIMARY KEY,
    grid_id INTEGER NOT NULL,
    traffic_index FLOAT NOT NULL,
    congestion_level VARCHAR,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_traffic_grid_time (grid_id, timestamp)
);
```

### usps_log
```sql
CREATE TABLE usps_log (
    id SERIAL PRIMARY KEY,
    grid_id INTEGER NOT NULL,
    rain_index FLOAT NOT NULL,
    drain_stress FLOAT NOT NULL,
    traffic_index FLOAT NOT NULL,
    usps_score FLOAT NOT NULL,
    severity_level VARCHAR NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_usps_grid_time (grid_id, timestamp),
    INDEX idx_usps_severity_time (severity_level, timestamp)
);
```

## Migration

Run database migration:

```bash
python migrate_environmental.py
```

## Testing

Test the environmental engine:

```bash
python test_environmental_engine.py
```

## Design Principles

### 1. Disaster Risk Decomposition
- **Hazard**: Rain + Drain Stress
- **Vulnerability**: Traffic (systemic)
- **Risk**: Composite USPS score

### 2. Transparent Calculations
- All formulas are documented
- No black-box AI
- Audit-ready logs

### 3. Deterministic Modeling
- Same inputs → Same outputs
- No random generation
- Reproducible results

### 4. Multi-Criteria Scoring
- Weighted aggregation
- Configurable weights
- Explainable contributions

## Integration with USPS Dashboard

The environmental engine integrates with the USPS dashboard to provide:
- Real-time USPS scores
- Time-series visualization
- Severity-based alerts
- Grid-level monitoring

## Performance Optimization

### Bulk Operations
- Use `/environmental/bulk-update` for batch processing
- Optimized database inserts
- Transaction management

### Indexing
- Grid ID + Timestamp indexes
- Severity + Timestamp indexes
- Optimized for time-series queries

### Caching
- Latest USPS values cached
- Summary statistics cached
- Configurable TTL

## Monitoring & Logging

All operations are logged with:
- Input parameters
- Computed values
- Timestamps
- Error conditions

Log levels:
- DEBUG: Detailed calculations
- INFO: State changes
- WARNING: Invalid inputs
- ERROR: Computation failures

## Future Enhancements

1. **Real-time Data Integration**
   - OpenWeather API
   - Traffic API (Google/TomTom)
   - IoT sensor networks

2. **Advanced Modeling**
   - Spatial interpolation
   - Temporal forecasting
   - Machine learning calibration

3. **Visualization**
   - Heat maps
   - Time-series charts
   - Alert dashboards

4. **Alerting**
   - Threshold-based alerts
   - SMS/Email notifications
   - WebSocket real-time updates

## References

- SCS-CN Method: USDA Natural Resources Conservation Service
- Disaster Risk Framework: UNDRR
- Urban Hydrology: ASCE Manual of Practice

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2024-01-15
