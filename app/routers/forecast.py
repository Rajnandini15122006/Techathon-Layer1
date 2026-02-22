"""
Forecast API Router
Time-series predictions for disaster risk
"""
from fastapi import APIRouter, HTTPException, Query
from app.services.forecast_engine import get_forecast_engine
from app.services.open_meteo_service import get_open_meteo_service

router = APIRouter(prefix="/api/forecast", tags=["forecast"])
forecast_engine = get_forecast_engine()
weather_service = get_open_meteo_service()


@router.get("/flood-risk")
async def predict_flood_risk(
    latitude: float = Query(18.5204, description="Latitude"),
    longitude: float = Query(73.8567, description="Longitude")
):
    """
    Predict flood risk for next 24 hours using time-series analysis
    
    Returns:
    - Hour-by-hour predictions
    - Next alert timing
    - Model accuracy
    - Recommendations
    """
    try:
        # Get current weather
        current = weather_service.get_current_weather(latitude, longitude)
        
        # Get forecast
        forecast = weather_service.get_hourly_forecast(latitude, longitude, hours=24)
        
        # Predict flood risk
        prediction = forecast_engine.predict_flood_risk(
            current_rainfall=current['precipitation'],
            forecast_rainfall=forecast['hourly_data'],
            current_drain_stress=0.5  # Default, can be calculated from USPS
        )
        
        return prediction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/temperature-trend")
async def predict_temperature_trend(
    latitude: float = Query(18.5204, description="Latitude"),
    longitude: float = Query(73.8567, description="Longitude")
):
    """
    Predict temperature trend and heat risk for next 24 hours
    
    Returns:
    - Temperature predictions
    - Heat risk levels
    - Trend analysis
    """
    try:
        # Get current weather
        current = weather_service.get_current_weather(latitude, longitude)
        
        # Get forecast
        forecast = weather_service.get_hourly_forecast(latitude, longitude, hours=24)
        
        # Predict temperature trend
        prediction = forecast_engine.predict_temperature_trend(
            current_temp=current['temperature'],
            forecast_temps=forecast['hourly_data']
        )
        
        return prediction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk-evolution")
async def predict_risk_evolution(
    current_risk: float = Query(50.0, description="Current USPS risk score (0-100)", ge=0, le=100),
    latitude: float = Query(18.5204, description="Latitude"),
    longitude: float = Query(73.8567, description="Longitude")
):
    """
    Predict how overall risk will evolve over next 24 hours
    
    Returns:
    - Hour-by-hour risk predictions
    - Peak risk timing
    - Risk trend analysis
    """
    try:
        # Get forecast
        forecast = weather_service.get_hourly_forecast(latitude, longitude, hours=24)
        
        # Predict risk evolution
        prediction = forecast_engine.predict_risk_evolution(
            current_risk=current_risk,
            weather_forecast=forecast['hourly_data']
        )
        
        return prediction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comprehensive")
async def get_comprehensive_forecast(
    current_risk: float = Query(50.0, description="Current USPS risk score", ge=0, le=100),
    latitude: float = Query(18.5204, description="Latitude"),
    longitude: float = Query(73.8567, description="Longitude")
):
    """
    Get comprehensive forecast including all predictions
    
    Returns:
    - Flood risk predictions
    - Temperature trend
    - Risk evolution
    - Combined recommendations
    """
    try:
        # Get current weather
        current = weather_service.get_current_weather(latitude, longitude)
        
        # Get forecast
        forecast = weather_service.get_hourly_forecast(latitude, longitude, hours=24)
        
        # Get all predictions
        flood_pred = forecast_engine.predict_flood_risk(
            current_rainfall=current['precipitation'],
            forecast_rainfall=forecast['hourly_data'],
            current_drain_stress=0.5
        )
        
        temp_pred = forecast_engine.predict_temperature_trend(
            current_temp=current['temperature'],
            forecast_temps=forecast['hourly_data']
        )
        
        risk_pred = forecast_engine.predict_risk_evolution(
            current_risk=current_risk,
            weather_forecast=forecast['hourly_data']
        )
        
        # Combine recommendations
        all_recommendations = []
        all_recommendations.extend(flood_pred.get('recommendations', []))
        
        if temp_pred['summary']['heat_wave_hours'] > 0:
            all_recommendations.append(
                f"🌡️ Heat wave conditions expected for {temp_pred['summary']['heat_wave_hours']} hours"
            )
        
        if risk_pred['summary']['risk_increasing']:
            all_recommendations.append(
                f"📈 Overall risk increasing by {risk_pred['summary']['max_increase']:.1f} points"
            )
        
        return {
            'status': 'success',
            'timestamp': current['timestamp'],
            'location': current['location'],
            'current_conditions': {
                'temperature': current['temperature'],
                'precipitation': current['precipitation'],
                'wind_speed': current['wind_speed'],
                'weather': current['weather_description']
            },
            'flood_forecast': flood_pred,
            'temperature_forecast': temp_pred,
            'risk_forecast': risk_pred,
            'combined_recommendations': all_recommendations,
            'model_info': {
                'type': 'Time-Series Forecasting',
                'methods': ['Exponential Smoothing', 'Threshold Analysis', 'Pattern Recognition'],
                'accuracy': flood_pred['summary']['model_accuracy'],
                'forecast_horizon': '24 hours'
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pune-forecast")
async def get_pune_forecast():
    """
    Get forecast specifically for Pune with current USPS data
    
    Convenience endpoint for main dashboard
    """
    try:
        # Use Pune coordinates
        return await get_comprehensive_forecast(
            current_risk=55.0,  # Can be fetched from USPS API
            latitude=18.5204,
            longitude=73.8567
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
