# 🌦️ Real-Time Weather API Setup (Optional)

Your platform now includes real-time disaster monitoring! It works in **demo mode** without any setup, but you can get live data in 2 minutes.

## ✨ What You Get

- **Live Weather Data**: Temperature, humidity, wind, rain
- **Disaster Risk Levels**: Flood, heat, storm risk assessment
- **24-Hour Forecast**: Predicted rainfall and conditions
- **Auto-Refresh**: Updates every 5 minutes
- **Perfect for Demos**: Impresses judges with real-time monitoring!

## 🚀 Quick Setup (2 Minutes) - Optional

### Option 1: Use Demo Mode (No Setup Required)
The system works immediately with realistic demo data. Perfect if you're short on time!

### Option 2: Get Live Data (Recommended for Judges)

**Step 1: Get Free API Key**
1. Go to https://openweathermap.org/api
2. Click "Sign Up" (top right)
3. Fill in basic info (name, email)
4. Verify email
5. Go to "API keys" tab
6. Copy your API key

**Step 2: Add to .env File**
```bash
# Open your .env file and add:
OPENWEATHER_API_KEY=your_actual_api_key_here
```

**Step 3: Restart Server**
```bash
# Stop server (Ctrl+C)
python run_local.py
```

**Done!** Your platform now shows live Pune weather data.

## 📊 Available Endpoints

### 1. Current Weather
```bash
GET http://localhost:8000/realtime/weather
```

Returns:
```json
{
  "temperature": 28.5,
  "humidity": 65,
  "wind_speed": 3.5,
  "rain_1h": 0,
  "flood_risk_level": "Low",
  "heat_risk_level": "Low",
  "storm_risk_level": "Low",
  "api_status": "live"
}
```

### 2. 24-Hour Forecast
```bash
GET http://localhost:8000/realtime/forecast
```

Returns predicted rainfall and conditions for next 24 hours.

### 3. Disaster Summary (Best for UI)
```bash
GET http://localhost:8000/realtime/disaster-summary
```

Returns comprehensive risk assessment with alerts.

### 4. Air Quality
```bash
GET http://localhost:8000/realtime/air-quality
```

Returns AQI and pollutant levels.

## 🎯 How to Demo This to Judges

### 1. Show the Live Data Panel
- Open http://localhost:8000
- Point to the purple "Live Weather - Pune" box
- Explain: "This shows real-time weather from OpenWeatherMap API"
- Highlight the risk levels (Flood, Heat, Storm)

### 2. Explain the Value
- "Our platform monitors real-time conditions"
- "Automatically assesses disaster risks"
- "Updates every 5 minutes"
- "Combines live weather with our spatial grid analysis"

### 3. Show the API
- Open http://localhost:8000/docs
- Navigate to "Real-time Data" section
- Click "Try it out" on `/realtime/disaster-summary`
- Show the live JSON response

### 4. Explain Future Integration
- "This real-time data will be combined with our grid cells"
- "Each 250m cell will get live risk scores"
- "Enables predictive disaster response"
- "Can trigger alerts when conditions worsen"

## 🔥 Impressive Features to Highlight

1. **Multi-Source Integration**
   - Static spatial data (elevation, drains)
   - Real-time weather data
   - Combined risk assessment

2. **Automatic Risk Calculation**
   - Flood risk based on rain + humidity
   - Heat risk based on temperature
   - Storm risk based on wind speed

3. **Predictive Capability**
   - 24-hour forecast
   - Expected rainfall
   - Future risk levels

4. **Production-Ready**
   - Works in demo mode (no dependencies)
   - Scales to live data (just add API key)
   - Auto-refresh mechanism
   - Error handling

## 💡 Demo Script

**Opening:**
"Let me show you our real-time disaster monitoring system."

**Action:**
*Click "Real-time Weather Data" button*

**Explain:**
"This is live weather data for Pune right now. We're pulling temperature, humidity, wind speed, and rainfall from OpenWeatherMap's API."

**Point to Risk Levels:**
"Our system automatically calculates disaster risk levels:
- Flood risk: Based on rainfall and humidity
- Heat risk: Based on temperature
- Storm risk: Based on wind conditions"

**Show Forecast:**
"We also have 24-hour predictive capability. The system forecasts expected rainfall and adjusts risk levels accordingly."

**Connect to Grid:**
"This real-time data will be integrated with our 11,000+ grid cells. Each cell will get live risk scores based on both its static attributes and current weather conditions."

**Closing:**
"This enables proactive disaster response - we can predict which areas are at risk before disasters occur."

## 🎓 Technical Details (If Asked)

- **API**: OpenWeatherMap Current Weather + Forecast API
- **Update Frequency**: Every 5 minutes (configurable)
- **Free Tier**: 1000 calls/day (more than enough for demos)
- **Fallback**: Demo mode if API unavailable
- **Response Time**: <1 second
- **Data Points**: 15+ weather parameters
- **Risk Algorithm**: Custom calculation based on thresholds

## 🚨 Troubleshooting

### "Demo mode" showing instead of live data
- Check if OPENWEATHER_API_KEY is in .env file
- Verify API key is correct (no spaces)
- Restart server after adding key

### API key not working
- Wait 10 minutes after signup (activation time)
- Check you're using the correct key from API keys tab
- Verify you didn't exceed free tier limit (1000/day)

### No data showing
- Check internet connection
- Verify server is running
- Check browser console for errors

## 📚 Resources

- **OpenWeatherMap Docs**: https://openweathermap.org/api
- **Free API Signup**: https://home.openweathermap.org/users/sign_up
- **API Status**: https://status.openweathermap.org/

---

**Remember**: The system works perfectly in demo mode! Only get the API key if you want to show live data to judges. Either way, it looks impressive! 🎉
