"""
Real-time weather and disaster data service using OpenWeatherMap API
Free tier: 1000 calls/day - perfect for demos
"""
import os
import logging
import requests
from typing import Dict, Optional, List
from datetime import datetime
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class RealtimeWeatherService:
    """
    Fetches real-time weather data for Pune grid cells
    Uses OpenWeatherMap API (free tier)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY", "demo")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        # Pune coordinates
        self.pune_lat = 18.5204
        self.pune_lon = 73.8567
    
    def get_current_weather(self) -> Dict:
        """
        Get current weather for Pune
        Returns real-time temperature, humidity, pressure, wind, rain
        """
        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": self.pune_lat,
                "lon": self.pune_lon,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract disaster-relevant data
                weather_data = {
                    "timestamp": datetime.now().isoformat(),
                    "location": "Pune, India",
                    "temperature": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "wind_speed": data["wind"]["speed"],
                    "wind_direction": data["wind"].get("deg", 0),
                    "clouds": data["clouds"]["all"],
                    "visibility": data.get("visibility", 10000),
                    "weather_condition": data["weather"][0]["main"],
                    "weather_description": data["weather"][0]["description"],
                    "rain_1h": data.get("rain", {}).get("1h", 0),
                    "rain_3h": data.get("rain", {}).get("3h", 0),
                    
                    # Disaster risk indicators
                    "flood_risk_level": self._calculate_flood_risk(data),
                    "heat_risk_level": self._calculate_heat_risk(data),
                    "storm_risk_level": self._calculate_storm_risk(data),
                    
                    "api_status": "live",
                    "data_source": "OpenWeatherMap"
                }
                
                logger.info(f"✓ Real-time weather data fetched: {weather_data['temperature']}°C, {weather_data['weather_condition']}")
                return weather_data
            else:
                logger.warning(f"Weather API returned status {response.status_code}")
                return self._get_demo_data()
                
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return self._get_demo_data()
    
    def get_forecast_5day(self) -> Dict:
        """
        Get 5-day weather forecast for Pune
        Useful for predicting flood/storm risks
        """
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "lat": self.pune_lat,
                "lon": self.pune_lon,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Process forecast data
                forecast_list = []
                for item in data["list"][:8]:  # Next 24 hours (3-hour intervals)
                    forecast_list.append({
                        "datetime": item["dt_txt"],
                        "temperature": item["main"]["temp"],
                        "humidity": item["main"]["humidity"],
                        "rain_probability": item.get("pop", 0) * 100,
                        "rain_volume": item.get("rain", {}).get("3h", 0),
                        "weather": item["weather"][0]["main"],
                        "description": item["weather"][0]["description"]
                    })
                
                # Calculate aggregate risk
                total_rain = sum(f["rain_volume"] for f in forecast_list)
                max_rain_prob = max(f["rain_probability"] for f in forecast_list)
                
                forecast_data = {
                    "timestamp": datetime.now().isoformat(),
                    "location": "Pune, India",
                    "forecast_24h": forecast_list,
                    "total_rain_24h": total_rain,
                    "max_rain_probability": max_rain_prob,
                    "flood_risk_24h": "High" if total_rain > 50 else "Medium" if total_rain > 20 else "Low",
                    "api_status": "live",
                    "data_source": "OpenWeatherMap"
                }
                
                logger.info(f"✓ 24h forecast: {total_rain:.1f}mm rain expected")
                return forecast_data
            else:
                return self._get_demo_forecast()
                
        except Exception as e:
            logger.error(f"Error fetching forecast: {e}")
            return self._get_demo_forecast()
    
    def get_air_pollution(self) -> Dict:
        """
        Get real-time air quality data for Pune
        """
        try:
            url = f"{self.base_url}/air_pollution"
            params = {
                "lat": self.pune_lat,
                "lon": self.pune_lon,
                "appid": self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                aqi_data = data["list"][0]
                
                aqi_levels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
                
                return {
                    "timestamp": datetime.now().isoformat(),
                    "location": "Pune, India",
                    "aqi": aqi_data["main"]["aqi"],
                    "aqi_level": aqi_levels.get(aqi_data["main"]["aqi"], "Unknown"),
                    "pm2_5": aqi_data["components"]["pm2_5"],
                    "pm10": aqi_data["components"]["pm10"],
                    "co": aqi_data["components"]["co"],
                    "no2": aqi_data["components"]["no2"],
                    "o3": aqi_data["components"]["o3"],
                    "api_status": "live",
                    "data_source": "OpenWeatherMap"
                }
            else:
                return {"api_status": "unavailable", "message": "Air quality data not available"}
                
        except Exception as e:
            logger.error(f"Error fetching air quality: {e}")
            return {"api_status": "error", "message": str(e)}
    
    def _calculate_flood_risk(self, weather_data: Dict) -> str:
        """Calculate flood risk based on current conditions"""
        rain_1h = weather_data.get("rain", {}).get("1h", 0)
        humidity = weather_data["main"]["humidity"]
        
        if rain_1h > 10 or humidity > 90:
            return "High"
        elif rain_1h > 5 or humidity > 80:
            return "Medium"
        else:
            return "Low"
    
    def _calculate_heat_risk(self, weather_data: Dict) -> str:
        """Calculate heat risk based on temperature"""
        temp = weather_data["main"]["temp"]
        feels_like = weather_data["main"]["feels_like"]
        
        if temp > 40 or feels_like > 42:
            return "High"
        elif temp > 35 or feels_like > 38:
            return "Medium"
        else:
            return "Low"
    
    def _calculate_storm_risk(self, weather_data: Dict) -> str:
        """Calculate storm risk based on wind and conditions"""
        wind_speed = weather_data["wind"]["speed"]
        condition = weather_data["weather"][0]["main"]
        
        if wind_speed > 15 or condition in ["Thunderstorm", "Squall"]:
            return "High"
        elif wind_speed > 10 or condition == "Rain":
            return "Medium"
        else:
            return "Low"
    
    def _get_demo_data(self) -> Dict:
        """
        Return realistic demo data when API is unavailable
        Shows what the data looks like
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "location": "Pune, India",
            "temperature": 28.5,
            "feels_like": 30.2,
            "humidity": 65,
            "pressure": 1013,
            "wind_speed": 3.5,
            "wind_direction": 180,
            "clouds": 40,
            "visibility": 10000,
            "weather_condition": "Clouds",
            "weather_description": "scattered clouds",
            "rain_1h": 0,
            "rain_3h": 0,
            "flood_risk_level": "Low",
            "heat_risk_level": "Low",
            "storm_risk_level": "Low",
            "api_status": "demo",
            "data_source": "Demo Data (Get free API key at openweathermap.org)"
        }
    
    def _get_demo_forecast(self) -> Dict:
        """Demo forecast data"""
        return {
            "timestamp": datetime.now().isoformat(),
            "location": "Pune, India",
            "forecast_24h": [
                {"datetime": "2024-01-01 12:00:00", "temperature": 28, "humidity": 65, 
                 "rain_probability": 20, "rain_volume": 0, "weather": "Clouds", "description": "few clouds"}
            ],
            "total_rain_24h": 0,
            "max_rain_probability": 20,
            "flood_risk_24h": "Low",
            "api_status": "demo",
            "data_source": "Demo Data"
        }

