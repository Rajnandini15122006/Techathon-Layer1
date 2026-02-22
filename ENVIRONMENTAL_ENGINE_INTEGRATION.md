# Environmental Engine Integration Guide

## ✅ Setup Complete!

Your Environmental Engine is now fully integrated and tested. Here's how to use it:

## Step-by-Step Usage

### 1. Start the Server

```bash
python run_local.py
```

The server will start at `http://localhost:8000`

### 2. Populate Test Data

```bash
python populate_environmental_data.py
```

This will:
- Fetch grid cells from the database
- Generate realistic environmental data
- Compute USPS scores using the Environmental Engine
- Store time-series data in the database

### 3. Access the Dashboards

#### Main Dashboard
```
http://localhost:8000/static/index.html
```

#### USPS Dashboard
```
http://localhost:8000/static/usps_dashboard.html
```

#### API Documentation
```
http://localhost:8000/docs
```

## API Endpoints Available

### 1. Update Environmental State (Single Grid)

```bash
POST http://localhost:8000/environmental/update
```

**Example Request:**
```json
{
  "grid_id": 1,
  "rainfall_mm": 45.5,
  "accumulated_1hr": 50.0,
  "traffic_congestion": 0.6
}
```

**Example Response:**
```json
{
  "grid_id": 1,
  "rain": {
    "rainfall_mm": 45.5,
    "rain_index": 0.455
  },
  "drain": {
    "runoff_mm": 48.2,
    "drain_stress": 0.85
  },
  "traffic": {
    "traffic_index": 0.6
  },
  "usps": {
    "usps_score": 0.635,
    "severity_level": "High Alert"
  }
}
```

### 2. Get Latest USPS Score

```bash
GET http://localhost:8000/environmental/usps/1
```

### 3. Get All Latest USPS Scores

```bash
GET http://localhost:8000/environmental/latest?limit=100
```

Filter by severity:
```bash
GET http://localhost:8000/environmental/latest?severity=Critical
```

### 4. Get Time-Series History

```bash
GET http://localhost:8000/environmental/history/1?hours=24
```

### 5. Get System Summary

```bash
GET http://localhost:8000/environmental/summary
```

**Example Response:**
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
  "stable_grids": 180
}
```

### 6. Bulk Update (Batch Processing)

```bash
POST http://localhost:8000/environmental/bulk-update
```

**Example Request:**
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

## Testing with cURL

### Update Environmental State
```bash
curl -X POST "http://localhost:8000/environmental/update" \
  -H "Content-Type: application/json" \
  -d '{
    "grid_id": 1,
    "rainfall_mm": 45.5,
    "accumulated_1hr": 50.0,
    "traffic_congestion": 0.6
  }'
```

### Get Latest USPS
```bash
curl "http://localhost:8000/environmental/usps/1"
```

### Get Summary
```bash
curl "http://localhost:8000/environmental/summary"
```

## Testing with Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Update environmental state
response = requests.post(
    f"{BASE_URL}/environmental/update",
    json={
        "grid_id": 1,
        "rainfall_mm": 45.5,
        "accumulated_1hr": 50.0,
        "traffic_congestion": 0.6
    }
)
print(response.json())

# Get latest USPS
response = requests.get(f"{BASE_URL}/environmental/usps/1")
print(response.json())

# Get summary
response = requests.get(f"{BASE_URL}/environmental/summary")
print(response.json())
```

## Integration with USPS Dashboard

The USPS Dashboard can now fetch real-time environmental data:

### JavaScript Integration

```javascript
// Fetch latest USPS scores
async function fetchUSPSData() {
  const response = await fetch('/environmental/latest?limit=100');
  const data = await response.json();
  
  // Update map with USPS scores
  data.forEach(cell => {
    updateGridCell(cell.grid_id, {
      usps_score: cell.usps_score,
      severity: cell.severity_level,
      rain_index: cell.rain_index,
      drain_stress: cell.drain_stress,
      traffic_index: cell.traffic_index
    });
  });
}

// Fetch system summary
async function fetchSummary() {
  const response = await fetch('/environmental/summary');
  const summary = await response.json();
  
  // Update dashboard statistics
  document.getElementById('total-grids').textContent = summary.total_grids;
  document.getElementById('avg-usps').textContent = summary.average_usps.toFixed(3);
  document.getElementById('critical-count').textContent = summary.critical_grids;
}

// Auto-refresh every 30 seconds
setInterval(fetchUSPSData, 30000);
setInterval(fetchSummary, 30000);
```

## Understanding USPS Scores

### Score Ranges
- **0.0 - 0.3**: Stable (Green)
- **0.3 - 0.6**: Watch (Yellow)
- **0.6 - 0.8**: High Alert (Orange)
- **0.8 - 1.0**: Critical (Red)

### Components
USPS is computed from three weighted components:

1. **Rain Index (40%)**: Normalized rainfall intensity
   - Measures primary hazard trigger
   - Based on current and accumulated rainfall

2. **Drain Stress (40%)**: SCS-CN runoff vs drain capacity
   - Measures hazard amplification
   - Uses hydrological modeling (SCS-CN method)
   - Accounts for land use and drainage infrastructure

3. **Traffic Index (20%)**: Congestion level
   - Measures systemic vulnerability
   - Indicates evacuation/response capacity

### Formula
```
USPS = 0.4 × RainIndex + 0.4 × DrainStress + 0.2 × TrafficIndex
```

## Real-Time Data Sources

### Current Implementation
- Synthetic data for testing
- Manual API updates
- Batch processing support

### Future Integration
1. **Weather APIs**
   - OpenWeather API
   - IMD (India Meteorological Department)
   - Local weather stations

2. **Traffic APIs**
   - Google Maps Traffic API
   - TomTom Traffic API
   - Local traffic sensors

3. **IoT Sensors**
   - Rain gauges
   - Water level sensors
   - Traffic cameras

## Monitoring & Alerts

### Database Queries

Check recent critical alerts:
```sql
SELECT grid_id, usps_score, severity_level, timestamp
FROM usps_log
WHERE severity_level = 'Critical'
  AND timestamp > NOW() - INTERVAL '1 hour'
ORDER BY usps_score DESC;
```

Get time-series for a grid:
```sql
SELECT timestamp, usps_score, rain_index, drain_stress, traffic_index
FROM usps_log
WHERE grid_id = 1
  AND timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp;
```

### Alert Thresholds

Configure alerts based on:
- USPS score exceeds 0.8 (Critical)
- Rapid USPS increase (>0.3 in 1 hour)
- Multiple grids in High Alert
- Sustained elevated USPS (>0.6 for 2+ hours)

## Performance Optimization

### Bulk Updates
Use `/environmental/bulk-update` for batch processing:
- Processes multiple grids in single transaction
- Optimized database inserts
- Reduced API overhead

### Caching
- Latest USPS values cached in memory
- Summary statistics cached (5-minute TTL)
- Time-series queries optimized with indexes

### Database Indexes
All tables have composite indexes:
- `(grid_id, timestamp)` for time-series queries
- `(severity_level, timestamp)` for alert queries
- `usps_score` for ranking queries

## Troubleshooting

### Server Not Starting
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <process_id> /F

# Restart server
python run_local.py
```

### Database Connection Issues
```bash
# Check database connection in .env file
# Verify DATABASE_URL is correct

# Run migration again
python migrate_environmental.py
```

### No Data in Dashboard
```bash
# Populate test data
python populate_environmental_data.py

# Verify data exists
curl http://localhost:8000/environmental/summary
```

## Next Steps

### 1. Integrate with USPS Dashboard UI
- Update `app/static/usps_dashboard.html`
- Add real-time data fetching
- Display USPS scores on map
- Show time-series charts

### 2. Add Real-Time Updates
- WebSocket support for live updates
- Auto-refresh dashboard
- Push notifications for critical alerts

### 3. Advanced Analytics
- Trend analysis
- Predictive modeling
- Spatial interpolation
- Risk forecasting

### 4. Alert System
- Email/SMS notifications
- Webhook integrations
- Escalation policies
- Alert history

## Documentation

- **API Docs**: http://localhost:8000/docs
- **Engine Details**: LAYER2_ENVIRONMENTAL_ENGINE.md
- **Test Results**: Run `python test_environmental_engine.py`

## Support

For issues or questions:
1. Check API documentation at `/docs`
2. Review test results
3. Check server logs
4. Verify database connection

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2024-01-15
