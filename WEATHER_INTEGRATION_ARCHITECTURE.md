# Weather Integration Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     PUNERAKSHAK SYSTEM                          │
│                  Real-Time Weather Integration                  │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│ Open-Meteo   │  ← Free Weather API (No Key Required)
│   API        │     Location: Pune (18.5204°N, 73.8567°E)
└──────┬───────┘
       │ HTTPS Request
       │ Every 5 minutes
       ↓
┌──────────────────────────────────────────────────────────────┐
│  BACKEND (Python/FastAPI)                                    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  OpenMeteoService                                  │    │
│  │  (app/services/open_meteo_service.py)             │    │
│  │                                                    │    │
│  │  • get_current_weather()                          │    │
│  │  • get_hourly_forecast()                          │    │
│  │  • calculate_flood_risk()                         │    │
│  │  • calculate_heat_risk()                          │    │
│  │  • calculate_storm_risk()                         │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                          │
│  ┌────────────────▼───────────────────────────────────┐    │
│  │  Weather Router                                    │    │
│  │  (app/routers/open_meteo.py)                      │    │
│  │                                                    │    │
│  │  GET /api/weather/current                         │    │
│  │  GET /api/weather/forecast                        │    │
│  │  GET /api/weather/disaster-risk                   │    │
│  │  GET /api/weather/pune-overview                   │    │
│  └────────────────┬───────────────────────────────────┘    │
└───────────────────┼──────────────────────────────────────────┘
                    │ JSON Response
                    │
       ┌────────────┼────────────┬────────────────┐
       │            │            │                │
       ↓            ↓            ↓                ↓
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   Index     │ │ PuneRakshak │ │ AI Forecast │ │    USPS     │
│  Dashboard  │ │  Dashboard  │ │  Dashboard  │ │  Dashboard  │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
       │            │            │                │
       └────────────┴────────────┴────────────────┘
                    │
                    ↓
            ┌───────────────┐
            │  USER BROWSER │
            │               │
            │  • Weather    │
            │  • Risk Badges│
            │  • Auto-refresh│
            └───────────────┘
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA FLOW                                │
└─────────────────────────────────────────────────────────────────┘

1. API REQUEST
   ┌──────────────┐
   │ Open-Meteo   │
   │ API Server   │
   └──────┬───────┘
          │
          │ GET https://api.open-meteo.com/v1/forecast
          │ ?latitude=18.5204&longitude=73.8567
          │ &current=temperature_2m,humidity,precipitation...
          │
          ↓
   ┌──────────────┐
   │ Raw Weather  │
   │    Data      │
   └──────┬───────┘

2. PROCESSING
          │
          ↓
   ┌──────────────────────────────────────┐
   │ OpenMeteoService.get_current_weather()│
   │                                      │
   │ • Parse JSON response                │
   │ • Extract weather parameters         │
   │ • Calculate risk indicators          │
   │   - Flood: rain + humidity           │
   │   - Heat: temperature                │
   │   - Storm: wind + weather code       │
   └──────┬───────────────────────────────┘
          │
          ↓
   ┌──────────────┐
   │ Structured   │
   │ Weather Data │
   └──────┬───────┘

3. API RESPONSE
          │
          ↓
   ┌──────────────────────────────────────┐
   │ /api/weather/disaster-risk           │
   │                                      │
   │ {                                    │
   │   "status": "success",               │
   │   "current_conditions": {            │
   │     "temperature": 22.4,             │
   │     "humidity": 59,                  │
   │     "precipitation": 0.0,            │
   │     "weather": "Partly cloudy"       │
   │   },                                 │
   │   "risk_assessment": {               │
   │     "flood_risk": {                  │
   │       "current": "Low",              │
   │       "forecast_24h": "Low"          │
   │     },                               │
   │     "heat_risk": {...},              │
   │     "storm_risk": {...}              │
   │   }                                  │
   │ }                                    │
   └──────┬───────────────────────────────┘

4. DASHBOARD UPDATE
          │
          ↓
   ┌──────────────────────────────────────┐
   │ JavaScript: loadWeatherData()        │
   │                                      │
   │ • Fetch API data                     │
   │ • Update DOM elements                │
   │ • Apply color coding                 │
   │ • Schedule next refresh (5 min)      │
   └──────┬───────────────────────────────┘
          │
          ↓
   ┌──────────────┐
   │ User sees    │
   │ live weather │
   │ & risk data  │
   └──────────────┘
```

## Component Interaction

```
┌─────────────────────────────────────────────────────────────────┐
│                   COMPONENT INTERACTION                         │
└─────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  FRONTEND (HTML/JavaScript)                                    │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  index.html                                          │    │
│  │                                                      │    │
│  │  <div id="weatherPanel">                            │    │
│  │    <div id="temp">--</div>                          │    │
│  │    <div id="humidity">--</div>                      │    │
│  │    <div id="wind">--</div>                          │    │
│  │    <div id="rain">--</div>                          │    │
│  │  </div>                                             │    │
│  │                                                      │    │
│  │  <div id="riskPanel">                               │    │
│  │    <div id="floodRisk">--</div>                     │    │
│  │    <div id="heatRisk">--</div>                      │    │
│  │    <div id="stormRisk">--</div>                     │    │
│  │  </div>                                             │    │
│  └──────────────────┬───────────────────────────────────┘    │
│                     │                                          │
│  ┌──────────────────▼───────────────────────────────────┐    │
│  │  JavaScript                                          │    │
│  │                                                      │    │
│  │  async function loadWeatherData() {                 │    │
│  │    const response = await fetch(                    │    │
│  │      '/api/weather/disaster-risk'                   │    │
│  │    );                                               │    │
│  │    const data = await response.json();              │    │
│  │                                                      │    │
│  │    // Update UI                                     │    │
│  │    document.getElementById('temp')                  │    │
│  │      .textContent = data.temperature + '°C';        │    │
│  │                                                      │    │
│  │    // Update risk badges                            │    │
│  │    updateRiskBadges(data.risk_assessment);          │    │
│  │  }                                                  │    │
│  │                                                      │    │
│  │  // Auto-refresh every 5 minutes                    │    │
│  │  setInterval(loadWeatherData, 300000);              │    │
│  └──────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────┘
```

## Risk Calculation Logic

```
┌─────────────────────────────────────────────────────────────────┐
│                   RISK CALCULATION FLOW                         │
└─────────────────────────────────────────────────────────────────┘

FLOOD RISK
──────────
Input: precipitation (mm), humidity (%)

┌─────────────────┐
│ precipitation   │
│ > 10mm          │ ──→ HIGH RISK (Red)
└─────────────────┘

┌─────────────────┐
│ humidity        │
│ > 90%           │ ──→ HIGH RISK (Red)
└─────────────────┘

┌─────────────────┐
│ precipitation   │
│ > 5mm           │ ──→ MEDIUM RISK (Yellow)
└─────────────────┘

┌─────────────────┐
│ humidity        │
│ > 80%           │ ──→ MEDIUM RISK (Yellow)
└─────────────────┘

Otherwise ──→ LOW RISK (Green)


HEAT RISK
─────────
Input: temperature (°C)

┌─────────────────┐
│ temperature     │
│ > 40°C          │ ──→ HIGH RISK (Red)
└─────────────────┘

┌─────────────────┐
│ temperature     │
│ > 35°C          │ ──→ MEDIUM RISK (Yellow)
└─────────────────┘

Otherwise ──→ LOW RISK (Green)


STORM RISK
──────────
Input: wind_speed (km/h), weather_code

┌─────────────────┐
│ wind_speed      │
│ > 50 km/h       │ ──→ HIGH RISK (Red)
└─────────────────┘

┌─────────────────┐
│ weather_code    │
│ = 95,96,99      │ ──→ HIGH RISK (Red)
│ (Thunderstorm)  │
└─────────────────┘

┌─────────────────┐
│ wind_speed      │
│ > 30 km/h       │ ──→ MEDIUM RISK (Yellow)
└─────────────────┘

┌─────────────────┐
│ weather_code    │
│ = 80,81,82      │ ──→ MEDIUM RISK (Yellow)
│ (Rain showers)  │
└─────────────────┘

Otherwise ──→ LOW RISK (Green)
```

## Integration Points

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTEGRATION POINTS                           │
└─────────────────────────────────────────────────────────────────┘

1. INDEX DASHBOARD
   ├─ Weather Panel (sidebar)
   │  ├─ Temperature display
   │  ├─ Humidity display
   │  ├─ Wind speed display
   │  └─ Precipitation display
   │
   └─ Risk Assessment Panel
      ├─ Flood risk badge (current)
      ├─ Flood risk badge (24h forecast)
      ├─ Heat risk badge
      └─ Storm risk badge

2. PUNERAKSHAK DASHBOARD
   ├─ Weather Card (sidebar)
   │  ├─ Current conditions grid
   │  └─ Data source indicator
   │
   └─ Risk List
      ├─ Flood risk items
      ├─ Heat risk items
      └─ Storm risk items

3. AI FORECAST DASHBOARD
   ├─ Weather data input for ML model
   ├─ 24-hour predictions
   ├─ Risk evolution chart
   └─ Alert generation

4. USPS DASHBOARD (Optional)
   ├─ Environmental parameters
   ├─ Rainfall integration
   └─ System pressure calculation

5. MONITORING DASHBOARD (Optional)
   ├─ Weather tracking
   ├─ Historical data
   └─ Trend analysis
```

## Auto-Refresh Mechanism

```
┌─────────────────────────────────────────────────────────────────┐
│                   AUTO-REFRESH CYCLE                            │
└─────────────────────────────────────────────────────────────────┘

Time: T=0 (Page Load)
│
├─ loadWeatherData() called
│  ├─ Fetch /api/weather/disaster-risk
│  ├─ Update UI elements
│  └─ Display data
│
├─ setInterval(loadWeatherData, 300000)
│  └─ Schedule next refresh in 5 minutes
│
Time: T=5min
│
├─ loadWeatherData() called automatically
│  ├─ Fetch fresh data
│  ├─ Update UI
│  └─ Display new data
│
├─ Schedule next refresh
│
Time: T=10min
│
├─ loadWeatherData() called automatically
│  └─ ... continues every 5 minutes
│
└─ Continues until page closed
```

## Error Handling

```
┌─────────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING FLOW                          │
└─────────────────────────────────────────────────────────────────┘

API Request
    │
    ├─ Success (200 OK)
    │  └─ Return live data
    │
    ├─ Network Error
    │  └─ Return fallback data
    │     ├─ Temperature: 28°C
    │     ├─ Humidity: 65%
    │     ├─ Wind: 10 km/h
    │     └─ All risks: LOW
    │
    ├─ Timeout
    │  └─ Return fallback data
    │
    └─ API Error (4xx, 5xx)
       └─ Return fallback data

Dashboard Display
    │
    ├─ Data available
    │  └─ Show live values
    │
    └─ Data unavailable
       ├─ Show "--" placeholders
       └─ Display error message
```

## Summary

This architecture provides:
- ✅ Real-time weather data from Open-Meteo
- ✅ Automatic risk calculation
- ✅ Multi-dashboard integration
- ✅ Auto-refresh every 5 minutes
- ✅ Graceful error handling
- ✅ No API key required
- ✅ Production-ready implementation

---

**Last Updated**: February 22, 2026
**Status**: OPERATIONAL ✅
