"""
Open-Meteo Weather API Router
Real-time weather data integration - NO API KEY REQUIRED
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.open_meteo_service import get_open_meteo_service

router = APIRouter(prefix="/api/weather", tags=["weather"])
weather_service = get_open_meteo_service()


@router.get("/current")
async def get_current_weather(
    latitude: Optional[float] = Query(None, description="Latitude (defaults to Pune)"),
    longitude: Optional[float] = Query(None, description="Longitude (defaults to Pune)")
):
    """
    Get current weather conditions
    
    Uses Open-Meteo API - completely free, no API key required
    """
    try:
        weather_data = weather_service.get_current_weather(latitude, longitude)
        return {
            "status": "success",
            "data": weather_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast")
async def get_hourly_forecast(
    latitude: Optional[float] = Query(None, description="Latitude (defaults to Pune)"),
    longitude: Optional[float] = Query(None, description="Longitude (defaults to Pune)"),
    hours: int = Query(24, description="Number of hours to forecast", ge=1, le=168)
):
    """
    Get hourly weather forecast
    
    Args:
        hours: Number of hours (1-168, default 24)
    """
    try:
        forecast_data = weather_service.get_hourly_forecast(latitude, longitude, hours)
        return {
            "status": "success",
            "data": forecast_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/disaster-risk")
async def get_disaster_risk_assessment(
    latitude: Optional[float] = Query(None, description="Latitude (defaults to Pune)"),
    longitude: Optional[float] = Query(None, description="Longitude (defaults to Pune)")
):
    """
    Get disaster risk assessment based on current weather
    
    Returns flood, heat, and storm risk levels
    """
    try:
        current = weather_service.get_current_weather(latitude, longitude)
        forecast = weather_service.get_hourly_forecast(latitude, longitude, 24)
        
        return {
            "status": "success",
            "location": current["location"],
            "timestamp": current["timestamp"],
            "current_conditions": {
                "temperature": current["temperature"],
                "precipitation": current["precipitation"],
                "wind_speed": current["wind_speed"],
                "humidity": current["humidity"],
                "weather": current["weather_description"]
            },
            "risk_assessment": {
                "flood_risk": {
                    "current": current["flood_risk_level"],
                    "forecast_24h": forecast["summary"]["flood_risk"],
                    "total_rain_24h": forecast["summary"]["total_precipitation_mm"]
                },
                "heat_risk": {
                    "current": current["heat_risk_level"],
                    "forecast_24h": forecast["summary"]["heat_risk"],
                    "max_temp_24h": forecast["summary"]["max_temperature"]
                },
                "storm_risk": {
                    "current": current["storm_risk_level"],
                    "forecast_24h": forecast["summary"]["storm_risk"],
                    "max_wind_24h": forecast["summary"]["max_wind_speed"]
                }
            },
            "data_source": "Open-Meteo (Free API)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pune-overview")
async def get_pune_weather_overview():
    """
    Get comprehensive weather overview for Pune
    
    Includes current conditions, forecast, and disaster risk assessment
    """
    try:
        current = weather_service.get_current_weather()
        forecast = weather_service.get_hourly_forecast(hours=48)
        
        return {
            "status": "success",
            "city": "Pune, India",
            "timestamp": current["timestamp"],
            "current": {
                "temperature": current["temperature"],
                "feels_like": current["feels_like"],
                "humidity": current["humidity"],
                "precipitation": current["precipitation"],
                "wind_speed": current["wind_speed"],
                "weather": current["weather_description"],
                "pressure": current["pressure"]
            },
            "forecast_48h": {
                "total_rain": forecast["summary"]["total_precipitation_mm"],
                "max_temperature": forecast["summary"]["max_temperature"],
                "max_wind": forecast["summary"]["max_wind_speed"]
            },
            "disaster_risks": {
                "flood": {
                    "current": current["flood_risk_level"],
                    "forecast": forecast["summary"]["flood_risk"]
                },
                "heat": {
                    "current": current["heat_risk_level"],
                    "forecast": forecast["summary"]["heat_risk"]
                },
                "storm": {
                    "current": current["storm_risk_level"],
                    "forecast": forecast["summary"]["storm_risk"]
                }
            },
            "hourly_forecast": forecast["hourly_data"][:12],  # Next 12 hours
            "data_source": "Open-Meteo (Free API)",
            "api_info": "No API key required - completely free"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
