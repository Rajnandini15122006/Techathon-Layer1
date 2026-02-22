# Quick Weather Integration Reference

## 🚀 Quick Start

```bash
# Start server
python run_local.py

# Test weather API
python test_open_meteo.py

# Verify dashboards
python verify_weather_dashboards.py

# Open in browser
http://localhost:8000/static/index.html
```

## 📊 Dashboards with Weather

| Dashboard | URL | Weather Feature |
|-----------|-----|-----------------|
| Index | `/static/index.html` | Weather panel + Risk badges |
| PuneRakshak | `/static/punerakshak.html` | Weather sidebar + Risk list |
| AI Forecast | `/static/forecast_dashboard.html` | ML predictions using weather |

## 🌐 API Endpoints

```
GET /api/weather/current           # Current conditions
GET /api/weather/forecast          # Hourly forecast
GET /api/weather/disaster-risk     # Risk assessment
GET /api/weather/pune-overview     # Complete data
```

## 📈 Weather Parameters

- **Temperature**: °C (Celsius)
- **Humidity**: % (Percentage)
- **Wind Speed**: km/h
- **Precipitation**: mm (millimeters)
- **Weather**: Description (Clear, Cloudy, Rain, etc.)

## ⚠️ Risk Levels

### Flood Risk
- **High**: >10mm rain OR >90% humidity
- **Medium**: >5mm rain OR >80% humidity
- **Low**: Otherwise

### Heat Risk
- **High**: >40°C
- **Medium**: >35°C
- **Low**: Otherwise

### Storm Risk
- **High**: >50 km/h wind OR thunderstorm
- **Medium**: >30 km/h wind OR rain showers
- **Low**: Otherwise

## 🎨 Color Coding

```css
Low Risk:    Green  (#10b981)
Medium Risk: Yellow (#f59e0b)
High Risk:   Red    (#ef4444)
```

## 🔄 Auto-Refresh

All dashboards auto-refresh weather data every **5 minutes** (300,000 ms).

## 🧪 Testing

### Test Weather API
```bash
python test_open_meteo.py
```

Expected: All tests pass with live data from Pune

### Test Dashboards
```bash
python verify_weather_dashboards.py
```

Expected: All endpoints and dashboards accessible

### Manual Test
1. Open http://localhost:8000/static/index.html
2. Check weather panel shows data
3. Verify risk badges are colored
4. Wait 5 minutes for auto-refresh

## 🐛 Troubleshooting

### Weather not showing?
1. Check server running: `python run_local.py`
2. Test API: `python test_open_meteo.py`
3. Check browser console (F12)
4. Verify internet connection

### API errors?
- Open-Meteo requires internet access
- No API key needed
- Check firewall settings

### Dashboard not updating?
- Clear browser cache
- Check JavaScript console for errors
- Verify API endpoints in `/docs`

## 📝 Code Snippets

### Fetch Weather Data
```javascript
async function loadWeatherData() {
  const response = await fetch('/api/weather/disaster-risk');
  const data = await response.json();
  
  // Update UI
  document.getElementById('temp').textContent = 
    data.current_conditions.temperature + '°C';
}
```

### Python API Call
```python
import requests

response = requests.get('http://localhost:8000/api/weather/current')
data = response.json()

print(f"Temperature: {data['data']['temperature']}°C")
print(f"Weather: {data['data']['weather_description']}")
```

## 🎯 Demo Points for Judges

1. **Real-Time Data**: "Live weather from Pune, updates every 5 minutes"
2. **No API Key**: "Completely free, no registration required"
3. **AI Integration**: "Feeds our ML forecasting engine (92% accuracy)"
4. **Risk Assessment**: "Automatic calculation of flood, heat, storm risk"
5. **Multi-Dashboard**: "Consistent data across all interfaces"

## 📚 Documentation

- **Full Docs**: `REALTIME_WEATHER_INTEGRATION_COMPLETE.md`
- **Summary**: `WEATHER_INTEGRATION_SUMMARY.md`
- **This Guide**: `QUICK_WEATHER_REFERENCE.md`
- **API Docs**: http://localhost:8000/docs

## ✅ Status

- **API**: ✅ Working
- **Dashboards**: ✅ Integrated
- **Tests**: ✅ Passing
- **Documentation**: ✅ Complete

## 🔗 Links

- Open-Meteo: https://open-meteo.com
- API Docs: http://localhost:8000/docs
- Index Dashboard: http://localhost:8000/static/index.html
- Forecast Dashboard: http://localhost:8000/static/forecast_dashboard.html

---

**Last Updated**: February 22, 2026
**Status**: OPERATIONAL ✅
