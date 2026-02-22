"""
Quick verification script to check if Open-Meteo integration is working
"""
import requests
import sys

BASE_URL = "http://localhost:8000"

def check_server():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=2)
        return response.status_code == 200
    except:
        return False

def test_weather_api():
    """Test weather API endpoints"""
    print("\n" + "="*60)
    print("VERIFYING OPEN-METEO INTEGRATION")
    print("="*60)
    
    # Check server
    print("\n1. Checking if server is running...")
    if not check_server():
        print("   ✗ Server is NOT running!")
        print("   → Start server with: python run_local.py")
        return False
    print("   ✓ Server is running")
    
    # Test current weather
    print("\n2. Testing /api/weather/current...")
    try:
        response = requests.get(f"{BASE_URL}/api/weather/current", timeout=5)
        if response.status_code == 200:
            data = response.json()
            weather = data['data']
            print(f"   ✓ API working!")
            print(f"   → Temperature: {weather['temperature']}°C")
            print(f"   → Humidity: {weather['humidity']}%")
            print(f"   → Wind: {weather['wind_speed']} km/h")
            print(f"   → Precipitation: {weather['precipitation']} mm")
            print(f"   → Weather: {weather['weather_description']}")
        else:
            print(f"   ✗ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test disaster risk
    print("\n3. Testing /api/weather/disaster-risk...")
    try:
        response = requests.get(f"{BASE_URL}/api/weather/disaster-risk", timeout=5)
        if response.status_code == 200:
            data = response.json()
            risks = data['risk_assessment']
            print(f"   ✓ Risk assessment working!")
            print(f"   → Flood Risk (Now): {risks['flood_risk']['current']}")
            print(f"   → Flood Risk (24h): {risks['flood_risk']['forecast_24h']}")
            print(f"   → Heat Risk: {risks['heat_risk']['current']}")
            print(f"   → Storm Risk: {risks['storm_risk']['current']}")
        else:
            print(f"   ✗ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Check index.html
    print("\n4. Checking index.html integration...")
    try:
        response = requests.get(f"{BASE_URL}/static/index.html", timeout=5)
        if response.status_code == 200:
            content = response.text
            if '/api/weather/disaster-risk' in content:
                print("   ✓ Index.html uses Open-Meteo API")
            else:
                print("   ✗ Index.html NOT using Open-Meteo API")
                print("   → Still using old endpoint")
                return False
        else:
            print(f"   ✗ Could not load index.html")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Check test page
    print("\n5. Checking test page...")
    try:
        response = requests.get(f"{BASE_URL}/static/weather_test.html", timeout=5)
        if response.status_code == 200:
            print("   ✓ Test page available")
            print(f"   → Open: {BASE_URL}/static/weather_test.html")
        else:
            print("   ✗ Test page not found")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    return True

def main():
    success = test_weather_api()
    
    print("\n" + "="*60)
    if success:
        print("✓ ALL CHECKS PASSED!")
        print("="*60)
        print("\nYour Open-Meteo integration is working correctly!")
        print("\nNext steps:")
        print("1. Open test page:")
        print(f"   {BASE_URL}/static/weather_test.html")
        print("\n2. Open main dashboard:")
        print(f"   {BASE_URL}/static/index.html")
        print("\n3. Check the weather panels on the left sidebar")
        print("\n4. Weather data updates every 5 minutes automatically")
    else:
        print("✗ SOME CHECKS FAILED")
        print("="*60)
        print("\nTroubleshooting:")
        print("1. Make sure server is running: python run_local.py")
        print("2. Check server logs for errors")
        print("3. Try restarting the server")
        print("4. Run: python test_open_meteo.py")
    print("="*60 + "\n")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
