"""
Open-Meteo Weather Service
Free, open-source weather API - NO API KEY REQUIRED
Perfect for real-time disaster risk assessment

Features:
- Current weather conditions
- Hourly forecasts
- Precipitation data
- Temperature, humidity, wind
- Completely free, unlimited requests
"""
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
import aiohttp

logger = logging.getLogger(__name__)


class OpenMeteoService:
    """
    Fetches real-time weather data using Open-Meteo API
    NO API KEY REQUIRED - Completely free and open source
    """
    
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1"
        
        # Pune coordinates
        self.pune_lat = 18.5204
        self.pune_lon = 73.8567
        
        logger.info("OpenMeteoService initialized - No API key required!")
    
    def get_current_weather(self, latitude: float = None, longitude: float = None) -> Dict:
        """
        Get current weather conditions for a location
        
        Args:
            latitude: Location latitude (defaults to Pune)
            longitude: Location longitude (defaults to Pune)
            
        Returns:
            Dictionary with current weather data
        """
        lat = latitude or self.pune_lat
        lon = longitude or self.pune_lon
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "precipitation",
                    "rain",
                    "showers",
                    "snowfall",
                    "weather_code",
                    "cloud_cover",
                    "pressure_msl",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "wind_gusts_10m"
                ],
                "timezone": "Asia/Kolkata"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current = data["current"]
                
                # Calculate disaster risk indicators
                rain_mm = current.get("precipitation", 0)
                temp = current.get("temperature_2m", 25)
                wind_speed = current.get("wind_speed_10m", 0)
                humidity = current.get("relative_humidity_2m", 50)
                
                weather_data = {
                    "timestamp": current["time"],
                    "location": f"Lat: {lat:.4f}, Lon: {lon:.4f}",
                    "temperature": temp,
                    "feels_like": current.get("apparent_temperature", temp),
                    "humidity": humidity,
                    "pressure": current.get("pressure_msl", 1013),
                    "wind_speed": wind_speed,
                    "wind_direction": current.get("wind_direction_10m", 0),
                    "wind_gusts": current.get("wind_gusts_10m", 0),
                    "clouds": current.get("cloud_cover", 0),
                    "precipitation": rain_mm,
                    "rain": current.get("rain", 0),
                    "showers": current.get("showers", 0),
                    "weather_code": current.get("weather_code", 0),
                    "weather_description": self._get_weather_description(current.get("weather_code", 0)),
                    
                    # Disaster risk indicators
                    "flood_risk_level": self._calculate_flood_risk(rain_mm, humidity),
                    "heat_risk_level": self._calculate_heat_risk(temp),
                    "storm_risk_level": self._calculate_storm_risk(wind_speed, current.get("weather_code", 0)),
                    
                    "api_status": "live",
                    "data_source": "Open-Meteo (Free API)"
                }
                
                logger.info(f"✓ Weather data: {temp}°C, {rain_mm}mm rain, {wind_speed}km/h wind")
                return weather_data
            else:
                logger.warning(f"Open-Meteo API returned status {response.status_code}")
                return self._get_fallback_data(lat, lon)
                
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return self._get_fallback_data(lat, lon)
    
    def get_hourly_forecast(
        self, 
        latitude: float = None, 
        longitude: float = None,
        hours: int = 24
    ) -> Dict:
        """
        Get hourly weather forecast
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            hours: Number of hours to forecast (default 24)
            
        Returns:
            Dictionary with hourly forecast data
        """
        lat = latitude or self.pune_lat
        lon = longitude or self.pune_lon
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "precipitation",
                    "rain",
                    "showers",
                    "weather_code",
                    "wind_speed_10m",
                    "wind_gusts_10m"
                ],
                "forecast_days": min(7, (hours // 24) + 1),
                "timezone": "Asia/Kolkata"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                hourly = data["hourly"]
                
                # Process hourly data
                forecast_list = []
                for i in range(min(hours, len(hourly["time"]))):
                    forecast_list.append({
                        "datetime": hourly["time"][i],
                        "temperature": hourly["temperature_2m"][i],
                        "humidity": hourly["relative_humidity_2m"][i],
                        "precipitation": hourly["precipitation"][i],
                        "rain": hourly["rain"][i],
                        "showers": hourly["showers"][i],
                        "weather_code": hourly["weather_code"][i],
                        "weather_description": self._get_weather_description(hourly["weather_code"][i]),
                        "wind_speed": hourly["wind_speed_10m"][i],
                        "wind_gusts": hourly["wind_gusts_10m"][i]
                    })
                
                # Calculate aggregate statistics
                total_rain = sum(f["precipitation"] for f in forecast_list)
                max_temp = max(f["temperature"] for f in forecast_list)
                max_wind = max(f["wind_speed"] for f in forecast_list)
                
                forecast_data = {
                    "timestamp": datetime.now().isoformat(),
                    "location": f"Lat: {lat:.4f}, Lon: {lon:.4f}",
                    "forecast_hours": hours,
                    "hourly_data": forecast_list,
                    "summary": {
                        "total_precipitation_mm": round(total_rain, 2),
                        "max_temperature": round(max_temp, 1),
                        "max_wind_speed": round(max_wind, 1),
                        "flood_risk": "High" if total_rain > 50 else "Medium" if total_rain > 20 else "Low",
                        "heat_risk": "High" if max_temp > 40 else "Medium" if max_temp > 35 else "Low",
                        "storm_risk": "High" if max_wind > 50 else "Medium" if max_wind > 30 else "Low"
                    },
                    "api_status": "live",
                    "data_source": "Open-Meteo (Free API)"
                }
                
                logger.info(f"✓ {hours}h forecast: {total_rain:.1f}mm rain expected")
                return forecast_data
            else:
                return self._get_fallback_forecast(lat, lon, hours)
                
        except Exception as e:
            logger.error(f"Error fetching forecast: {e}")
            return self._get_fallback_forecast(lat, lon, hours)
    
    async def get_grid_weather_async(
        self, 
        grid_cells: List[Dict]
    ) -> List[Dict]:
        """
        Fetch weather data for multiple grid cells asynchronously
        
        Args:
            grid_cells: List of grid cells with latitude/longitude
            
        Returns:
            List of grid cells with weather data added
        """
        async with aiohttp.ClientSession() as session:
            tasks = []
            for cell in grid_cells:
                task = self._fetch_cell_weather_async(
                    session, 
                    cell['latitude'], 
                    cell['longitude']
                )
                tasks.append(task)
            
            weather_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Add weather data to cells
            for cell, weather in zip(grid_cells, weather_results):
                if isinstance(weather, dict) and not isinstance(weather, Exception):
                    cell['weather'] = weather
                else:
                    cell['weather'] = self._get_fallback_data(
                        cell['latitude'], 
                        cell['longitude']
                    )
            
            return grid_cells
    
    async def _fetch_cell_weather_async(
        self, 
        session: aiohttp.ClientSession, 
        lat: float, 
        lon: float
    ) -> Dict:
        """Async fetch weather for a single cell"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": ["temperature_2m", "precipitation", "wind_speed_10m", "relative_humidity_2m"],
                "timezone": "Asia/Kolkata"
            }
            
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    current = data["current"]
                    return {
                        "temperature": current.get("temperature_2m", 25),
                        "precipitation": current.get("precipitation", 0),
                        "wind_speed": current.get("wind_speed_10m", 0),
                        "humidity": current.get("relative_humidity_2m", 50)
                    }
                else:
                    return self._get_fallback_data(lat, lon)
        except Exception as e:
            logger.error(f"Error fetching weather for ({lat}, {lon}): {e}")
            return self._get_fallback_data(lat, lon)
    
    def _get_weather_description(self, weather_code: int) -> str:
        """
        Convert WMO weather code to description
        https://open-meteo.com/en/docs
        """
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(weather_code, "Unknown")
    
    def _calculate_flood_risk(self, rain_mm: float, humidity: float) -> str:
        """Calculate flood risk based on precipitation and humidity"""
        if rain_mm > 10 or humidity > 90:
            return "High"
        elif rain_mm > 5 or humidity > 80:
            return "Medium"
        else:
            return "Low"
    
    def _calculate_heat_risk(self, temp: float) -> str:
        """Calculate heat risk based on temperature"""
        if temp > 40:
            return "High"
        elif temp > 35:
            return "Medium"
        else:
            return "Low"
    
    def _calculate_storm_risk(self, wind_speed: float, weather_code: int) -> str:
        """Calculate storm risk based on wind and weather conditions"""
        # Wind speed in km/h
        if wind_speed > 50 or weather_code in [95, 96, 99]:  # Thunderstorm codes
            return "High"
        elif wind_speed > 30 or weather_code in [80, 81, 82]:  # Rain shower codes
            return "Medium"
        else:
            return "Low"
    
    def _get_fallback_data(self, lat: float, lon: float) -> Dict:
        """Fallback data when API is unavailable"""
        return {
            "timestamp": datetime.now().isoformat(),
            "location": f"Lat: {lat:.4f}, Lon: {lon:.4f}",
            "temperature": 28.0,
            "feels_like": 30.0,
            "humidity": 65,
            "pressure": 1013,
            "wind_speed": 10,
            "wind_direction": 180,
            "wind_gusts": 15,
            "clouds": 40,
            "precipitation": 0,
            "rain": 0,
            "showers": 0,
            "weather_code": 2,
            "weather_description": "Partly cloudy",
            "flood_risk_level": "Low",
            "heat_risk_level": "Low",
            "storm_risk_level": "Low",
            "api_status": "fallback",
            "data_source": "Fallback Data"
        }
    
    def _get_fallback_forecast(self, lat: float, lon: float, hours: int) -> Dict:
        """Fallback forecast data"""
        return {
            "timestamp": datetime.now().isoformat(),
            "location": f"Lat: {lat:.4f}, Lon: {lon:.4f}",
            "forecast_hours": hours,
            "hourly_data": [],
            "summary": {
                "total_precipitation_mm": 0,
                "max_temperature": 28,
                "max_wind_speed": 10,
                "flood_risk": "Low",
                "heat_risk": "Low",
                "storm_risk": "Low"
            },
            "api_status": "fallback",
            "data_source": "Fallback Data"
        }


# Global instance
_service_instance: Optional[OpenMeteoService] = None


def get_open_meteo_service() -> OpenMeteoService:
    """Get or create global Open-Meteo service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = OpenMeteoService()
    return _service_instance
