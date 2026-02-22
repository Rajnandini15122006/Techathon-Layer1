# Open-Meteo Weather Integration

## Overview

PuneRakshak now integrates with **Open-Meteo**, a free and open-source weather API that requires **NO API KEY**. This provides real-time weather data for disaster risk assessment.

## Why Open-Meteo?

✅ **Completely Free** - No API key required, unlimited requests
✅ **No Registration** - Start using immediately
✅ **High Quality Data** - Uses multiple weather models (NOAA, DWD, MeteoFrance)
✅ **Global Coverage** - Works anywhere in the world
✅ **Real-time Updates** - Hourly weather data
✅ **Comprehensive** - Temperature, precipitation, wind, humidity, and more

## API Endpoints

### 1. Current Weather
```
GET /api/weather/current
```

Get current weather conditions for Pune (or any location).

**Parameters:**
- `latitude` (optional): Location latitude (defaults to Pune: 18.5204)
- `longitude` (optional): Location longitude (defaults to Pune: 73.8567)

**Response:**
```json
{
  "status": "success",
  "data": {
    "timestamp": "2024-01-01T12:00:00+05:30",
    "location": "Lat: 18.5204, Lon: 73.8567",
    "temperature": 28.5,
    "feels_like": 30.2,
    "humidity": 65,
    "precipitation": 0,
    "wind_speed": 10,
    "weather_description": "Partly cloudy",
    "flood_risk_level": "Low",
    "heat_risk_level": "Low",
    "storm_risk_level": "Low",
    "api_status": "live",
    "data_source": "Open-Meteo (Free API)"
  }
}
```

### 2. Hourly Forecast
```
GET /api/weather/forecast?hours=24
```

Get hourly weather forecast (up to 7 days / 168 hours).

**Parameters:**
- `latitude` (optional): Location latitude
- `longitude` (optional): Location longitude
- `hours` (optional): Number of hours to forecast (1-168, default 24)

**Response:**
```json
{
  "status": "success",
  "data": {
    "forecast_hours": 24,
    "hourly_data": [
      {
        "datetime": "2024-01-01T13:00",
        "temperature": 29.0,
        "humidity": 63,
        "precipitation": 0,
        "weather_description": "Clear sky",
        "wind_speed": 12
      }
    ],
    "summary": {
      "total_precipitation_mm": 5.2,
      "max_temperature": 32.5,
      "max_wind_speed": 18.0,
      "flood_risk": "Low",
      "heat_risk": "Medium",
      "storm_risk": "Low"
    }
  }
}
```

### 3. Disaster Risk Assessment
```
GET /api/weather/disaster-risk
```

Get comprehensive disaster risk assessment combining current conditions and 24-hour forecast.

**Response:**
```json
{
  "status": "success",
  "current_conditions": {
    "temperature": 28.5,
    "precipitation": 0,
    "wind_speed": 10,
    "humidity": 65,
    "weather": "Partly cloudy"
  },
  "risk_assessment": {
    "flood_risk": {
      "current": "Low",
      "forecast_24h": "Medium",
      "total_rain_24h": 15.5
    },
    "heat_risk": {
      "current": "Low",
      "forecast_24h": "High",
      "max_temp_24h": 41.2
    },
    "storm_risk": {
      "current": "Low",
      "forecast_24h": "Medium",
      "max_wind_24h": 35.0
    }
  }
}
```

### 4. Pune Weather Overview
```
GET /api/weather/pune-overview
```

Get comprehensive weather overview for Pune including current conditions, 48-hour forecast, and disaster risks.

## Integration with USPS Dashboard

The Open-Meteo API can be integrated with the USPS Environmental Engine to use real-time weather data instead of manual sliders.

### Example Integration:

```python
from app.services.open_meteo_service import get_open_meteo_service

# Get real-time weather
weather_service = get_open_meteo_service()
current_weather = weather_service.get_current_weather(lat, lon)

# Use in Environmental Engine
rainfall_mm = current_weather["precipitation"]
humidity = current_weather["humidity"]
wind_speed = current_weather["wind_speed"]

# Calculate USPS with real data
env_state = env_engine.compute_environmental_state(
    rainfall_mm=rainfall_mm,
    accumulated_1hr=rainfall_mm,  # Use current as proxy
    land_use=land_use,
    grid_area_m2=62500.0,
    drain_capacity_m3=drain_capacity,
    traffic_congestion=traffic_level
)
```

## Testing

Run the test script to verify the integration:

```bash
# Start the server
python run_local.py

# In another terminal, run tests
python test_open_meteo.py
```

## Available Weather Data

Open-Meteo provides:

- **Temperature**: Current, feels-like, min/max
- **Precipitation**: Rain, showers, snowfall
- **Wind**: Speed, direction, gusts
- **Humidity**: Relative humidity
- **Pressure**: Sea level pressure
- **Cloud Cover**: Total, low, mid, high
- **Weather Codes**: WMO standard codes
- **Visibility**: Viewing distance
- **Soil Data**: Temperature and moisture at various depths

## Risk Level Calculations

### Flood Risk
- **High**: Precipitation > 10mm/hr OR Humidity > 90%
- **Medium**: Precipitation > 5mm/hr OR Humidity > 80%
- **Low**: Below medium thresholds

### Heat Risk
- **High**: Temperature > 40°C
- **Medium**: Temperature > 35°C
- **Low**: Below medium thresholds

### Storm Risk
- **High**: Wind > 50 km/h OR Thunderstorm conditions
- **Medium**: Wind > 30 km/h OR Heavy rain
- **Low**: Below medium thresholds

## API Documentation

Full API documentation available at:
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Open-Meteo Documentation

For more details about Open-Meteo:
- **Website**: https://open-meteo.com
- **API Docs**: https://open-meteo.com/en/docs
- **GitHub**: https://github.com/open-meteo/open-meteo

## Next Steps

1. **Real-time USPS**: Integrate Open-Meteo with USPS dashboard for live weather data
2. **Grid Weather**: Fetch weather for each grid cell (spatial variation)
3. **Alerts**: Create automatic alerts based on weather thresholds
4. **Historical Data**: Use Open-Meteo's historical API for trend analysis
5. **Forecasting**: Use 7-day forecasts for proactive disaster planning

## Advantages Over OpenWeatherMap

| Feature | Open-Meteo | OpenWeatherMap |
|---------|-----------|----------------|
| API Key | ❌ Not required | ✅ Required |
| Free Tier | ♾️ Unlimited | 1000 calls/day |
| Registration | ❌ Not required | ✅ Required |
| Data Quality | ⭐⭐⭐⭐⭐ Multiple models | ⭐⭐⭐⭐ Single model |
| Forecast Length | 7 days | 5 days (free) |
| Historical Data | ✅ Available | ❌ Paid only |

## Example Use Cases

### 1. Real-time Dashboard
Display current weather conditions on the main dashboard.

### 2. Automated Alerts
Trigger alerts when weather conditions indicate high disaster risk.

### 3. Predictive Analysis
Use forecast data to predict flood/heat/storm risks 24-48 hours in advance.

### 4. Grid-Level Weather
Fetch weather for each grid cell to create accurate spatial risk maps.

### 5. Historical Analysis
Analyze past weather patterns to improve risk models.

## Support

For issues or questions:
1. Check Open-Meteo documentation: https://open-meteo.com/en/docs
2. Review API response in browser: https://api.open-meteo.com/v1/forecast?latitude=18.5204&longitude=73.8567&current=temperature_2m,precipitation
3. Test endpoints using the interactive docs: http://localhost:8000/docs

---

**Status**: ✅ Fully Integrated and Tested
**API Key Required**: ❌ No
**Cost**: 💰 Free Forever
