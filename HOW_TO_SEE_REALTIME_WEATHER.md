# How to See Real-Time Weather Data

## Quick Test Page

I've created a dedicated test page to verify the Open-Meteo integration is working.

### Step 1: Make sure server is running
```bash
python run_local.py
```

### Step 2: Open the test page
```
http://localhost:8000/static/weather_test.html
```

This page will:
- ✅ Automatically test all weather API endpoints
- ✅ Display current weather (temperature, humidity, wind, rain)
- ✅ Show disaster risk levels (flood, heat, storm)
- ✅ Show detailed JSON responses
- ✅ Log all API calls

## Main Dashboard

### Step 3: Open the main dashboard
```
http://localhost:8000/static/index.html
```

Look for:
- **Real-Time Weather panel** (left sidebar)
  - Should show current temperature, humidity, wind, rainfall
- **Risk Assessment panel** (left sidebar)
  - Should show flood/heat/storm risk levels

## Troubleshooting

### If you don't see weather data:

1. **Check browser console** (F12 → Console tab)
   - Look for any error messages
   - Check if API calls are being made

2. **Test API directly**
   ```bash
   # In browser or curl
   http://localhost:8000/api/weather/current
   ```
   Should return JSON with weather data

3. **Check server logs**
   - Look at the terminal where `python run_local.py` is running
   - Should see API requests being logged

4. **Verify internet connection**
   - Open-Meteo requires internet to fetch live data
   - If offline, it will show fallback data

### Common Issues

**Issue**: "Failed to fetch" error
- **Solution**: Make sure server is running on port 8000

**Issue**: Weather shows "--" or old values
- **Solution**: Check browser console for JavaScript errors
- **Solution**: Hard refresh the page (Ctrl+F5)

**Issue**: API returns 404
- **Solution**: Verify Open-Meteo router is registered in app/main.py
- **Solution**: Restart the server

## API Endpoints to Test

You can test these directly in your browser:

1. **Current Weather**
   ```
   http://localhost:8000/api/weather/current
   ```

2. **Disaster Risk**
   ```
   http://localhost:8000/api/weather/disaster-risk
   ```

3. **24-Hour Forecast**
   ```
   http://localhost:8000/api/weather/forecast?hours=24
   ```

4. **Pune Overview**
   ```
   http://localhost:8000/api/weather/pune-overview
   ```

## What You Should See

### Test Page (weather_test.html)
- Green "✓ API Working" status boxes
- Current weather cards with live data
- Risk assessment cards
- JSON response data
- Activity log showing API calls

### Main Dashboard (index.html)
- Temperature: e.g., "22.4°C"
- Humidity: e.g., "59%"
- Wind Speed: e.g., "3.1 km/h"
- Rainfall: e.g., "0.0 mm"
- Risk levels: "Low", "Medium", or "High"

## Expected Data

Based on current Pune weather:
- Temperature: ~20-35°C (varies by time of day)
- Humidity: ~40-80%
- Wind: ~0-20 km/h
- Rainfall: 0 mm (unless raining)
- Flood Risk: Low (unless heavy rain)
- Heat Risk: Low-Medium (depends on temperature)
- Storm Risk: Low (unless stormy)

## Still Not Working?

1. **Run the test script**
   ```bash
   python test_open_meteo.py
   ```
   This will test all endpoints and show detailed results

2. **Check if router is registered**
   ```bash
   # Look for this line in app/main.py
   app.include_router(open_meteo.router)
   ```

3. **Restart server**
   ```bash
   # Stop server (Ctrl+C)
   # Start again
   python run_local.py
   ```

4. **Clear browser cache**
   - Hard refresh: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
   - Or clear cache in browser settings

## Success Indicators

✅ Test page shows green status boxes
✅ Weather values are numbers (not "--" or "undefined")
✅ Risk levels show "Low", "Medium", or "High"
✅ Browser console has no errors
✅ Server logs show API requests
✅ Data updates every 5 minutes

## Need Help?

1. Check browser console (F12)
2. Check server terminal output
3. Run `python test_open_meteo.py`
4. Open test page: http://localhost:8000/static/weather_test.html
5. Test API directly: http://localhost:8000/api/weather/current

---

**Quick Links:**
- Test Page: http://localhost:8000/static/weather_test.html
- Main Dashboard: http://localhost:8000/static/index.html
- API Docs: http://localhost:8000/docs
- Current Weather API: http://localhost:8000/api/weather/current
