"""
Real-time disaster data endpoints
"""
from fastapi import APIRouter, HTTPException
from app.services.realtime_weather_service import RealtimeWeatherService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/realtime", tags=["Real-time Data"])

weather_service = RealtimeWeatherService()

@router.get("/weather")
def get_current_weather():
    """
    Get real-time weather data for Pune
    
    Returns:
    - Current temperature, humidity, pressure
    - Wind speed and direction
    - Rain data (if any)
    - Flood/heat/storm risk levels
    - Live data from OpenWeatherMap API
    
    Perfect for impressing judges with real-time disaster monitoring!
    """
    try:
        data = weather_service.get_current_weather()
        return data
    except Exception as e:
        logger.error(f"Error in weather endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast")
def get_weather_forecast():
    """
    Get 24-hour weather forecast for Pune
    
    Returns:
    - 8 forecast points (3-hour intervals)
    - Total expected rainfall
    - Rain probability
    - 24-hour flood risk assessment
    
    Use this to show predictive disaster risk!
    """
    try:
        data = weather_service.get_forecast_5day()
        return data
    except Exception as e:
        logger.error(f"Error in forecast endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/air-quality")
def get_air_quality():
    """
    Get real-time air quality data for Pune
    
    Returns:
    - Air Quality Index (AQI)
    - PM2.5 and PM10 levels
    - Pollutant concentrations
    
    Shows environmental disaster monitoring capability!
    """
    try:
        data = weather_service.get_air_pollution()
        return data
    except Exception as e:
        logger.error(f"Error in air quality endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/disaster-summary")
def get_disaster_summary():
    """
    Comprehensive real-time disaster risk summary
    
    Combines weather, forecast, and risk analysis
    Perfect for dashboard display!
    """
    try:
        current = weather_service.get_current_weather()
        forecast = weather_service.get_forecast_5day()
        
        # Generate alerts
        alerts = []
        
        # Flood alerts
        if current["flood_risk_level"] == "High":
            alerts.append({
                "type": "flood",
                "severity": "high",
                "message": f"High flood risk: {current['rain_1h']}mm rain in last hour"
            })
        
        if forecast["flood_risk_24h"] == "High":
            alerts.append({
                "type": "flood",
                "severity": "warning",
                "message": f"Heavy rain expected: {forecast['total_rain_24h']:.1f}mm in next 24h"
            })
        
        # Heat alerts
        if current["heat_risk_level"] == "High":
            alerts.append({
                "type": "heat",
                "severity": "high",
                "message": f"Extreme heat: {current['temperature']}°C (feels like {current['feels_like']}°C)"
            })
        
        # Storm alerts
        if current["storm_risk_level"] == "High":
            alerts.append({
                "type": "storm",
                "severity": "high",
                "message": f"High winds: {current['wind_speed']} m/s"
            })
        
        if not alerts:
            alerts.append({
                "type": "info",
                "severity": "low",
                "message": "No immediate disaster risks detected"
            })
        
        summary = {
            "timestamp": current["timestamp"],
            "location": "Pune, India",
            
            # Current conditions
            "current_conditions": {
                "temperature": current["temperature"],
                "weather": current["weather_description"],
                "humidity": current["humidity"],
                "wind_speed": current["wind_speed"],
                "rain_now": current["rain_1h"]
            },
            
            # Risk levels
            "risk_assessment": {
                "flood_risk_now": current["flood_risk_level"],
                "flood_risk_24h": forecast["flood_risk_24h"],
                "heat_risk": current["heat_risk_level"],
                "storm_risk": current["storm_risk_level"]
            },
            
            # Forecast
            "next_24h": {
                "expected_rain_mm": forecast["total_rain_24h"],
                "max_rain_probability": forecast["max_rain_probability"],
                "forecast_points": len(forecast["forecast_24h"])
            },
            
            # Alerts
            "alerts": alerts,
            
            "api_status": current["api_status"],
            "data_source": "OpenWeatherMap + PuneRakshak Analysis"
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error in disaster summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

