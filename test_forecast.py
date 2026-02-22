"""
Test Time-Series Forecasting System
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_flood_forecast():
    """Test flood risk prediction"""
    print("\n" + "="*60)
    print("TEST 1: Flood Risk Prediction")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/forecast/flood-risk")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"✓ Model: {data['model']}")
        print(f"✓ Current rainfall: {data['current_conditions']['rainfall']} mm")
        print(f"✓ Current risk: {data['current_conditions']['risk_level']}")
        
        if data['next_alert']:
            alert = data['next_alert']
            print(f"\n⚠️  ALERT PREDICTED:")
            print(f"   Risk Level: {alert['risk_level']}")
            print(f"   In: {alert['hour']} hours")
            print(f"   Cumulative Rain: {alert['cumulative_rainfall']} mm")
            print(f"   Confidence: {alert['confidence']*100:.0f}%")
        else:
            print(f"\n✓ No high-risk conditions predicted")
        
        print(f"\n📊 24h Summary:")
        print(f"   Max Rainfall: {data['summary']['max_rainfall_24h']} mm")
        print(f"   High Risk Hours: {data['summary']['high_risk_hours']}")
        print(f"   Model Accuracy: {data['summary']['model_accuracy']*100:.0f}%")
        
        print(f"\n💡 Recommendations:")
        for rec in data['recommendations']:
            print(f"   {rec}")
    else:
        print(f"✗ Error: {response.status_code}")

def test_temperature_forecast():
    """Test temperature trend prediction"""
    print("\n" + "="*60)
    print("TEST 2: Temperature Trend Prediction")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/forecast/temperature-trend")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"✓ Current temperature: {data['current_temperature']}°C")
        print(f"✓ Trend: {data['trend']}")
        
        print(f"\n📊 24h Summary:")
        print(f"   Max Temperature: {data['summary']['max_temp_24h']}°C")
        print(f"   Min Temperature: {data['summary']['min_temp_24h']}°C")
        print(f"   Average: {data['summary']['avg_temp_24h']}°C")
        print(f"   Heat Wave Hours: {data['summary']['heat_wave_hours']}")
        
        # Show next 6 hours
        print(f"\n⏰ Next 6 Hours:")
        for pred in data['predictions'][:6]:
            print(f"   +{pred['hour']}h: {pred['temperature']}°C - {pred['heat_risk']}")
    else:
        print(f"✗ Error: {response.status_code}")

def test_risk_evolution():
    """Test risk evolution prediction"""
    print("\n" + "="*60)
    print("TEST 3: Risk Evolution Prediction")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/forecast/risk-evolution?current_risk=55")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"✓ Model: {data['model']}")
        print(f"✓ Current risk: {data['current_risk']}")
        
        print(f"\n📊 24h Summary:")
        print(f"   Peak Risk: {data['summary']['peak_risk']}")
        print(f"   Peak Hour: +{data['summary']['peak_hour']}h")
        print(f"   Average Risk: {data['summary']['avg_risk_24h']}")
        print(f"   Risk Increasing: {data['summary']['risk_increasing']}")
        print(f"   Max Increase: +{data['summary']['max_increase']}")
        
        # Show critical hours
        critical_hours = [p for p in data['predictions'] if p['risk_level'] in ['HIGH', 'CRITICAL']]
        if critical_hours:
            print(f"\n⚠️  Critical Hours:")
            for pred in critical_hours[:5]:
                print(f"   +{pred['hour']}h: {pred['risk_score']:.1f} - {pred['risk_level']}")
    else:
        print(f"✗ Error: {response.status_code}")

def test_comprehensive():
    """Test comprehensive forecast"""
    print("\n" + "="*60)
    print("TEST 4: Comprehensive Forecast")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/forecast/comprehensive")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"✓ Status: {data['status']}")
        print(f"✓ Location: {data['location']}")
        
        print(f"\n🌤️  Current Conditions:")
        curr = data['current_conditions']
        print(f"   Temperature: {curr['temperature']}°C")
        print(f"   Precipitation: {curr['precipitation']} mm")
        print(f"   Wind: {curr['wind_speed']} km/h")
        print(f"   Weather: {curr['weather']}")
        
        print(f"\n🤖 Model Info:")
        model = data['model_info']
        print(f"   Type: {model['type']}")
        print(f"   Methods: {', '.join(model['methods'])}")
        print(f"   Accuracy: {model['accuracy']*100:.0f}%")
        print(f"   Horizon: {model['forecast_horizon']}")
        
        print(f"\n💡 Combined Recommendations:")
        for rec in data['combined_recommendations'][:5]:
            print(f"   {rec}")
    else:
        print(f"✗ Error: {response.status_code}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TIME-SERIES FORECASTING SYSTEM TEST")
    print("AI-Powered Disaster Prediction")
    print("="*60)
    
    try:
        test_flood_forecast()
        test_temperature_forecast()
        test_risk_evolution()
        test_comprehensive()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS COMPLETED!")
        print("="*60)
        print("\nAPI Endpoints:")
        print("  GET /api/forecast/flood-risk")
        print("  GET /api/forecast/temperature-trend")
        print("  GET /api/forecast/risk-evolution")
        print("  GET /api/forecast/comprehensive")
        print("  GET /api/forecast/pune-forecast")
        print("\nDashboard:")
        print("  http://localhost:8000/static/forecast_dashboard.html")
        print("\nAPI Documentation:")
        print("  http://localhost:8000/docs")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to server")
        print("Make sure the server is running:")
        print("  python run_local.py")
    except Exception as e:
        print(f"\n✗ Error: {e}")
