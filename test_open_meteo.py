"""
Test Open-Meteo Weather Integration
NO API KEY REQUIRED - Completely free!
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_current_weather():
    """Test current weather endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Current Weather for Pune")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/weather/current")
    
    if response.status_code == 200:
        data = response.json()
        weather = data["data"]
        
        print(f"✓ Status: {data['status']}")
        print(f"✓ Location: {weather['location']}")
        print(f"✓ Temperature: {weather['temperature']}°C")
        print(f"✓ Feels Like: {weather['feels_like']}°C")
        print(f"✓ Humidity: {weather['humidity']}%")
        print(f"✓ Precipitation: {weather['precipitation']} mm")
        print(f"✓ Wind Speed: {weather['wind_speed']} km/h")
        print(f"✓ Weather: {weather['weather_description']}")
        print(f"\n✓ Flood Risk: {weather['flood_risk_level']}")
        print(f"✓ Heat Risk: {weather['heat_risk_level']}")
        print(f"✓ Storm Risk: {weather['storm_risk_level']}")
        print(f"\n✓ Data Source: {weather['data_source']}")
        print(f"✓ API Status: {weather['api_status']}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)


def test_forecast():
    """Test hourly forecast endpoint"""
    print("\n" + "="*60)
    print("TEST 2: 24-Hour Forecast")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/weather/forecast?hours=24")
    
    if response.status_code == 200:
        data = response.json()
        forecast = data["data"]
        
        print(f"✓ Status: {data['status']}")
        print(f"✓ Location: {forecast['location']}")
        print(f"✓ Forecast Hours: {forecast['forecast_hours']}")
        
        summary = forecast["summary"]
        print(f"\n✓ Total Rain (24h): {summary['total_precipitation_mm']} mm")
        print(f"✓ Max Temperature: {summary['max_temperature']}°C")
        print(f"✓ Max Wind Speed: {summary['max_wind_speed']} km/h")
        
        print(f"\n✓ Flood Risk (24h): {summary['flood_risk']}")
        print(f"✓ Heat Risk (24h): {summary['heat_risk']}")
        print(f"✓ Storm Risk (24h): {summary['storm_risk']}")
        
        print(f"\n✓ First 3 hours forecast:")
        for i, hour in enumerate(forecast["hourly_data"][:3]):
            print(f"  Hour {i+1}: {hour['temperature']}°C, {hour['precipitation']}mm, {hour['weather_description']}")
        
        print(f"\n✓ Data Source: {forecast['data_source']}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)


def test_disaster_risk():
    """Test disaster risk assessment endpoint"""
    print("\n" + "="*60)
    print("TEST 3: Disaster Risk Assessment")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/weather/disaster-risk")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"✓ Status: {data['status']}")
        print(f"✓ Location: {data['location']}")
        
        current = data["current_conditions"]
        print(f"\n✓ Current Conditions:")
        print(f"  Temperature: {current['temperature']}°C")
        print(f"  Precipitation: {current['precipitation']} mm")
        print(f"  Wind Speed: {current['wind_speed']} km/h")
        print(f"  Humidity: {current['humidity']}%")
        print(f"  Weather: {current['weather']}")
        
        risks = data["risk_assessment"]
        print(f"\n✓ Flood Risk:")
        print(f"  Current: {risks['flood_risk']['current']}")
        print(f"  24h Forecast: {risks['flood_risk']['forecast_24h']}")
        print(f"  Expected Rain: {risks['flood_risk']['total_rain_24h']} mm")
        
        print(f"\n✓ Heat Risk:")
        print(f"  Current: {risks['heat_risk']['current']}")
        print(f"  24h Forecast: {risks['heat_risk']['forecast_24h']}")
        print(f"  Max Temp: {risks['heat_risk']['max_temp_24h']}°C")
        
        print(f"\n✓ Storm Risk:")
        print(f"  Current: {risks['storm_risk']['current']}")
        print(f"  24h Forecast: {risks['storm_risk']['forecast_24h']}")
        print(f"  Max Wind: {risks['storm_risk']['max_wind_24h']} km/h")
        
        print(f"\n✓ Data Source: {data['data_source']}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)


def test_pune_overview():
    """Test Pune weather overview endpoint"""
    print("\n" + "="*60)
    print("TEST 4: Pune Weather Overview")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/weather/pune-overview")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"✓ Status: {data['status']}")
        print(f"✓ City: {data['city']}")
        
        current = data["current"]
        print(f"\n✓ Current Weather:")
        print(f"  Temperature: {current['temperature']}°C (feels like {current['feels_like']}°C)")
        print(f"  Humidity: {current['humidity']}%")
        print(f"  Precipitation: {current['precipitation']} mm")
        print(f"  Wind: {current['wind_speed']} km/h")
        print(f"  Pressure: {current['pressure']} hPa")
        print(f"  Conditions: {current['weather']}")
        
        forecast = data["forecast_48h"]
        print(f"\n✓ 48-Hour Forecast:")
        print(f"  Total Rain: {forecast['total_rain']} mm")
        print(f"  Max Temperature: {forecast['max_temperature']}°C")
        print(f"  Max Wind: {forecast['max_wind']} km/h")
        
        risks = data["disaster_risks"]
        print(f"\n✓ Disaster Risks:")
        print(f"  Flood: {risks['flood']['current']} (forecast: {risks['flood']['forecast']})")
        print(f"  Heat: {risks['heat']['current']} (forecast: {risks['heat']['forecast']})")
        print(f"  Storm: {risks['storm']['current']} (forecast: {risks['storm']['forecast']})")
        
        print(f"\n✓ Next 3 Hours:")
        for hour in data["hourly_forecast"][:3]:
            print(f"  {hour['datetime']}: {hour['temperature']}°C, {hour['weather_description']}")
        
        print(f"\n✓ Data Source: {data['data_source']}")
        print(f"✓ API Info: {data['api_info']}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)


def test_custom_location():
    """Test weather for custom location"""
    print("\n" + "="*60)
    print("TEST 5: Custom Location (Mumbai)")
    print("="*60)
    
    # Mumbai coordinates
    lat = 19.0760
    lon = 72.8777
    
    response = requests.get(f"{BASE_URL}/api/weather/current?latitude={lat}&longitude={lon}")
    
    if response.status_code == 200:
        data = response.json()
        weather = data["data"]
        
        print(f"✓ Location: {weather['location']}")
        print(f"✓ Temperature: {weather['temperature']}°C")
        print(f"✓ Weather: {weather['weather_description']}")
        print(f"✓ Precipitation: {weather['precipitation']} mm")
    else:
        print(f"✗ Error: {response.status_code}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("OPEN-METEO WEATHER API INTEGRATION TEST")
    print("NO API KEY REQUIRED - Completely Free!")
    print("="*60)
    
    try:
        test_current_weather()
        test_forecast()
        test_disaster_risk()
        test_pune_overview()
        test_custom_location()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS COMPLETED!")
        print("="*60)
        print("\nAPI Endpoints Available:")
        print("  GET /api/weather/current")
        print("  GET /api/weather/forecast")
        print("  GET /api/weather/disaster-risk")
        print("  GET /api/weather/pune-overview")
        print("\nAPI Documentation:")
        print("  http://localhost:8000/docs")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to server")
        print("Make sure the server is running:")
        print("  python run_local.py")
    except Exception as e:
        print(f"\n✗ Error: {e}")
